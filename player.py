import pygame
from mutagen.mp3 import MP3
import time
import threading

class MusicPlayer:
    def __init__(self, playlist_manager, history_manager):
        pygame.mixer.init()
        self.playlist_manager = playlist_manager
        self.history_manager = history_manager
        self.current_song = None
        self.current_song_title = None
        self.paused = False
        self.volume = 0.5
        pygame.mixer.music.set_volume(self.volume)
        self.playing = False
        self._position = 0
        
    def play(self, song_path=None, song_title=None):
        if song_path:
            try:
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                self.current_song = song_path
                self.current_song_title = song_title
                self.playing = True
                self.paused = False
                if song_title:
                    self.history_manager.add_to_history(song_path, song_title)
                return True
            except pygame.error:
                print(f"Error playing {song_path}")
                return False
        elif self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.playing = True
            return True
        return False

    def pause(self):
        if self.playing and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            self.playing = False

    def resume(self):
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False
        self.current_song = None
        self.current_song_title = None

    def set_volume(self, volume):
        self.volume = float(volume)
        pygame.mixer.music.set_volume(self.volume)

    def get_current_time(self):
        if self.playing:
            return pygame.mixer.music.get_pos() / 1000
        return 0

    def get_song_length(self):
        if self.current_song:
            audio = MP3(self.current_song)
            return audio.info.length
        return 0

    def seek(self, position):
        if self.current_song:
            pygame.mixer.music.play(start=position)
            self.playing = True
            self.paused = False
