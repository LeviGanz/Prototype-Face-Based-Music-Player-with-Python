import os
import json
import random
from mutagen import File
import customtkinter as ctk
from tkinter import ttk

class PlaylistManager:
    # Emotion class numbers
    UNTAGGED = 0
    NEUTRAL = 1
    HAPPY = 2
    SAD = 3

    def __init__(self):
        self.current_folder = None
        self.playlist = []
        self.supported_formats = ['.mp3', '.wav', '.ogg']
        
        # Get application directory
        app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define tags file path in Data folder
        data_dir = os.path.join(app_dir, "Data")
        self.tags_file = os.path.join(data_dir, "song_tags.json")
        
        # Create Data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        self.song_tags = self.load_song_tags()
        
        # Emotion mapping
        self.emotion_map = {
            'neutral': self.NEUTRAL,
            'happy': self.HAPPY,
            'sad': self.SAD
        }
        self.emotion_names = {
            self.NEUTRAL: 'neutral',
            self.HAPPY: 'happy',
            self.SAD: 'sad'
        }

    def load_song_tags(self):
        """Load saved song tags from file"""
        if os.path.exists(self.tags_file):
            try:
                with open(self.tags_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading song tags: {e}")
        return {}

    def save_song_tags(self):
        """Save song tags to file"""
        try:
            with open(self.tags_file, 'w') as f:
                json.dump(self.song_tags, f, indent=4)
        except Exception as e:
            print(f"Error saving song tags: {e}")

    def load_folder(self, folder_path):
        """Load music files from folder"""
        try:
            if not os.path.exists(folder_path):
                print(f"Folder not found: {folder_path}")
                return False
                
            # Clear existing playlist
            self.playlist.clear()
            
            # Load saved emotion tags
            saved_tags = self.load_song_tags()
            
            # Walk through directory
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
                        file_path = os.path.join(root, file)
                        
                        # Create song entry
                        song = {
                            'path': file_path,
                            'title': os.path.splitext(file)[0],
                            'emotions': saved_tags.get(file_path, {'emotions': [], 'emotion_numbers': []})['emotions'],
                            'emotion_numbers': saved_tags.get(file_path, {'emotions': [], 'emotion_numbers': []})['emotion_numbers']
                        }
                        
                        self.playlist.append(song)
                        
            # Sort playlist by title
            self.playlist.sort(key=lambda x: x['title'].lower())
            
            print(f"Loaded {len(self.playlist)} songs from {folder_path}")
            return True
            
        except Exception as e:
            print(f"Error loading folder: {e}")
            return False

    def add_tag(self, song_path, emotion):
        """Add an emotion tag to a song"""
        if song_path not in self.song_tags:
            self.song_tags[song_path] = {'emotions': [], 'emotion_numbers': []}
            
        tags = self.song_tags[song_path]
        
        # Add emotion name if not present
        if emotion not in tags['emotions']:
            tags['emotions'].append(emotion)
            
        # Add emotion number if not present
        emotion_number = self.emotion_map.get(emotion, self.UNTAGGED)
        if emotion_number not in tags['emotion_numbers']:
            tags['emotion_numbers'].append(emotion_number)
            
        self.save_song_tags()
            
        # Update playlist entry
        for song in self.playlist:
            if song['path'] == song_path:
                if emotion not in song['emotions']:
                    song['emotions'].append(emotion)
                if emotion_number not in song['emotion_numbers']:
                    song['emotion_numbers'].append(emotion_number)
                break

    def remove_tag(self, song_path, emotion):
        """Remove an emotion tag from a song"""
        if song_path in self.song_tags:
            tags = self.song_tags[song_path]
            emotion_number = self.emotion_map.get(emotion, self.UNTAGGED)
            
            if emotion in tags['emotions']:
                tags['emotions'].remove(emotion)
            if emotion_number in tags['emotion_numbers']:
                tags['emotion_numbers'].remove(emotion_number)
                
            self.save_song_tags()
            
            # Update playlist entry
            for song in self.playlist:
                if song['path'] == song_path:
                    if emotion in song['emotions']:
                        song['emotions'].remove(emotion)
                    if emotion_number in song['emotion_numbers']:
                        song['emotion_numbers'].remove(emotion_number)
                    break

    def get_songs_by_tag(self, emotion):
        """Get all songs with a specific emotion tag"""
        emotion_number = self.emotion_map.get(emotion, self.UNTAGGED)
        return [song for song in self.playlist if emotion_number in song.get('emotion_numbers', [])]

    def search_songs(self, query):
        """Search songs by title"""
        query = query.lower()
        return [song for song in self.playlist if query in song['title'].lower()]

    def get_recommendations(self, emotion):
        """Get song recommendations based on emotion"""
        try:
            print(f"Getting recommendations for emotion: {emotion}")  # Debug
            
            # Get songs matching the emotion
            matching_songs = self.get_songs_by_tag(emotion)
            print(f"Found {len(matching_songs)} songs with {emotion} tag")  # Debug
            
            # If no songs found for the emotion, use happy songs as fallback
            if not matching_songs and emotion != 'happy':
                print("No matching songs found, falling back to happy songs")  # Debug
                matching_songs = self.get_songs_by_tag('happy')
            
            # If still no songs, return empty list
            if not matching_songs:
                print("No recommendations found")  # Debug
                return []
            
            # Get the song titles
            recommendations = [song['title'] for song in matching_songs]
            
            # Shuffle the recommendations
            random.shuffle(recommendations)
            
            # Return at most 10 recommendations
            recommendations = recommendations[:10]
            print(f"Returning {len(recommendations)} recommendations")  # Debug
            
            return recommendations
            
        except Exception as e:
            print(f"Error getting recommendations: {str(e)}")  # Debug
            return []

    def get_playlist(self):
        return self.playlist

    def get_current_folder(self):
        return self.current_folder

class PlaylistFrame(ctk.CTkFrame):
    def __init__(self, parent, playlist_manager, language_manager, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.playlist_manager = playlist_manager
        self.language_manager = language_manager
        
        # Create top frame for search and filters
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill="x", padx=5, pady=5)
        
        # Create search frame with search bar
        self.search_frame = ctk.CTkFrame(self.top_frame)
        self.search_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        self.search_entry = ctk.CTkEntry(
            self.search_frame, 
            placeholder_text=self.language_manager.get_text("search_songs"),
            textvariable=self.search_var,
            width=200
        )
        self.search_entry.pack(side="left", padx=5, pady=5)
        
        # Create filter buttons
        self.filter_frame = ctk.CTkFrame(self.top_frame)
        self.filter_frame.pack(side="right", padx=5)
        
        self.filter_buttons = {}
        emotions = ['all', 'neutral', 'happy', 'sad']
        
        for emotion in emotions:
            btn = ctk.CTkButton(
                self.filter_frame,
                text=self.language_manager.get_text(emotion),
                command=lambda e=emotion: self.filter_playlist(e),
                width=80
            )
            btn.pack(side="left", padx=2)
            self.filter_buttons[emotion] = btn
        
        # Create playlist tree with scrollbar
        self.tree = ttk.Treeview(
            self,
            columns=("Title", "Tags"),
            show="headings",
            selectmode="browse"
        )
        
        self.tree.heading("Title", text=self.language_manager.get_text("title"))
        self.tree.heading("Tags", text=self.language_manager.get_text("tags"))
        
        self.tree.column("Title", width=300)
        self.tree.column("Tags", width=150)
        
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Create tag buttons
        self.tag_frame = ctk.CTkFrame(self)
        self.tag_frame.pack(fill="x", padx=5, pady=5)
        
        tag_emotions = ['neutral', 'happy', 'sad']
        for emotion in tag_emotions:
            btn = ctk.CTkButton(
                self.tag_frame,
                text=f"{self.language_manager.get_text('tag')} {self.language_manager.get_text(emotion)}",
                command=lambda e=emotion: self.tag_selected_song(e),
                width=120
            )
            btn.pack(side="left", padx=2)
        
        self.remove_tag_btn = ctk.CTkButton(
            self.tag_frame,
            text=self.language_manager.get_text("remove_tag"),
            command=self.remove_selected_tag,
            width=120
        )
        self.remove_tag_btn.pack(side="right", padx=2)
        
        # Bind double click
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Initialize state
        self.current_filter = 'all'
        self.current_search = ''
        
        # Update playlist
        self.update_playlist()
    
    def update_playlist(self):
        """Update the playlist display"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get playlist with filters
        playlist = self.playlist_manager.get_playlist()
        
        if self.current_search:
            playlist = self.playlist_manager.search_songs(self.current_search)
        
        if self.current_filter != 'all':
            playlist = self.playlist_manager.get_songs_by_tag(self.current_filter)
        
        # Add songs to tree
        for song in playlist:
            tags = ", ".join(song['emotions']) if song['emotions'] else ""
            self.tree.insert("", "end", values=(song['title'], tags), tags=(song['path'],))
    
    def on_search_change(self, *args):
        """Handle search input changes"""
        self.current_search = self.search_var.get()
        self.update_playlist()
    
    def filter_playlist(self, emotion):
        """Filter playlist by emotion"""
        self.current_filter = emotion
        self.update_playlist()
        
        # Update button states
        for btn_emotion, btn in self.filter_buttons.items():
            if btn_emotion == emotion:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color=("gray70", "gray30"))
    
    def tag_selected_song(self, emotion):
        """Add emotion tag to selected song"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            song_path = self.tree.item(item, "tags")[0]
            self.playlist_manager.add_tag(song_path, emotion)
            self.update_playlist()
    
    def remove_selected_tag(self):
        """Remove tag from selected song"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            song_path = self.tree.item(item, "tags")[0]
            current_tags = self.tree.item(item, "values")[1].split(", ")
            
            if current_tags and current_tags[0]:
                tag_to_remove = current_tags[-1]
                self.playlist_manager.remove_tag(song_path, tag_to_remove)
                self.update_playlist()
    
    def on_double_click(self, event):
        """Handle double click on song"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            song_path = self.tree.item(item, "tags")[0]
            
            if hasattr(self, "on_song_selected") and callable(self.on_song_selected):
                self.on_song_selected(song_path)
