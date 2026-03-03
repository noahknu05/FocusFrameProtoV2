import matplotlib.pyplot as plt 
from pathlib import Path  
import pandas as pd 
from FocusFrameProtoV2.plot import Statistics
from focus_main import Focus

class Stats_plotter: 
    def __init__(self, tsip_data_frame=None, screen_time_data_frame=None):
        self.tsip_data_frame = tsip_data_frame
        self.screen_time_data_frame = screen_time_data_frame

    def plot_top_apps(self):
        if self.tsip_data_frame is None or self.tsip_data_frame.empty:
            print("No time spent in programs data to plot.")
            return
        # Filter programs with at least 0.1 hours and group by program
        filtered_data = self.tsip_data_frame[self.tsip_data_frame["Total_Hours"] >= 0.05]
        if filtered_data.empty:
            print("No programs with at least 0.1 hours to plot.")
            return
        grouped = (filtered_data.groupby("Program")["Total_Hours"].sum().sort_values(ascending = False).head(10))

        if grouped.empty:
            print("No data to plot for time spent in programs.")
            return
    
        
        fig, ax = plt.subplots()
        ax.bar(grouped.index, grouped.values)
        ax.set_ylabel("Time used")
        ax.set_xlabel("Programs used")
        ax.set_title("Top used programs (all time)")
        plt.show()

   

    def plot_screen_time(self):
        if self.screen_time_data_frame is None or self.screen_time_data_frame.empty:
            print("No screen time data to plot.")
            return
        Dates = self.screen_time_data_frame["Date"]
        Times = self.screen_time_data_frame["Total_Hours"]
        plt.plot(Dates, Times)
        plt.xlabel("Date")
        plt.ylabel("Hours spent on screen")
        plt.title("Screentime")
        plt.show()

if __name__ == "__main__":
    focus = Focus()
    plotter = Stats_plotter(
        tsip_data_frame=focus.data_handler.df_time_spent_in_programs,
        screen_time_data_frame=focus.data_handler.df_time_spent_on_screen
    )
    plotter.plot_screen_time()
    plotter.plot_top_apps()