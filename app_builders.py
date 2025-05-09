import os
import shutil
import subprocess
import sys
import pkg_resources
import PyInstaller.__main__

def check_and_install_dependencies():
    """Check and install required dependencies"""
    required = {
        'customtkinter': '>=5.2.1',
        'pygame': '>=2.5.2',
        'pillow': '>=10.1.0',
        'opencv-python': '>=4.8.1',
        'mutagen': '>=1.47.0',
        'numpy': '>=1.24.0',
        'tk': '>=0.1.0'
    }
    
    print("Checking dependencies...")
    for package, version in required.items():
        try:
            pkg_resources.require(f"{package}{version}")
            print(f"✓ {package} already installed")
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
            print(f"Installing {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package}{version}"])
                print(f"✓ {package} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"Error installing {package}: {e}")
                return False
    return True

def clean_build_dirs():
    """Clean up build directories"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                print(f"Removing {dir_name} directory...")
                shutil.rmtree(dir_name)
            except Exception as e:
                print(f"Error cleaning {dir_name}: {e}")
                return False
    return True

def build_launcher():
    """Build the launcher using PyInstaller"""
    try:
        print("Building launcher...")
        PyInstaller.__main__.run([
            'KaisarPlayer.spec',
            '--noconfirm',
            '--clean',
            '--log-level=WARN'
        ])
        
        # Ensure Emotion_Data folder is copied to the dist directory
        emotion_data_src = os.path.join('Data', 'Emotion_Data')
        emotion_data_dst = os.path.join('dist', 'Data', 'Emotion_Data')
        
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(emotion_data_dst), exist_ok=True)
        
        # Copy the directory if it exists
        if os.path.exists(emotion_data_src):
            print(f"Copying Emotion_Data folder to {emotion_data_dst}...")
            if os.path.exists(emotion_data_dst):
                shutil.rmtree(emotion_data_dst)
            shutil.copytree(emotion_data_src, emotion_data_dst)
            print("Emotion_Data folder copied successfully")
        else:
            print(f"Warning: Emotion_Data folder not found at {emotion_data_src}")
            
        return True
    except Exception as e:
        print(f"Build error: {e}")
        return False

if __name__ == "__main__":
    try:
        # Get current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_dir)
        
        print("Starting rebuild process...")
        
        # Check and install dependencies
        if not check_and_install_dependencies():
            print("Failed to install dependencies")
            sys.exit(1)
            
        # Clean directories
        if not clean_build_dirs():
            print("Failed to clean build directories")
            sys.exit(1)
            
        # Build launcher
        if not build_launcher():
            print("Failed to build launcher")
            sys.exit(1)
            
        print("Build complete! Check the dist/KaisarPlayer directory for the executable.")
        
    except Exception as e:
        print(f"Error during rebuild: {e}")
        sys.exit(1)
