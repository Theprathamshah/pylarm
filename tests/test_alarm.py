import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from pylarm.alarm import Alarm, AlarmManager


class TestAlarm(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory and file path for the test database
        self.temp_db_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_db_dir.name) / "test_alarms.json"

    def tearDown(self):
        # Clean up the temporary directory
        self.temp_db_dir.cleanup()

    def test_alarm_dataclass_initialization(self):
        target_time = datetime(2026, 8, 1, 12, 0)
        alarm = Alarm(time=target_time, label="Wake up", ringtone="Ping")
        
        self.assertEqual(alarm.time, target_time)
        self.assertEqual(alarm.label, "Wake up")
        self.assertEqual(alarm.ringtone, "Ping")
        self.assertTrue(alarm.is_active)
        self.assertTrue(isinstance(alarm.id, str))
        self.assertTrue(len(alarm.id) > 0)

    def test_add_alarm_future_today(self):
        manager = AlarmManager(db_path=self.db_path)
        mock_now = datetime(2026, 8, 1, 10, 0)
        
        alarm = manager.add_alarm("12:00", "Lunch", _now=mock_now)
        
        self.assertEqual(alarm.time, datetime(2026, 8, 1, 12, 0))
        self.assertEqual(alarm.label, "Lunch")
        self.assertTrue(alarm.is_active)
        self.assertIn(alarm, manager.alarms)
        self.assertTrue(self.db_path.exists())

    def test_add_alarm_past_today_schedules_tomorrow(self):
        manager = AlarmManager(db_path=self.db_path)
        mock_now = datetime(2026, 8, 1, 10, 0)
        
        alarm = manager.add_alarm("09:00", "Morning exercise", _now=mock_now)
        
        self.assertEqual(alarm.time, datetime(2026, 8, 2, 9, 0))
        self.assertEqual(alarm.label, "Morning exercise")
        self.assertTrue(alarm.is_active)

    def test_add_alarm_invalid_format(self):
        manager = AlarmManager(db_path=self.db_path)
        
        with self.assertRaises(ValueError):
            manager.add_alarm("25:00", "Invalid Hour")
            
        with self.assertRaises(ValueError):
            manager.add_alarm("12-00", "Invalid Separator")

        with self.assertRaises(ValueError):
            manager.add_alarm("abc", "Non-numeric")

    def test_get_due_alarms(self):
        manager = AlarmManager(db_path=self.db_path)
        mock_now = datetime(2026, 8, 1, 10, 0)
        
        due_alarm_1 = Alarm(time=datetime(2026, 8, 1, 9, 30), label="Due 1")
        due_alarm_2 = Alarm(time=datetime(2026, 8, 1, 10, 0), label="Due 2 (exact)")
        future_alarm = Alarm(time=datetime(2026, 8, 1, 10, 30), label="Future")
        inactive_past_alarm = Alarm(time=datetime(2026, 8, 1, 9, 0), label="Already inactive", is_active=False)
        
        manager.alarms.extend([due_alarm_1, due_alarm_2, future_alarm, inactive_past_alarm])
        
        # Manually save to disk to emulate existing state
        with manager._lock:
            manager._save_to_disk()
        
        due = manager.get_due_alarms(_now=mock_now)
        
        self.assertEqual(len(due), 2)
        self.assertIn(due_alarm_1, due)
        self.assertIn(due_alarm_2, due)
        
        # Triggered alarms should be removed from memory
        self.assertNotIn(due_alarm_1, manager.alarms)
        self.assertNotIn(due_alarm_2, manager.alarms)
        self.assertIn(future_alarm, manager.alarms)
        
        # Reloading from disk should only contain the future alarm
        # because triggered alarms and inactive alarms are not stored
        manager2 = AlarmManager(db_path=self.db_path)
        self.assertEqual(len(manager2.alarms), 1)
        self.assertEqual(manager2.alarms[0].label, "Future")


    def test_persistence_load(self):
        # Create alarms, save, reload with a new manager instance and verify
        manager1 = AlarmManager(db_path=self.db_path)
        mock_now = datetime(2026, 8, 1, 10, 0)
        manager1.add_alarm("12:00", "Lunch", _now=mock_now)
        manager1.add_alarm("15:00", "Coffee", _now=mock_now)
        
        # Load from disk with new manager
        manager2 = AlarmManager(db_path=self.db_path)
        self.assertEqual(len(manager2.alarms), 2)
        self.assertEqual(manager2.alarms[0].label, "Lunch")
        self.assertEqual(manager2.alarms[1].label, "Coffee")


if __name__ == "__main__":
    unittest.main()
