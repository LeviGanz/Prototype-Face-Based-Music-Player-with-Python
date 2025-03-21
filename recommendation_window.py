import customtkinter as ctk
from player import MusicPlayer
from tkinter import messagebox

class RecommendationWindow(ctk.CTkToplevel):
    def __init__(self, parent, recommended_songs, playlist_manager, language_manager, detected_emotion):
        super().__init__(parent)
        
        self.recommended_songs = recommended_songs
        self.playlist_manager = playlist_manager
        self.language_manager = language_manager
        self.detected_emotion = detected_emotion
        
        # Configure window
        self.title(self.language_manager.get_text("recommendations"))
        self.geometry("600x400")
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Show emotion label
        emotion_text = self._get_emotion_text()
        emotion_label = ctk.CTkLabel(
            self.main_frame,
            text=emotion_text,
            font=("Helvetica", 16, "bold")
        )
        emotion_label.pack(pady=(0, 20))
        
        # Create scrollable frame for songs
        self.songs_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.songs_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Add recommended songs
        self._add_recommended_songs()
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.center_window()
        
    def center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def _get_emotion_text(self):
        """Get appropriate text based on detected emotion"""
        emotions = {
            0: self.language_manager.get_text("emotion_untagged"),
            1: self.language_manager.get_text("emotion_neutral"),
            2: self.language_manager.get_text("emotion_happy"),
            3: self.language_manager.get_text("emotion_sad")
        }
        emotion_name = emotions.get(self.detected_emotion, "Unknown")
        return f"{self.language_manager.get_text('detected_emotion')}: {emotion_name}"
        
    def _add_recommended_songs(self):
        """Add recommended songs to the window"""
        if not self.recommended_songs:
            no_songs_label = ctk.CTkLabel(
                self.songs_frame,
                text=self.language_manager.get_text("no_recommendations"),
                wraplength=500
            )
            no_songs_label.pack(pady=10)
            return
            
        for song in self.recommended_songs:
            # Create frame for song
            song_frame = ctk.CTkFrame(self.songs_frame)
            song_frame.pack(fill="x", padx=5, pady=2)
            
            # Add song title
            title_label = ctk.CTkLabel(
                song_frame,
                text=song['title'],
                wraplength=400
            )
            title_label.pack(side="left", padx=5, pady=5)
            
            # Add play button
            play_button = ctk.CTkButton(
                song_frame,
                text=self.language_manager.get_text("play"),
                width=60,
                command=lambda s=song: self._play_song(s)
            )
            play_button.pack(side="right", padx=5, pady=5)
            
    def _play_song(self, song):
        """Play the selected song"""
        try:
            # Play the song
            self.playlist_manager.play_song(song['path'])
            # Close the window
            self.destroy()
        except Exception as e:
            print(f"Error playing song: {e}")
            messagebox.showerror("Error", str(e))
