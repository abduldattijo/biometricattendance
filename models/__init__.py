"""Models package initialization"""
from .database import db, Employee, FaceEncoding, Attendance

__all__ = ['db', 'Employee', 'FaceEncoding', 'Attendance']
