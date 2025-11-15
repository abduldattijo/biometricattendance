/**
 * Attendance Marking JavaScript
 * Handles face recognition and attendance logging
 */

let webcamStream = null;
let isProcessing = false;

const video = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const captureBtn = document.getElementById('capture-btn');
const feedbackOverlay = document.getElementById('feedback-overlay');
const resultContainer = document.getElementById('result-container');
const todayAttendanceList = document.getElementById('today-attendance-list');

// Initialize webcam
async function initWebcam() {
    try {
        webcamStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            }
        });

        video.srcObject = webcamStream;

        // Wait for video to be ready
        return new Promise((resolve) => {
            video.onloadedmetadata = () => {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                captureBtn.disabled = false;
                resolve();
            };
        });
    } catch (error) {
        console.error('Webcam error:', error);
        showToast('Failed to access webcam. Please check permissions.', 'error');
        throw error;
    }
}

// Capture and recognize
captureBtn.addEventListener('click', async function() {
    if (isProcessing) return;

    isProcessing = true;
    captureBtn.disabled = true;
    feedbackOverlay.style.display = 'block';

    try {
        // Capture current frame
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpeg', 0.9);

        // Send to server for recognition
        const response = await fetch('/attendance/api/recognize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData })
        });

        const data = await response.json();

        if (data.success) {
            if (data.recognized) {
                showSuccessResult(data);
            } else {
                showFailureResult(data);
            }
        } else {
            showToast('Recognition error: ' + data.error, 'error');
        }

    } catch (error) {
        console.error('Recognition error:', error);
        showToast('Error during recognition: ' + error.message, 'error');
    } finally {
        isProcessing = false;
        captureBtn.disabled = false;
        feedbackOverlay.style.display = 'none';
    }
});

// Show success result
function showSuccessResult(data) {
    const alreadyCheckedIn = data.already_checked_in;
    const iconClass = alreadyCheckedIn ? 'bi-info-circle-fill' : 'bi-check-circle-fill';
    const bgClass = alreadyCheckedIn ? 'bg-warning' : 'bg-success';
    const title = alreadyCheckedIn ? 'Already Checked In' : 'Attendance Marked';

    resultContainer.innerHTML = `
        <div class="card result-card border-success">
            <div class="card-header ${bgClass} text-white">
                <h5 class="mb-0">
                    <i class="bi ${iconClass}"></i> ${title}
                </h5>
            </div>
            <div class="card-body">
                <h3 class="text-success">${data.employee_name}</h3>
                <p class="mb-2">
                    <strong>Employee ID:</strong> ${data.employee_id}<br>
                    <strong>Department:</strong> ${data.department || '-'}<br>
                    <strong>Confidence:</strong> <span class="badge bg-success">${(data.confidence * 100).toFixed(1)}%</span><br>
                    <strong>Time:</strong> ${new Date(data.timestamp || data.last_checkin).toLocaleTimeString()}
                </p>
                <p class="text-muted">${data.message}</p>
            </div>
        </div>
    `;
    resultContainer.style.display = 'block';

    // Reload today's attendance if new check-in
    if (!alreadyCheckedIn) {
        loadTodayAttendance();
        showToast(data.message, 'success');
    } else {
        showToast(data.message, 'info');
    }
}

// Show failure result
function showFailureResult(data) {
    resultContainer.innerHTML = `
        <div class="card result-card border-danger">
            <div class="card-header bg-danger text-white">
                <h5 class="mb-0">
                    <i class="bi bi-x-circle-fill"></i> Not Recognized
                </h5>
            </div>
            <div class="card-body">
                <p>${data.message}</p>
                <p class="text-muted">
                    ${data.confidence ? `Best match: ${(data.confidence * 100).toFixed(1)}%` : ''}
                </p>
                <div class="alert alert-warning">
                    <strong>Tips:</strong>
                    <ul class="mb-0">
                        <li>Ensure good lighting</li>
                        <li>Remove glasses or masks</li>
                        <li>Look directly at camera</li>
                        <li>Try again or use manual check-in below</li>
                    </ul>
                </div>
            </div>
        </div>
    `;
    resultContainer.style.display = 'block';

    showToast('Face not recognized', 'error');
}

// Manual check-in
document.getElementById('manual-checkin-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const employeeId = document.getElementById('manual-employee-id').value.trim();

    if (!employeeId) {
        showToast('Please enter Employee ID', 'error');
        return;
    }

    try {
        const response = await fetch('/attendance/api/manual_checkin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ employee_id: employeeId })
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
            document.getElementById('manual-employee-id').value = '';

            // Show result
            resultContainer.innerHTML = `
                <div class="card result-card border-info">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0">
                            <i class="bi bi-check-circle-fill"></i> Manual Check-in
                        </h5>
                    </div>
                    <div class="card-body">
                        <h3 class="text-info">${data.employee_name}</h3>
                        <p class="mb-2">
                            <strong>Employee ID:</strong> ${data.employee_id}<br>
                            <strong>Time:</strong> ${new Date(data.timestamp).toLocaleTimeString()}
                        </p>
                        <p class="text-muted">Checked in manually</p>
                    </div>
                </div>
            `;
            resultContainer.style.display = 'block';

            loadTodayAttendance();
        } else {
            showToast('Manual check-in failed: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Manual check-in error:', error);
        showToast('Error during manual check-in', 'error');
    }
});

// Load today's attendance
function loadTodayAttendance() {
    fetch('/attendance/api/today')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayTodayAttendance(data.records);
            } else {
                todayAttendanceList.innerHTML = '<div class="alert alert-danger">Failed to load attendance</div>';
            }
        })
        .catch(error => {
            console.error('Error loading attendance:', error);
            todayAttendanceList.innerHTML = '<div class="alert alert-danger">Error loading attendance</div>';
        });
}

// Display today's attendance
function displayTodayAttendance(records) {
    if (records.length === 0) {
        todayAttendanceList.innerHTML = '<div class="text-center text-muted py-3">No attendance records today</div>';
        return;
    }

    let html = '<div class="list-group">';

    records.forEach(record => {
        const time = new Date(record.timestamp).toLocaleTimeString();
        const confidence = record.confidence ?
            `<span class="badge bg-success">${(record.confidence * 100).toFixed(0)}%</span>` :
            `<span class="badge bg-secondary">Manual</span>`;

        html += `
            <div class="list-group-item">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-0">${record.employee_name}</h6>
                        <small class="text-muted">${record.employee_id}</small>
                    </div>
                    <div class="text-end">
                        <div>${time}</div>
                        ${confidence}
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    todayAttendanceList.innerHTML = html;
}

// Initialize on page load
(async function init() {
    try {
        await initWebcam();
        loadTodayAttendance();
    } catch (error) {
        console.error('Initialization error:', error);
    }

    // Auto-refresh attendance every 30 seconds
    setInterval(loadTodayAttendance, 30000);
})();

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
    }
});
