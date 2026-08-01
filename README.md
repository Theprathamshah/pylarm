# PyLarm - CLI Alarm Clock Core

PyLarm is a simple, clean, and highly testable Python backend for a CLI alarm clock. It contains pure business logic with no UI dependencies.

## Structure

- [pylarm/alarm.py](file:///Volumes/PortableSSD/projects/pylarm/pylarm/alarm.py): Defines the `Alarm` dataclass and the `AlarmManager`.
- [pylarm/__init__.py](file:///Volumes/PortableSSD/projects/pylarm/pylarm/__init__.py): Exposes `Alarm` and `AlarmManager`.
- [tests/test_alarm.py](file:///Volumes/PortableSSD/projects/pylarm/tests/test_alarm.py): Complete unit test coverage using Python's built-in `unittest` module.

## Usage Example

```python
from datetime import datetime
from pylarm import AlarmManager

# 1. Initialize the manager
manager = AlarmManager()

# 2. Add some alarms (format: HH:MM, Label)
# If the time is set in the past for today, it automatically schedules for tomorrow!
alarm1 = manager.add_alarm("14:30", "Lunch break")
alarm2 = manager.add_alarm("07:00", "Morning gym")

print(f"Scheduled: {alarm1.label} at {alarm1.time}")
print(f"Scheduled: {alarm2.label} at {alarm2.time}")

# 3. Retrieve and trigger due alarms
# Typically run this in a loop or ticker
due_alarms = manager.get_due_alarms()
for alarm in due_alarms:
    print(f"🔔 ALARM: {alarm.label} ({alarm.time})!")
```

## Running Tests

To run the unit test suite:

```bash
python3 -m unittest discover -s tests
```
