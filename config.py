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

    # Image quality thresholds (relaxed for standard webcams and real-world conditions)
    MIN_BLUR_THRESHOLD = 40.0  # Relaxed from 100.0 - prevents "blurry" errors on standard webcams
    MIN_BRIGHTNESS = 40  # Relaxed from 60 - works in dim lighting
    MAX_BRIGHTNESS = 200  # Maximum mean brightness
    MIN_CONTRAST = 30.0  # Standard deviation
    MIN_FACE_SIZE = 0.10  # Relaxed from 0.15 - prevents "come closer" errors
    MAX_FACE_SIZE = 0.70  # Face must not exceed 70% of frame
    MAX_CENTER_OFFSET = 0.20  # Face center within 20% of frame center

    # Head pose thresholds with INTENTIONAL OVERLAPS to prevent dead zones
    # 5° overlap between front and left/right ensures smooth transitions
    # Yaw: negative = head turned LEFT, positive = head turned RIGHT
    # Pitch: negative = head tilted DOWN, positive = head tilted UP
    POSE_REQUIREMENTS = {
        'front': {'yaw': (-30, 30), 'pitch': (-25, 25)},      # Wide front zone
        'left': {'yaw': (-70, -25), 'pitch': (-25, 25)},      # 5° overlap with front (-30 to -25)
        'right': {'yaw': (25, 70), 'pitch': (-25, 25)},       # 5° overlap with front (25 to 30)
        'up': {'yaw': (-25, 25), 'pitch': (20, 55)},          # Slight overlap with front
        'down': {'yaw': (-25, 25), 'pitch': (-55, -20)}       # Slight overlap with front
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
