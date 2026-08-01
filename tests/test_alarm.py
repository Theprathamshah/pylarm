import unittest
from datetime import datetime, timedelta
from pylarm.alarm import Alarm, AlarmManager


class TestAlarm(unittest.TestCase):
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
        manager = AlarmManager()
        
        mock_now = datetime(2026, 8, 1, 10, 0)
        
        
        alarm = manager.add_alarm("12:00", "Lunch", _now=mock_now)
        
        self.assertEqual(alarm.time, datetime(2026, 8, 1, 12, 0))
        self.assertEqual(alarm.label, "Lunch")
        self.assertTrue(alarm.is_active)
        self.assertIn(alarm, manager.alarms)

    def test_add_alarm_past_today_schedules_tomorrow(self):
        manager = AlarmManager()
        
        mock_now = datetime(2026, 8, 1, 10, 0)
        
        
        alarm = manager.add_alarm("09:00", "Morning exercise", _now=mock_now)
        
        
        self.assertEqual(alarm.time, datetime(2026, 8, 2, 9, 0))
        self.assertEqual(alarm.label, "Morning exercise")
        self.assertTrue(alarm.is_active)

    def test_add_alarm_invalid_format(self):
        manager = AlarmManager()
        
        with self.assertRaises(ValueError):
            manager.add_alarm("25:00", "Invalid Hour")
            
        with self.assertRaises(ValueError):
            manager.add_alarm("12-00", "Invalid Separator")

        with self.assertRaises(ValueError):
            manager.add_alarm("abc", "Non-numeric")

    def test_get_due_alarms(self):
        manager = AlarmManager()
        mock_now = datetime(2026, 8, 1, 10, 0)
        
        due_alarm_1 = Alarm(time=datetime(2026, 8, 1, 9, 30), label="Due 1")
        due_alarm_2 = Alarm(time=datetime(2026, 8, 1, 10, 0), label="Due 2 (exact)")
        future_alarm = Alarm(time=datetime(2026, 8, 1, 10, 30), label="Future")
        inactive_past_alarm = Alarm(time=datetime(2026, 8, 1, 9, 0), label="Already inactive", is_active=False)
        
        manager.alarms.extend([due_alarm_1, due_alarm_2, future_alarm, inactive_past_alarm])
        
        
        due = manager.get_due_alarms(_now=mock_now)
        
        self.assertEqual(len(due), 2)
        self.assertIn(due_alarm_1, due)
        self.assertIn(due_alarm_2, due)
        self.assertNotIn(future_alarm, due)
        self.assertNotIn(inactive_past_alarm, due)
        
        
        self.assertFalse(due_alarm_1.is_active)
        self.assertFalse(due_alarm_2.is_active)
        self.assertTrue(future_alarm.is_active)
        
        
        due_again = manager.get_due_alarms(_now=mock_now)
        self.assertEqual(len(due_again), 0)


if __name__ == "__main__":
    unittest.main()
