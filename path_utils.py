import os
import sys

def get_base_directory():
    """
    Get the base directory of the application, handling both development and executable environments.
    
    Returns:
        str: The base directory path
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as compiled exe
        return os.path.dirname(sys.executable)
    else:
        # Running in development environment
        return os.path.dirname(os.path.abspath(__file__))

def get_data_directory():
    """
    Get the Data directory path.
    
    Returns:
        str: The Data directory path
    """
    return os.path.join(get_base_directory(), "Data")

def get_languages_directory():
    """
    Get the Languages directory path within the Data directory.
    
    Returns:
        str: The Languages directory path
    """
    return os.path.join(get_data_directory(), "Languages")

def get_temp_image_directory():
    """
    Get the Temp_Image directory path within the Data directory.
    
    Returns:
        str: The Temp_Image directory path
    """
    return os.path.join(get_data_directory(), "Temp_Image")

def get_music_tag_directory():
    """
    Get the Music_Tag directory path within the Data directory.
    
    Returns:
        str: The Music_Tag directory path
    """
    return os.path.join(get_data_directory(), "Music_Tag")

def get_emotions_file_path():
    """
    Get the emotions.json file path within the Data directory.
    
    Returns:
        str: The emotions.json file path
    """
    return os.path.join(get_data_directory(), "emotions.json")