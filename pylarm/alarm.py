from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
import uuid


@dataclass
class Alarm:
    """Represents an alarm entry with a target datetime, label, and active status."""
    time: datetime
    label: str
    is_active: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


class AlarmManager:
    """Manages scheduling and retrieval of alarms in a thread-safe manner."""
    
    def __init__(self) -> None:
        self.alarms: list[Alarm] = []
        self._lock = threading.Lock()

    def add_alarm(self, time_str: str, label: str, *, _now: datetime | None = None) -> Alarm:
        """
        Parses a time string in 'HH:MM' format and adds a new alarm.
        
        If the specified time has already passed for the current day,
        the alarm is scheduled for the same time on the following day.
        
        Args:
            time_str: The alarm time in 'HH:MM' format (24-hour clock).
            label: A descriptive label for the alarm.
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
        
        alarm_datetime = datetime.combine(now.date(), parsed_time)

        
        if alarm_datetime <= now:
            alarm_datetime += timedelta(days=1)

        alarm = Alarm(time=alarm_datetime, label=label)
        with self._lock:
            self.alarms.append(alarm)
        return alarm

    def get_due_alarms(self, *, _now: datetime | None = None) -> list[Alarm]:
        """
        Retrieves all active alarms that are due (alarm time <= current time).
        
        Marks the returned alarms as inactive.
        
        Args:
            _now: Optional datetime override for testing. Defaults to datetime.now().
            
        Returns:
            A list of due Alarm instances.
        """
        now = _now or datetime.now()
        due_alarms: list[Alarm] = []
        
        with self._lock:
            for alarm in self.alarms:
                if alarm.is_active and alarm.time <= now:
                    alarm.is_active = False
                    due_alarms.append(alarm)
                
        return due_alarms

    def get_all_alarms(self) -> list[Alarm]:
        """
        Returns a thread-safe snapshot of all scheduled alarms.
        
        Returns:
            A list of Alarm instances.
        """
        with self._lock:
            return list(self.alarms)
