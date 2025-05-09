import json
import os
import cv2
import numpy as np
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
            # Get the song title for display
            song_title = song.get('title', os.path.basename(song['path']))
            song_path = song['path']
            
            # Get the parent window (main application)
            parent = self.master
            player_found = False
            
            # Try multiple approaches to find and use the player
            # Approach 1: Direct player access
            if hasattr(parent, 'player'):
                # Use the player directly
                parent.player.play(song_path, song_title)
                # Update UI if needed
                if hasattr(parent, 'ui') and hasattr(parent.ui, 'current_song_label'):
                    parent.ui.current_song_label.configure(text=song_title)
                if hasattr(parent, 'ui') and hasattr(parent.ui, 'play_button'):
                    parent.ui.play_button.configure(text="⏸")
                # Ensure the player's current_song_title is updated
                parent.player.current_song_title = song_title
                print(f"Playing song via direct player access: {song_title}")
                player_found = True
            
            # Approach 2: Access through UI
            elif hasattr(parent, 'ui') and hasattr(parent.ui, 'player'):
                # Access through UI
                parent.ui.player.play(song_path, song_title)
                # Update UI
                if hasattr(parent.ui, 'current_song_label'):
                    parent.ui.current_song_label.configure(text=song_title)
                if hasattr(parent.ui, 'play_button'):
                    parent.ui.play_button.configure(text="⏸")
                # Ensure the player's current_song_title is updated
                parent.ui.player.current_song_title = song_title
                print(f"Playing song via UI player access: {song_title}")
                player_found = True
            
            # Approach 3: Find player in parent's attributes
            else:
                # Try to find player in any attribute of parent
                for attr_name in dir(parent):
                    if attr_name.startswith('__'):
                        continue
                    try:
                        attr = getattr(parent, attr_name)
                        # Check if this attribute has a player
                        if hasattr(attr, 'player') and hasattr(attr.player, 'play'):
                            attr.player.play(song_path, song_title)
                            # Ensure the player's current_song_title is updated
                            attr.player.current_song_title = song_title
                            # Update UI if possible
                            if hasattr(attr, 'current_song_label'):
                                attr.current_song_label.configure(text=song_title)
                            print(f"Playing song via {attr_name}.player: {song_title}")
                            player_found = True
                            break
                    except:
                        pass
            
            if not player_found:
                print(f"Could not find player instance to play: {song_title}")
                # As a last resort, try to create a temporary player
                try:
                    from player import MusicPlayer
                    temp_player = MusicPlayer(self.playlist_manager, None)
                    temp_player.play(song_path, song_title)
                    temp_player.current_song_title = song_title
                    print(f"Playing song via temporary player: {song_title}")
                except Exception as temp_err:
                    print(f"Failed to create temporary player: {temp_err}")
            
            # Close the recommendation window
            self.destroy()
        except Exception as e:
            print(f"Error playing song: {e}")
            messagebox.showerror("Error", str(e))

class EmotionManager:
    # Emotion class numbers
    UNTAGGED = 0
    NEUTRAL = 1
    HAPPY = 2
    SAD = 3

    def __init__(self):
        print("Initializing EmotionManager...")
        # Get data directory using path_utils
        from path_utils import get_data_directory
        data_dir = get_data_directory()
        self.emotions_file = os.path.join(data_dir, "emotions.json")
        
        # Create Data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        self.emotions = {}
        self.available_emotions = ["Neutral", "Happy", "Sad"]
        self.load_emotions()
        
        # Define the emotion data directory
        emotion_data_dir = os.path.join(data_dir, "Emotion_Data")
        
        # Create Emotion_Data directory if it doesn't exist
        os.makedirs(emotion_data_dir, exist_ok=True)
        
        # Initialize OpenCV face cascade from local files
        face_cascade_path = os.path.join(emotion_data_dir, 'haarcascade_frontalface_default.xml')
        eye_cascade_path = os.path.join(emotion_data_dir, 'haarcascade_eye.xml')
        smile_cascade_path = os.path.join(emotion_data_dir, 'haarcascade_smile.xml')
        
        # Check if files exist, if not, use OpenCV's built-in cascades as fallback
        if not os.path.exists(face_cascade_path):
            print(f"Warning: {face_cascade_path} not found, using OpenCV's built-in cascade")
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            
        if not os.path.exists(eye_cascade_path):
            print(f"Warning: {eye_cascade_path} not found, using OpenCV's built-in cascade")
            eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
            
        if not os.path.exists(smile_cascade_path):
            print(f"Warning: {smile_cascade_path} not found, using OpenCV's built-in cascade")
            smile_cascade_path = cv2.data.haarcascades + 'haarcascade_smile.xml'
        
        # Load the cascade classifiers
        print(f"Loading face cascade from: {face_cascade_path}")
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        
        print(f"Loading eye cascade from: {eye_cascade_path}")
        self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
        
        print(f"Loading smile cascade from: {smile_cascade_path}")
        self.smile_cascade = cv2.CascadeClassifier(smile_cascade_path)
        
        # Verify cascades loaded correctly
        if self.face_cascade.empty():
            print("Error: Face cascade failed to load")
            # Fall back to OpenCV's built-in cascade
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
        if self.eye_cascade.empty():
            print("Error: Eye cascade failed to load")
            # Fall back to OpenCV's built-in cascade
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            
        if self.smile_cascade.empty():
            print("Error: Smile cascade failed to load")
            # Fall back to OpenCV's built-in cascade
            self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        
        print("EmotionManager initialized")

    def load_emotions(self):
        if os.path.exists(self.emotions_file):
            try:
                with open(self.emotions_file, 'r') as f:
                    self.emotions = json.load(f)
            except Exception as e:
                print(f"Error loading emotions: {e}")
                self.emotions = {}

    def save_emotions(self):
        try:
            with open(self.emotions_file, 'w') as f:
                json.dump(self.emotions, f, indent=4)
        except Exception as e:
            print(f"Error saving emotions: {e}")

    def set_emotion(self, song_path, emotion):
        if emotion in self.available_emotions:
            # Convert emotion name to number
            emotion_number = self.NEUTRAL
            if emotion == "Happy":
                emotion_number = self.HAPPY
            elif emotion == "Sad":
                emotion_number = self.SAD
            elif emotion == "Neutral":
                emotion_number = self.NEUTRAL
                
            # Store both emotion name and number
            if not song_path in self.emotions:
                self.emotions[song_path] = {}
            self.emotions[song_path] = {
                "name": emotion,
                "number": emotion_number
            }
            self.save_emotions()

    def get_emotion(self, song_path):
        if song_path in self.emotions:
            return self.emotions[song_path]["name"]
        return "Untagged"
        
    def get_emotion_number(self, song_path):
        """Get the numeric emotion value for a song"""
        if song_path in self.emotions:
            return self.emotions[song_path]["number"]
        return self.UNTAGGED

    def get_songs_by_emotion(self, emotion):
        """Get songs by emotion name"""
        return [song for song, data in self.emotions.items() if data["name"] == emotion]
        
    def get_songs_by_emotion_number(self, emotion_number):
        """Get songs by emotion number"""
        return [song for song, data in self.emotions.items() if data["number"] == emotion_number]

    def clear_emotions(self):
        self.emotions = {}
        self.save_emotions()

    @staticmethod
    def get_emotion_name(emotion_class):
        """Convert emotion class number to name"""
        emotion_names = {
            EmotionManager.UNTAGGED: 'untagged',
            EmotionManager.NEUTRAL: 'neutral',
            EmotionManager.HAPPY: 'happy',
            EmotionManager.SAD: 'sad'
        }
        return emotion_names.get(emotion_class, 'unknown')

    def process_image(self, image_path, root, playlist_manager, language_manager):
        """Process image and show recommendations"""
        try:
            # Load and process image
            image = cv2.imread(image_path)
            if image is None:
                raise Exception("Failed to load image")
                
            # Detect emotion from image
            emotion_number = self.detect_emotion(image)
            
            # Get emotion name
            emotion_name = self._get_emotion_name(emotion_number)
            print(f"Detected emotion: {emotion_name} (tag: {emotion_number})")
            
            # Show recommendation window with detected emotion
            self._show_recommendations(root, emotion_number, playlist_manager, language_manager)
            
        except Exception as e:
            print(f"Error processing image: {e}")
            messagebox.showerror("Error", str(e))
    
    def process_frame(self, frame, root, playlist_manager, language_manager):
        """Process frame directly and show recommendations"""
        try:
            if frame is None:
                raise Exception("Invalid frame")
                
            # Detect emotion from frame
            emotion_number = self.detect_emotion(frame)
            
            # Get emotion name
            emotion_name = self._get_emotion_name(emotion_number)
            print(f"Detected emotion: {emotion_name} (tag: {emotion_number})")
            
            # Show recommendation window with detected emotion
            self._show_recommendations(root, emotion_number, playlist_manager, language_manager)
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            messagebox.showerror("Error", str(e))
            
    def _get_emotion_name(self, emotion_number):
        """Convert emotion number to name"""
        emotions = {
            0: "Untagged",
            1: "Neutral",
            2: "Happy",
            3: "Sad"
        }
        return emotions.get(emotion_number, "Unknown")
        
    def _show_recommendations(self, root, emotion_number, playlist_manager, language_manager):
        """Show recommendation window with appropriate songs"""
        try:
            # Get songs based on emotion number
            recommended_songs = []
            all_songs = playlist_manager.get_playlist()
            
            for song in all_songs:
                # Use self.get_emotion_number instead of playlist_manager.get_song_emotion
                song_emotion = self.get_emotion_number(song['path'])
                
                # Filter songs based on emotion number
                if emotion_number == 0:  # Untagged - show all songs
                    recommended_songs.append(song)
                elif emotion_number == 1:  # Neutral - show neutral and happy songs
                    if song_emotion in [1, 2]:
                        recommended_songs.append(song)
                elif emotion_number == 2:  # Happy - show only happy songs
                    if song_emotion == 2:
                        recommended_songs.append(song)
                elif emotion_number == 3:  # Sad - show happy songs
                    if song_emotion == 2:
                        recommended_songs.append(song)
            
            # Limit to maximum 10 songs
            if len(recommended_songs) > 10:
                recommended_songs = recommended_songs[:10]
                
            # Show recommendation window using the internal class
            RecommendationWindow(
                root,
                recommended_songs,
                playlist_manager,
                language_manager,
                emotion_number
            )
            
        except Exception as e:
            print(f"Error showing recommendations: {e}")
            messagebox.showerror("Error", str(e))

    def detect_emotion(self, image):
        """Detect emotion from image and return emotion class number"""
        try:
            print("Starting emotion detection")
            
            if image is None:
                print("Input image is None")
                return self.UNTAGGED
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply preprocessing to improve detection in various lighting conditions
            # 1. Apply histogram equalization to improve contrast
            gray = cv2.equalizeHist(gray)
            
            # 2. Apply Gaussian blur to reduce noise
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # 3. Apply adaptive thresholding for better feature detection in low light
            # Create a copy for thresholding
            thresh = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            # 4. Combine original and thresholded image for better detection
            enhanced = cv2.addWeighted(gray, 0.7, thresh, 0.3, 0)
            
            # Try multiple detection approaches
            faces = []
            
            # First attempt with standard parameters
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,
                minNeighbors=4,
                minSize=(20, 20)
            )
            
            # If no faces found, try with enhanced image
            if len(faces) == 0:
                print("Trying enhanced image detection")
                faces = self.face_cascade.detectMultiScale(
                    enhanced,
                    scaleFactor=1.03,
                    minNeighbors=3,
                    minSize=(20, 20)
                )
            
            # If still no faces, try with more aggressive parameters
            if len(faces) == 0:
                print("Trying more aggressive detection parameters")
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.01,
                    minNeighbors=2,
                    minSize=(15, 15)
                )
            
            if len(faces) == 0:
                print("No faces detected after multiple attempts")
                return self.UNTAGGED
            
            # Process the first face found
            x, y, w, h = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            
            # Apply contrast enhancement to face region
            face_roi = cv2.equalizeHist(face_roi)
            
            # Detect eyes with multiple parameter sets
            eyes = []
            eyes = self.eye_cascade.detectMultiScale(
                face_roi,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(10, 10)
            )
            
            if len(eyes) < 2:
                # Try again with different parameters
                eyes = self.eye_cascade.detectMultiScale(
                    face_roi,
                    scaleFactor=1.05,
                    minNeighbors=3,
                    minSize=(8, 8)
                )
            
            # Detect smile with multiple parameter sets
            smile = []
            smile = self.smile_cascade.detectMultiScale(
                face_roi,
                scaleFactor=1.5,
                minNeighbors=15,
                minSize=(20, 20)
            )
            
            if len(smile) == 0:
                # Try again with different parameters
                smile = self.smile_cascade.detectMultiScale(
                    face_roi,
                    scaleFactor=1.3,
                    minNeighbors=10,
                    minSize=(15, 15)
                )
            
            print(f"Detection results: {len(faces)} faces, {len(eyes)} eyes, {len(smile)} smiles")
            
            # Determine emotion based on facial features with improved logic
            if len(smile) > 0:
                # Smile detected - likely happy
                print("Smile detected - classifying as HAPPY")
                return self.HAPPY
            elif len(eyes) >= 2:
                # Eyes detected but no smile - likely neutral
                print("Two eyes detected, no smile - classifying as NEUTRAL")
                return self.NEUTRAL
            elif len(eyes) > 0:
                # At least one eye detected - still neutral
                print("At least one eye detected - classifying as NEUTRAL")
                return self.NEUTRAL
            else:
                # Eyes not clearly detected - might be sad or eyes closed
                print("No eyes clearly detected - classifying as SAD")
                return self.SAD
            
        except Exception as e:
            print(f"Emotion detection error: {e}")
            return self.UNTAGGED
