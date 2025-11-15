# Quick Start Guide

## Installation (5 minutes)

### Option 1: Using Setup Script (Recommended)

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Application

```bash
# Activate virtual environment (if not already activated)
source .venv/bin/activate

# Start the application
python app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
```

## Access the Application

Open your browser and go to:
```
http://localhost:5000
```

## First Steps

### 1. Test the System
1. Navigate to **System Test** from the menu
2. Click "Start Webcam" to verify camera works
3. Click "Test Database Connection" to verify database

### 2. Enroll Your First Employee
1. Navigate to **Enroll Employee**
2. Fill in:
   - Employee ID: `EMP001`
   - Name: `Your Name`
   - Department: `Testing`
3. Click **Start Guided Face Capture**
4. Follow the on-screen instructions:
   - Look straight (front)
   - Turn left
   - Turn right
   - Tilt head up
   - Tilt head down
5. System will auto-capture when quality is good
6. Review images and click **Confirm Enrollment**

### 3. Test Face Recognition
1. Navigate to **Mark Attendance**
2. Click **Capture Photo**
3. System should recognize you and mark attendance
4. Check **Dashboard** to see your attendance logged

### 4. View Reports
1. Navigate to **Reports**
2. Select date range (defaults to last 7 days)
3. Click **Generate Report**
4. Export to CSV if needed

## Troubleshooting Quick Fixes

### Webcam Not Working
- **Chrome**: Go to Settings > Privacy > Camera > Allow
- **Firefox**: Click camera icon in address bar > Allow
- **Safari**: Safari > Settings for This Website > Camera > Allow

### Module Not Found Error
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or run on different port
python app.py --port 5001
```

### Face Not Recognized
- Ensure good lighting
- Try re-enrolling with better images
- Check if glasses/mask are different from enrollment
- Use manual check-in as fallback

## Default Configuration

- **Recognition Threshold**: 0.30 (optimized for West African faces)
- **Required Poses**: 5 (front, left, right, up, down)
- **Auto-Capture Countdown**: 3 seconds
- **Min Brightness**: 60
- **Max Brightness**: 200
- **Min Contrast**: 30
- **Min Blur Score**: 100

## Next Steps

1. **Enroll Multiple Employees**: Test with 5-10 people
2. **Test Recognition Accuracy**: Have each person check in multiple times
3. **Adjust Threshold**: Edit `config.py` if needed
4. **Export Reports**: Test CSV export functionality
5. **Monitor Dashboard**: Check real-time statistics

## Common Commands

```bash
# Start application
python app.py

# Stop application
Ctrl+C

# Activate virtual environment
source .venv/bin/activate

# Deactivate virtual environment
deactivate

# View logs (if created)
tail -f data/logs/app.log

# Check Python packages
pip list

# Update requirements
pip freeze > requirements.txt
```

## Performance Tips

- **Good Lighting**: Ensure even lighting on face
- **Stable Position**: Hold still during capture
- **Clean Lens**: Keep webcam lens clean
- **Close Distance**: Face should fill 30-50% of frame
- **Remove Obstructions**: No glasses, masks, or hats if possible

## Getting Help

1. Check **README.md** for detailed documentation
2. Review **Troubleshooting** section in README
3. Check browser console for JavaScript errors (F12)
4. Verify webcam permissions in browser settings
5. Ensure all dependencies are installed

## File Locations

- **Database**: `data/attendance.db`
- **Logs**: `data/logs/app.log`
- **Enrolled Faces**: `static/enrolled_faces/[employee_id]/`
- **Attendance Images**: `static/attendance_images/`
- **Configuration**: `config.py`

## Success Checklist

- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] Application starts without errors
- [ ] Webcam test successful
- [ ] Database connection successful
- [ ] First employee enrolled successfully
- [ ] Face recognition working
- [ ] Attendance logged correctly
- [ ] Dashboard shows statistics
- [ ] Reports can be generated

---

**Ready to test!** Start with the System Test page to verify everything works.
