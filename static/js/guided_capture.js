/**
 * Guided Face Capture JavaScript
 * Handles multi-pose enrollment with real-time quality feedback
 */

const REQUIRED_POSES = ['front', 'left', 'right']; // Simplified: removed 'up', 'down'
const VALIDATION_INTERVAL = 800; // ms (increased from 500ms for smoother feedback)
const COUNTDOWN_SECONDS = 3;
const FRAMES_TO_HOLD = 1; // Reduced from 2 - captures faster (~0.8s hold)

let webcamStream = null;
let currentPoseIndex = 0;
let capturedImages = {};
let validationTimer = null;
let countdownTimer = null;
let isCountingDown = false;
let isProcessing = false;
let employeeData = null;
let stabilityCounter = 0; // Tracks consecutive "ready" frames

const video = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const feedbackText = document.getElementById('feedback-text');
const countdownDiv = document.getElementById('countdown');
const progressBar = document.getElementById('progress-bar');
const progressText = document.getElementById('progress-text');
const flashOverlay = document.getElementById('flash-overlay');
const capturedImagesGrid = document.getElementById('captured-images-grid');
const noCaptures = document.getElementById('no-captures');
const confirmEnrollmentBtn = document.getElementById('confirm-enrollment-btn');

// Load employee data
function loadEmployeeData() {
    const data = sessionStorage.getItem('enrollmentData');
    if (!data) {
        showToast('No enrollment data found. Redirecting...', 'error');
        setTimeout(() => window.location.href = '/enroll', 2000);
        return null;
    }

    employeeData = JSON.parse(data);

    // Display employee info
    document.getElementById('display-employee-id').textContent = employeeData.employee_id;
    document.getElementById('display-name').textContent = employeeData.name;
    document.getElementById('display-department').textContent = employeeData.department || '-';

    return employeeData;
}

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
                resolve();
            };
        });
    } catch (error) {
        console.error('Webcam error:', error);
        feedbackText.textContent = 'Failed to access webcam. Please check permissions.';
        throw error;
    }
}

// Get current pose
function getCurrentPose() {
    if (currentPoseIndex < REQUIRED_POSES.length) {
        return REQUIRED_POSES[currentPoseIndex];
    }
    return null;
}

// Update progress
function updateProgress() {
    const progress = (currentPoseIndex / REQUIRED_POSES.length) * 100;
    progressBar.style.width = `${progress}%`;
    progressText.textContent = `${currentPoseIndex}/${REQUIRED_POSES.length}`;

    if (currentPoseIndex === REQUIRED_POSES.length) {
        progressBar.classList.remove('progress-bar-animated');
        progressBar.classList.add('bg-success');
    }
}

// Update head guide animation
function updateHeadGuide(pose) {
    const headVisual = document.getElementById('head-visual');
    const headGuideLabel = document.getElementById('head-guide-label');
    const arrowLeft = document.getElementById('arrow-left');
    const arrowRight = document.getElementById('arrow-right');
    const arrowUp = document.getElementById('arrow-up');
    const arrowDown = document.getElementById('arrow-down');

    if (!headVisual) {
        console.error('Head visual element not found!');
        return;
    }

    // Get current pose to check if it's changing
    const h = String.fromCharCode(45); // hyphen (ASCII 45)
    const posePrefix = 'pose' + h;
    const currentPoseClasses = Array.from(headVisual.classList).filter(c => c.startsWith(posePrefix));
    const currentPose = currentPoseClasses.length > 0 ? currentPoseClasses[0].replace(posePrefix, '') : null;

    console.log(`Updating head guide: ${currentPose} → ${pose}`);

    // Remove all pose classes (using proper ASCII hyphens)
    headVisual.classList.remove('pose' + h + 'front', 'pose' + h + 'left', 'pose' + h + 'right', 'pose' + h + 'up', 'pose' + h + 'down', 'pose' + h + 'changing');

    // Hide all arrows
    arrowLeft.style.display = 'none';
    arrowRight.style.display = 'none';
    arrowUp.style.display = 'none';
    arrowDown.style.display = 'none';

    // Pose label map
    const poseLabels = {
        'front': 'FRONT',
        'left': 'TURN LEFT',
        'right': 'TURN RIGHT',
        'up': 'TILT UP',
        'down': 'TILT DOWN'
    };

    // Add current pose class and show relevant arrow
    if (pose) {
        // Add pulse animation if pose is changing
        if (currentPose !== pose) {
            headVisual.classList.add('pose-changing');
            setTimeout(() => {
                headVisual.classList.remove('pose-changing');
            }, 600);
        }

        // Use explicit string concatenation with ASCII hyphen to avoid encoding issues
        const poseClass = 'pose' + h + pose;
        headVisual.classList.add(poseClass);

        // Debug: Log what class was added
        console.log('Applied class:', poseClass, 'Full classList:', headVisual.classList.toString());

        // Update label
        if (headGuideLabel) {
            headGuideLabel.textContent = poseLabels[pose] || pose.toUpperCase();
        }

        // Show directional arrow
        if (pose === 'left') {
            arrowLeft.style.display = 'block';
        } else if (pose === 'right') {
            arrowRight.style.display = 'block';
        } else if (pose === 'up') {
            arrowUp.style.display = 'block';
        } else if (pose === 'down') {
            arrowDown.style.display = 'block';
        }

        // Force a style recalculation
        void headVisual.offsetWidth;
    }
}

// Test function to cycle through poses (for debugging)
window.testHeadPoses = function() {
    const poses = ['front', 'left', 'right', 'up', 'down'];
    let index = 0;

    const cycleInterval = setInterval(() => {
        updateHeadGuide(poses[index]);
        console.log(`Test: Showing ${poses[index]} pose`);
        index++;
        if (index >= poses.length) {
            clearInterval(cycleInterval);
            console.log('Test complete!');
        }
    }, 2000);
}

// Update feedback display with visual indicators
function updateFeedbackDisplay(data) {
    const currentPose = getCurrentPose();
    const videoContainer = document.getElementById('video-container');
    const headGuide = document.getElementById('head-guide');
    const headGuideStatus = document.getElementById('head-guide-status');
    const faceOverlay = document.getElementById('face-guide-overlay');

    console.log(`updateFeedbackDisplay called with currentPose: ${currentPose}`);

    // Update head guide pose (Shows the GOAL)
    updateHeadGuide(currentPose);

    // Clear previous classes
    feedbackText.className = '';
    videoContainer.classList.remove('status-perfect', 'status-adjusting', 'status-warning');
    headGuide.classList.remove('status-correct', 'status-adjusting');
    if (faceOverlay) faceOverlay.classList.remove('active');

    // --- VISUAL CORRECTION: Show correction arrows when user needs to adjust ---
    // If we are trying to do "Front" but the user needs to turn
    if (currentPose === 'front' && !data.pose_pass) {
        const arrowLeft = document.getElementById('arrow-left');
        const arrowRight = document.getElementById('arrow-right');
        const arrowUp = document.getElementById('arrow-up');
        const arrowDown = document.getElementById('arrow-down');

        // Check the feedback text from server to see which way to turn
        if (data.feedback.includes("Turn LEFT") || data.feedback.includes("turn left")) {
            if (arrowLeft) arrowLeft.style.display = 'block';
        }
        else if (data.feedback.includes("Turn RIGHT") || data.feedback.includes("turn right")) {
            if (arrowRight) arrowRight.style.display = 'block';
        }

        // Handle Pitch corrections
        if (data.feedback.includes("Tilt head UP") || data.feedback.includes("tilt up")) {
            if (arrowUp) arrowUp.style.display = 'block';
        }
        else if (data.feedback.includes("Tilt head DOWN") || data.feedback.includes("tilt down")) {
            if (arrowDown) arrowDown.style.display = 'block';
        }
    }
    // -----------------------------------------------------------------------

    // Parse feedback messages
    const feedbackParts = data.feedback.split(' | ');

    // Create structured feedback HTML
    let feedbackHTML = '';

    // Add pose instruction prominently
    const poseIcons = {
        'front': '👤',
        'left': '↪️',
        'right': '↩️',
        'up': '⬆️',
        'down': '⬇️'
    };

    const poseNames = {
        'front': 'LOOK STRAIGHT',
        'left': 'TURN LEFT',
        'right': 'TURN RIGHT',
        'up': 'TILT UP',
        'down': 'TILT DOWN'
    };

    feedbackHTML += `<div class="pose-instruction">${poseIcons[currentPose] || '📸'} ${poseNames[currentPose] || currentPose.toUpperCase()}</div>`;

    // Determine status and color
    if (data.ready_to_capture) {
        feedbackText.className = 'feedback-perfect';
        videoContainer.classList.add('status-perfect');
        headGuide.classList.add('status-correct');
        feedbackHTML += '<div class="status-indicator status-ready">✓ PERFECT! Hold still...</div>';

        // Show checkmark on head guide
        headGuideStatus.innerHTML = '<span class="status-icon-correct">✓</span>';

        // Turn the face guide frame green/solid
        if (faceOverlay) faceOverlay.classList.add('active');
    } else if (data.pose_pass && !data.quality_pass) {
        feedbackText.className = 'feedback-warning';
        videoContainer.classList.add('status-warning');
        headGuide.classList.add('status-adjusting');
        feedbackHTML += '<div class="status-indicator status-adjusting">✓ HEAD POSITION CORRECT!</div>';
        feedbackHTML += '<div class="status-indicator status-adjusting">⚠️ Now improve image quality:</div>';

        // Show partial checkmark on head guide
        headGuideStatus.innerHTML = '<span class="status-icon-correct">✓</span>';

        // Add specific quality issues - SHOW ALL OF THEM
        for (let i = 1; i < feedbackParts.length; i++) {
            feedbackHTML += `<div class="feedback-detail" style="font-size: 16px; font-weight: bold; background: rgba(255,193,7,0.3); padding: 8px; margin: 5px 0;">⚠️ ${feedbackParts[i]}</div>`;
        }
    } else if (!data.pose_pass && data.quality_pass) {
        feedbackText.className = 'feedback-adjusting';
        videoContainer.classList.add('status-adjusting');
        headGuide.classList.add('status-adjusting');
        feedbackHTML += '<div class="status-indicator status-adjusting">✓ IMAGE QUALITY GOOD!</div>';
        feedbackHTML += '<div class="status-indicator status-adjusting">↻ Adjust head position:</div>';

        // Show rotating arrow on head guide
        headGuideStatus.innerHTML = '<span class="status-icon-adjusting">↻</span>';

        // Add pose feedback - MAKE IT BIG AND CLEAR
        if (feedbackParts.length > 1) {
            feedbackHTML += `<div class="feedback-detail" style="font-size: 18px; font-weight: bold; background: rgba(255,193,7,0.5); padding: 10px; margin: 5px 0;">↻ ${feedbackParts[1]}</div>`;
        }
    } else {
        feedbackText.className = 'feedback-adjusting';
        videoContainer.classList.add('status-adjusting');
        headGuide.classList.add('status-adjusting');
        feedbackHTML += '<div class="status-indicator status-adjusting">📋 FOLLOW THESE STEPS:</div>';

        // Show waiting icon on head guide
        headGuideStatus.innerHTML = '<span class="status-icon-adjusting">⏳</span>';

        // Add ALL feedback messages - MAKE THEM VISIBLE
        for (let i = 1; i < feedbackParts.length; i++) {
            const message = feedbackParts[i];
            feedbackHTML += `<div class="feedback-detail" style="font-size: 16px; font-weight: bold; background: rgba(255,193,7,0.3); padding: 8px; margin: 5px 0; border-left: 4px solid #ffc107;">• ${message}</div>`;
        }
    }

    feedbackText.innerHTML = feedbackHTML;
}

// Validate frame
async function validateFrame() {
    if (isCountingDown || isProcessing) return;

    const currentPose = getCurrentPose();
    if (!currentPose) {
        console.log('No current pose - enrollment complete?');
        return;
    }

    console.log(`Validating frame for pose: ${currentPose}, index: ${currentPoseIndex}`);

    // Capture current frame
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/jpeg', 0.9);

    try {
        const response = await fetch('/enroll/api/validate_frame', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image: imageData,
                pose_type: currentPose
            })
        });

        const data = await response.json();

        if (data.success) {
            // === ENHANCED DEBUG LOGGING ===
            console.log('='.repeat(50));
            console.log('🔍 VALIDATION DEBUG - Frame Check Results');
            console.log('='.repeat(50));
            console.log('📊 Overall Status:');
            console.log('  ├─ Quality Pass:', data.quality_pass ? '✅' : '❌');
            console.log('  ├─ Pose Pass:', data.pose_pass ? '✅' : '❌');
            console.log('  └─ Ready to Capture:', data.ready_to_capture ? '✅ YES' : '❌ NO');
            console.log('');
            console.log('💬 Feedback:', data.feedback);
            console.log('');

            if (data.quality_results) {
                console.log('🎨 Quality Check Details:');
                const checks = data.quality_results.checks;
                for (const [check, result] of Object.entries(checks)) {
                    const icon = result.pass ? '✅' : '❌';
                    console.log(`  ${icon} ${check}:`, result.pass ? 'PASS' : 'FAIL', result.message || '');
                }
                console.log('');
            }

            if (data.pose) {
                console.log('🎯 Pose Details:');
                console.log('  ├─ Yaw (Left/Right):', data.pose.yaw?.toFixed(1) + '°');
                console.log('  ├─ Pitch (Up/Down):', data.pose.pitch?.toFixed(1) + '°');
                console.log('  └─ Roll (Tilt):', data.pose.roll?.toFixed(1) + '°');
                console.log('');
            }

            console.log('⏱️  Stability:', `${stabilityCounter}/${FRAMES_TO_HOLD} frames`);
            console.log('='.repeat(50));
            console.log('');

            // Update feedback with color coding
            updateFeedbackDisplay(data);

            // Stability check: require holding correct pose before countdown
            if (data.ready_to_capture) {
                // Increment the stability counter
                stabilityCounter++;
                console.log(`Stability: ${stabilityCounter}/${FRAMES_TO_HOLD}`);

                // Only start countdown if we've been stable for enough frames
                if (stabilityCounter >= FRAMES_TO_HOLD && !isCountingDown) {
                    startCountdown(imageData);
                    stabilityCounter = 0; // Reset for next pose
                }
            } else {
                // If user moves out of position, reset the counter immediately
                stabilityCounter = 0;
            }
        } else {
            feedbackText.textContent = 'Error: ' + data.error;
            feedbackText.className = 'feedback-error';
        }
    } catch (error) {
        console.error('Validation error:', error);
    }
}

// Start countdown
function startCountdown(imageData) {
    isCountingDown = true;
    let count = COUNTDOWN_SECONDS;

    feedbackText.style.display = 'none';
    countdownDiv.style.display = 'block';
    countdownDiv.textContent = count;

    countdownTimer = setInterval(() => {
        count--;
        if (count > 0) {
            countdownDiv.textContent = count;
        } else {
            clearInterval(countdownTimer);
            captureImage(imageData);
        }
    }, 1000);
}

// Capture image
function captureImage(imageData) {
    isCountingDown = false;
    isProcessing = true;

    // Flash effect
    flashOverlay.classList.add('active');
    setTimeout(() => flashOverlay.classList.remove('active'), 300);

    // Hide countdown, show feedback
    countdownDiv.style.display = 'none';
    feedbackText.style.display = 'block';
    feedbackText.textContent = '✓ Captured! Processing...';

    const currentPose = getCurrentPose();

    // Store captured image
    capturedImages[currentPose] = imageData;

    // Add to display
    addCapturedImageToDisplay(currentPose, imageData);

    // Move to next pose
    currentPoseIndex++;
    updateProgress();

    // Update head guide for next pose
    const nextPose = getCurrentPose();
    if (nextPose) {
        updateHeadGuide(nextPose);
    }

    // Check if complete
    if (currentPoseIndex === REQUIRED_POSES.length) {
        completeCaptureSession();
    } else {
        // Show success message and give user time to see it
        feedbackText.innerHTML = '<div class="pose-instruction">✅ CAPTURED!</div><div class="status-indicator status-ready">Great! Get ready for the next pose...</div>';

        setTimeout(() => {
            isProcessing = false;
            // Clear the success message and show next instruction
            const nextPose = getCurrentPose();
            feedbackText.innerHTML = '<div class="pose-instruction">📸 GET READY</div><div class="status-indicator status-adjusting">Prepare for next position...</div>';
        }, 2500); // Increased from 1.5s to 2.5s
    }
}

// Add captured image to display
function addCapturedImageToDisplay(poseType, imageData) {
    noCaptures.style.display = 'none';

    const poseLabels = {
        'front': 'Front',
        'left': 'Left',
        'right': 'Right',
        'up': 'Up',
        'down': 'Down'
    };

    const col = document.createElement('div');
    col.className = 'col-6';
    col.innerHTML = `
        <img src="${imageData}" class="captured-image" alt="${poseType}">
        <div class="pose-label text-success">
            <i class="bi bi-check-circle-fill"></i> ${poseLabels[poseType]}
        </div>
    `;

    capturedImagesGrid.appendChild(col);
}

// Complete capture session
function completeCaptureSession() {
    feedbackText.innerHTML = '<div class="pose-instruction">✅ COMPLETE!</div><div class="status-indicator status-ready">All images captured! Review and confirm enrollment.</div>';

    // Hide head guide
    const headGuide = document.getElementById('head-guide');
    if (headGuide) {
        headGuide.style.display = 'none';
    }

    // Stop validation
    if (validationTimer) {
        clearInterval(validationTimer);
    }

    // Show confirm button
    confirmEnrollmentBtn.style.display = 'block';

    showToast('All face images captured successfully!', 'success');
}

// Confirm enrollment
confirmEnrollmentBtn.addEventListener('click', async function() {
    if (Object.keys(capturedImages).length < REQUIRED_POSES.length) {
        showToast('Not all images captured', 'error');
        return;
    }

    this.disabled = true;
    this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enrolling...';

    try {
        const enrollmentPayload = {
            ...employeeData,
            images: capturedImages
        };

        const response = await fetch('/enroll/api/enroll', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(enrollmentPayload)
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');

            // Clear session storage
            sessionStorage.removeItem('enrollmentData');

            // Redirect to employees page
            setTimeout(() => {
                window.location.href = '/employees';
            }, 2000);
        } else {
            showToast('Enrollment failed: ' + data.error, 'error');
            this.disabled = false;
            this.innerHTML = '<i class="bi bi-check-circle"></i> Confirm Enrollment';
        }
    } catch (error) {
        console.error('Enrollment error:', error);
        showToast('Enrollment error: ' + error.message, 'error');
        this.disabled = false;
        this.innerHTML = '<i class="bi bi-check-circle"></i> Confirm Enrollment';
    }
});

// Cancel enrollment
document.getElementById('cancel-btn').addEventListener('click', function() {
    if (confirm('Are you sure you want to cancel enrollment? All captured images will be lost.')) {
        // Stop webcam
        if (webcamStream) {
            webcamStream.getTracks().forEach(track => track.stop());
        }

        // Clear session storage
        sessionStorage.removeItem('enrollmentData');

        // Redirect
        window.location.href = '/enroll';
    }
});

// Initialize on page load
(async function init() {
    // Load employee data
    if (!loadEmployeeData()) {
        return;
    }

    try {
        // Initialize webcam
        await initWebcam();

        feedbackText.innerHTML = '<div class="pose-instruction">📸 GET READY</div><div class="status-indicator status-adjusting">Position yourself in frame</div>';
        updateProgress();

        // Initialize head guide
        updateHeadGuide(getCurrentPose());

        // Start validation loop
        validationTimer = setInterval(validateFrame, VALIDATION_INTERVAL);

    } catch (error) {
        console.error('Initialization error:', error);
        showToast('Failed to initialize. Please check webcam permissions.', 'error');
    }
})();

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
    }
    if (validationTimer) {
        clearInterval(validationTimer);
    }
    if (countdownTimer) {
        clearInterval(countdownTimer);
    }
});
