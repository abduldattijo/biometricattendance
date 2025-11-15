"""
Attendance routes for the Face Recognition Attendance System
Handles face recognition and attendance marking
"""
from flask import Blueprint, render_template, request, jsonify, current_app
from models import db, Employee, FaceEncoding, Attendance
from models.face_engine import FaceRecognitionEngine
from config import Config
import cv2
import numpy as np
import base64
from pathlib import Path
from datetime import datetime, timedelta
import logging

attendance_bp = Blueprint('attendance', __name__)
logger = logging.getLogger(__name__)

# Initialize components (lazy loading)
face_engine = None


def get_face_engine():
    """Get or create face engine instance"""
    global face_engine
    if face_engine is None:
        face_engine = FaceRecognitionEngine(
            model_name=Config.FACE_MODEL_NAME,
            detection_threshold=Config.FACE_DETECTION_THRESHOLD
        )
    return face_engine


@attendance_bp.route('/')
def index():
    """Attendance marking page"""
    return render_template('attendance.html')


@attendance_bp.route('/api/recognize', methods=['POST'])
def recognize_face():
    """
    Recognize a face and mark attendance
    """
    try:
        data = request.get_json()

        # Decode image
        image_data = data.get('image')

        if not image_data:
            return jsonify({'success': False, 'error': 'No image provided'}), 400

        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Get face engine
        engine = get_face_engine()

        # Load all enrolled face encodings
        face_encodings = FaceEncoding.query.filter_by(pose_type='average').all()

        if len(face_encodings) == 0:
            return jsonify({
                'success': False,
                'error': 'No enrolled employees found. Please enroll employees first.'
            }), 404

        # Extract embeddings and employee IDs
        known_embeddings = []
        known_ids = []

        for face_enc in face_encodings:
            embedding = face_enc.get_encoding()
            known_embeddings.append(embedding)
            known_ids.append(face_enc.employee_id)

        logger.info(f"Loaded {len(known_embeddings)} face encodings for recognition")

        # Perform recognition
        employee_id, confidence = engine.recognize_face(
            image,
            known_embeddings,
            known_ids,
            threshold=Config.FACE_RECOGNITION_THRESHOLD
        )

        if employee_id is None:
            return jsonify({
                'success': True,
                'recognized': False,
                'message': 'Face not recognized',
                'confidence': float(confidence)
            })

        # Get employee details
        employee = Employee.query.filter_by(employee_id=employee_id).first()

        if not employee:
            return jsonify({
                'success': False,
                'error': 'Employee record not found'
            }), 404

        # Check if already checked in today (prevent duplicate check-ins within 1 hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_attendance = Attendance.query.filter(
            Attendance.employee_id == employee_id,
            Attendance.timestamp >= one_hour_ago
        ).first()

        if recent_attendance:
            return jsonify({
                'success': True,
                'recognized': True,
                'already_checked_in': True,
                'employee_id': employee_id,
                'employee_name': employee.name,
                'confidence': float(confidence),
                'message': f'{employee.name} already checked in at {recent_attendance.timestamp.strftime("%H:%M")}',
                'last_checkin': recent_attendance.timestamp.isoformat()
            })

        # Save attendance image (optional)
        image_path = None
        try:
            attendance_dir = Config.ATTENDANCE_IMAGES_DIR
            attendance_dir.mkdir(parents=True, exist_ok=True)

            timestamp_str = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            image_filename = f"{employee_id}_{timestamp_str}.jpg"
            image_path_full = attendance_dir / image_filename
            cv2.imwrite(str(image_path_full), image)

            image_path = str(image_path_full.relative_to(Config.BASE_DIR))
        except Exception as e:
            logger.error(f"Failed to save attendance image: {e}")

        # Create attendance record
        attendance_record = Attendance(
            employee_id=employee_id,
            employee_name=employee.name,
            confidence=float(confidence),
            status='present',
            image_path=image_path
        )

        db.session.add(attendance_record)
        db.session.commit()

        logger.info(f"Attendance marked for {employee_id} ({employee.name}) with confidence {confidence:.3f}")

        return jsonify({
            'success': True,
            'recognized': True,
            'already_checked_in': False,
            'employee_id': employee_id,
            'employee_name': employee.name,
            'department': employee.department,
            'confidence': float(confidence),
            'timestamp': attendance_record.timestamp.isoformat(),
            'message': f'Welcome {employee.name}! Checked in successfully.'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Recognition error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@attendance_bp.route('/api/manual_checkin', methods=['POST'])
def manual_checkin():
    """
    Manual check-in using employee ID (fallback)
    """
    try:
        data = request.get_json()
        employee_id = data.get('employee_id')

        if not employee_id:
            return jsonify({'success': False, 'error': 'Employee ID required'}), 400

        # Get employee
        employee = Employee.query.filter_by(employee_id=employee_id, is_active=True).first()

        if not employee:
            return jsonify({
                'success': False,
                'error': f'Employee {employee_id} not found or inactive'
            }), 404

        # Check if already checked in today
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_attendance = Attendance.query.filter(
            Attendance.employee_id == employee_id,
            Attendance.timestamp >= one_hour_ago
        ).first()

        if recent_attendance:
            return jsonify({
                'success': False,
                'error': f'Already checked in at {recent_attendance.timestamp.strftime("%H:%M")}'
            }), 400

        # Create attendance record
        attendance_record = Attendance(
            employee_id=employee_id,
            employee_name=employee.name,
            confidence=None,  # Manual check-in
            status='present'
        )

        db.session.add(attendance_record)
        db.session.commit()

        logger.info(f"Manual attendance marked for {employee_id} ({employee.name})")

        return jsonify({
            'success': True,
            'employee_id': employee_id,
            'employee_name': employee.name,
            'timestamp': attendance_record.timestamp.isoformat(),
            'message': f'{employee.name} checked in manually'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Manual check-in error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@attendance_bp.route('/api/today')
def today_attendance():
    """Get today's attendance records"""
    try:
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        records = Attendance.query.filter(
            Attendance.timestamp >= today_start,
            Attendance.timestamp <= today_end
        ).order_by(Attendance.timestamp.desc()).all()

        records_data = [record.to_dict() for record in records]

        return jsonify({
            'success': True,
            'records': records_data,
            'count': len(records_data),
            'date': today.isoformat()
        })

    except Exception as e:
        logger.error(f"Today attendance error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
