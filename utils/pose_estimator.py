"""
Head Pose Estimation for Guided Enrollment
Estimates yaw, pitch, and roll from facial landmarks
"""
import cv2
import numpy as np
from typing import Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PoseEstimator:
    """Estimate head pose from facial landmarks"""

    def __init__(self):
        """Initialize pose estimator with 3D model points"""
        # 3D model points of facial landmarks (in mm)
        # Reference: Generic human face model
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ], dtype=np.float64)

    def estimate_pose(
        self,
        landmarks: np.ndarray,
        image_shape: Tuple[int, int]
    ) -> Optional[Dict[str, float]]:
        """
        Estimate head pose from facial landmarks

        Args:
            landmarks: 5 facial landmarks from InsightFace (left_eye, right_eye, nose, left_mouth, right_mouth)
            image_shape: Image shape (height, width)

        Returns:
            Dictionary with yaw, pitch, roll angles in degrees, or None if estimation fails
        """
        if landmarks is None or len(landmarks) < 5:
            logger.warning("Insufficient landmarks for pose estimation")
            return None

        height, width = image_shape[:2]

        # Convert InsightFace 5-point landmarks to 6 points needed for pose estimation
        # InsightFace format: [left_eye, right_eye, nose, left_mouth, right_mouth]
        # We need: [nose_tip, chin, left_eye_left, right_eye_right, left_mouth, right_mouth]

        # Extract points
        left_eye = landmarks[0]
        right_eye = landmarks[1]
        nose = landmarks[2]
        left_mouth = landmarks[3]
        right_mouth = landmarks[4]

        # Estimate chin position (below mouth)
        mouth_center = (left_mouth + right_mouth) / 2
        chin = mouth_center + np.array([0, (mouth_center[1] - nose[1]) * 0.5])

        # 2D image points
        image_points = np.array([
            nose,           # Nose tip
            chin,           # Chin
            left_eye,       # Left eye (approximation)
            right_eye,      # Right eye (approximation)
            left_mouth,     # Left mouth corner
            right_mouth     # Right mouth corner
        ], dtype=np.float64)

        # Camera internals (approximate)
        focal_length = width
        center = (width / 2, height / 2)
        camera_matrix = np.array(
            [[focal_length, 0, center[0]],
             [0, focal_length, center[1]],
             [0, 0, 1]], dtype=np.float64
        )

        # Assuming no lens distortion
        dist_coeffs = np.zeros((4, 1))

        # Solve PnP
        try:
            success, rotation_vec, translation_vec = cv2.solvePnP(
                self.model_points,
                image_points,
                camera_matrix,
                dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE
            )

            if not success:
                logger.warning("PnP solver failed")
                return None

            # Convert rotation vector to rotation matrix
            rotation_mat, _ = cv2.Rodrigues(rotation_vec)

            # Calculate Euler angles
            # Extract yaw, pitch, roll
            yaw = np.arctan2(rotation_mat[1, 0], rotation_mat[0, 0])
            pitch = np.arctan2(-rotation_mat[2, 0], np.sqrt(rotation_mat[2, 1]**2 + rotation_mat[2, 2]**2))
            roll = np.arctan2(rotation_mat[2, 1], rotation_mat[2, 2])

            # Convert to degrees
            yaw_deg = np.degrees(yaw)
            pitch_deg = np.degrees(pitch)
            roll_deg = np.degrees(roll)

            logger.debug(f"Pose: yaw={yaw_deg:.1f}°, pitch={pitch_deg:.1f}°, roll={roll_deg:.1f}°")

            return {
                'yaw': float(yaw_deg),
                'pitch': float(pitch_deg),
                'roll': float(roll_deg)
            }

        except Exception as e:
            logger.error(f"Pose estimation error: {e}")
            return None

    def check_pose_requirement(
        self,
        pose: Dict[str, float],
        pose_type: str,
        pose_requirements: Dict[str, Dict[str, Tuple[float, float]]]
    ) -> Tuple[bool, str]:
        """
        Check if current pose matches the required pose

        Args:
            pose: Current pose angles (yaw, pitch, roll)
            pose_type: Required pose type ('front', 'left', 'right', 'up', 'down')
            pose_requirements: Dictionary of pose requirements from config

        Returns:
            Tuple of (matches_requirement, feedback_message)
        """
        if pose is None:
            return False, "Could not detect head pose"

        if pose_type not in pose_requirements:
            logger.error(f"Unknown pose type: {pose_type}")
            return False, "Unknown pose requirement"

        requirements = pose_requirements[pose_type]
        yaw = pose['yaw']
        pitch = pose['pitch']

        # Check yaw range
        yaw_min, yaw_max = requirements['yaw']
        yaw_ok = yaw_min <= yaw <= yaw_max

        # Check pitch range
        pitch_min, pitch_max = requirements['pitch']
        pitch_ok = pitch_min <= pitch <= pitch_max

        # Generate feedback message
        if yaw_ok and pitch_ok:
            return True, f"Good! Hold still..."

        # Provide specific feedback
        feedback = []

        if not yaw_ok:
            if pose_type == 'left' and yaw > yaw_max:
                feedback.append("Turn MORE to the LEFT")
            elif pose_type == 'left' and yaw < yaw_min:
                feedback.append("Turn LESS to the left")
            elif pose_type == 'right' and yaw < yaw_min:
                feedback.append("Turn MORE to the RIGHT")
            elif pose_type == 'right' and yaw > yaw_max:
                feedback.append("Turn LESS to the right")
            elif pose_type == 'front':
                if yaw < 0:
                    feedback.append("Turn RIGHT to center")
                else:
                    feedback.append("Turn LEFT to center")

        if not pitch_ok:
            if pose_type == 'up' and pitch < pitch_min:
                feedback.append("Tilt head UP more")
            elif pose_type == 'up' and pitch > pitch_max:
                feedback.append("Tilt head down less")
            elif pose_type == 'down' and pitch > pitch_max:
                feedback.append("Tilt head DOWN more")
            elif pose_type == 'down' and pitch < pitch_min:
                feedback.append("Tilt head up less")
            elif pose_type == 'front':
                if pitch < 0:
                    feedback.append("Tilt head UP")
                else:
                    feedback.append("Tilt head DOWN")

        return False, " | ".join(feedback) if feedback else "Adjust head position"

    def get_pose_instruction(self, pose_type: str) -> str:
        """
        Get instruction text for a pose type

        Args:
            pose_type: Pose type ('front', 'left', 'right', 'up', 'down')

        Returns:
            Instruction text for the user
        """
        instructions = {
            'front': 'Look straight at the camera',
            'left': 'Turn your head to the LEFT',
            'right': 'Turn your head to the RIGHT',
            'up': 'Tilt your head UP (chin up)',
            'down': 'Tilt your head DOWN (chin down)'
        }
        return instructions.get(pose_type, 'Follow the instruction')
