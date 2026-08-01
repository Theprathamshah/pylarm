import os
import subprocess
import sys
import time
import threading
from datetime import datetime
from pylarm.alarm import AlarmManager


def play_alarm_sound(duration_seconds: int = 30) -> None:
    """Plays the macOS system sound in a loop for a set duration in the background."""
    def sound_loop():
        sound_path = "/System/Library/Sounds/Glass.aiff"
        start_time = time.time()
        use_afplay = os.path.exists(sound_path)
        
        while time.time() - start_time < duration_seconds:
            if use_afplay:
                try:
                    subprocess.run(
                        ["afplay", sound_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except Exception:
                    use_afplay = False  
            else:
                sys.stdout.write("\a")
                sys.stdout.flush()
                time.sleep(1)

    threading.Thread(target=sound_loop, daemon=True).start()


def run_alarm_daemon(manager: AlarmManager, stop_event: threading.Event) -> None:
    """Daemon thread loop that checks for due alarms every second."""
    while not stop_event.is_set():
        try:
            due_alarms = manager.get_due_alarms()
            for alarm in due_alarms:
                
                play_alarm_sound(duration_seconds=30)
                
                
                sys.stdout.write("\n" + "=" * 50 + "\n")
                sys.stdout.write("🔔   ALARM TRIGGERED!   🔔\n".center(50))
                sys.stdout.write(f"Label: {alarm.label}".center(50) + "\n")
                sys.stdout.write(f"Time:  {alarm.time.strftime('%Y-%m-%d %H:%M:%S')}".center(50) + "\n")
                sys.stdout.write("=" * 50 + "\n")
                sys.stdout.write(r"""
  ____  __   __ _         _     ____  __  __ 
 |  _ \ \ \ / /| |       / \   |  _ \|  \/  |
 | |_) | \ V / | |      / _ \  | |_) | |\/| |
 |  __/   | |  | |___  / ___ \ |  _ <| |  | |
 |_|      |_|  |_____|/_/   \_\|_| \_\|_|  |_|
                                           
""")
                sys.stdout.write("\n(pylarm) Enter command (add, list, exit): ")
                sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"\nError in background daemon: {e}\n")
            sys.stderr.flush()
        
        
        for _ in range(10):
            if stop_event.is_set():
                break
            time.sleep(0.1)



def main() -> None:
    manager = AlarmManager()
    stop_event = threading.Event()
    
    
    daemon_thread = threading.Thread(
        target=run_alarm_daemon, 
        args=(manager, stop_event), 
        daemon=True
    )
    daemon_thread.start()
    
    print("=== PyLarm CLI Alarm Clock ===")
    print("Available commands: add, list, exit")
    print("==============================")
    
    while True:
        try:
            command = input("(pylarm) Enter command (add, list, exit): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting pylarm. Goodbye!")
            stop_event.set()
            break
            
        if command == "exit":
            print("Exiting pylarm. Goodbye!")
            stop_event.set()
            break
            
        elif command == "add":
            time_str = input("Enter alarm time (HH:MM): ").strip()
            label = input("Enter alarm label: ").strip()
            
            try:
                alarm = manager.add_alarm(time_str, label)
                print(f"✅ Alarm successfully set for {alarm.time.strftime('%Y-%m-%d %H:%M:%S')}")
            except ValueError as e:
                print(f"❌ Error: {e}")
                
        elif command == "list":
            alarms = manager.get_all_alarms()
            if not alarms:
                print("No alarms scheduled.")
                continue
                
            print("\n--- Scheduled Alarms ---")
            for idx, alarm in enumerate(alarms, 1):
                status = "Active" if alarm.is_active else "Triggered/Inactive"
                print(f"{idx}. [{status}] Time: {alarm.time.strftime('%Y-%m-%d %H:%M:%S')} | Label: {alarm.label}")
            print("------------------------\n")
            
        elif command == "":
            continue
        else:
            print(f"Unknown command: '{command}'. Available commands: add, list, exit")


if __name__ == "__main__":
    main()
