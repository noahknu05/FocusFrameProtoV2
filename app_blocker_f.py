import threading
import time
import psutil

class AppBlocker:
    def __init__(self, active_titles, blocked_apps = [], whitelist=None):
        self.block_apps = False
        self.blocked_apps = blocked_apps
        self.app_state = "Off"
        self.game_state = "Off"
        self.active_titles = active_titles
        self.whitelist = whitelist if whitelist is not None else []
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.triggerd = False

        self._gamepaths =[
            r"C:\Program Files (x86)\Steam\steamapps\common",
            r"C:\Program Files\Epic Games",
            r"C:\Program Files (x86)\Epic Games",
            r"C:\Program Files (x86)\Battle.net\Games",
            r"C:\Riot Games",
        ]
        self._launcher_exes = {
            "steamwebhelper.exe",
            "epicgameslauncher.exe",
            "battle.net.exe",
            "riotclientservices.exe",
            "ubisoftconnect.exe",
        }


    def close_apps(self):
        seen_pids = []
        for pid, info in self.active_titles.items():
            if pid in seen_pids:
                continue
            seen_pids.append(pid)
            exe_path = info.get("exe_path", "")
            exe_name = info.get("exe", "").lower()

            if exe_name in self.whitelist:
                continue

            should_kill = False
            if self.game_state == "On":
                if any(exe_path.startswith(path) for path in self._gamepaths) or exe_name in self._launcher_exes:
                    should_kill = True

            if self.app_state == "On":
                if any(blocked.lower() in exe_name for blocked in self.blocked_apps):
                    should_kill = True
                

            if should_kill:
                try:
                    # Check if process still exists before attempting to kill
                    if not psutil.pid_exists(pid):
                        continue
                    
                    print("pid", pid, "info", info)
                    process = psutil.Process(pid)
                    # Kill entire process tree for launchers/games
                    for child in process.children(recursive=True):
                        child.terminate()
                    process.terminate()
                    print(f"Terminated: {info['title']} (PID: {pid})") 
                except Exception as e:
                    print(f"Failed to terminate {pid}: {e}")

    def _run(self):
        while self.block_apps:
            self.close_apps()
            time.sleep(1)
    
    def start(self):
        if not self.thread.is_alive():
            self.block_apps = True
            # Create new thread if the old one finished
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    
    def stop(self):
        self.block_apps = False


