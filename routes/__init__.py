"""Routes package initialization"""
from .dashboard import dashboard_bp
from .enrollment import enrollment_bp
from .attendance import attendance_bp

__all__ = ['dashboard_bp', 'enrollment_bp', 'attendance_bp']
