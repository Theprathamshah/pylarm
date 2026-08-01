import os
import subprocess
import sys
import time
import threading
from datetime import datetime
from pylarm.alarm import AlarmManager


RINGTONES = {
    "darwin": {
        "1": ("Glass", "/System/Library/Sounds/Glass.aiff"),
        "2": ("Hero", "/System/Library/Sounds/Hero.aiff"),
        "3": ("Ping", "/System/Library/Sounds/Ping.aiff"),
        "4": ("Submarine", "/System/Library/Sounds/Submarine.aiff"),
        "5": ("Tink", "/System/Library/Sounds/Tink.aiff"),
        "6": ("Basso", "/System/Library/Sounds/Basso.aiff"),
    },
    "win32": {
        "1": ("Hand / Stop Alert", "SystemHand"),
        "2": ("Exclamation Alert", "SystemExclamation"),
        "3": ("Asterisk Sound", "SystemAsterisk"),
        "4": ("Question Sound", "SystemQuestion"),
        "5": ("Default Beep", "SystemDefault"),
    },
    "linux": {
        "1": ("Default Alarm", "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"),
        "2": ("System Bell", "/usr/share/sounds/ubuntu/stereo/bell.ogg"),
        "3": ("Complete Sound", "/usr/share/sounds/sound-theme-freedesktop/stereo/complete.oga"),
    }
}


def get_os_platform() -> str:
    """Standardizes OS platform check."""
    if sys.platform.startswith("linux"):
        return "linux"
    elif sys.platform == "win32":
        return "win32"
    elif sys.platform == "darwin":
        return "darwin"
    return "other"


def get_ringtone_name(ringtone_key: str) -> str:
    """Returns the human-readable name of the ringtone key on the current OS."""
    platform = get_os_platform()
    os_ringtones = RINGTONES.get(platform, {})
    entry = os_ringtones.get(ringtone_key)
    return entry[0] if entry else "Default (Beep)"


def play_alarm_sound(ringtone_key: str, duration_seconds: int = 30) -> None:
    """Plays the specified system sound in a loop for the specified duration, compatible with macOS, Windows, and Linux."""
    def fallback_bell(duration_seconds: float, start_time: float) -> None:
        """Standard terminal beep fallback."""
        sys.stdout.write("\a")
        sys.stdout.flush()
        time.sleep(1)

    def sound_loop():
        start_time = time.time()
        platform = get_os_platform()
        
        
        os_ringtones = RINGTONES.get(platform, {})
        sound_entry = os_ringtones.get(ringtone_key)
        
        
        if not sound_entry and os_ringtones:
            sound_entry = os_ringtones.get("1")
            
        sound_value = sound_entry[1] if sound_entry else None
        
        if platform == "win32":
            sound_alias = sound_value or "SystemHand"
            try:
                import winsound
                while time.time() - start_time < duration_seconds:
                    winsound.PlaySound(sound_alias, winsound.SND_ALIAS)
                    time.sleep(1)
            except Exception:
                try:
                    while time.time() - start_time < duration_seconds:
                        winsound.Beep(1000, 500)  
                        time.sleep(0.5)
                except Exception:
                    while time.time() - start_time < duration_seconds:
                        fallback_bell(duration_seconds, start_time)
                    
        elif platform == "darwin":
            sound_path = sound_value or "/System/Library/Sounds/Glass.aiff"
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
                    fallback_bell(duration_seconds, start_time)
                    
        elif platform == "linux":
            sound_path = sound_value
            
            if not sound_path or not os.path.exists(sound_path):
                linux_sounds = [
                    "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga",
                    "/usr/share/sounds/ubuntu/stereo/bell.ogg",
                    "/usr/share/sounds/sound-theme-freedesktop/stereo/complete.oga"
                ]
                sound_path = next((path for path in linux_sounds if os.path.exists(path)), None)
            
            players = ["paplay", "aplay", "play"]
            player = None
            for cmd in players:
                try:
                    if subprocess.call(["which", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                        player = cmd
                        break
                except Exception:
                    pass
            
            while time.time() - start_time < duration_seconds:
                if sound_path and player:
                    try:
                        subprocess.run(
                            [player, sound_path],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    except Exception:
                        fallback_bell(duration_seconds, start_time)
                else:
                    fallback_bell(duration_seconds, start_time)
        else:
            
            while time.time() - start_time < duration_seconds:
                fallback_bell(duration_seconds, start_time)

    threading.Thread(target=sound_loop, daemon=True).start()


def run_alarm_daemon(manager: AlarmManager, stop_event: threading.Event) -> None:
    """Daemon thread loop that checks for due alarms every second."""
    while not stop_event.is_set():
        try:
            due_alarms = manager.get_due_alarms()
            for alarm in due_alarms:
                
                play_alarm_sound(alarm.ringtone, duration_seconds=30)
                
                
                sys.stdout.write("\n" + "=" * 50 + "\n")
                sys.stdout.write("🔔   ALARM TRIGGERED!   🔔\n".center(50))
                sys.stdout.write(f"Label: {alarm.label}".center(50) + "\n")
                sys.stdout.write(f"Time:  {alarm.time.strftime('%Y-%m-%d %H:%M:%S')}".center(50) + "\n")
                sys.stdout.write(f"Tone:  {get_ringtone_name(alarm.ringtone)}".center(50) + "\n")
                sys.stdout.write("=" * 50 + "\n")
                sys.stdout.write(r"""
  ____ __   __ _        _     ____  __  __ 
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
            
            
            platform = get_os_platform()
            os_ringtones = RINGTONES.get(platform, {})
            ringtone_choice = "1"
            
            if os_ringtones:
                print("\nAvailable Ringtones:")
                for key, (name, _) in os_ringtones.items():
                    print(f"  {key}. {name}")
                
                choice = input("Select ringtone (default: 1): ").strip()
                if choice in os_ringtones:
                    ringtone_choice = choice
            
            try:
                alarm = manager.add_alarm(time_str, label, ringtone_choice)
                print(f"✅ Alarm successfully set for {alarm.time.strftime('%Y-%m-%d %H:%M:%S')} with ringtone '{get_ringtone_name(alarm.ringtone)}'")
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
                print(f"{idx}. [{status}] Time: {alarm.time.strftime('%Y-%m-%d %H:%M:%S')} | Label: {alarm.label} | Tone: {get_ringtone_name(alarm.ringtone)}")
            print("------------------------\n")
            
        elif command == "":
            continue
        else:
            print(f"Unknown command: '{command}'. Available commands: add, list, exit")


if __name__ == "__main__":
    main()
