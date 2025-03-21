import customtkinter as ctk
import tkinter as tk
import os
import shutil
import json
from tkinter import messagebox
from player import MusicPlayer
from playlist import PlaylistManager
from history import HistoryManager
from settings import SettingsManager
from emotion_manager import EmotionManager
from language_manager import LanguageManager
from ui import PlayerUI
from camera_manager import CameraManager

class MusicPlayerApp:
    def __init__(self):
        try:
            # Set up the application
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("dark-blue")
            
            # Create root window
            self.root = ctk.CTk()
            self.root.title("KaisarPlayer")
            self.root.geometry("800x600")
            
            # Create Data folder structure
            self._create_data_folders()
            
            # Initialize managers
            self.settings_manager = SettingsManager()
            self.emotion_manager = EmotionManager()
            self.language_manager = LanguageManager()
            self.playlist_manager = PlaylistManager()
            self.history_manager = HistoryManager()
            self.player = MusicPlayer(self.playlist_manager, self.history_manager)
            
            # Initialize UI
            self.ui = PlayerUI(self.root, self.player, self.playlist_manager, 
                             self.history_manager, self.settings_manager, 
                             self.emotion_manager, self.language_manager)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def run(self):
        self.root.mainloop()
        
    def _create_data_folders(self):
        """Create necessary Data folder structure"""
        try:
            # Use path_utils to get directory paths
            from path_utils import get_data_directory, get_languages_directory, get_temp_image_directory, get_emotions_file_path
            
            # Get directory paths
            data_dir = get_data_directory()
            languages_dir = get_languages_directory()
            temp_image_dir = get_temp_image_directory()
            emotions_file = get_emotions_file_path()
            
            # Create directories if they don't exist
            os.makedirs(data_dir, exist_ok=True)
            os.makedirs(languages_dir, exist_ok=True)
            os.makedirs(temp_image_dir, exist_ok=True)
            
            # Create emotions.json file if it doesn't exist
            if not os.path.exists(emotions_file):
                with open(emotions_file, 'w') as f:
                    json.dump({}, f, indent=4)
                print(f"Created emotions file at {emotions_file}")
            
            # Copy language files if they don't exist in Data/Languages
            # For PyInstaller, the languages folder is included in the executable directory
            import sys
            app_dir = os.path.dirname(os.path.abspath(__file__))
            source_lang_dir = os.path.join(app_dir, "languages")
            if not os.path.exists(source_lang_dir) and hasattr(sys, '_MEIPASS'):
                source_lang_dir = os.path.join(sys._MEIPASS, "languages")
                
            if os.path.exists(source_lang_dir):
                for lang_file in os.listdir(source_lang_dir):
                    src_file = os.path.join(source_lang_dir, lang_file)
                    dst_file = os.path.join(languages_dir, lang_file)
                    if not os.path.exists(dst_file):
                        shutil.copy2(src_file, dst_file)
                        
            print(f"Data folder structure created at {data_dir}")
            
        except Exception as e:
            print(f"Error creating Data folders: {e}")
            messagebox.showerror("Error", f"Failed to create Data folders: {e}")

if __name__ == "__main__":
    app = MusicPlayerApp()
    app.run()
