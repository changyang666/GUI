import sys
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QGroupBox, 
                             QGridLayout, QScrollArea, QTextEdit, QSplitter)
from PyQt5.QtCore import Qt
import requests

class TeamInputGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Create a splitter for input area and result display
        splitter = QSplitter(Qt.Vertical)

        # Input area
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)

        # Map input
        map_layout = QHBoxLayout()
        map_layout.addWidget(QLabel('Map:'), stretch=1)
        self.map_input = QLineEdit()
        map_layout.addWidget(self.map_input, stretch=3)
        input_layout.addLayout(map_layout)

        # Create scroll area for team inputs
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QHBoxLayout(scroll_content)

        # Team inputs
        self.team_inputs = []
        team_names = ["Defender team", "Attacker team"]
        for i in range(2):
            team_group = QGroupBox(team_names[i])
            team_layout = QGridLayout()
            team_players = []

            # Add feature labels
            team_layout.addWidget(QLabel("Agent"), 0, 1)
            team_layout.addWidget(QLabel("Rating"), 0, 2)
            team_layout.addWidget(QLabel("ACS"), 0, 3)
            team_layout.addWidget(QLabel("KAST"), 0, 4)
            team_layout.addWidget(QLabel("ADR"), 0, 5)

            for j in range(5):
                team_layout.addWidget(QLabel(f"Player {j+1}"), j+1, 0)
                player_features = []
                for k in range(5):
                    feature_input = QLineEdit()
                    team_layout.addWidget(feature_input, j+1, k+1)
                    player_features.append(feature_input)
                team_players.append(player_features)

            team_group.setLayout(team_layout)
            scroll_layout.addWidget(team_group)
            self.team_inputs.append(team_players)

        scroll.setWidget(scroll_content)
        input_layout.addWidget(scroll)

        # Submit button
        submit_btn = QPushButton('Submit')
        submit_btn.clicked.connect(self.submit_data)
        input_layout.addWidget(submit_btn)

        splitter.addWidget(input_widget)

        # Result display area
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        splitter.addWidget(self.result_display)

        main_layout.addWidget(splitter)

        self.setLayout(main_layout)
        self.setWindowTitle('Valorant Predict GUI')
        self.setGeometry(100, 100, 1000, 500)
        self.show()

    def submit_data(self):
        # Prepare data for API
        data = []
        
        team_names = ["CT team", "T team"]
        for i, team in enumerate(self.team_inputs):
            data["teams"][team_names[i]] = []
            for player in team:
                player_data = {f"Feature {k+1}": feature.text() for k, feature in enumerate(player)}
                data["teams"][team_names[i]].append(player_data)

        # Send data to API
        try:
            # Replace 'https://api.example.com/submit' with your actual API endpoint
            response = requests.post('http://0.0.0.0:8000/predict', json=data)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            
            # Display API response
            result_text = f"API Response:\n{response.text}"
            self.result_display.setPlainText(result_text)
        except requests.exceptions.RequestException as e:
            # Handle API errors
            error_text = f"Error communicating with API: {str(e)}"
            self.result_display.setPlainText(error_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TeamInputGUI()
    sys.exit(app.exec_())