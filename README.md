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

## Running the CLI Application

You can start the interactive CLI application by running the script from the root of the project:

```bash
python3 main.py
# Or run it as a module:
python3 -m pylarm
```

### CLI Commands:
- `add`: Add an alarm by entering a time in `HH:MM` format and a label.
- `list`: Show all scheduled alarms with their status.
- `exit`: Stop the application and background daemon thread.

## Running Tests

To run the unit test suite:

```bash
python3 -m unittest discover -s tests
```

