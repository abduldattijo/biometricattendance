# Face Recognition Attendance System - POC

A fully functional facial recognition attendance system optimized for West African employees, built with Flask and InsightFace.

## Features

- **Guided Enrollment System**: Multi-pose face capture with real-time quality feedback (like smartphone face unlock)
- **High Accuracy Recognition**: InsightFace buffalo_l model optimized for diverse skin tones
- **Quality Enforcement**: Automatic checks for blur, brightness, contrast, and face positioning
- **Professional Web Interface**: Clean Bootstrap 5 UI with real-time webcam integration
- **Attendance Management**: Complete tracking, reporting, and export capabilities
- **Manual Fallback**: Option for manual check-in when recognition fails

## Technology Stack

### Backend
- **Flask**: Web framework
- **InsightFace**: Face recognition (buffalo_l model)
- **SQLAlchemy**: ORM for database operations
- **OpenCV**: Image processing and webcam handling
- **SQLite**: Database for POC

### Frontend
- **Bootstrap 5**: UI framework
- **JavaScript**: Webcam integration and real-time feedback
- **Chart.js**: Dashboard visualizations
- **HTML5/CSS3**: Modern web standards

## System Requirements

- **Operating System**: macOS (tested on M1/M2/M3 and Intel)
- **Python**: 3.8 or higher
- **Webcam**: Built-in or external camera
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: At least 2GB free space

## Installation

### 1. Clone or Navigate to Project Directory

```bash
cd /Users/muhammaddattijo/Downloads/biometricattendance
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note for Apple Silicon (M1/M2/M3) Macs:**

If you encounter issues, you may need to install additional dependencies:

```bash
brew install cmake
```

### 4. Download InsightFace Models

The InsightFace models will be automatically downloaded on first run. This may take a few minutes.

### 5. Initialize Database

The database will be automatically created when you first run the application.

## Running the Application

### Start the Server

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage Guide

### 1. Dashboard
- View total enrolled employees
- See today's attendance count
- Monitor weekly attendance trends
- View recent check-ins

### 2. Enroll Employee

**Steps:**
1. Navigate to "Enroll Employee" from the menu
2. Fill in employee details:
   - Employee ID (required)
   - Full Name (required)
   - Department (optional)
   - Email (optional)
   - Phone (optional)
3. Click "Start Guided Face Capture"
4. Follow on-screen instructions for 5 poses:
   - **Front**: Look straight at camera
   - **Left**: Turn head to the left
   - **Right**: Turn head to the right
   - **Up**: Tilt head up (chin up)
   - **Down**: Tilt head down (chin down)
5. System will automatically capture when quality is good
6. Review captured images
7. Click "Confirm Enrollment"

**Tips for Best Results:**
- Ensure good lighting (avoid backlighting)
- Remove glasses if possible
- Remove face masks or coverings
- Hold still when system counts down
- Position face to fill 30-50% of frame

### 3. Mark Attendance

**Steps:**
1. Navigate to "Mark Attendance" from the menu
2. Position yourself in front of the camera
3. Click "Capture Photo"
4. System will recognize your face and mark attendance
5. See confirmation with your name and confidence score

**Fallback - Manual Check-in:**
If face recognition fails, use the manual check-in:
1. Enter your Employee ID
2. Click "Check In"

### 4. View Employees

- See all enrolled employees
- Search by ID, name, or department
- Delete employees if needed
- View number of face images per employee

### 5. Attendance Reports

**Generate Reports:**
1. Navigate to "Reports"
2. Select start and end dates
3. Click "Generate Report"
4. View attendance records in table
5. Export to CSV for further analysis

### 6. System Test

- Test webcam functionality
- View system configuration
- Check database connection
- Verify browser compatibility

## Project Structure

```
biometricattendance/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── models/
│   ├── database.py            # SQLAlchemy models
│   └── face_engine.py         # Face recognition engine
├── routes/
│   ├── dashboard.py           # Dashboard routes
│   ├── enrollment.py          # Enrollment routes
│   └── attendance.py          # Attendance routes
├── utils/
│   ├── quality_checker.py     # Image quality validation
│   ├── pose_estimator.py      # Head pose estimation
│   └── guided_enrollment.py   # Guided enrollment logic
├── templates/                  # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── enroll.html
│   ├── enroll_guided.html
│   ├── attendance.html
│   ├── employees.html
│   ├── reports.html
│   └── test.html
├── static/
│   ├── css/
│   │   └── style.css          # Custom styles
│   ├── js/
│   │   ├── guided_capture.js  # Guided enrollment UI
│   │   └── attendance.js      # Attendance marking
│   ├── enrolled_faces/        # Stored face images
│   └── attendance_images/     # Attendance photos
└── data/
    ├── attendance.db          # SQLite database
    └── logs/                  # Application logs
```

## Configuration

Edit `config.py` to customize settings:

### Face Recognition Settings
- `FACE_MODEL_NAME`: InsightFace model (default: 'buffalo_l')
- `FACE_RECOGNITION_THRESHOLD`: Similarity threshold (default: 0.30)
  - Lower = more strict
  - Higher = more lenient

### Image Quality Settings
- `MIN_BLUR_THRESHOLD`: Minimum sharpness (default: 100.0)
- `MIN_BRIGHTNESS`: Minimum brightness (default: 60)
- `MAX_BRIGHTNESS`: Maximum brightness (default: 200)
- `MIN_CONTRAST`: Minimum contrast (default: 30.0)

### Enrollment Settings
- `REQUIRED_POSES`: List of required poses
- `CAPTURE_COUNTDOWN`: Seconds before auto-capture (default: 3)

## API Endpoints

### Enrollment
- `POST /enroll/api/validate_frame` - Validate frame quality and pose
- `POST /enroll/api/enroll` - Enroll new employee
- `DELETE /enroll/api/employee/<employee_id>` - Delete employee

### Attendance
- `POST /attendance/api/recognize` - Recognize face and mark attendance
- `POST /attendance/api/manual_checkin` - Manual check-in
- `GET /attendance/api/today` - Get today's attendance

### Dashboard
- `GET /api/stats` - Get dashboard statistics
- `GET /api/employees` - Get all employees
- `GET /api/attendance/report` - Get attendance report

## Troubleshooting

### Webcam Not Working
- Check browser permissions (allow camera access)
- Try a different browser (Chrome/Firefox recommended)
- Ensure no other application is using the webcam
- Restart the browser

### Face Not Recognized
- Ensure good lighting
- Remove glasses or sunglasses
- Remove face masks
- Try multiple times
- Use manual check-in as fallback

### Low Recognition Accuracy
- Re-enroll with better quality images
- Adjust `FACE_RECOGNITION_THRESHOLD` in config.py
- Ensure consistent lighting between enrollment and recognition
- Check that webcam is clean

### Installation Issues on Mac
```bash
# If InsightFace installation fails
pip install insightface --no-cache-dir

# If OpenCV installation fails
brew install opencv
pip install opencv-python

# For M1/M2/M3 Macs
pip install onnxruntime-silicon
```

## Performance Optimization

### For Production Deployment

1. **Use PostgreSQL instead of SQLite**
   ```python
   SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/attendance'
   ```

2. **Enable GPU acceleration** (if available)
   ```python
   providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
   ```

3. **Use FAISS for faster search** (100+ employees)
   ```bash
   pip install faiss-cpu
   ```

4. **Deploy with Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

## Security Considerations

**For Production:**
- Change `SECRET_KEY` in config.py
- Use HTTPS (SSL/TLS)
- Implement user authentication
- Add role-based access control
- Encrypt face embeddings at rest
- Implement rate limiting
- Add CSRF protection
- Regular security audits

## Testing

### Manual Testing Checklist

- [ ] Webcam initializes correctly
- [ ] Guided enrollment captures all 5 poses
- [ ] Quality checks reject poor images
- [ ] Face recognition works accurately
- [ ] Attendance is logged correctly
- [ ] Dashboard shows correct statistics
- [ ] Reports generate and export properly
- [ ] Manual check-in works as fallback

### Accuracy Testing

Test with at least 10-20 real users:
1. Enroll each user
2. Test recognition multiple times
3. Calculate accuracy: (Correct recognitions / Total attempts) × 100
4. Target: >99% accuracy
5. Adjust threshold if needed

## Known Limitations (POC)

- SQLite database (not suitable for production scale)
- No user authentication system
- No liveness detection (can be fooled by photos)
- Limited to ~100 employees for optimal performance
- Single-device deployment
- No offline mode
- No mobile app

## Future Enhancements

- [ ] Liveness detection (blink detection, movement)
- [ ] Multi-camera support
- [ ] Raspberry Pi deployment
- [ ] Mobile app for managers
- [ ] Integration with HR/payroll systems
- [ ] Advanced analytics and insights
- [ ] Email notifications
- [ ] Shift management
- [ ] Leave tracking integration
- [ ] GPU acceleration for larger deployments

## Credits

- **InsightFace**: Face recognition models
- **Flask**: Web framework
- **Bootstrap**: UI framework
- **OpenCV**: Image processing

## License

This is a POC (Proof of Concept) system for demonstration purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review configuration settings
3. Check browser console for errors
4. Verify webcam permissions

## Version

**Version**: 1.0.0 (POC)
**Date**: November 2024
**Status**: Proof of Concept - Ready for Testing

---

**Built for West African Employees with Care and Precision**
