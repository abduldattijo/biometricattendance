"""
Configuration settings for the Face Recognition Attendance System
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.absolute()

class Config:
    """Application configuration"""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True

    # Database settings
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'data' / 'attendance.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File storage paths
    ENROLLED_FACES_DIR = BASE_DIR / 'static' / 'enrolled_faces'
    ATTENDANCE_IMAGES_DIR = BASE_DIR / 'static' / 'attendance_images'
    LOGS_DIR = BASE_DIR / 'data' / 'logs'

    # Face recognition settings
    FACE_MODEL_NAME = 'buffalo_l'  # Best for diverse faces including West African
    FACE_DETECTION_THRESHOLD = 0.5
    FACE_RECOGNITION_THRESHOLD = 0.30  # Calibrated for West African faces (0.25-0.30)

    # Image quality thresholds (critical for darker skin tones)
    MIN_BLUR_THRESHOLD = 100.0  # Laplacian variance
    MIN_BRIGHTNESS = 60  # Minimum mean brightness
    MAX_BRIGHTNESS = 200  # Maximum mean brightness
    MIN_CONTRAST = 30.0  # Standard deviation (essential for West African faces)
    MIN_FACE_SIZE = 0.15  # Face must occupy at least 15% of frame
    MAX_FACE_SIZE = 0.70  # Face must not exceed 70% of frame
    MAX_CENTER_OFFSET = 0.20  # Face center within 20% of frame center

    # Head pose thresholds for guided enrollment (more forgiving to avoid oscillation)
    POSE_REQUIREMENTS = {
        'front': {'yaw': (-20, 20), 'pitch': (-20, 20)},  # Wider tolerance for front pose
        'left': {'yaw': (-50, -20), 'pitch': (-20, 20)},   # Wider range
        'right': {'yaw': (20, 50), 'pitch': (-20, 20)},    # Wider range
        'up': {'yaw': (-20, 20), 'pitch': (15, 40)},       # Wider tolerance
        'down': {'yaw': (-20, 20), 'pitch': (-40, -15)}    # Wider tolerance
    }

    # Enrollment settings
    REQUIRED_POSES = ['front', 'left', 'right', 'up', 'down']
    CAPTURE_COUNTDOWN = 3  # Seconds before auto-capture

    # Performance settings
    MAX_EMPLOYEES = 100  # POC limit
    RECOGNITION_TIMEOUT = 2  # Seconds

    # Create directories if they don't exist
    @staticmethod
    def init_app():
        """Initialize application directories"""
        Config.ENROLLED_FACES_DIR.mkdir(parents=True, exist_ok=True)
        Config.ATTENDANCE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        Config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
