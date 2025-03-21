# KaisarsPlayer - Face-Based Music Player

A modern music player that uses facial emotion recognition to recommend songs based on your mood.

## Features

- 🎵 Play, pause, and navigate through your music library
- 📊 Track your listening history with play counts and timestamps
- 🌐 Support for both English and Indonesian languages
- 🎨 Modern and intuitive user interface using CustomTkinter
- 😊 Face-based emotion detection for music recommendations
- 🏷️ Tag songs with emotions for better recommendations
- 📱 Responsive design that adapts to your window size
- 🔍 Filter and search songs by emotion tags

## Emotion Detection

The player uses MediaPipe Face Mesh technology to detect your facial expressions and recommend music based on your current mood:

- 😊 **Happy**: Suggests similar upbeat songs or new untagged tracks
- 😢 **Sad**: Recommends happy and uplifting music to improve your mood
- 😐 **Neutral**: Offers a mix of songs matching your current state

## Emotion Tagging System

The player allows you to manually tag songs with emotions to improve recommendations:

- **0 - Untagged**: Songs that haven't been assigned an emotion yet
- **1 - Happy**: Upbeat, energetic, and positive songs
- **2 - Sad**: Melancholic, slow, or emotional songs
- **3 - Neutral**: Songs with balanced emotional content

Tagged songs are stored in an emotions.json file and used to enhance the recommendation system.

## Project Structure

### Core Files for App building Purpose
- `main.py` - The entry point of the application that initializes all components
- `ui.py` - Contains the main user interface implementation using CustomTkinter
- `player.py` - Handles music playback functionality using Pygame
- `playlist.py` - Manages playlists and song organization
- `history.py` - Tracks and manages playback history
- `path_utils.py` - Provides utility functions for handling file paths
- `settings.py` - Handles application settings and preferences
- `language_manager.py` - Manages multilingual support
- `emotion_manager.py` - Handles emotion detection and analysis
- `camera_manager.py` - Manages camera operations and image capture
- `recommendation_window.py` - Handles song recommendations based on emotions

### Build and Configuration Files
- `app_builders.py` - Script to build the executable using PyInstaller
- `KaisarPlayer.spec` - PyInstaller specification file for building the executable
- `requirements.txt` - Lists all Python package dependencies

### KaisarPlayers Data Files
- `settings.json` - Contains application settings and preferences
- `languages.json` - Contains language translation files
- `emotions.json` - Contains emotion tag data for songs
- `Temp_Image` - Contains temporary images captured during emotion detection
- `Languages` - Contains language translation files
- `en.json` - English translation file, inside Languages folder
- `id.json` - Indonesian translation file, inside Languages folder

### Resource Directories for App building Purpose
- `icons/` - Contains application icons and visual assets
- `languages/` - Contains language translation files
- `build/` - Contains build artifacts (created during build process)
- `dist/` - Contains the final executable (created during build process)
- `__pycache__/` - Python cache directory (automatically generated)

## How to Use

1. **Basic Controls**:
   - Use Play/Pause (▶️/⏸️) to control playback
   - Navigate songs with Previous (⏮️) and Next (⏭️) buttons
   - Adjust volume using the slider

2. **Emotion-Based Recommendations**:
   - Click the camera button (📷) in the main player
   - Look at the camera naturally for 5 seconds
   - The system will analyze your facial expression
   - Choose from the recommended songs that match your mood

3. **Song Management**:
   - Tag songs with emotions using the "Tag song" button
   - Select the appropriate emotion (Happy, Sad, Neutral) from the dropdown menu
   - Filter your playlist by emotion using the emotion filter dropdown
   - View your listening history with dates and play counts
   - Manage your playlist easily with drag-and-drop

4. **Emotion Filtering**:
   - Use the emotion filter dropdown to view songs by emotion tag
   - Search for songs within a specific emotion category
   - Quickly identify songs that match your current mood

## Requirements

- Python 3.12 or later
- Required packages (install using `pip install -r requirements.txt`):
  - customtkinter
  - pygame
  - pillow
  - mediapipe
  - opencv-python
  - mutagen

## Language Support

The player supports both English and Indonesian languages. Change the language in the settings menu (⚙️).
