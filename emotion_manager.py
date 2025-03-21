import json
import os
import cv2
import mediapipe as mp
import numpy as np
from recommendation_window import RecommendationWindow
from tkinter import messagebox

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
        
        # Initialize MediaPipe face mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize OpenCV face cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Define facial feature indices
        self.mouth_landmarks = [61, 291, 0, 17, 269, 39, 270, 409, 287, 375, 321, 405, 314, 17, 84, 181, 91, 146]
        self.left_eye = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.right_eye = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        
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
                
            # Convert to RGB for face detection
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect face and get emotion
            results = self.face_mesh.process(rgb_image)
            
            if not results.multi_face_landmarks:
                raise Exception("No face detected")
                
            # Analyze facial landmarks for emotion
            emotion_number = self._analyze_emotion(results.multi_face_landmarks[0])
            
            # Get emotion name
            emotion_name = self._get_emotion_name(emotion_number)
            print(f"Detected emotion: {emotion_name} (tag: {emotion_number})")
            
            # Show recommendation window with detected emotion
            self._show_recommendations(root, emotion_number, playlist_manager, language_manager)
            
        except Exception as e:
            print(f"Error processing image: {e}")
            messagebox.showerror("Error", str(e))
            
    def _analyze_emotion(self, face_landmarks):
        """Analyze facial landmarks to determine emotion"""
        # Your existing emotion analysis logic here
        # For now, returning a sample emotion (you should implement your actual emotion detection logic)
        return 1  # Default to neutral
        
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
                elif emotion_number == 1:  # Neutral - show untagged and neutral
                    if song_emotion in [0, 1]:
                        recommended_songs.append(song)
                elif emotion_number == 2:  # Happy - show only happy
                    if song_emotion == 2:
                        recommended_songs.append(song)
                elif emotion_number == 3:  # Sad - show neutral and happy
                    if song_emotion in [1, 2]:
                        recommended_songs.append(song)
            
            # Show recommendation window
            from recommendation_window import RecommendationWindow
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
            
            # Convert to RGB for MediaPipe
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = self.face_mesh.process(rgb_image)
            
            if not results.multi_face_landmarks:
                print("No face landmarks detected")
                return self.UNTAGGED
            
            # Get facial measurements
            landmarks = results.multi_face_landmarks[0]
            measurements = self.get_facial_measurements(image, landmarks)
            
            # Determine emotion based on measurements
            emotion_class = self.classify_emotion(measurements)
            print(f"Detected emotion: {self.get_emotion_name(emotion_class)}")
            
            return emotion_class
            
        except Exception as e:
            print(f"Emotion detection error: {e}")
            return self.UNTAGGED

    def get_facial_measurements(self, image, landmarks):
        """Get facial measurements"""
        try:
            h, w = image.shape[:2]
            
            def get_point(idx):
                pt = landmarks.landmark[idx]
                return np.array([int(pt.x * w), int(pt.y * h)])
            
            # Mouth measurements
            mouth_points = [get_point(idx) for idx in self.mouth_landmarks[:8]]
            mouth_height = np.linalg.norm(mouth_points[0] - mouth_points[2])
            mouth_width = np.linalg.norm(mouth_points[4] - mouth_points[6])
            mouth_ratio = mouth_height / (mouth_width + 1e-6)
            
            # Eye measurements
            left_eye_points = [get_point(idx) for idx in self.left_eye[:8]]
            right_eye_points = [get_point(idx) for idx in self.right_eye[:8]]
            
            left_eye_height = np.linalg.norm(left_eye_points[1] - left_eye_points[5])
            left_eye_width = np.linalg.norm(left_eye_points[0] - left_eye_points[4])
            
            right_eye_height = np.linalg.norm(right_eye_points[1] - right_eye_points[5])
            right_eye_width = np.linalg.norm(right_eye_points[0] - right_eye_points[4])
            
            left_eye_ratio = left_eye_height / (left_eye_width + 1e-6)
            right_eye_ratio = right_eye_height / (right_eye_width + 1e-6)
            
            return {
                'mouth_ratio': mouth_ratio,
                'left_eye_ratio': left_eye_ratio,
                'right_eye_ratio': right_eye_ratio
            }
            
        except Exception as e:
            print(f"Error getting facial measurements: {e}")
            return None

    def classify_emotion(self, measurements):
        """Classify emotion based on facial measurements"""
        if measurements is None:
            return self.UNTAGGED
            
        try:
            mouth_ratio = measurements['mouth_ratio']
            left_eye_ratio = measurements['left_eye_ratio']
            right_eye_ratio = measurements['right_eye_ratio']
            
            # Simple rule-based classification
            if mouth_ratio > 0.5:  # Mouth open vertically - likely happy
                return self.HAPPY
            elif left_eye_ratio < 0.2 and right_eye_ratio < 0.2:  # Eyes nearly closed - likely sad
                return self.SAD
            else:  # Default to neutral
                return self.NEUTRAL
                
        except Exception as e:
            print(f"Error classifying emotion: {e}")
            return self.UNTAGGED
