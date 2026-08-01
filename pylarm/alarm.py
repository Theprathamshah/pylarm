from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import threading
import uuid


@dataclass
class Alarm:
    """Represents an alarm entry with a target datetime, label, active status, and ringtone."""
    time: datetime
    label: str
    is_active: bool = True
    ringtone: str = "default"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


class AlarmManager:
    """Manages scheduling and retrieval of alarms in a thread-safe and persistent manner."""
    
    def __init__(self, db_path: Path | None = None) -> None:
        self.alarms: list[Alarm] = []
        self._lock = threading.Lock()
        
        # Default persistence location: user home directory ~/.pylarm_db.json
        if db_path is None:
            self.db_path = Path.home() / ".pylarm_db.json"
        else:
            self.db_path = db_path
            
        self._load_from_disk()

    def _save_to_disk(self) -> None:
        """Saves current alarms state to a JSON file. Call this within a locked context."""
        serialized = []
        for alarm in self.alarms:
            serialized.append({
                "id": alarm.id,
                "time": alarm.time.isoformat(),
                "label": alarm.label,
                "is_active": alarm.is_active,
                "ringtone": alarm.ringtone
            })
        try:
            temp_path = self.db_path.with_suffix(".tmp")
            with open(temp_path, "w") as f:
                json.dump(serialized, f, indent=4)
            os.replace(temp_path, self.db_path)
        except Exception:
            pass

    def _load_from_disk(self) -> None:
        """Loads alarms from the JSON file database."""
        if not self.db_path.exists():
            return
        try:
            with open(self.db_path, "r") as f:
                data = json.load(f)
            alarms = []
            for item in data:
                if not item.get("is_active", True):
                    continue
                alarms.append(Alarm(
                    id=item["id"],
                    time=datetime.fromisoformat(item["time"]),
                    label=item["label"],
                    is_active=item["is_active"],
                    ringtone=item.get("ringtone", "default")
                ))
            with self._lock:
                self.alarms = alarms
        except Exception:
            with self._lock:
                self.alarms = []


    def add_alarm(self, time_str: str, label: str, ringtone: str = "default", *, _now: datetime | None = None) -> Alarm:
        """
        Parses a time string in 'HH:MM' format and adds a new alarm.
        
        If the specified time has already passed for the current day,
        the alarm is scheduled for the same time on the following day.
        
        Args:
            time_str: The alarm time in 'HH:MM' format (24-hour clock).
            label: A descriptive label for the alarm.
            ringtone: Name of the selected ringtone. Defaults to "default".
            _now: Optional datetime override for testing. Defaults to datetime.now().
            
        Returns:
            The created Alarm instance.
            
        Raises:
            ValueError: If the time_str is not in the correct 'HH:MM' format.
        """
        try:
            parsed_time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError as e:
            raise ValueError(
                f"Invalid time format '{time_str}'. Expected 'HH:MM' (24-hour clock)."
            ) from e

        now = _now or datetime.now()
        # Combine today's date with the parsed time
        alarm_datetime = datetime.combine(now.date(), parsed_time)

        # If the alarm time is in the past or exactly now, schedule it for tomorrow
        if alarm_datetime <= now:
            alarm_datetime += timedelta(days=1)

        alarm = Alarm(time=alarm_datetime, label=label, ringtone=ringtone)
        with self._lock:
            self.alarms.append(alarm)
            self._save_to_disk()
        return alarm

    def get_due_alarms(self, *, _now: datetime | None = None) -> list[Alarm]:
        """
        Retrieves all active alarms that are due (alarm time <= current time).
        
        Removes the triggered alarms from memory and disk to prevent database bloating.
        
        Args:
            _now: Optional datetime override for testing. Defaults to datetime.now().
            
        Returns:
            A list of due Alarm instances.
        """
        now = _now or datetime.now()
        due_alarms: list[Alarm] = []
        
        with self._lock:
            remaining_alarms = []
            for alarm in self.alarms:
                if alarm.is_active and alarm.time <= now:
                    alarm.is_active = False
                    due_alarms.append(alarm)
                else:
                    remaining_alarms.append(alarm)
            
            if due_alarms:
                self.alarms = remaining_alarms
                self._save_to_disk()
                
        return due_alarms

    def get_all_alarms(self) -> list[Alarm]:
        """
        Returns a thread-safe snapshot of all scheduled alarms.
        
        Returns:
            A list of Alarm instances.
        """
        with self._lock:
            return list(self.alarms)
