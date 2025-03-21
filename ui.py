import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from PIL import Image
import time
import threading
from emotion_manager import EmotionManager
from camera_manager import CameraManager

class PlayerUI:
    def __init__(self, root, player, playlist_manager, history_manager, settings_manager, emotion_manager, language_manager):
        self.root = root
        self.player = player
        self.playlist_manager = playlist_manager
        self.history_manager = history_manager
        self.settings_manager = settings_manager
        self.emotion_manager = emotion_manager
        self.language_manager = language_manager
        
        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Initialize camera manager as None
        self.camera_manager = None
        
        # Load saved language
        self.language_manager.set_language(self.settings_manager.get_language())
        
        self._setup_ui()
        self._load_saved_settings()
        
    def _setup_ui(self):
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        
        # Create tabs
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        self.tab_player = self.tab_view.add(self.language_manager.get_text("player"))
        self.tab_playlist = self.tab_view.add(self.language_manager.get_text("playlist"))
        self.tab_history = self.tab_view.add(self.language_manager.get_text("history"))
        
        # Setup each tab
        self._setup_player_tab()
        self._setup_playlist_tab()
        self._setup_history_tab()
        self._setup_settings_button()

    def _setup_player_tab(self):
        # Create main player frame with dark grey background
        player_frame = ctk.CTkFrame(self.tab_player, fg_color="#2B2B2B")
        player_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Current song frame
        current_song_frame = ctk.CTkFrame(player_frame, fg_color="#2B2B2B")
        current_song_frame.pack(pady=10, fill="x")
        
        self.current_song_label = ctk.CTkLabel(
            current_song_frame,
            text=self.language_manager.get_text("no_song_playing"),
            font=("Helvetica", 16),
            wraplength=400
        )
        self.current_song_label.pack(pady=10)
        
        # Control buttons frame
        self.controls_frame = ctk.CTkFrame(player_frame, fg_color="#2B2B2B")
        self.controls_frame.pack(pady=10)
        
        # Previous button
        self.prev_button = ctk.CTkButton(
            self.controls_frame,
            text="⏮",
            width=40,
            command=self._play_previous,
            fg_color="#404040",
            hover_color="#505050"
        )
        self.prev_button.pack(side="left", padx=5)
        
        # Play button
        self.play_button = ctk.CTkButton(
            self.controls_frame,
            text="▶",
            width=40,
            command=self._play_pause,
            fg_color="#404040",
            hover_color="#505050"
        )
        self.play_button.pack(side="left", padx=5)
        
        # Next button
        self.next_button = ctk.CTkButton(
            self.controls_frame,
            text="⏭",
            width=40,
            command=self._play_next,
            fg_color="#404040",
            hover_color="#505050"
        )
        self.next_button.pack(side="left", padx=5)
        
        # Volume slider frame
        volume_frame = ctk.CTkFrame(player_frame, fg_color="#2B2B2B")
        volume_frame.pack(pady=10)
        
        volume_label = ctk.CTkLabel(
            volume_frame,
            text=self.language_manager.get_text("volume")
        )
        volume_label.pack(side="left", padx=5)
        
        self.volume_slider = ctk.CTkSlider(
            volume_frame,
            from_=0,
            to=100,
            command=self._update_volume,
            width=200
        )
        self.volume_slider.pack(side="left", padx=5)
        self.volume_slider.set(50)

        # Emotion detection button (moved below volume slider)
        emotion_frame = ctk.CTkFrame(player_frame, fg_color="#2B2B2B")
        emotion_frame.pack(pady=10)
        
        self.emotion_button = ctk.CTkButton(
            emotion_frame,
            text=self.language_manager.get_text("detect_emotion"),
            width=120,
            command=self._open_camera,
            fg_color="#404040",
            hover_color="#505050"
        )
        self.emotion_button.pack(padx=20)
        
    def _setup_playlist_tab(self):
        # Create frames
        playlist_frame = ctk.CTkFrame(self.tab_playlist)
        playlist_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Controls frame
        controls_frame = ctk.CTkFrame(playlist_frame)
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        # Tag emotion button
        tag_button = ctk.CTkButton(
            controls_frame,
            text=self.language_manager.get_text("tag_emotion"),
            command=self._tag_emotion
        )
        tag_button.pack(side="left", padx=5)

        # Emotion filter
        filter_frame = ctk.CTkFrame(controls_frame)
        filter_frame.pack(side="right", padx=5)
        
        filter_label = ctk.CTkLabel(filter_frame, text=self.language_manager.get_text("filter_by_emotion"))
        filter_label.pack(side="left", padx=5)
        
        self.emotion_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "Happy", "Sad", "Neutral", "Untagged"],
            command=self._filter_playlist
        )
        self.emotion_filter.pack(side="right", padx=5)

        # Create scrollable frame for playlist
        self.playlist_scrollable = ctk.CTkScrollableFrame(playlist_frame)
        self.playlist_scrollable.pack(fill="both", expand=True, padx=5, pady=5)

        # Initialize empty list to store song buttons
        self.playlist_buttons = []
        
        # Add songs from playlist
        self._refresh_playlist()

    def _filter_playlist(self, emotion):
        # Clear existing buttons
        for button in self.playlist_buttons:
            button.destroy()
        self.playlist_buttons.clear()

        # Add new buttons for each song that matches the filter
        playlist = self.playlist_manager.get_playlist()
        for song in playlist:
            song_emotion = self.emotion_manager.get_emotion(song['path'])
            song_emotion_number = self.emotion_manager.get_emotion_number(song['path'])
            
            # Skip if doesn't match filter
            if emotion != "All":
                if emotion == "Untagged" and song_emotion_number != 0:
                    continue
                elif emotion == "Happy" and song_emotion_number != 2:
                    continue
                elif emotion == "Sad" and song_emotion_number != 3:
                    continue
                elif emotion == "Neutral" and song_emotion_number != 1:
                    continue
            
            # Create frame for song row
            song_frame = ctk.CTkFrame(self.playlist_scrollable)
            song_frame.pack(fill="x", padx=5, pady=2)
            
            # Create button for song
            btn = ctk.CTkButton(
                song_frame,
                text=song['title'],
                command=lambda s=song: self._play_song(s),
                anchor="w",
                height=30
            )
            btn.pack(side="left", fill="x", expand=True)
            
            # Create label for emotion
            emotion_label = ctk.CTkLabel(
                song_frame,
                text=song_emotion if song_emotion != "Untagged" else "",
                width=80
            )
            emotion_label.pack(side="right", padx=5)
            
            self.playlist_buttons.append(song_frame)

    def _refresh_playlist(self):
        # Clear existing buttons
        for button in self.playlist_buttons:
            button.destroy()
        self.playlist_buttons.clear()

        # Add new buttons for each song
        playlist = self.playlist_manager.get_playlist()
        for song in playlist:
            # Create frame for song row
            song_frame = ctk.CTkFrame(self.playlist_scrollable)
            song_frame.pack(fill="x", padx=5, pady=2)
            
            # Create button for song
            btn = ctk.CTkButton(
                song_frame,
                text=song['title'],
                command=lambda s=song: self._play_song(s),
                anchor="w",
                height=30
            )
            btn.pack(side="left", fill="x", expand=True)
            
            # Add emotion label with number
            emotion = self.emotion_manager.get_emotion(song['path'])
            emotion_number = self.emotion_manager.get_emotion_number(song['path'])
            
            # Format display text
            emotion_display = ""
            if emotion != "Untagged":
                emotion_display = f"{emotion} ({emotion_number})"
                
            emotion_label = ctk.CTkLabel(
                song_frame,
                text=emotion_display,
                width=100
            )
            emotion_label.pack(side="right", padx=5)
            
            self.playlist_buttons.append(song_frame)

    def _tag_emotion(self):
        # Create emotion tagging dialog
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.language_manager.get_text("tag_emotion"))
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()  # Make dialog modal

        # Create title label
        title_label = ctk.CTkLabel(
            dialog, 
            text=self.language_manager.get_text("tag_emotion"),
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)

        # Create emotion radio buttons with better styling
        emotion_var = ctk.StringVar(value="Neutral")
        
        emotions_frame = ctk.CTkFrame(dialog)
        emotions_frame.pack(fill="x", padx=20, pady=10)
        
        emotions_label = ctk.CTkLabel(
            emotions_frame, 
            text=self.language_manager.get_text("select_emotion"),
            font=("Arial", 12)
        )
        emotions_label.pack(pady=5)
        
        # Emotion mapping with numbers
        emotion_mapping = [
            ("Happy", 2),
            ("Sad", 3),
            ("Neutral", 1)
        ]
        
        for emotion, number in emotion_mapping:
            rb_frame = ctk.CTkFrame(emotions_frame)
            rb_frame.pack(fill="x", pady=2)
            
            rb = ctk.CTkRadioButton(
                rb_frame,
                text=f"{self.language_manager.get_text(emotion.lower())} ({number})",
                variable=emotion_var,
                value=emotion,
                font=("Arial", 12)
            )
            rb.pack(side="left", padx=10)
        
        # Create a frame for the song list with a title
        songs_label = ctk.CTkLabel(
            dialog, 
            text=self.language_manager.get_text("select_songs"),
            font=("Arial", 12)
        )
        songs_label.pack(pady=5)
        
        songs_frame = ctk.CTkScrollableFrame(dialog)
        songs_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add select all checkbox
        select_all_var = ctk.BooleanVar()
        select_all_cb = ctk.CTkCheckBox(
            songs_frame,
            text=self.language_manager.get_text("select_all"),
            variable=select_all_var,
            font=("Arial", 12)
        )
        select_all_cb.pack(pady=5, anchor="w")
        
        # Add checkboxes for each song
        song_vars = {}
        song_checkboxes = []
        for song in self.playlist_manager.get_playlist():
            var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(
                songs_frame,
                text=song['title'],
                variable=var,
                font=("Arial", 11)
            )
            checkbox.pack(pady=2, anchor="w")
            song_vars[song['path']] = var
            song_checkboxes.append(checkbox)
            
        # Select all functionality
        def toggle_select_all():
            for checkbox in song_checkboxes:
                checkbox.select() if select_all_var.get() else checkbox.deselect()
                
        select_all_cb.configure(command=toggle_select_all)
            
        def apply_emotions():
            emotion = emotion_var.get()
            for song_path, var in song_vars.items():
                if var.get():
                    self.emotion_manager.set_emotion(song_path, emotion)
            dialog.destroy()
            self._refresh_playlist()
            
        # Create a styled confirm button
        confirm_button = ctk.CTkButton(
            dialog,
            text=self.language_manager.get_text("confirm"),
            command=apply_emotions,
            font=("Arial", 12, "bold"),
            height=35
        )
        confirm_button.pack(pady=15, padx=20, fill="x")

    def _play_song(self, song):
        success = self.player.play(song['path'], song['title'])
        if success:
            # Update UI
            self.current_song_label.configure(text=song['title'])
            self.play_button.configure(text="⏸")
            # Add to history
            self.history_manager.add_to_history(song['path'], song['title'])
            self._refresh_history()
            return True
        return False

    def _play_next(self):
        playlist = self.playlist_manager.get_playlist()
        current_song = self.player.current_song
        
        # Find current song index
        current_index = -1
        for i, song in enumerate(playlist):
            if song['path'] == current_song:
                current_index = i
                break
        
        # Play next song if available
        if current_index >= 0 and current_index + 1 < len(playlist):
            next_song = playlist[current_index + 1]
            self._play_song(next_song)

    def _play_previous(self):
        playlist = self.playlist_manager.get_playlist()
        current_song = self.player.current_song
        
        # Find current song index
        current_index = -1
        for i, song in enumerate(playlist):
            if song['path'] == current_song:
                current_index = i
                break
        
        # Play previous song if available
        if current_index > 0:
            prev_song = playlist[current_index - 1]
            self._play_song(prev_song)

    def _play_pause(self):
        if self.player.current_song is None:
            # If no song is playing, play the first song in playlist
            playlist = self.playlist_manager.get_playlist()
            if playlist:
                self._play_song(playlist[0])
        elif self.player.playing:
            self.player.pause()
            self.play_button.configure(text="▶")
        else:
            self.player.resume()
            self.play_button.configure(text="⏸")
            if self.player.current_song_title:
                self.current_song_label.configure(text=self.player.current_song_title)

    def _update_volume(self, value):
        self.player.set_volume(value)
        self.settings_manager.set_volume(value)

    def _setup_history_tab(self):
        history_frame = ctk.CTkFrame(self.tab_history)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Add clear history button
        clear_button = ctk.CTkButton(
            history_frame,
            text=self.language_manager.get_text("clear_history"),
            command=self._clear_history
        )
        clear_button.pack(pady=5)

        # Create scrollable frame for history
        self.history_scrollable = ctk.CTkScrollableFrame(history_frame)
        self.history_scrollable.pack(fill="both", expand=True, padx=5, pady=5)

        # Initialize empty list to store history buttons
        self.history_buttons = []
        
        # Add history entries
        self._refresh_history()

    def _refresh_history(self):
        # Clear existing entries
        for widget in self.history_scrollable.winfo_children():
            widget.destroy()
        self.history_buttons = []
            
        # Add new entries for each history item
        history_entries = self.history_manager.get_history()
        for entry in reversed(history_entries):  # Show newest first
            song_name = entry.get('title', os.path.basename(entry['path']))
            date_str = entry.get('date', '')
            time_str = entry.get('time', '')
            play_count = entry.get('play_count', 1)
            
            # Create frame for history entry
            entry_frame = ctk.CTkFrame(self.history_scrollable)
            entry_frame.pack(fill="x", padx=5, pady=2)
            
            # Create play button
            btn = ctk.CTkButton(
                entry_frame,
                text=song_name,
                command=lambda s=entry: self._play_song({
                    'path': s['path'],
                    'title': s.get('title', os.path.basename(s['path']))
                }),
                anchor="w",
                height=30
            )
            btn.pack(side="left", fill="x", expand=True)
            
            # Create info label
            info_text = f"{date_str} {time_str}"
            if play_count > 1:
                info_text += f" (Played {play_count}x)"
            
            info_label = ctk.CTkLabel(
                entry_frame,
                text=info_text,
                width=150
            )
            info_label.pack(side="right", padx=5)
            
            self.history_buttons.append(entry_frame)

    def _clear_history(self):
        self.history_manager.clear_history()
        self._refresh_history()

    def _setup_settings_button(self):
        settings_button = ctk.CTkButton(
            self.main_frame,
            text="⚙",
            width=40,
            command=self._show_settings_window
        )
        settings_button.place(relx=0.95, rely=0.95, anchor="se")

    def _show_settings_window(self):
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title(self.language_manager.get_text("settings"))
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        
        # Language selection
        language_frame = ctk.CTkFrame(settings_window)
        language_frame.pack(fill="x", padx=20, pady=10)
        
        language_label = ctk.CTkLabel(language_frame, text=self.language_manager.get_text("language"))
        language_label.pack(side="left", padx=5)
        
        current_language = "english" if self.language_manager.current_language == "en_US" else "indonesian"
        language_var = ctk.StringVar(value=self.language_manager.get_text(current_language))
        
        language_menu = ctk.CTkOptionMenu(
            language_frame,
            values=[self.language_manager.get_text("english"), 
                   self.language_manager.get_text("indonesian")],
            variable=language_var,
            command=self._change_language
        )
        language_menu.pack(side="right", padx=5)
        
        # Music folder selection
        folder_frame = ctk.CTkFrame(settings_window)
        folder_frame.pack(fill="x", padx=20, pady=10)
        
        folder_label = ctk.CTkLabel(folder_frame, text=self.language_manager.get_text("music_folder"))
        folder_label.pack(side="left", padx=5)
        
        current_folder = self.settings_manager.get_music_folder()
        folder_path_label = ctk.CTkLabel(folder_frame, 
                                       text=current_folder if current_folder else self.language_manager.get_text("no_folder_selected"))
        folder_path_label.pack(pady=5)
        
        change_folder_button = ctk.CTkButton(
            folder_frame,
            text=self.language_manager.get_text("change_folder"),
            command=lambda: self._select_music_folder(folder_path_label)
        )
        change_folder_button.pack(side="right", padx=5)

    def _change_language(self, selection):
        language_code = "en_US" if selection == self.language_manager.get_text("english") else "id_ID"
        self.language_manager.set_language(language_code)
        self.settings_manager.set_language(language_code)
        
        # Rebuild UI with new language
        self._rebuild_ui()

    def _rebuild_ui(self):
        # Store current geometry
        current_geometry = self.root.geometry()
        
        # Clear all widgets
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Rebuild UI
        self._setup_ui()
        
        # Restore geometry
        self.root.geometry(current_geometry)
        
        # Refresh playlist if exists
        if self.playlist_manager.get_current_folder():
            self._refresh_playlist()

    def _select_music_folder(self, label_widget=None):
        folder = filedialog.askdirectory()
        if folder:
            self.settings_manager.set_music_folder(folder)
            if label_widget:
                label_widget.configure(text=folder)
            if self.playlist_manager.load_folder(folder):
                self._refresh_playlist()

    def _load_saved_settings(self):
        # Load saved music folder
        folder = self.settings_manager.get_music_folder()
        if folder and os.path.exists(folder):
            self.playlist_manager.load_folder(folder)
            self._refresh_playlist()
        
        # Load saved volume
        volume = self.settings_manager.get_volume()
        self.volume_slider.set(volume)
        self.player.set_volume(volume)

    def _open_camera(self):
        """Open camera window for emotion detection"""
        try:
            # Ensure any existing camera manager is cleaned up
            if self.camera_manager is not None:
                try:
                    self.camera_manager.destroy()
                except:
                    pass
                self.camera_manager = None
            
            # Initialize camera manager with root window and UI instance
            self.camera_manager = CameraManager(
                root_window=self.root,
                parent_ui=self,
                playlist_manager=self.playlist_manager,
                language_manager=self.language_manager
            )
            
            # Ensure the camera window is on top
            self.camera_manager.lift()
            self.camera_manager.focus_force()
            
        except Exception as e:
            print(f"Error opening camera: {str(e)}")
            messagebox.showerror("Error", str(e))
            if self.camera_manager is not None:
                try:
                    self.camera_manager.destroy()
                except:
                    pass
                self.camera_manager = None

    def process_captured_image(self, image_path):
        """Process the captured image from camera"""
        try:
            if not os.path.exists(image_path):
                raise Exception("Captured image not found")
                
            # Process the image using emotion manager
            self.emotion_manager.process_image(
                image_path,
                self.root,
                self.playlist_manager,
                self.language_manager
            )
        except Exception as e:
            print(f"Error processing captured image: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            # Clean up temp image
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"Deleted temp image: {image_path}")
            except Exception as e:
                print(f"Error cleaning up temp image: {e}")
            
            # Clean up camera manager
            if self.camera_manager is not None:
                try:
                    self.camera_manager.destroy()
                except:
                    pass
                self.camera_manager = None
