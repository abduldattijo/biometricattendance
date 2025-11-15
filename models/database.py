"""
Database models for the Face Recognition Attendance System
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pickle
import numpy as np

db = SQLAlchemy()


class Employee(db.Model):
    """Employee model for storing employee information"""
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    face_encodings = db.relationship('FaceEncoding', backref='employee', lazy=True, cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='employee', lazy=True)

    def to_dict(self):
        """Convert employee to dictionary"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'name': self.name,
            'department': self.department,
            'email': self.email,
            'phone': self.phone,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'is_active': self.is_active,
            'face_count': len(self.face_encodings)
        }


class FaceEncoding(db.Model):
    """Face encoding model for storing face embeddings"""
    __tablename__ = 'face_encodings'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), nullable=False, index=True)
    encoding = db.Column(db.LargeBinary, nullable=False)  # Pickled numpy array
    image_path = db.Column(db.String(500))
    pose_type = db.Column(db.String(20))  # 'front', 'left', 'right', 'up', 'down'
    quality_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_encoding(self, encoding_array: np.ndarray):
        """Store numpy array as pickled binary"""
        self.encoding = pickle.dumps(encoding_array)

    def get_encoding(self) -> np.ndarray:
        """Retrieve numpy array from pickled binary"""
        return pickle.loads(self.encoding)

    def to_dict(self):
        """Convert face encoding to dictionary"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'image_path': self.image_path,
            'pose_type': self.pose_type,
            'quality_score': self.quality_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Attendance(db.Model):
    """Attendance model for storing attendance records"""
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), nullable=False, index=True)
    employee_name = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    confidence = db.Column(db.Float)
    status = db.Column(db.String(20), default='present')
    image_path = db.Column(db.String(500))

    def to_dict(self):
        """Convert attendance record to dictionary"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee_name,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'confidence': self.confidence,
            'status': self.status,
            'image_path': self.image_path
        }
