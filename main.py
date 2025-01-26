import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests

class F1ChartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("F1 Chart Visualization")

        # Data storage
        self.data = {}

        # UI Setup
        self.setup_ui()

    def setup_ui(self):
        # Frame for chart controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(control_frame, text="F1 Chart Controls").pack()

        # Dropdown for chart types
        ttk.Label(control_frame, text="Select Chart Type:").pack(pady=5)
        self.chart_type = ttk.Combobox(control_frame, values=[
            "Total Points Distribution",
            "Average Finish Position by Driver",
            "Most Wins by Driver",
            "Constructor Championship Standings",
            "Podium Finishes by Driver"
        ], state="readonly")
        self.chart_type.current(0)
        self.chart_type.pack()

        # Input for season
        ttk.Label(control_frame, text="Enter Season:").pack(pady=5)
        self.season_entry = ttk.Entry(control_frame)
        self.season_entry.pack()

        # Button to fetch data
        ttk.Button(control_frame, text="Fetch Data", command=self.fetch_data).pack(pady=5)

        # Button to update chart
        ttk.Button(control_frame, text="Update Chart", command=self.update_chart).pack(pady=5)

        # Matplotlib Figure
        self.figure, self.ax = plt.subplots(figsize=(5, 5))
        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def fetch_data(self):
        season = self.season_entry.get()
        if not season.isdigit():
            messagebox.showerror("Error", "Please enter a valid season year.")
            return

        try:
            # Fetch driver standings
            standings_url = f"https://ergast.com/api/f1/{season}/driverStandings.json"
            standings_response = requests.get(standings_url)
            standings_response.raise_for_status()
            self.data['standings'] = standings_response.json()

            # Fetch race results
            results_url = f"https://ergast.com/api/f1/{season}/results.json?limit=1000"
            results_response = requests.get(results_url)
            results_response.raise_for_status()
            self.data['results'] = results_response.json()

            # Fetch constructor standings
            constructor_standings_url = f"https://ergast.com/api/f1/{season}/constructorStandings.json"
            constructor_standings_response = requests.get(constructor_standings_url)
            constructor_standings_response.raise_for_status()
            self.data['constructor_standings'] = constructor_standings_response.json()

            messagebox.showinfo("Success", "Data fetched successfully!")
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch data: {e}")

    def plot_total_points_distribution(self):
        standings = self.data['standings']['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
        drivers = [driver['Driver']['familyName'] for driver in standings]
        points = [float(driver['points']) for driver in standings]

        self.ax.bar(drivers, points)
        self.ax.set_title("Total Points Distribution")
        self.ax.set_xlabel("Driver")
        self.ax.set_ylabel("Total Points")
        self.ax.tick_params(axis='x', rotation=90)

    def plot_average_finish_position_by_driver(self):
        results = self.data['results']['MRData']['RaceTable']['Races']
        finish_positions = {}

        for race in results:
            for result in race['Results']:
                driver = result['Driver']['familyName']
                position = int(result['position'])
                if driver not in finish_positions:
                    finish_positions[driver] = []
                finish_positions[driver].append(position)

        drivers = list(finish_positions.keys())
        avg_positions = [sum(positions) / len(positions) for positions in finish_positions.values()]

        self.ax.bar(drivers, avg_positions)
        self.ax.set_title("Average Finish Position by Driver")
        self.ax.set_xlabel("Driver")
        self.ax.set_ylabel("Average Finish Position")
        self.ax.tick_params(axis='x', rotation=90)

    def plot_most_wins_by_driver(self):
        results = self.data['results']['MRData']['RaceTable']['Races']
        win_counts = {}

        for race in results:
            winner = race['Results'][0]
            driver = winner['Driver']['familyName']
            win_counts[driver] = win_counts.get(driver, 0) + 1

        drivers = list(win_counts.keys())
        wins = list(win_counts.values())

        self.ax.bar(drivers, wins)
        self.ax.set_title("Most Wins by Driver")
        self.ax.set_xlabel("Driver")
        self.ax.set_ylabel("Wins")
        self.ax.tick_params(axis='x', rotation=90)

    def plot_constructor_championship_standings(self):
        standings = self.data['constructor_standings']['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
        constructors = [constructor['Constructor']['name'] for constructor in standings]
        points = [float(constructor['points']) for constructor in standings]

        self.ax.bar(constructors, points)
        self.ax.set_title("Constructor Championship Standings")
        self.ax.set_xlabel("Constructor")
        self.ax.set_ylabel("Points")
        self.ax.tick_params(axis='x', rotation=90)

    def plot_podium_finishes_by_driver(self):
        results = self.data['results']['MRData']['RaceTable']['Races']
        podium_counts = {}

        for race in results:
            for result in race['Results']:
                position = int(result['position'])
                if position <= 3:
                    driver = result['Driver']['familyName']
                    podium_counts[driver] = podium_counts.get(driver, 0) + 1

        drivers = list(podium_counts.keys())
        podiums = list(podium_counts.values())

        self.ax.bar(drivers, podiums)
        self.ax.set_title("Podium Finishes by Driver")
        self.ax.set_xlabel("Driver")
        self.ax.set_ylabel("Podium Finishes")
        self.ax.tick_params(axis='x', rotation=90)

    def update_chart(self):
        chart_type = self.chart_type.get()
        if not self.data:
            messagebox.showerror("Error", "No data available. Please fetch data first.")
            return

        self.ax.clear()

        if chart_type == "Total Points Distribution":
            self.plot_total_points_distribution()
        elif chart_type == "Average Finish Position by Driver":
            self.plot_average_finish_position_by_driver()
        elif chart_type == "Most Wins by Driver":
            self.plot_most_wins_by_driver()
        elif chart_type == "Constructor Championship Standings":
            self.plot_constructor_championship_standings()
        elif chart_type == "Podium Finishes by Driver":
            self.plot_podium_finishes_by_driver()

        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = F1ChartApp(root)
    root.mainloop()
