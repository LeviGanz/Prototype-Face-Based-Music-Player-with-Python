import json
import os
import shutil
import customtkinter as ctk
from tkinter import messagebox, filedialog
from camera_manager import CameraManager
from path_utils import get_data_directory

class SettingsManager:
    def __init__(self):
        # Get Data directory using path_utils
        data_dir = get_data_directory()
        
        # Define settings file path in Data folder
        self.settings_file = os.path.join(data_dir, "settings.json")
        
        # Create Data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        self.settings = {
            'music_folder': '',
            'volume': 0.5,
            'last_played': None,
            'language': 'en_US',
            'theme': 'light',
            'emotion_tags': {},  # Store emotion tags persistently
            'window_position': None,
            'last_playlist': None
        }
        self.load_settings()
        self.apply_settings()

    def load_settings(self):
        """Load settings with improved error handling"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    # Update settings while preserving defaults
                    self.settings.update(saved_settings)
                    
                # Verify music folder still exists
                if self.settings['music_folder'] and not os.path.exists(self.settings['music_folder']):
                    self.settings['music_folder'] = ''
                    
            except Exception as e:
                print(f"Error loading settings: {e}")
                # Create backup of corrupted settings
                if os.path.exists(self.settings_file):
                    backup_file = f"{self.settings_file}.backup"
                    try:
                        shutil.copy2(self.settings_file, backup_file)
                    except Exception as be:
                        print(f"Error creating settings backup: {be}")

    def save_settings(self):
        """Save settings with backup"""
        try:
            # Create settings directory if it doesn't exist
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            # Create backup of existing settings
            if os.path.exists(self.settings_file):
                backup_file = f"{self.settings_file}.backup"
                shutil.copy2(self.settings_file, backup_file)
            
            # Save new settings
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
                
        except Exception as e:
            print(f"Error saving settings: {e}")
            messagebox.showerror(
                "Error",
                "Failed to save settings. Please check application permissions."
            )

    def apply_settings(self):
        """Apply settings on startup"""
        # Apply theme
        ctk.set_appearance_mode(self.get_theme())

    def get_music_folder(self):
        return self.settings.get('music_folder', '')

    def set_music_folder(self, folder):
        if folder and os.path.exists(folder):
            self.settings['music_folder'] = folder
            self.save_settings()

    def get_volume(self):
        return self.settings.get('volume', 0.5)

    def set_volume(self, volume):
        self.settings['volume'] = volume
        self.save_settings()

    def get_last_played(self):
        return self.settings.get('last_played')

    def set_last_played(self, song_path):
        self.settings['last_played'] = song_path
        self.save_settings()

    def get_language(self):
        return self.settings.get('language', 'en_US')

    def set_language(self, language):
        self.settings['language'] = language
        self.save_settings()

    def get_theme(self):
        return self.settings.get('theme', 'light')

    def set_theme(self, theme):
        self.settings['theme'] = theme
        self.save_settings()

    def get_emotion_tags(self):
        """Get saved emotion tags for songs"""
        return self.settings.get('emotion_tags', {})

    def save_emotion_tag(self, song_path, emotion):
        """Save emotion tag for a song"""
        if 'emotion_tags' not in self.settings:
            self.settings['emotion_tags'] = {}
        self.settings['emotion_tags'][song_path] = emotion
        self.save_settings()

    def load_emotion_tags(self):
        """Load emotion tags and return them"""
        return self.settings.get('emotion_tags', {})

    def clear_invalid_tags(self):
        """Clear tags for songs that no longer exist"""
        if 'emotion_tags' in self.settings:
            valid_tags = {
                path: emotion 
                for path, emotion in self.settings['emotion_tags'].items() 
                if os.path.exists(path)
            }
            self.settings['emotion_tags'] = valid_tags
            self.save_settings()

    def set_emotion_tag(self, song_path, emotion):
        """Set and persist emotion tag for a song"""
        if 'emotion_tags' not in self.settings:
            self.settings['emotion_tags'] = {}
        
        self.settings['emotion_tags'][song_path] = emotion
        self.save_settings()

    def get_emotion_tag(self, song_path):
        """Get emotion tag for a song"""
        return self.settings.get('emotion_tags', {}).get(song_path, "Untagged")

    def get_songs_by_emotion(self, emotion):
        """Get all songs tagged with specific emotion"""
        tags = self.settings.get('emotion_tags', {})
        return [song for song, tag in tags.items() if tag == emotion]

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, settings_manager, language_manager, playlist_manager):
        super().__init__(parent)
        
        self.settings_manager = settings_manager
        self.language_manager = language_manager
        self.playlist_manager = playlist_manager
        
        # Configure window
        self.title(language_manager.get_text("settings"))
        self.geometry("400x600")
        
        # Create main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Music folder settings
        folder_label = ctk.CTkLabel(
            main_frame,
            text=language_manager.get_text("music_folder"),
            font=("Helvetica", 16, "bold")
        )
        folder_label.pack(pady=(0, 10))
        
        # Show current folder
        self.current_folder_label = ctk.CTkLabel(
            main_frame,
            text=settings_manager.get_music_folder() or language_manager.get_text("no_folder_selected"),
            wraplength=300
        )
        self.current_folder_label.pack(pady=(0, 10))
        
        # Choose folder button
        choose_folder_button = ctk.CTkButton(
            main_frame,
            text=language_manager.get_text("choose_folder"),
            command=self.choose_music_folder
        )
        choose_folder_button.pack(pady=(0, 20))
        
        # Theme settings
        theme_label = ctk.CTkLabel(
            main_frame,
            text=language_manager.get_text("theme"),
            font=("Helvetica", 16, "bold")
        )
        theme_label.pack(pady=(0, 10))
        
        # Theme buttons
        theme_frame = ctk.CTkFrame(main_frame)
        theme_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        light_button = ctk.CTkButton(
            theme_frame,
            text=language_manager.get_text("light"),
            command=lambda: self.change_theme("light")
        )
        light_button.pack(side="left", expand=True, padx=5)
        
        dark_button = ctk.CTkButton(
            theme_frame,
            text=language_manager.get_text("dark"),
            command=lambda: self.change_theme("dark")
        )
        dark_button.pack(side="left", expand=True, padx=5)
        
        # Language settings
        language_label = ctk.CTkLabel(
            main_frame,
            text=language_manager.get_text("language"),
            font=("Helvetica", 16, "bold")
        )
        language_label.pack(pady=(0, 10))
        
        # Language buttons
        language_frame = ctk.CTkFrame(main_frame)
        language_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        en_button = ctk.CTkButton(
            language_frame,
            text="English",
            command=lambda: self.change_language("en")
        )
        en_button.pack(side="left", expand=True, padx=5)
        
        id_button = ctk.CTkButton(
            language_frame,
            text="Indonesia",
            command=lambda: self.change_language("id")
        )
        id_button.pack(side="left", expand=True, padx=5)
        
        # Camera Permission Check
        camera_label = ctk.CTkLabel(
            main_frame,
            text=language_manager.get_text("camera_settings"),
            font=("Helvetica", 16, "bold")
        )
        camera_label.pack(pady=(20, 10))
        
        check_camera_button = ctk.CTkButton(
            main_frame,
            text=language_manager.get_text("check_camera_access"),
            command=self.check_camera_permission
        )
        check_camera_button.pack(pady=(0, 20))
        
        # Close button
        close_button = ctk.CTkButton(
            main_frame,
            text=language_manager.get_text("close"),
            command=self.destroy
        )
        close_button.pack(pady=(20, 0))
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        
    def choose_music_folder(self):
        """Choose music folder and update settings"""
        folder = filedialog.askdirectory()
        if folder:
            self.settings_manager.set_music_folder(folder)
            self.current_folder_label.configure(text=folder)
            self.playlist_manager.load_folder(folder)
        
    def change_theme(self, theme):
        """Change application theme."""
        self.settings_manager.set_theme(theme)
        ctk.set_appearance_mode(theme)
        
    def change_language(self, language):
        """Change application language and restart the application."""
        self.settings_manager.set_language(language)
        self.language_manager.set_language(language)
        
        # Show message about restart
        messagebox.showinfo(
            self.language_manager.get_text("restart_required"),
            self.language_manager.get_text("restart_message")
        )
        
        # Get the root window
        root = self.master
        while root.master is not None:
            root = root.master
        
        # Schedule application restart
        root.after(500, self._restart_application)
        
    def check_camera_permission(self):
        """Check camera permission and show result."""
        if CameraManager.verify_camera_access():
            messagebox.showinfo(
                self.language_manager.get_text("camera_access"),
                self.language_manager.get_text("camera_enabled")
            )
        else:
            messagebox.showerror(
                self.language_manager.get_text("camera_access"),
                self.language_manager.get_text("camera_disabled")
            )
            
    def _restart_application(self):
        """Restart the application to apply language changes."""
        try:
            # Get the root window
            root = self.master
            while root.master is not None:
                root = root.master
                
            # Close the settings window
            self.destroy()
            
            # Close the main application
            root.destroy()
            
            # Restart the application
            import sys
            import os
            import subprocess
            
            # Get the current executable path
            if getattr(sys, 'frozen', False):
                # Running as compiled exe
                application_path = sys.executable
                subprocess.Popen([application_path])
            else:
                # Running in development environment
                application_path = os.path.abspath(__file__)
                script_dir = os.path.dirname(application_path)
                main_script = os.path.join(script_dir, "main.py")
                subprocess.Popen([sys.executable, main_script])
                
        except Exception as e:
            print(f"Error restarting application: {e}")
            messagebox.showerror(
                "Error",
                f"Failed to restart application: {e}"
            )
