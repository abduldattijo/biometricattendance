"""
Dashboard routes for the Face Recognition Attendance System
"""
from flask import Blueprint, render_template, jsonify
from models import db, Employee, Attendance
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    """Dashboard home page"""
    return render_template('dashboard.html')


@dashboard_bp.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    try:
        # Total employees
        total_employees = Employee.query.filter_by(is_active=True).count()

        # Today's attendance
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        today_attendance = Attendance.query.filter(
            Attendance.timestamp >= today_start,
            Attendance.timestamp <= today_end
        ).count()

        # Recent check-ins (last 10)
        recent_checkins = Attendance.query.order_by(
            Attendance.timestamp.desc()
        ).limit(10).all()

        recent_checkins_data = [
            {
                'id': record.id,
                'employee_id': record.employee_id,
                'employee_name': record.employee_name,
                'timestamp': record.timestamp.isoformat() if record.timestamp else None,
                'confidence': record.confidence
            }
            for record in recent_checkins
        ]

        # Weekly attendance trend (last 7 days)
        weekly_data = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_start = datetime.combine(day, datetime.min.time())
            day_end = datetime.combine(day, datetime.max.time())

            count = Attendance.query.filter(
                Attendance.timestamp >= day_start,
                Attendance.timestamp <= day_end
            ).count()

            weekly_data.append({
                'date': day.isoformat(),
                'count': count
            })

        return jsonify({
            'success': True,
            'total_employees': total_employees,
            'today_attendance': today_attendance,
            'attendance_percentage': round((today_attendance / total_employees * 100) if total_employees > 0 else 0, 1),
            'recent_checkins': recent_checkins_data,
            'weekly_trend': weekly_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/employees')
def employees_list():
    """Employee list page"""
    return render_template('employees.html')


@dashboard_bp.route('/api/employees')
def get_employees():
    """Get all employees"""
    try:
        employees = Employee.query.order_by(Employee.enrolled_at.desc()).all()

        employees_data = [emp.to_dict() for emp in employees]

        return jsonify({
            'success': True,
            'employees': employees_data,
            'count': len(employees_data)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/reports')
def reports():
    """Attendance reports page"""
    return render_template('reports.html')


@dashboard_bp.route('/api/attendance/report')
def get_attendance_report():
    """Get attendance report for date range"""
    try:
        from flask import request

        # Get date range from query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        # Default to today if not provided
        if not start_date_str:
            start_date = datetime.utcnow().date()
        else:
            start_date = datetime.fromisoformat(start_date_str).date()

        if not end_date_str:
            end_date = datetime.utcnow().date()
        else:
            end_date = datetime.fromisoformat(end_date_str).date()

        # Convert to datetime
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        # Query attendance records
        records = Attendance.query.filter(
            Attendance.timestamp >= start_datetime,
            Attendance.timestamp <= end_datetime
        ).order_by(Attendance.timestamp.desc()).all()

        records_data = [record.to_dict() for record in records]

        return jsonify({
            'success': True,
            'records': records_data,
            'count': len(records_data),
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/test')
def test_page():
    """System test page"""
    return render_template('test.html')
