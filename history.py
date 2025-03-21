import json
import os
from datetime import datetime

class HistoryManager:
    def __init__(self):
        # Get application directory
        app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define history file path in Data folder
        data_dir = os.path.join(app_dir, "Data")
        self.history_file = os.path.join(data_dir, "history.json")
        
        # Create Data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        self.history = []
        self.play_counts = {}  # Track play counts for today
        self.load_history()
        self._clean_old_counts()

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])
                    self.play_counts = data.get('play_counts', {})
            except Exception as e:
                print(f"Error loading history: {e}")
                # Initialize empty if error
                self.history = []
                self.play_counts = {}

    def save_history(self):
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            with open(self.history_file, 'w') as f:
                json.dump({
                    'history': self.history,
                    'play_counts': self.play_counts
                }, f, indent=4)
        except Exception as e:
            print(f"Error saving history: {e}")

    def _clean_old_counts(self):
        today = datetime.now().strftime('%Y-%m-%d')
        # Reset play counts if it's a new day
        if not any(entry.get('date') == today for entry in self.history):
            self.play_counts = {}
            self.save_history()

    def add_to_history(self, song_path, title):
        current_time = datetime.now()
        date_str = current_time.strftime('%Y-%m-%d')
        time_str = current_time.strftime('%H:%M:%S')
        
        # Update play count for today
        if song_path not in self.play_counts:
            self.play_counts[song_path] = 0
        self.play_counts[song_path] += 1

        # Create new entry
        entry = {
            'path': song_path,
            'title': title,
            'date': date_str,
            'time': time_str,
            'play_count': self.play_counts[song_path]
        }
        
        # Remove old entries of the same song from today
        self.history = [h for h in self.history if not (
            h['path'] == song_path and h['date'] == date_str
        )]
        
        # Add new entry
        self.history.append(entry)
        
        # Keep only last 100 entries
        if len(self.history) > 100:
            self.history = self.history[-100:]
            
        self.save_history()

    def get_history(self):
        return self.history

    def clear_history(self):
        self.history = []
        self.play_counts = {}
        self.save_history()
