import os
import sys
import tkinter as tk
from tkinter import ttk
import pandas as pd
from focus_main import Focus
import ctypes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


myappid = 'focusframe.productivity.app.1.0'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class FocusFrameApp:
    def __init__(self):
        # Initialize Focus first so we can get paths from DataHandler
        self.focus = Focus()
       
        
        # Get paths from DataHandler
        self.app_folder = self.focus.data_handler.app_folder
        self.all_programs_csv_path = self.focus.data_handler.all_programs_csv_path
        self.block_list_csv_path = self.focus.data_handler.block_list_csv_path
        self.tsip_programs_path = self.focus.data_handler.df_tsip_programs_path
        self.time_spent_on_screen_path = self.focus.data_handler.df_time_spent_on_screen_path

    
        self.auto_refresh_active_stats = False
        self.auto_refresh_id_stats = None
        self.auto_refresh_active_activeprograms = False
        self.auto_refresh_id_activeprograms = None

    
        self._setup_window()
        self._setup_styles()
        self._setup_notebook()
        self._build_tab1_program_blocker()
        self._build_tab3_web_blocker()
        self._build_tab2_activate_deactivate()
        self._build_tab4_stats()
        self._load_saved_data()

        self.focus.start_background_tasks()
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)



    def _setup_window(self):
        self.window = tk.Tk()
        self.window.geometry("1600x840")
        self.window.title("FocusFrame")
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        logo_path = os.path.join(base_path, "logo.png")
        self.logo_img = tk.PhotoImage(file=logo_path)
        self.window.iconphoto(True, self.logo_img)

    def _setup_styles(self):
        style = ttk.Style()
        style.configure("Treeview", rowheight=30)
        # Make headings bigger
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        # Make tab labels bigger - remove background color
        style.configure("TNotebook.Tab", 
                       font=("Arial", 12, "bold"),
                       borderwidth=2,
                       focuscolor="none",
                       padding=[15, 8])  # Add more space between tabs [horizontal, vertical]
        # Style for selected/active tab
        style.map("TNotebook.Tab",
                 bordercolor=[("selected", "black"),
                             ("active", "black")])
        
        
        style.configure("DarkFrame.TFrame",
                       relief="solid",
                       borderwidth=2)

    def _setup_notebook(self):
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True)

        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        self.tab4 = ttk.Frame(self.notebook)

    # ==================== Tab1 program blocker =================
    def _build_tab1_program_blocker(self):
        self.notebook.add(self.tab1, text="Program Blocker")
      
        self.tab1.rowconfigure(0, weight=1)
        self.tab1.columnconfigure(0, weight=2)
        self.tab1.columnconfigure(1, weight=1)
        self.tab1.columnconfigure(2, weight=1)

        left = ttk.Frame(self.tab1, style="DarkFrame.TFrame")
        left.grid(row=0, column=0, sticky="nsew")
        for r, w in [(0, 0), (1, 1), (2, 0), (3, 0)]:
            left.rowconfigure(r, weight=w)
        left.columnconfigure(0, weight=1)

        # -------------------- Active windows on the left -----------------------
        ttk.Label(left, text="Active Windows", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=(5, 0))
        self.active_programs = ttk.Treeview(left, columns=("exe", "title"), show="headings")
        self.active_programs.heading("exe", text="Executable")
        self.active_programs.heading("title", text="Window Title")
        self.active_programs.column("exe", width=150, stretch=True)
        self.active_programs.column("title", width=150, stretch=True)
        self.active_programs.grid(row=1, column=0, sticky="nsew", padx=5)

        ttk.Button(left, text="Send to block list",
                   command=lambda: self.add_program(self.active_programs, self.program_list)
                   ).grid(row=2, column=0, pady=2)
        ttk.Button(left, text="Update Active Programs",
                   command=self.update_active_programs
                   ).grid(row=3, column=0, pady=(2, 5))

        # ------------------------------ All scanned programs in the middle -----------------------
        mid = ttk.Frame(self.tab1, style="DarkFrame.TFrame")
        mid.grid(row=0, column=1, sticky="nsew")
        mid.rowconfigure(1, weight=1)
        mid.columnconfigure(0, weight=1)

        ttk.Label(mid, text="All scanned programs", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=(5, 0))

        self.all_programs = ttk.Treeview(mid, columns="program", show="headings")
        self.all_programs.heading("program", text="Executable")
        self.all_programs.column("program", width=150, stretch=True)
        self.all_programs.grid(row=1, column=0, sticky="nsew", padx=5)

        ttk.Button(mid, text="Send to block list",
                   command=lambda: self.add_to_web_blocklist(self.treeview_to_list(self.all_programs))
                   ).grid(row=2, column=0, pady=(2, 5))

        # ------------- Block list on the right ------------- 
        right = ttk.Frame(self.tab1, style="DarkFrame.TFrame")
        right.grid(row=0, column=2, sticky="nsew")
        for r, w in [(0, 0), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0)]:
            right.rowconfigure(r, weight=w)
        right.columnconfigure(0, weight=1)

        ttk.Label(right, text="Block list", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=(5, 0))

        self.program_list = ttk.Treeview(right, columns="program", show="headings")
        self.program_list.grid(row=1, column=0, sticky="nsew", padx=5)

        ttk.Button(right, text="Save block list",
                   command=self.save_block_list).grid(row=2, column=0, pady=2)

        self.enter_string = tk.StringVar(value="")
        ttk.Entry(right, textvariable=self.enter_string).grid(row=3, column=0, pady=2, padx=5, sticky="ew")

        ttk.Button(right, text="ADD typed program",
                   command=lambda: self.add_program_string(self.enter_string, self.program_list)
                   ).grid(row=4, column=0, pady=2)
        ttk.Button(right, text="Delete Selected",
                   command=lambda: self.delete_program(self.program_list)
                   ).grid(row=5, column=0, pady=(2, 5))

    def add_to_web_blocklist(self,  site):
        self.focus.web_blocker.add_blocked_site(site)
        self.add_program(self.all_programs, self.program_list)


    # ==================== Tab3 web blocker =================
    def _build_tab3_web_blocker(self):
        self.notebook.add(self.tab3, text="Web Blocker")

        self.tab3.rowconfigure(0, weight=1)
        self.tab3.columnconfigure(0, weight=1)
        self.tab3.columnconfigure(1, weight=1)

        # --------------------------- Prev blocked -------------------- TO BE ADDED
        left = ttk.Frame(self.tab3, style="DarkFrame.TFrame")
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        self.all_websites = ttk.Treeview(left, columns="website", show="headings")
        self.all_websites.heading("website", text="registered websites")
        self.all_websites.column("website", width=300, stretch=True)
        self.all_websites.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        ttk.Button(left, text="Send to blocked websites",
                   command=lambda: self.add_program(self.all_websites, self.blocked_websites)
                   ).grid(row=1, column=0, pady=2)
        ttk.Button(left, text="Delete Selected",
                   command=lambda: self.remove_blocked_site(self.all_websites)
                   ).grid(row=2, column=0,  pady=(2, 5))

        # ----------------------------- Blocked websites on the right -----------------------
        right = ttk.Frame(self.tab3, style="DarkFrame.TFrame")
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self.blocked_websites = ttk.Treeview(right, columns="website", show="headings")
        self.blocked_websites.heading("website", text="blocked websites")
        self.blocked_websites.column("website", width=300, stretch=True)
        self.blocked_websites.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.entry_string_web = tk.StringVar(value="")
        ttk.Entry(right, textvariable=self.entry_string_web).grid(row=1, column=0, pady=2, padx=5, sticky="ew")

        ttk.Button(right, text="Add typed website",
                   command=lambda: self.add_program_string(self.entry_string_web, self.blocked_websites)
                   ).grid(row=2, column=0, pady=2)
        ttk.Button(right, text="Delete Selected",
                   command=lambda: self.remove_blocked_site(self.blocked_websites)
                   ).grid(row=3, column=0, pady=(2, 5))
        
    # ==================== Tab2 activate/deactivate blockers =================
    def _build_tab2_activate_deactivate(self):
        self.notebook.add(self.tab2, text="Acvivate/Deactivate Blockers")

        self.tab2.rowconfigure(0, weight=1)
        for c in range(3):
            self.tab2.columnconfigure(c, weight=1)

        left = ttk.Frame(self.tab2, style="DarkFrame.TFrame")
        left.grid(row=0, column=0, sticky="nsew")
        mid = ttk.Frame(self.tab2, style="DarkFrame.TFrame")
        mid.grid(row=0, column=1, sticky="nsew")
        right = ttk.Frame(self.tab2, style="DarkFrame.TFrame")
        right.grid(row=0, column=2, sticky="nsew")

        # ------------- App Blocker on the left -------------
        tk.Label(left, text="App Blocker", font=("Arial", 18, "bold")).place(relx=0.5, rely=0.2, anchor="center")
        self.btn_left = tk.Button(left, text="START", bg="green", fg="white",
                                  font=("Arial", 14, "bold"), takefocus=0,
                                  command=self.activate_app_blocker)
        self.btn_left.place(relx=0.5, rely=0.5, anchor="center", width=200, height=100)
        self.status_left = tk.Label(left, text="inactive", font=("Arial", 12), fg="gray")
        self.status_left.place(relx=0.5, rely=0.75, anchor="center")

        # ------------- Web Blocker in the middle -------------
        tk.Label(mid, text="Web Blocker", font=("Arial", 18, "bold")).place(relx=0.5, rely=0.2, anchor="center")
        self.btn_mid = tk.Button(mid, text="START", bg="green", fg="white",
                                 font=("Arial", 14, "bold"), takefocus=0,
                                 command=self.activate_web_blocker)
        self.btn_mid.place(relx=0.5, rely=0.5, anchor="center", width=200, height=100)
        self.status_mid = tk.Label(mid, text="inactive", font=("Arial", 12), fg="gray")
        self.status_mid.place(relx=0.5, rely=0.75, anchor="center")

        # ------------- Game Blocker on the right -------------
        tk.Label(right, text="Game Blocker", font=("Arial", 18, "bold")).place(relx=0.5, rely=0.2, anchor="center")
        self.btn_right = tk.Button(right, text="START", bg="green", fg="white",
                                   font=("Arial", 14, "bold"), takefocus=0,
                                   command=self.activate_game_blocker)
        self.btn_right.place(relx=0.5, rely=0.5, anchor="center", width=200, height=100)
        self.status_right = tk.Label(right, text="inactive", font=("Arial", 12), fg="gray")
        self.status_right.place(relx=0.5, rely=0.75, anchor="center")


    # ==================== Tab4 stats / screen time =================
    def _build_tab4_stats(self):
        self.notebook.add(self.tab4, text="stats")

        self.tab4.rowconfigure(0, weight=1)
        self.tab4.columnconfigure(0, weight=1)

        tsip_frame = ttk.Frame(self.tab4, style="DarkFrame.TFrame")
        tsip_frame.grid(row=0, column=0, sticky="nsew")
        tsip_frame.rowconfigure(1, weight=1)
        tsip_frame.columnconfigure(0, weight=1)

        ttk.Label(tsip_frame, text="Time spent in programs", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=(5, 0))

        self.programs_stat = ttk.Treeview(
            tsip_frame,
            columns=("exe", "total_hrs", "hrs", "mins", "secs"),
            show="headings"
        )
        for col, label, width,  *rest in [
            ("exe", "Program", 150),
            ("total_hrs", "Total Hours", 100, ),
            ("hrs", "Hr", 50),
            ("mins", "Min", 50),
            ("secs", "Sec", 50),
        ]:
            self.programs_stat.heading(col, text=label)
            self.programs_stat.column(col, width=width, stretch=False)
        self.programs_stat.grid(row=1, column=0, sticky="nsew", padx=5)

        # ------------------- Screen time --------------------------------
        screen_time_frame = ttk.Frame(self.tab4, style="DarkFrame.TFrame")
        screen_time_frame.grid(row=1, column=0, sticky="nsew")
        screen_time_frame.rowconfigure(1, weight=1)
        screen_time_frame.columnconfigure(0, weight=1)
        ttk.Label(screen_time_frame, text="Time spent on screen", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=(5, 0))
        self.screen_time_stat = ttk.Treeview(
            screen_time_frame,
            columns=("date", "total_hrs", "hrs", "mins", "secs"),
            show="headings"
        )
        for col, label, width in [                   
            ("date", "Date", 100),
            ("total_hrs", "Total Hours", 100),
            ("hrs", "Hr", 50),
            ("mins", "Min", 50),
            ("secs", "Sec", 50),
        ]:
            self.screen_time_stat.heading(col, text=label)
            self.screen_time_stat.column(col, width=width, stretch=False)
        self.screen_time_stat.grid(row=1, column=0, sticky="nsew", padx=5)

         # ADD these lines at the end:
        self.tab4.columnconfigure(1, weight=2)

        chart_frame = ttk.Frame(self.tab4, style="DarkFrame.TFrame")
        chart_frame.grid(row=0, column=1, sticky="nsew")
        chart_frame.rowconfigure(0, weight=1)
        chart_frame.rowconfigure(1, weight=1)
        chart_frame.columnconfigure(0, weight=1)

        self.fig_apps, self.ax_apps = plt.subplots(figsize=(5, 3))
        self.canvas_apps = FigureCanvasTkAgg(self.fig_apps, master=chart_frame)
        self.canvas_apps.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        screen_chart = ttk.Frame(self.tab4, style="DarkFrame.TFrame")
        screen_chart.grid(row=0, column=2, sticky="nsew")
        screen_chart.rowconfigure(0, weight=1)
        screen_chart.columnconfigure(0, weight=1)

        self.fig_screen, self.ax_screen = plt.subplots(figsize=(5, 3))
        self.canvas_screen = FigureCanvasTkAgg(self.fig_screen, master=screen_chart)
        self.canvas_screen.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

   
        self.tab4.rowconfigure(1, weight=1)

        session_frame = ttk.Frame(self.tab4, style="DarkFrame.TFrame")
        session_frame.grid(row=1, column=1, columnspan=2, sticky="nsew")

        self.session_label = tk.Label(session_frame, text="Current Session", font=("Arial", 18, "bold"))
        self.session_label.place(relx=0.5, rely=0.35, anchor="center")

        # Format initial session time properly
        session_seconds = int(self.focus.session_time())
        hours = session_seconds // 3600
        minutes = (session_seconds % 3600) // 60
        seconds = session_seconds % 60
        formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        self.session_time_label = tk.Label(session_frame, text=formatted_time, font=("Arial", 32, "bold"), fg="#2196F3")
        self.session_time_label.place(relx=0.5, rely=0.55, anchor="center")

  
    def _load_saved_data(self):
        try:
            block_list_csv = pd.read_csv(self.block_list_csv_path)
            for name in block_list_csv["Name"]:
                self.program_list.insert(parent="", index=tk.END, values=(name,))
        except FileNotFoundError:
            pass

        try:
            all_programs_csv = pd.read_csv(self.all_programs_csv_path)
            for name in all_programs_csv["program"]:
                self.all_programs.insert(parent="", index=tk.END, values=(name,))
        except FileNotFoundError:
            pass

   

    # ============== FUNCS ====================

    #------------- Active Programs --------------------
    def update_all_programs(self):
        active_list = self.treeview_to_list(self.active_programs)
        all_list = self.treeview_to_list(self.all_programs)
        whitelist_lower = [e.lower() for e in self.focus.whitelist]

        for exe in active_list:
            if exe.lower() not in whitelist_lower and exe not in all_list:
                self.all_programs.insert(parent="", index=tk.END, values=(exe,))
                all_list.append(exe)

        pd.DataFrame(all_list, columns=["program"]).to_csv(self.all_programs_csv_path, index=False)

    def update_active_programs(self):
        print("Fetching active programs...")
        try:
            selected = [
                (self.active_programs.item(i)["values"][0], self.active_programs.item(i)["values"][1])
                for i in self.active_programs.selection()
            ]

            data_snapshot = self.focus.active_titles.copy()
            print(f"Found {len(data_snapshot)} active windows.")

            for i in self.active_programs.get_children():
                self.active_programs.delete(i)

            new_items = {}
            for pid, info in data_snapshot.items():
                exe = info.get("exe", "Unknown")
                title = info.get("title", "No Title")
                path = info.get("path", "No Path")
                if exe.lower() not in self.focus.whitelist or path.lower() in self.focus.ignored_paths:
                    item_id = self.active_programs.insert(parent="", index=tk.END, values=(exe, title))
                    new_items[(exe, title)] = item_id

            for exe, title in selected:
                if (exe, title) in new_items:
                    self.active_programs.selection_add(new_items[(exe, title)])

        except RuntimeError:
            print("System busy, please try again in a second.")
        except Exception as e:
            print(f"An error occurred: {e}")

        self.update_all_programs()

    def auto_update_active_programs(self):
        if self.auto_refresh_active_activeprograms and self.notebook.index(self.notebook.select()) == 0:
            try:
                self.update_active_programs()
            except Exception:
                pass
            self.auto_refresh_id_activeprograms = self.window.after(1000, self.auto_update_active_programs)

    #-------------------- Other funcs -----------------
    def treeview_to_list(self, table):
        return [table.item(i)["values"][0] for i in table.get_children()]
    def remove_blocked_site(self, table):
        selected_values = []
        for i in table.selection():
            values = table.item(i)["values"]
            if values:
                selected_values.append(values[0])
        
        for i in table.selection():
            table.delete(i)

        if table is self.blocked_websites and self.focus.web_blocker.state == "On":
            for site in selected_values:
                self.focus.web_blocker.remove_blocked_site(site)
                self.focus.web_blocker.flush_dns()
    def add_program(self, from_table, to_table):
        existing = self.treeview_to_list(to_table)
        added_sites = []
        for i in from_table.selection():
            value = from_table.item(i)["values"][0]
            if value not in existing:
                to_table.insert(parent="", index=tk.END, values=(value,))
                # Track sites added to blocked_websites for web blocker update
                if to_table is self.blocked_websites:
                    added_sites.append(value)
        
        # If we added sites to blocked_websites and web blocker is active, update blocker
        if added_sites and to_table is self.blocked_websites and self.focus.web_blocker.state == "On":
            for site in added_sites:
                self.focus.web_blocker.add_blocked_site(site)

    def add_program_string(self, string_var, to_table):
        value = string_var.get()
        if value and value not in self.treeview_to_list(to_table):
            to_table.insert(parent="", index=tk.END, values=(value,))
            # If this is the blocked_websites table and web blocker is active, add to blocker
            if to_table is self.blocked_websites and self.focus.web_blocker.state == "On":
                self.focus.web_blocker.add_blocked_site(value)
        string_var.set("")

    def delete_program(self, table):
        # Get the selected values before deleting them
        selected_values = []
        for i in table.selection():
            values = table.item(i)["values"]
            if values:
                selected_values.append(values[0])
        
        # Delete from the table
        for i in table.selection():
            table.delete(i)
            
        # Update web blocker if this is the blocked websites table and blocker is active
        if table is self.blocked_websites and self.focus.web_blocker.state == "On":
            for site in selected_values:
                self.focus.web_blocker.remove_blocked_site(site)
                
        # Save changes to CSV file depending on which table was modified
        if table is self.program_list:
            self._save_list_to_csv(self.treeview_to_list(table))
        elif table is self.all_programs:
            # Save the all_programs list to its CSV file
            current_programs = self.treeview_to_list(table)
            pd.DataFrame(current_programs, columns=["program"]).to_csv(self.all_programs_csv_path, index=False)
        elif table is self.all_websites:
            # For websites, you might want to save to a separate CSV if needed
            # (Currently no CSV saving mechanism exists for websites)
            pass

    def save_block_list(self):
        self._save_list_to_csv(self.treeview_to_list(self.program_list))

    def _save_list_to_csv(self, lst):
        pd.DataFrame(lst, columns=["Name"]).to_csv(self.block_list_csv_path, index=False)

                           





    # ------------------------------------------------------------------ #
    #  Stats                                                                #
    # ------------------------------------------------------------------ #

    def update_stats(self):
        for item in self.programs_stat.get_children():
            self.programs_stat.delete(item)
        self.focus.update_time_tracking()
        self.focus.save_time_data_on_demand()
        df = self.focus.data_handler.df_time_spent_in_programs
        for _, row in df.iterrows():
            self.programs_stat.insert(parent="", index=tk.END, values=(
                row["Program"], row["Total_Hours"], row["Hours"], row["Minutes"], row["Seconds"]
            ))
        print(f"Stats updated: {len(df)} programs")
        for item in self.screen_time_stat.get_children():
            self.screen_time_stat.delete(item)
        df_screen = self.focus.data_handler.df_time_spent_on_screen
        for _, row in df_screen.iterrows():
            self.screen_time_stat.insert(parent="", index=tk.END, values=(
                row["Date"], row["Total_Hours"], row["Hours"], row["Minutes"], row["Seconds"]
            ))
        print(f"Stats updated: {len(df_screen)} days")

        # Update session time display
        session_seconds = int(self.focus.session_time())
        hours = session_seconds // 3600
        minutes = (session_seconds % 3600) // 60
        seconds = session_seconds % 60
        formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.session_time_label.config(text=formatted_time)

        self.ax_apps.clear()
        filtered = df[df["Total_Hours"] >= 0.05]
        if not filtered.empty:
            grouped = filtered.groupby("Program")["Total_Hours"].sum().sort_values(ascending=False).head(10)
            self.ax_apps.bar(grouped.index, grouped.values)
            self.ax_apps.set_title("Top used programs")
            self.ax_apps.tick_params(axis='x', rotation=45)
        self.fig_apps.tight_layout()
        self.canvas_apps.draw()

        self.ax_screen.clear()
        df_screen = self.focus.data_handler.df_time_spent_on_screen
        if df_screen is not None and not df_screen.empty:
            self.ax_screen.plot(df_screen["Date"], df_screen["Total_Hours"])
            self.ax_screen.set_title("Screen time")
            self.ax_screen.tick_params(axis='x', rotation=45)
        self.fig_screen.tight_layout()
        self.canvas_screen.draw()

    def auto_update_stats(self):
        if self.auto_refresh_active_stats and self.notebook.index(self.notebook.select()) == 3:
            try:
                self.update_stats()
            except Exception:
                pass
            self.auto_refresh_id_stats = self.window.after(1000, self.auto_update_stats)

    # ------------------------------------------------------------------ #
    #  Blocker toggles                                                      #
    # ------------------------------------------------------------------ #

    def activate_app_blocker(self):
        lst = self.treeview_to_list(self.program_list)
        self.focus.blocked_apps = lst
        self.focus.app_blocker.blocked_apps = lst
        self.focus.toggle_app_blocking()
        if self.focus.app_blocker.app_state == "On":
            self.btn_left.config(text="STOP", bg="red")
            self.status_left.config(text="ACTIVE", fg="red")
        else:
            self.btn_left.config(text="START", bg="green")
            self.status_left.config(text="inactive", fg="gray")

    def activate_web_blocker(self):
        for site in self.treeview_to_list(self.blocked_websites):
            self.focus.web_blocker.add_blocked_site(site)
        if self.focus.web_blocker.state == "On":
            self.focus.web_blocker.unblock_websites()
            self.focus.web_blocker.state = "Off"
            self.btn_mid.config(text="START", bg="green")
            self.status_mid.config(text="inactive", fg="gray")
        else:
            self.focus.web_blocker.block_websites()
            self.focus.web_blocker.state = "On"
            self.btn_mid.config(text="STOP", bg="red")
            self.status_mid.config(text="ACTIVE", fg="red")

    def activate_game_blocker(self):
        self.focus.toggle_game_blocking()
        if self.focus.app_blocker.game_state == "On":
            self.btn_right.config(text="STOP", bg="red")
            self.status_right.config(text="ACTIVE", fg="red")
        else:
            self.btn_right.config(text="START", bg="green")
            self.status_right.config(text="inactive", fg="gray")

    # ------------------------------------------------------------------ #
    #  Tab change / close                                                   #
    # ------------------------------------------------------------------ #

    def on_tab_changed(self, event):
        current_tab = self.notebook.index(self.notebook.select())

        if current_tab == 0:
            self.auto_refresh_active_activeprograms = True
            self.auto_update_active_programs()
        else:
            self.auto_refresh_active_activeprograms = False
            if self.auto_refresh_id_activeprograms:
                self.window.after_cancel(self.auto_refresh_id_activeprograms)
                self.auto_refresh_id_activeprograms = None

        if current_tab == 3:
            self.auto_refresh_active_stats = True
            self.auto_update_stats()
        else:
            self.auto_refresh_active_stats = False
            if self.auto_refresh_id_stats:
                self.window.after_cancel(self.auto_refresh_id_stats)
                self.auto_refresh_id_stats = None

    def on_close(self):
        print("Closing application...")
        try:
            self.auto_refresh_active_stats = False
            self.auto_refresh_active_activeprograms = False
            if self.auto_refresh_id_stats:
                self.window.after_cancel(self.auto_refresh_id_stats)
            if self.auto_refresh_id_activeprograms:
                self.window.after_cancel(self.auto_refresh_id_activeprograms)
            if self.focus.app_blocker.block_apps:
                self.focus.app_blocker.stop()
            self.focus.save_time_data_on_demand()
            if self.focus.web_blocker.state == "On":
                self.focus.web_blocker.unblock_websites()
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            print("Exiting...")
            self.window.quit()
            sys.exit(0)
    


    def run(self):
        try:
            self.window.protocol("WM_DELETE_WINDOW", self.on_close)
            self.window.mainloop()
        except KeyboardInterrupt:
            self.on_close()
        


if __name__ == "__main__":
    app = FocusFrameApp()
    app.run()