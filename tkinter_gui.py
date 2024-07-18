import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import io
from PIL import Image, ImageTk

class TeamInputGUI:
    def __init__(self, master):
        self.master = master
        master.title('Valorant Predict GUI')
        master.geometry('900x720')
        self.set_icon()
        self.create_widgets()
        
    def set_icon(self):
        icon = Image.open('icon.png')
        photo = ImageTk.PhotoImage(icon)
        self.master.iconphoto(False, photo)

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame for map input and model selection
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        # Map input
        map_frame = ttk.Frame(top_frame)
        map_frame.pack(side=tk.LEFT)
        ttk.Label(map_frame, text="Map:").pack(side=tk.LEFT)
        self.map_input = ttk.Combobox(map_frame, values=['Ascent', 'Bind', 'Breeze', 'Fracture', 'Haven', 'Icebox', 'Lotus', 'Pearl', 'Split', 'Sunset'])
        self.map_input.pack(side=tk.LEFT, padx=(5, 20))

        # Model Selection
        model_frame = ttk.Frame(top_frame)
        model_frame.pack(side=tk.LEFT)
        ttk.Label(model_frame, text="Model:").pack(side=tk.LEFT)
        self.api = ttk.Combobox(model_frame, values=["XGBoost", "Neural Network"])
        self.api.pack(side=tk.LEFT, padx=5)

        # Team inputs
        teams_frame = ttk.Frame(main_frame)
        teams_frame.pack(fill=tk.X, expand=False)  # Changed to X, not expanding vertically

        self.team_inputs = []
        team_names = ["Defender team", "Attacker team"]
        feature_names = ["Agent", "Rating", "ACS", "KAST (%)", "ADR"]

        for team_index, team_name in enumerate(team_names):
            team_frame = ttk.LabelFrame(teams_frame, text=team_name, padding="5")  # Reduced padding
            team_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            team_players = []
            for i in range(5):
                player_frame = ttk.Frame(team_frame)
                player_frame.pack(fill=tk.X)
                ttk.Label(player_frame, text=f"P{i+1}", width=3).pack(side=tk.LEFT)  # Shortened label
                player_features = []
                for j, feature in enumerate(feature_names):
                    feature_frame = ttk.Frame(player_frame)
                    feature_frame.pack(side=tk.LEFT, padx=5)  # Reduced padding
                    ttk.Label(feature_frame, text=feature, font=('Arial', 8)).pack()  # Smaller font
                    if j == 0:
                        entry = ttk.Combobox(feature_frame, width=10, values=['Astra', 'Breach', 'Brimstone', 'Chamber', 'Cypher', 'Deadlock', 'Fade', 'Gekko',
                        'Harbor', 'Iso', 'Jett', 'Kayo', 'Killjoy', 'Neon', 'Omen', 'Phoenix', 'Raze',
                        'Reyna', 'Sage', 'Skye', 'Sova', 'Viper', 'Yoru'])
                    else:
                        entry = ttk.Entry(feature_frame, width=10)
                    entry.pack()
                    player_features.append(entry)
                team_players.append(player_features)
            self.team_inputs.append(team_players)

        # Submit button
        submit_btn = ttk.Button(main_frame, text='Predict !', command=self.submit_data)
        submit_btn.pack(pady=10)

        # Result display area
        self.result_frame = ttk.Frame(main_frame)
        self.result_frame.pack(fill=tk.BOTH, expand=True)

    def submit_data(self):
        data = []
        for team in self.team_inputs:
            for player in team:
                player_data = [entry.get() for entry in player]
                data.extend(player_data)
        
        data.append(self.map_input.get())
        
        json_data = json.dumps({"data": data})
        
        try:
            response = requests.post(f'http://{"127.0.0.1" if self.api.get() == "XGBoost" else "127.0.0.2"}:8000/predict', data=json_data)
            response.raise_for_status()
            
            result = response.json()
            self.display_result(result)
        except requests.exceptions.RequestException as e:
            self.display_error(f"Error communicating with API: {str(e)}")

    def display_result(self, result):
        # Clear previous results
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        # Create horizontal bar chart
        fig, ax = plt.subplots(figsize=(8, 3))
        teams = ['Defender', 'Attacker']
        probas = [result['ct_proba'], result['t_proba']]
        colors = ['blue' if result['ct_prediction'] == 'win' else 'red',
                  'blue' if result['t_prediction'] == 'win' else 'red']

        ax.barh(teams, probas, color=colors)
        ax.set_xlim(0, 1)
        ax.set_xlabel('Win Probability')
        ax.set_title('Team Win Probabilities')

        for i, v in enumerate(probas):
            ax.text(v, i, f'{v:.2%}', va='center')

        # Embed the chart in the GUI
        canvas = FigureCanvasTkAgg(fig, master=self.result_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Display text results
        text_result = f"Defender team: {result['ct_prediction']} (probability: {result['ct_proba']:.2%})\n"
        text_result += f"Attacker team: {result['t_prediction']} (probability: {result['t_proba']:.2%})"
        result_label = ttk.Label(self.result_frame, text=text_result, justify=tk.LEFT)
        result_label.pack(pady=10)

    def display_error(self, error_message):
        # Clear previous results
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        # Display error message
        error_label = ttk.Label(self.result_frame, text=error_message, foreground='red')
        error_label.pack(pady=10)

if __name__ == '__main__':
    root = tk.Tk()
    gui = TeamInputGUI(root)
    root.mainloop()