import os
import sys
import tkinter as tk
from tkinter import ttk
import pandas as pd
from focus_main import Focus
import ctypes

# Set app ID so Windows treats it as "FocusFrame" not "python.exe"
myappid = 'focusframe.productivity.app.1.0'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

APPDATA = os.getenv("APPDATA")
APP_FOLDER = os.path.join(APPDATA, "FocusFrame")
all_programs_csv_path = os.path.join(APP_FOLDER, "all_programs.csv")
block_list_csv_path = os.path.join(APP_FOLDER, "block_list.csv")
tsip_programs_path_app_data = os.path.join(APP_FOLDER, "time_spent_in_programs.csv")
time_spent_on_screen_path_app_data = os.path.join(APP_FOLDER, "time_spent_on_screen.csv")

if not os.path.exists(APP_FOLDER):
    os.makedirs(APP_FOLDER)

focus = Focus(
    tsip_programs_path=tsip_programs_path_app_data,
    time_spent_on_screen_path=time_spent_on_screen_path_app_data
)

window = tk.Tk()
window.geometry("1600x840")
window.title("FocusFrame")
window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)

style = ttk.Style()
style.configure("Treeview", rowheight=30)

#To help exe find the logo when running as .exe
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

logo_path = os.path.join(base_path, "logo.png")
logo_img = tk.PhotoImage(file=logo_path)
window.iconphoto(True, logo_img)

notebook = ttk.Notebook(window)
notebook.pack(fill="both", expand=True)

tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)
tab4 = ttk.Frame(notebook)

focus.start_background_tasks()

"----TAB 1-------"
notebook.add(tab1, text="Program Blocker")

tab1.rowconfigure(0, weight=1)
tab1.columnconfigure(0, weight=2)
tab1.columnconfigure(1, weight=1)
tab1.columnconfigure(2, weight=1)

def save_block_list():
    lst = treeview_to_list(program_list)
    list_to_df(lst)

# Left frame - Active Windows
Left_frame = ttk.Frame(tab1, borderwidth=10, relief=tk.GROOVE)
Left_frame.grid(row=0, column=0, sticky="nsew")
Left_frame.rowconfigure(0, weight=0)
Left_frame.rowconfigure(1, weight=1)
Left_frame.rowconfigure(2, weight=0)
Left_frame.rowconfigure(3, weight=0)
Left_frame.columnconfigure(0, weight=1)

left_label = ttk.Label(Left_frame, text="Active Windows")
left_label.grid(row=0, column=0, pady=(5, 0))

active_programs = ttk.Treeview(Left_frame, columns=("exe", "title"), show="headings")
active_programs.heading("exe", text="Executable")
active_programs.heading("title", text="Window Title")
active_programs.column("exe", width=150, stretch=True)
active_programs.column("title", width=150, stretch=True)
active_programs.grid(row=1, column=0, sticky="nsew", padx=5)

send_to_block_list_button = ttk.Button(Left_frame, text="Send to block list", command=lambda: add_program(active_programs, program_list))
send_to_block_list_button.grid(row=2, column=0, pady=2)

update_programs_button_tab1 = ttk.Button(Left_frame, text="Update Active Programs", command=lambda: update_active_programs())
update_programs_button_tab1.grid(row=3, column=0, pady=(2, 5))

# Middle frame - All scanned programs
middle_frame = ttk.Frame(tab1, borderwidth=10, relief=tk.GROOVE)
middle_frame.grid(row=0, column=1, sticky="nsew")
middle_frame.rowconfigure(0, weight=0)
middle_frame.rowconfigure(1, weight=1)
middle_frame.rowconfigure(2, weight=0)
middle_frame.columnconfigure(0, weight=1)

label_middle = ttk.Label(middle_frame, text="All scanned programs")
label_middle.grid(row=0, column=0, pady=(5, 0))

all_programs = ttk.Treeview(middle_frame, columns="program", show="headings")
all_programs.heading("program", text="Executable")
all_programs.column("program", width=150, stretch=True)
all_programs.grid(row=1, column=0, sticky="nsew", padx=5)

send_to_block_button = ttk.Button(middle_frame, text="Send to block list", command=lambda: add_program(all_programs, program_list))
send_to_block_button.grid(row=2, column=0, pady=(2, 5))

# Right frame - Block list
right_frame = ttk.Frame(tab1, borderwidth=10, relief=tk.GROOVE)
right_frame.grid(row=0, column=2, sticky="nsew")
right_frame.rowconfigure(0, weight=0)
right_frame.rowconfigure(1, weight=1)
right_frame.rowconfigure(2, weight=0)
right_frame.rowconfigure(3, weight=0)
right_frame.rowconfigure(4, weight=0)
right_frame.rowconfigure(5, weight=0)
right_frame.columnconfigure(0, weight=1)

label_right = ttk.Label(right_frame, text="Block list")
label_right.grid(row=0, column=0, pady=(5, 0))

program_list = ttk.Treeview(right_frame, columns="program", show="headings")
program_list.grid(row=1, column=0, sticky="nsew", padx=5)

save_button = ttk.Button(right_frame, text="Save block list", command=save_block_list)
save_button.grid(row=2, column=0, pady=2)

enter_string = tk.StringVar(value="")
text_input = ttk.Entry(right_frame, textvariable=enter_string)
text_input.grid(row=3, column=0, pady=2, padx=5, sticky="ew")

add_button = ttk.Button(right_frame, text="ADD typed program", command=lambda: add_program_string(enter_string, program_list))
add_button.grid(row=4, column=0, pady=2)

delete_button = ttk.Button(right_frame, text="Delete Selected", command=lambda: delete_program(program_list))
delete_button.grid(row=5, column=0, pady=(2, 5))

# Load stored programs
try:
    block_list_csv = pd.read_csv(block_list_csv_path)
    for name in block_list_csv["Name"]:
        program_list.insert(parent="", index=tk.END, values=(name))
except FileNotFoundError:
    block_list_csv = pd.DataFrame({"Name": []})
try:
    all_programs_csv = pd.read_csv(all_programs_csv_path)
    for name in all_programs_csv["program"]:
        all_programs.insert(parent="", index=tk.END, values=(name))
except FileNotFoundError:
    all_programs_csv = pd.DataFrame({"program": []})


def add_program(from_table, to_table):
    lst = treeview_to_list(to_table)
    for i in from_table.selection():
        if from_table.item(i)["values"][0] in lst:
            continue
        to_table.insert(parent="", index=tk.END, values=(from_table.item(i)["values"][0]))


def update_all_programs():
    active_list = []
    all_list = []
    for i in active_programs.get_children():
        active_list.append(active_programs.item(i)["values"][0])
    for i in all_programs.get_children():
        all_list.append(all_programs.item(i)["values"][0])
    for i in active_list:
        # Filter out FocusFrame itself
        if i.lower() not in [exe.lower() for exe in focus.whitelist] and i not in all_list:
            all_programs.insert(parent="", index=tk.END, values=(i,))
            all_list.append(i)
    df = pd.DataFrame(all_list, columns=['program'])
    df.to_csv(all_programs_csv_path, index=False)


def update_active_programs():
    print("Fetching active programs...")
    try:
        # Save currently selected items
        selected_items = []
        for item_id in active_programs.selection():
            item_values = active_programs.item(item_id)['values']
            if item_values:
                selected_items.append((item_values[0], item_values[1]))  # exe, title
        
        data_snapshot = focus.active_titles.copy()
        print(f"Found {len(data_snapshot)} active windows.")
        for i in active_programs.get_children():
            active_programs.delete(i)
        
        # Store new item IDs for restoring selection
        new_items = {}
        
        for pid, info in data_snapshot.items():
            exe = info.get("exe", "Unknown")
            title = info.get("title", "No Title")
            path = info.get("path", "No Path")
            # Filter out FocusFrame itself (python.exe or FocusFrame.exe)
            if exe.lower() not in focus.whitelist or path.lower() in focus.ignored_paths:
                item_id = active_programs.insert(parent="", index=tk.END, values=(exe, title))
                new_items[(exe, title)] = item_id
        
        # Restore selection
        for exe, title in selected_items:
            if (exe, title) in new_items:
                active_programs.selection_add(new_items[(exe, title)])
            
    except RuntimeError:
        print("System busy, please try again in a second.")
    except Exception as e:
        print(f"An error occurred: {e}")
    update_all_programs()

auto_refresh_active_activeprograms = False
auto_refresh_id_activeprograms = None

def auto_update_active_programs():
    global auto_refresh_id_activeprograms
    if auto_refresh_active_activeprograms and notebook.index(notebook.select()) == 0:
        try:
            update_active_programs()
        except:
            pass  # Window might not be focused
        auto_refresh_id_activeprograms = window.after(1000, auto_update_active_programs)  # Schedule next update

def treeview_to_list(table):
    value_list = []
    for i in table.get_children():
        value_list.append(table.item(i)["values"][0])
    return value_list


def list_to_df(lst):
    df = pd.DataFrame(lst, columns=['Name'])
    df.to_csv(block_list_csv_path, index=False)


def add_program_string(enter_string, to_table):
    lst = treeview_to_list(to_table)
    if enter_string.get() in lst:
        return
    else:
        to_table.insert(parent="", index=tk.END, values=(enter_string.get()))
        enter_string.set("")


def delete_program(table):
    for i in table.selection():
        table.delete(i)
    selected_in_list = treeview_to_list(table)
    if table == program_list:
        list_to_df(selected_in_list)


"------TAB 3 - Web Blocker--------"
notebook.add(tab3, text="Web Blocker")

tab3.rowconfigure(0, weight=1)
tab3.columnconfigure(0, weight=1)
tab3.columnconfigure(1, weight=1)

Left_frame_web = ttk.Frame(tab3, borderwidth=10, relief=tk.GROOVE)
Left_frame_web.grid(row=0, column=0, sticky="nsew")
Left_frame_web.rowconfigure(0, weight=1)
Left_frame_web.rowconfigure(1, weight=0)
Left_frame_web.rowconfigure(2, weight=0)
Left_frame_web.columnconfigure(0, weight=1)

right_frame_web = ttk.Frame(tab3, borderwidth=10, relief=tk.GROOVE)
right_frame_web.grid(row=0, column=1, sticky="nsew")
right_frame_web.rowconfigure(0, weight=1)
right_frame_web.rowconfigure(1, weight=0)
right_frame_web.rowconfigure(2, weight=0)
right_frame_web.rowconfigure(3, weight=0)
right_frame_web.columnconfigure(0, weight=1)

all_websites = ttk.Treeview(Left_frame_web, columns="website", show="headings")
all_websites.heading("website", text="registered websites")
all_websites.column("website", width=300, stretch=True)
all_websites.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

add_to_blocked_websites_button = ttk.Button(Left_frame_web, text="Send to blocked websites", command=lambda: add_program(all_websites, blocked_websites))
add_to_blocked_websites_button.grid(row=1, column=0, pady=2)

delete_button_all_websites = ttk.Button(Left_frame_web, text="Delete Selected", command=lambda: delete_program(all_websites))
delete_button_all_websites.grid(row=2, column=0, pady=(2, 5))

blocked_websites = ttk.Treeview(right_frame_web, columns="website", show="headings")
blocked_websites.heading("website", text="blocked websites")
blocked_websites.column("website", width=300, stretch=True)
blocked_websites.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

entry_string_web = tk.StringVar(value="")
entry_web = ttk.Entry(right_frame_web, textvariable=entry_string_web)
entry_web.grid(row=1, column=0, pady=2, padx=5, sticky="ew")

add_website_button = ttk.Button(right_frame_web, text="Add typed website", command=lambda: add_program_string(entry_string_web, blocked_websites))
add_website_button.grid(row=2, column=0, pady=2)

delete_button_blocked_websites = ttk.Button(right_frame_web, text="Delete Selected", command=lambda: delete_program(blocked_websites))
delete_button_blocked_websites.grid(row=3, column=0, pady=(2, 5))


"------TAB 2 - Activate/Deactivate--------"
notebook.add(tab2, text="Acvivate/Deactivate Blockers")

tab2.rowconfigure(0, weight=1)
tab2.columnconfigure(0, weight=1)
tab2.columnconfigure(1, weight=1)
tab2.columnconfigure(2, weight=1)

Left_frame_2 = ttk.Frame(tab2, borderwidth=10, relief=tk.GROOVE)
Left_frame_2.grid(row=0, column=0, sticky="nsew")

middle_frame_2 = ttk.Frame(tab2, borderwidth=10, relief=tk.GROOVE)
middle_frame_2.grid(row=0, column=1, sticky="nsew")

right_frame_2 = ttk.Frame(tab2, borderwidth=10, relief=tk.GROOVE)
right_frame_2.grid(row=0, column=2, sticky="nsew")


def activate_app_blocker():
    lst = treeview_to_list(program_list)
    focus.blocked_apps = lst
    focus.app_blocker.blocked_apps = lst
    print(lst)
    focus.toggle_app_blocking()
    if focus.app_blocker.app_state == "On":
        btn_left.config(text="STOP", bg="red")
        status_left.config(text="ACTIVE", fg="red")
    else:
        btn_left.config(text="START", bg="green")
        status_left.config(text="inactive", fg="gray")


def activate_game_blocker():
    focus.toggle_game_blocking()
    if focus.app_blocker.game_state == "On":
        btn_right.config(text="STOP", bg="red")
        status_right.config(text="ACTIVE", fg="red")
    else:
        btn_right.config(text="START", bg="green")
        status_right.config(text="inactive", fg="gray")


def activate_web_blocker():
    blocked_sites = treeview_to_list(blocked_websites)
    for site in blocked_sites:
        focus.web_blocker.add_blocked_site(site)
    if focus.web_blocker.state == "On":
        focus.web_blocker.unblock_websites()
        focus.web_blocker.state = "Off"
        btn_mid.config(text="START", bg="green")
        status_mid.config(text="inactive", fg="gray")
    else:
        focus.web_blocker.block_websites()
        focus.web_blocker.state = "On"
        btn_mid.config(text="STOP", bg="red")
        status_mid.config(text="ACTIVE", fg="red")


label_left = tk.Label(Left_frame_2, text="App Blocker", font=("Arial", 18, "bold"))
label_left.place(relx=0.5, rely=0.2, anchor="center")
btn_left = tk.Button(Left_frame_2, text="START", bg="green", fg="white", font=("Arial", 14, "bold"), takefocus=0, command=activate_app_blocker)
btn_left.place(relx=0.5, rely=0.5, anchor="center", width=150, height=80)
status_left = tk.Label(Left_frame_2, text="inactive", font=("Arial", 12), fg="gray")
status_left.place(relx=0.5, rely=0.75, anchor="center")

label_mid = tk.Label(middle_frame_2, text="Web Blocker", font=("Arial", 18, "bold"))
label_mid.place(relx=0.5, rely=0.2, anchor="center")
btn_mid = tk.Button(middle_frame_2, text="START", bg="green", fg="white", font=("Arial", 14, "bold"), takefocus=0, command=activate_web_blocker)
btn_mid.place(relx=0.5, rely=0.5, anchor="center", width=150, height=80)
status_mid = tk.Label(middle_frame_2, text="inactive", font=("Arial", 12), fg="gray")
status_mid.place(relx=0.5, rely=0.75, anchor="center")

label_right = tk.Label(right_frame_2, text="Game Blocker", font=("Arial", 18, "bold"))
label_right.place(relx=0.5, rely=0.2, anchor="center")
btn_right = tk.Button(right_frame_2, text="START", bg="green", fg="white", font=("Arial", 14, "bold"), takefocus=0, command=activate_game_blocker)
btn_right.place(relx=0.5, rely=0.5, anchor="center", width=150, height=80)
status_right = tk.Label(right_frame_2, text="inactive", font=("Arial", 12), fg="gray")
status_right.place(relx=0.5, rely=0.75, anchor="center")


"------TAB 4 - Stats--------"
notebook.add(tab4, text="stats")

tab4.rowconfigure(0, weight=1)
tab4.columnconfigure(0, weight=1)

Left_frame_4 = ttk.Frame(tab4, borderwidth=10, relief=tk.GROOVE)
Left_frame_4.grid(row=0, column=0, sticky="nsew")
Left_frame_4.rowconfigure(0, weight=0)
Left_frame_4.rowconfigure(1, weight=1)
Left_frame_4.rowconfigure(2, weight=0)
Left_frame_4.columnconfigure(0, weight=1)

left_label_4 = ttk.Label(Left_frame_4, text="Time spent in programs")
left_label_4.grid(row=0, column=0, pady=(5, 0))

programs_stat = ttk.Treeview(Left_frame_4, columns=("exe", "total_hrs", "hrs", "mins", "secs"), show="headings")
programs_stat.heading("exe", text="Program")
programs_stat.heading("total_hrs", text="Total Hours")
programs_stat.heading("hrs", text="Hr")
programs_stat.heading("mins", text="Min")
programs_stat.heading("secs", text="Sec")
programs_stat.column("exe", width=150, stretch=False)
programs_stat.column("total_hrs", width=100, stretch=False)
programs_stat.column("hrs", width=50, stretch=False)
programs_stat.column("mins", width=50, stretch=False)
programs_stat.column("secs", width=50, stretch=False)
programs_stat.grid(row=1, column=0, sticky="nsew", padx=5)


auto_refresh_active_stats = False
auto_refresh_id_stats = None

def update_stats():
    for item in programs_stat.get_children():
        programs_stat.delete(item)
    focus.update_time_tracking()
    focus.save_time_data_on_demand()
    df_tsip = focus.data_handler.df_time_spent_in_programs
    for index, row in df_tsip.iterrows():
        programs_stat.insert(parent="", index=tk.END, values=(
            row["Program"], row["Total_Hours"], row["Hours"], row["Minutes"], row["Seconds"]
        ))
    print(f"Stats updated: {len(df_tsip)} programs")

def auto_update_stats():
    global auto_refresh_id_stats
    if auto_refresh_active_stats and notebook.index(notebook.select()) == 3:
        try:
            update_stats()
        except:
            pass  # Window might not be focused
        auto_refresh_id_stats = window.after(1000, auto_update_stats)  # Schedule next update

def on_tab_changed(event):
    global auto_refresh_active_stats, auto_refresh_id_stats, auto_refresh_active_activeprograms, auto_refresh_id_activeprograms
    current_tab = notebook.index(notebook.select())
    
    # Handle Active Programs tab (index 0)
    if current_tab == 0:
        auto_refresh_active_activeprograms = True
        auto_update_active_programs()  # Start auto-refresh
    else:
        auto_refresh_active_activeprograms = False
        if auto_refresh_id_activeprograms:
            window.after_cancel(auto_refresh_id_activeprograms)
            auto_refresh_id_activeprograms = None
    
    # Handle Stats tab (index 3)
    if current_tab == 3:
        auto_refresh_active_stats = True
        auto_update_stats()  # Start auto-refresh
    else:
        auto_refresh_active_stats = False
        if auto_refresh_id_stats:
            window.after_cancel(auto_refresh_id_stats)
            auto_refresh_id_stats = None

notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

update_stats_button = ttk.Button(Left_frame_4, text="Update Stats", command=update_stats)
update_stats_button.grid(row=2, column=0, pady=(2, 5))


def on_close():
    global auto_refresh_active_stats, auto_refresh_id_stats
    print("Closing application...")
    try:
        auto_refresh_active_stats = False
        if auto_refresh_id_stats:
            window.after_cancel(auto_refresh_id_stats)
        if focus.app_blocker.block_apps:
            focus.app_blocker.stop()
        focus.save_time_data_on_demand()
        if focus.web_blocker.state == "On":
            focus.web_blocker.unblock_websites()
    except Exception as e:
        print(f"Error during cleanup: {e}")
    finally:
        print("Exiting...")
        window.quit()
        sys.exit(0)


if __name__ == "__main__":
    window.protocol("WM_DELETE_WINDOW", on_close)
    window.mainloop()