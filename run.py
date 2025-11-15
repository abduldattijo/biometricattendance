"""
Simple runner script with clear output
"""
import os
import sys

print("=" * 60)
print("FACE RECOGNITION ATTENDANCE SYSTEM")
print("=" * 60)
print()
print("Starting application...")
print("This may take a moment on first run (downloading models)...")
print()

# Import and run
from app import create_app

app = create_app()

print()
print("=" * 60)
print("APPLICATION STARTED SUCCESSFULLY!")
print("=" * 60)
print()
print("Access the application at:")
print("  http://localhost:5000")
print()
print("Available pages:")
print("  - Dashboard:         http://localhost:5000/")
print("  - Enroll Employee:   http://localhost:5000/enroll")
print("  - Mark Attendance:   http://localhost:5000/attendance")
print("  - View Employees:    http://localhost:5000/employees")
print("  - Reports:           http://localhost:5000/reports")
print("  - System Test:       http://localhost:5000/test")
print()
print("Press Ctrl+C to stop the server")
print("=" * 60)
print()

app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
