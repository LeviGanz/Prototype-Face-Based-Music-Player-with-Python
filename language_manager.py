import json
import os

class LanguageManager:
    def __init__(self):
        # Get directories using path_utils
        from path_utils import get_data_directory, get_languages_directory
        data_dir = get_data_directory()
        languages_dir = get_languages_directory()
        self.language_file = os.path.join(data_dir, "language.json")
        
        # Create directories if they don't exist
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(languages_dir, exist_ok=True)
        
        self.current_language = "en_US"
        self.available_languages = ["en_US", "id_ID"]
        self.translations = {
            "en_US": {
                "settings": "Settings",
                "language": "Language",
                "music_folder": "Music Folder",
                "change_folder": "Change Folder",
                "tag_emotions": "Tag Emotions",
                "filter_by_emotion": "Filter by emotion",
                "all": "All",
                "happy": "Happy",
                "sad": "Sad",
                "neutral": "Neutral",
                "untagged": "Untagged",
                "volume": "Volume",
                "now_playing": "Now Playing",
                "playlist": "Playlist",
                "history": "History",
                "settings_saved": "Settings saved",
                "english": "English (US)",
                "indonesian": "Indonesian",
                "player": "Player",
                "tag_emotion": "Tag Emotion",
                "confirm": "Confirm",
                "clear_history": "Clear History",
                "no_folder_selected": "No folder selected",
                "select_emotion": "Select an emotion:",
                "select_songs": "Select songs to tag:",
                "select_all": "Select All",
                "no_song_playing": "No song playing",
                "detect_emotion": "Detect Emotion",
                "emotion_detection": "Emotion Detection",
                "preparing_camera": "Preparing camera...",
                "capturing_in": "Capturing in...",
                "recommendations": "Recommended Songs",
                "recommended_songs": "Recommended Songs For You",
                "camera_error": "Camera error occurred",
                "no_face_detected": "No face detected",
                "close": "Close",
                "play_song": "Play Song",
                "untagged_emotion_message": "I'll show you some random songs to try!",
                "neutral_emotion_message": "You seem calm. Here are some balanced songs.",
                "happy_emotion_message": "Great to see you happy! Here are some upbeat songs!",
                "sad_emotion_message": "Here are some cheerful songs to lift your mood!",
                "start_capture": "Start Capture",
                "processing_image": "Processing image...",
                "detecting_emotion": "Detecting emotion...",
                "getting_recommendations": "Getting song recommendations..."
            },
            "id_ID": {
                "settings": "Pengaturan",
                "language": "Bahasa",
                "music_folder": "Folder Musik",
                "change_folder": "Ubah Folder",
                "tag_emotions": "Tag Emosi",
                "filter_by_emotion": "Filter berdasarkan emosi",
                "all": "Semua",
                "happy": "Senang",
                "sad": "Sedih",
                "neutral": "Netral",
                "untagged": "Belum Ditandai",
                "volume": "Volume",
                "now_playing": "Sedang Diputar",
                "playlist": "Daftar Putar",
                "history": "Riwayat",
                "settings_saved": "Pengaturan tersimpan",
                "english": "Bahasa Inggris (AS)",
                "indonesian": "Bahasa Indonesia",
                "player": "Pemutar",
                "tag_emotion": "Tag Emosi",
                "confirm": "Konfirmasi",
                "clear_history": "Hapus Riwayat",
                "no_folder_selected": "Belum ada folder dipilih",
                "select_emotion": "Pilih emosi:",
                "select_songs": "Pilih lagu untuk ditag:",
                "select_all": "Pilih Semua",
                "no_song_playing": "Tidak ada lagu diputar",
                "detect_emotion": "Deteksi Emosi",
                "emotion_detection": "Deteksi Emosi",
                "preparing_camera": "Menyiapkan kamera...",
                "capturing_in": "Mengambil gambar dalam...",
                "recommendations": "Rekomendasi Lagu",
                "recommended_songs": "Rekomendasi Lagu Untuk Anda",
                "camera_error": "Terjadi kesalahan kamera",
                "no_face_detected": "Wajah tidak terdeteksi",
                "close": "Tutup",
                "play_song": "Putar Lagu",
                "untagged_emotion_message": "Mari coba beberapa lagu acak!",
                "neutral_emotion_message": "Anda terlihat tenang. Ini beberapa lagu yang seimbang.",
                "happy_emotion_message": "Senang melihat Anda bahagia! Ini beberapa lagu yang ceria!",
                "sad_emotion_message": "Ini beberapa lagu ceria untuk memperbaiki suasana hati!",
                "start_capture": "Mulai Ambil Gambar",
                "processing_image": "Memproses gambar...",
                "detecting_emotion": "Mendeteksi emosi...",
                "getting_recommendations": "Mendapatkan rekomendasi lagu..."
            }
        }
        self.load_language()

    def load_language(self):
        if os.path.exists(self.language_file):
            try:
                with open(self.language_file, 'r') as f:
                    saved_language = json.load(f)
                    if saved_language in self.available_languages:
                        self.current_language = saved_language
            except Exception as e:
                print(f"Error loading language: {e}")

    def save_language(self):
        try:
            with open(self.language_file, 'w') as f:
                json.dump(self.current_language, f)
        except Exception as e:
            print(f"Error saving language: {e}")

    def set_language(self, language):
        if language in self.available_languages:
            self.current_language = language
            self.save_language()

    def get_text(self, key):
        return self.translations[self.current_language].get(key, key)
