import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Stats_plotter:
    def __init__(self, parent, tsip_data_frame=None, screen_time_data_frame=None):
        self.parent = parent
        self.tsip_data_frame = tsip_data_frame
        self.screen_time_data_frame = screen_time_data_frame

        # Create figure and axis
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)

        # Embed into existing UI
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def clear(self):
        self.ax.clear()

    def plot_top_apps(self):
        if self.tsip_data_frame is None or self.tsip_data_frame.empty:
            return

        filtered = self.tsip_data_frame[
            self.tsip_data_frame["Total_Hours"] >= 0.05
        ]

        grouped = (
            filtered.groupby("Program")["Total_Hours"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        if grouped.empty:
            return

        self.clear()

        self.ax.bar(grouped.index, grouped.values)
        self.ax.set_title("Top used programs (all time)")
        self.ax.set_ylabel("Time used")
        self.ax.tick_params(axis="x", rotation=45)

        self.canvas.draw()

    def plot_screen_time(self):
        if self.screen_time_data_frame is None or self.screen_time_data_frame.empty:
            return

        self.clear()

        dates = self.screen_time_data_frame["Date"]
        times = self.screen_time_data_frame["Total_Hours"]

        self.ax.plot(dates, times)
        self.ax.set_title("Screentime")
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Hours spent on screen")

        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    plotter = Stats_plotter(root)
    plotter.plot_screen_time()
    plotter.plot_top_apps()
    root.mainloop()