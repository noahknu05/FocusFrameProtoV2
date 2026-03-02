import pandas as pd
import os

class DataHandler:
    def __init__(self, whitelist):
        self.df_tsip_programs_path = "time_spent_in_programs.csv"
        self.df_time_spent_in_programs = self.load_time_spent_in_programs()
        self.df_time_spent_on_screen_path = "time_spent_on_screen.csv"
        self.df_time_spent_on_screen = self.load_time_spent_on_screen()
        self.whitelist = whitelist

       

    def save_dataframe_to_csv(self, df, filename):
        df.to_csv(filename, index=False)

    def load_data_from_csv(self, filename):
        try:
            return pd.read_csv(filename)
        except FileNotFoundError:
            if filename == self.df_time_spent_on_screen_path:
                print(f"File {filename} not found. Returning empty DataFrame.")
                return pd.DataFrame(columns=["Date", "Hours"])
            elif filename == self.df_tsip_programs_path:
                print(f"File {filename} not found. Returning empty DataFrame.")
                return pd.DataFrame(columns=["Program", "Hours", "Minutes", "Seconds"])

    # Load data into DataFrames
    def load_time_spent_in_programs(self):
        if os.path.exists(self.df_tsip_programs_path):
            self.df_time_spent_in_programs = self.load_data_from_csv(self.df_tsip_programs_path)
        else:
            self.df_time_spent_in_programs = pd.DataFrame(columns=["Program", "Hours", "Minutes", "Seconds", "Total_Hours"])
            self.save_dataframe_to_csv(self.df_time_spent_in_programs, self.df_tsip_programs_path)
        return self.df_time_spent_in_programs
            
    def load_time_spent_on_screen(self):
        if os.path.exists(self.df_time_spent_on_screen_path):
            self.df_time_spent_on_screen = self.load_data_from_csv(self.df_time_spent_on_screen_path)
        else:
            self.df_time_spent_on_screen = pd.DataFrame(columns=["Date", "Hours", "Minutes", "Seconds", "Total_Hours"])
            self.save_dataframe_to_csv(self.df_time_spent_on_screen, self.df_time_spent_on_screen_path)
        return self.df_time_spent_on_screen
    #------------------------------------------------------------

    # Add new data to the Dataframes
    def add_data_to_tsip(self, program, hours=0, minutes=0, seconds=0):
        if program in self.whitelist:
            return
        df_tsip = self.df_time_spent_in_programs.set_index("Program")
        
        if program in df_tsip.index:
            pass
        else:
            hours_spent = round((hours + (minutes / 60) + (seconds / 3600)), 2)
            df_tsip.loc[program] = [hours, minutes, seconds, hours_spent]
            
        df_tsip.at[program, "Hours"] += hours
        df_tsip.at[program, "Minutes"] += minutes
        df_tsip.at[program, "Seconds"] += seconds
        
        if df_tsip.at[program, "Seconds"] >= 60:
            df_tsip.at[program, "Minutes"] += df_tsip.at[program, "Seconds"] // 60
            df_tsip.at[program, "Seconds"] = df_tsip.at[program, "Seconds"] % 60
        if df_tsip.at[program, "Minutes"] >= 60:
            df_tsip.at[program, "Hours"] += df_tsip.at[program, "Minutes"] // 60
            df_tsip.at[program, "Minutes"] = df_tsip.at[program, "Minutes"] % 60
        
        # Calculate and update Total_Hours
        final_seconds = df_tsip.at[program, "Seconds"]
        final_minutes = df_tsip.at[program, "Minutes"]
        final_hours = df_tsip.at[program, "Hours"]
        total_hr = round(final_hours + (final_minutes / 60) + (final_seconds / 3600), 2)
        df_tsip.at[program, "Total_Hours"] = total_hr
        
        df_tsip.sort_values(by=["Total_Hours"], ascending=False, inplace=True)
        df_tsip.reset_index(inplace=True)
        self.df_time_spent_in_programs = df_tsip
        self.save_dataframe_to_csv(df_tsip, self.df_tsip_programs_path)

    def add_data_to_tsos(self, date, hours= 0, minutes=0, seconds=0):
        df_tsos = self.df_time_spent_on_screen.set_index("Date")
        
        if date in df_tsos.index:
            pass
        else:
            hours_spent = round((hours + (minutes / 60) + (seconds / 3600)), 2)
            df_tsos.loc[date] = [hours, minutes, seconds, hours_spent]
            
        df_tsos.at[date, "Hours"] += hours
        df_tsos.at[date, "Minutes"] += minutes
        df_tsos.at[date, "Seconds"] += seconds
        
        if df_tsos.at[date, "Seconds"] >= 60:
            df_tsos.at[date, "Minutes"] += df_tsos.at[date, "Seconds"] // 60
            df_tsos.at[date, "Seconds"] = df_tsos.at[date, "Seconds"] % 60
        if df_tsos.at[date, "Minutes"] >= 60:
            df_tsos.at[date, "Hours"] += df_tsos.at[date, "Minutes"] // 60
            df_tsos.at[date, "Minutes"] = df_tsos.at[date, "Minutes"] % 60
        
        # Calculate and update Total_Hours
        final_seconds = df_tsos.at[date, "Seconds"]
        final_minutes = df_tsos.at[date, "Minutes"]
        final_hours = df_tsos.at[date, "Hours"]
        total_hr = round(final_hours + (final_minutes / 60) + (final_seconds / 3600), 2)
        df_tsos.at[date, "Total_Hours"] = total_hr
        
        df_tsos.reset_index(inplace=True)
        self.df_time_spent_on_screen = df_tsos
        self.save_dataframe_to_csv(df_tsos, self.df_time_spent_on_screen_path)

    def update_data_frames(self, program, hours, minutes, seconds, date):
        self.add_data_to_tsip(program, hours, minutes, seconds)
        self.add_data_to_tsos(date, hours, minutes, seconds)

if __name__ == "__main__":
    data_handler = DataHandler()
    data_handler.add_data_to_tsip("Test Program", 1)
    data_handler.add_data_to_tsos("2024-06-01", 1)