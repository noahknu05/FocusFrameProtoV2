import os.path
from unittest import case
import pywinctl as pwc
import psutil
import time
import threading
import datetime
from app_blocker_f import AppBlocker
from web_blocker_f import WebBlocker
from data_handler_f import DataHandler


class Focus:
    def __init__(self, tsip_programs_path=None, time_spent_on_screen_path=None):
        self.seen_pids = set()
        self.active_titles = {}
        
        self.start_time = time.time()


        self.whitelist = ["wallpaper32.exe", "python.exe", "ondedrive.exe", "msedgewebview2.exe"]
        self.ignored_paths = [r"C:\windows",
                              r"\Program Files (x86)\Microsoft\EdgeWebVie",
                               self.get_program_files_path("NVIDIA"),
                                 self.get_program_files_path("MSI"),
                                 self.get_program_files_path("WindowsApps")]
        
        self.blocked_apps = []

        self.time_tracking = {}  # Store accumulated time per app
        self.current_pid = None  # Track current active window
        self.last_check_time = time.time()  # Track when we last checked
        self.time_per_app = {}
        self.last_saved_time = {}  # Track what's already been saved to CSV

        self.app_blocker = AppBlocker(active_titles=self.active_titles, whitelist=self.whitelist, blocked_apps=self.blocked_apps)  # Initialize AppBlocker instance
        self.app_blocker.triggerd = False

        self.web_blocker = WebBlocker(blocked_sites=[])  # Initialize WebBlocker instance

        self.data_handler = DataHandler(
            whitelist=self.whitelist,
            tsip_programs_path=tsip_programs_path,
            time_spent_on_screen_path=time_spent_on_screen_path
        )  # Initialize DataHandler instance
        


    def get_program_files_path(self, name):
        normal = os.path.join(r"C:\Program Files", name)    
        x86 = os.path.join(r"C:\Program Files (x86)", name)
        if os.path.exists(normal):
            return normal
        elif os.path.exists(x86):       
            return x86
        return normal
    

    def session_time(self):
        return time.time() - self.start_time
    

            

    def gather_active_window_info(self): 
        """Continuously gathers window info in background thread"""
        while True:
            # Remove closed programs from active_titles
            dead_pids = [pid for pid in list(self.active_titles.keys()) if not psutil.pid_exists(pid)]
            for pid in dead_pids:
                del self.active_titles[pid]
            
            for win in pwc.getAllWindows():
                try:
                    pid = win.getPID()
                    process = psutil.Process(pid)
                    exe_path = process.exe()
                    stripped_exe = (exe_path).strip().lower()
                    if stripped_exe in self.whitelist:
                        continue
                    if win.title and exe_path:
                        if any(stripped_exe.startswith(ignored.strip().lower()) for ignored in self.ignored_paths):
                            continue
                        if pid in self.active_titles:
                            if self.active_titles[pid]["exe"] == "Chrome.exe":
                                self.active_titles[pid] = {"title": win.title,
                                    "exe": os.path.basename(exe_path), 
                                    "exe_path": exe_path}
                            elif exe_path in self.active_titles[pid].values() and win.title.strip().lower() in exe_path.strip().lower():
                                self.active_titles[pid]["title"] = win.title
                                self.active_titles[pid]["exe"] = os.path.basename(exe_path)
                                self.active_titles[pid]["exe_path"] = exe_path
                                
                            else:
                                continue
                        else:
                            self.active_titles[pid] = {"title": win.title,
                                                "exe": os.path.basename(exe_path), 
                                                "exe_path": exe_path}
                except Exception:
                    pass
            time.sleep(1)


    def display_active_windows_info(self):
        for pid in self.active_titles:            
            print("===============================================================")
            print(f"PID: {pid}")
            print(f"Title: {self.active_titles[pid]['title']}")
            print(f"EXE: {self.active_titles[pid]['exe']}")
            print(f"EXE Path: {self.active_titles[pid]['exe_path']}")
            print("===============================================================")

    def display_current_window_info(self):
        active_window = pwc.getActiveWindow()
        if active_window:
            try:
                time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print("===============================================================")
                print(f"Title: {active_window.title}")
                print("===============================================================")
            except Exception as e:
                print(f"Error", e)
        else:
            print("No active window detected.")
    


    def update_time_tracking(self):
        """Update time tracking for the current active window"""
        current_time = time.time()
        if self.current_pid and self.current_pid in self.active_titles:
            time_spent = current_time - self.last_check_time
            exe = self.active_titles[self.current_pid]['exe']
            
            if exe not in self.time_tracking:
                self.time_tracking[exe] = 0
            self.time_tracking[exe] += time_spent 
            self.last_check_time = current_time
    
    def track_time_used_in_windows(self):
        """Track time spent in different windows"""
        while True:
            active_window = pwc.getActiveWindow()
            current_time = time.time()
            if active_window:
                pid = active_window.getPID()
                
                # If window changed, record time for the previous window
                if self.current_pid and self.current_pid != pid:
                    time_spent = current_time - self.last_check_time
                    if self.current_pid in self.active_titles:
                        title = self.active_titles[self.current_pid]['title'] #For testing
                        exe = self.active_titles[self.current_pid]['exe']
                        
                        # Accumulate time
                        if exe not in self.time_tracking:
                            self.time_tracking[exe] = 0
                        self.time_tracking[exe] += time_spent
                                            
                    # Reset timer only when switching windows
                    self.last_check_time = current_time
                    self.current_pid = pid

                elif self.current_pid is None:
                    # Initialize on first window
                    self.current_pid = pid
                    self.last_check_time = current_time
            
            time.sleep(1)  # Check every 1 second

    
    def display_time_summary(self):
        """Display total time spent in each app"""        
        self.update_time_tracking()
        
        print("\n" + "="*60)
        print("TIME Spent on different apps")
        print("="*60)
        for exe, total_time in sorted(self.time_tracking.items(), key=lambda x: x[1], reverse=True):
            hours = int(total_time // 3600)
            minutes = int((total_time % 3600) // 60)
            seconds = int(total_time % 60)
            print(f"{exe:30s} | {hours:2d}h {minutes:2d}m {seconds:2d}s")
        print("="*60 + "\n")
    def save_time_data(self):
        """Save incremental time data - only saves the difference since last save"""
        while True:
            self.update_time_tracking()
            today = datetime.datetime.now().strftime("%Y-%m-%d")

            for exe, total_time in self.time_tracking.items():
                baseline = self.last_saved_time.get(exe, 0)
                time_diff = int(total_time - baseline)
                
                if time_diff > 0:
                    self.data_handler.update_data_frames(program=exe, seconds=time_diff, minutes=0, hours=0, date=today)
                    self.last_saved_time[exe] = total_time  # Update baseline after saving
            
            time.sleep(5)  # Save every 5 seconds
    
    def save_time_data_on_demand(self):
        """Save incremental time data on-demand (call this manually)"""
        self.update_time_tracking()
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        for exe, total_time in self.time_tracking.items():
            baseline = self.last_saved_time.get(exe, 0)
            time_diff = int(total_time - baseline)
            
            if time_diff > 0:
                self.data_handler.update_data_frames(program=exe, seconds=time_diff, minutes=0, hours=0, date=today)
                self.last_saved_time[exe] = total_time  # Update baseline after saving
    
    def start_background_tasks(self):
        t1 = threading.Thread(target=self.track_time_used_in_windows, daemon=True)
        t2 = threading.Thread(target=self.gather_active_window_info, daemon=True)
        t1.start()
        t2.start()
 
    def toggle_game_blocking(self):
        if self.app_blocker.game_state == "Off":
            self.app_blocker.game_state = "On"
        else:
            self.app_blocker.game_state = "Off"

        if self.app_blocker.game_state == "On" or self.app_blocker.app_state == "On":
            if not self.app_blocker.thread.is_alive():
                self.app_blocker.start()
        else:
            self.app_blocker.stop()
        
        print(f"Game Blocking is now: {self.app_blocker.game_state}")        
    def toggle_app_blocking(self):
        if self.app_blocker.app_state == "Off":
            self.app_blocker.app_state = "On"
        else:
            self.app_blocker.app_state = "Off"
        if self.app_blocker.game_state == "On" or self.app_blocker.app_state == "On":
            if not self.app_blocker.thread.is_alive():
                self.app_blocker.start()
        else:
            self.app_blocker.stop()

    def appblocker_test_menu(self):
        while True:
            if (self.app_blocker.app_state == "On" or self.app_blocker.game_state == "On") and not self.app_blocker.thread.is_alive():
                self.app_blocker.start()
            else:
                self.app_blocker.stop()  

            print("===============================================================")
            print("Appblocker MENU")
            print("\n1. Display Active Windows Info")
            print("2. Display Current Window Info")
            print(" ")
            print(f"3. Block Games {self.app_blocker.game_state} ")
            print(f"4. Block Apps {self.app_blocker.app_state} ")
            print(" ")
            print("5. Display Time Summary")
            print("6. Display Active Winodws")
            print("7. Active title list")
            print("8. Time tracking dict")
            print("0. Exit")
            app_menu_input = input("EnterCommad: ")

            match app_menu_input:
                case "1":
                    self.display_active_windows_info()
                case "2":
                    self.display_current_window_info()


                case "3":
                    if self.app_blocker.game_state == "Off":
                        self.app_blocker.game_state = "On"
                    else:
                        self.app_blocker.game_state = "Off"
                case "4":                    
                    if self.app_blocker.app_state == "Off":
                        self.app_blocker.app_state = "On"
                    else:
                        self.app_blocker.app_state = "Off"
                case "5":           
                    self.save_time_data_on_demand()  # Save before displaying
                    self.display_time_summary()
                case "6":
                    self.display_active_windows_info()
                case "7":
                    print(self.active_titles)
                case "8":
                    print(self.time_tracking)
                case "0":
                    print("Exiting appblocker")
                    break
            time.sleep(1)
            

    def test_main(self):
        self.start_background_tasks()
        while True:
            try:
                print("===============================================================")
                print("AppBlocker and WebBlocker Test Menu")
                menu_opt = input("\n1. Test AppBlocker\n2. Test WebBlocker\n3. Test DataHandler\n")
                print("0. Exit\nEnter Command: ")
                match menu_opt:
                    case "1":
                        self.appblocker_test_menu()
                    case "2":
                        self.web_blocker.test_menu()
                    case "3":
                        self.save_time_data_on_demand()  # Save current data before displaying
                        print(self.data_handler.df_time_spent_in_programs)

                        self.display_time_summary()
                    case "0":
                        self.save_time_data_on_demand()  # Save before exiting
                        print("Exiting...")
                        break
            except KeyboardInterrupt:
                self.save_time_data_on_demand()  # Save before exiting
                self.web_blocker.unblock_websites()
                print("Exiting...")         



if __name__ == "__main__":
    focus = Focus()
    focus.test_main()