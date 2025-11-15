"""
Guided Enrollment System
Coordinates multi-pose capture with quality checks and pose validation
"""
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from .quality_checker import ImageQualityChecker
from .pose_estimator import PoseEstimator
import logging

logger = logging.getLogger(__name__)


class GuidedEnrollment:
    """Manage guided enrollment process with multi-pose capture"""

    def __init__(
        self,
        required_poses: List[str],
        pose_requirements: Dict,
        quality_checker: ImageQualityChecker,
        pose_estimator: PoseEstimator
    ):
        """
        Initialize guided enrollment

        Args:
            required_poses: List of required poses (e.g., ['front', 'left', 'right', 'up', 'down'])
            pose_requirements: Pose angle requirements from config
            quality_checker: ImageQualityChecker instance
            pose_estimator: PoseEstimator instance
        """
        self.required_poses = required_poses
        self.pose_requirements = pose_requirements
        self.quality_checker = quality_checker
        self.pose_estimator = pose_estimator

        self.current_pose_index = 0
        self.captured_images = {}
        self.capture_metadata = {}

    def reset(self):
        """Reset enrollment session"""
        self.current_pose_index = 0
        self.captured_images = {}
        self.capture_metadata = {}
        logger.info("Enrollment session reset")

    def get_current_pose(self) -> Optional[str]:
        """Get the current pose requirement"""
        if self.current_pose_index < len(self.required_poses):
            return self.required_poses[self.current_pose_index]
        return None

    def get_progress(self) -> Dict:
        """Get enrollment progress"""
        return {
            'current_pose_index': self.current_pose_index,
            'total_poses': len(self.required_poses),
            'current_pose': self.get_current_pose(),
            'completed_poses': list(self.captured_images.keys()),
            'is_complete': self.is_complete()
        }

    def is_complete(self) -> bool:
        """Check if enrollment is complete"""
        return len(self.captured_images) == len(self.required_poses)

    def validate_frame(
        self,
        image: np.ndarray,
        face_bbox: Tuple[int, int, int, int],
        landmarks: np.ndarray
    ) -> Dict:
        """
        Validate a frame for the current pose requirement

        Args:
            image: Input image (BGR)
            face_bbox: Face bounding box (x1, y1, x2, y2)
            landmarks: Facial landmarks

        Returns:
            Dictionary with validation results and feedback
        """
        current_pose = self.get_current_pose()
        if current_pose is None:
            return {
                'ready_to_capture': False,
                'feedback': 'Enrollment complete',
                'quality_pass': False,
                'pose_pass': False
            }

        # Perform quality checks
        quality_results = self.quality_checker.check_all(image, face_bbox, landmarks)

        # Estimate pose
        pose = self.pose_estimator.estimate_pose(landmarks, image.shape)

        # Check pose requirement
        pose_pass = False
        pose_feedback = ""

        if pose is not None:
            pose_pass, pose_feedback = self.pose_estimator.check_pose_requirement(
                pose,
                current_pose,
                self.pose_requirements
            )
        else:
            pose_feedback = "Could not detect head pose"

        # Combine feedback
        feedback_messages = []

        # Pose instruction
        pose_instruction = self.pose_estimator.get_pose_instruction(current_pose)
        feedback_messages.append(f"📸 {pose_instruction}")

        # Quality feedback
        if not quality_results['overall_pass']:
            feedback_messages.extend(quality_results['feedback_messages'])
        elif not pose_pass:
            feedback_messages.append(pose_feedback)
        else:
            feedback_messages.append("✓ Perfect! Hold still...")

        # Determine if ready to capture
        ready_to_capture = quality_results['overall_pass'] and pose_pass

        return {
            'ready_to_capture': ready_to_capture,
            'feedback': ' | '.join(feedback_messages),
            'quality_pass': quality_results['overall_pass'],
            'pose_pass': pose_pass,
            'quality_results': quality_results,
            'pose': pose,
            'quality_score': quality_results['quality_score']
        }

    def capture_current_pose(
        self,
        image: np.ndarray,
        validation_result: Dict
    ) -> bool:
        """
        Capture the current pose if validation passes

        Args:
            image: Input image to capture
            validation_result: Result from validate_frame

        Returns:
            True if capture was successful
        """
        if not validation_result['ready_to_capture']:
            logger.warning("Attempted to capture when not ready")
            return False

        current_pose = self.get_current_pose()
        if current_pose is None:
            logger.warning("No current pose to capture")
            return False

        # Store image and metadata
        self.captured_images[current_pose] = image.copy()
        self.capture_metadata[current_pose] = {
            'quality_score': validation_result['quality_score'],
            'pose': validation_result['pose'],
            'quality_results': validation_result['quality_results']
        }

        logger.info(f"Captured pose: {current_pose} ({self.current_pose_index + 1}/{len(self.required_poses)})")

        # Move to next pose
        self.current_pose_index += 1

        return True

    def get_captured_images(self) -> Dict[str, np.ndarray]:
        """Get all captured images"""
        return self.captured_images.copy()

    def get_capture_metadata(self) -> Dict:
        """Get metadata for all captures"""
        return self.capture_metadata.copy()

    def draw_feedback(
        self,
        image: np.ndarray,
        validation_result: Dict,
        face_bbox: Tuple[int, int, int, int] = None
    ) -> np.ndarray:
        """
        Draw visual feedback on image

        Args:
            image: Input image
            validation_result: Validation result
            face_bbox: Optional face bounding box

        Returns:
            Image with feedback overlay
        """
        output = image.copy()
        height, width = output.shape[:2]

        # Draw bounding box if provided
        if face_bbox is not None:
            x1, y1, x2, y2 = [int(v) for v in face_bbox]

            # Color based on readiness: green if ready, red if not
            if validation_result['ready_to_capture']:
                color = (0, 255, 0)  # Green
                thickness = 3
            else:
                color = (0, 0, 255)  # Red
                thickness = 2

            cv2.rectangle(output, (x1, y1), (x2, y2), color, thickness)

        # Draw feedback text
        feedback_text = validation_result['feedback']

        # Background for text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        font_thickness = 2

        # Split feedback into multiple lines if too long
        max_width = width - 40
        words = feedback_text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            (text_width, text_height), _ = cv2.getTextSize(test_line, font, font_scale, font_thickness)

            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Draw lines
        y_offset = 30
        for line in lines:
            (text_width, text_height), baseline = cv2.getTextSize(line, font, font_scale, font_thickness)

            # Background rectangle
            cv2.rectangle(
                output,
                (10, y_offset - text_height - 5),
                (10 + text_width + 10, y_offset + baseline + 5),
                (0, 0, 0),
                -1
            )

            # Text
            cv2.putText(
                output,
                line,
                (15, y_offset),
                font,
                font_scale,
                (255, 255, 255),
                font_thickness
            )

            y_offset += text_height + baseline + 10

        # Draw progress bar
        progress = self.current_pose_index / len(self.required_poses)
        bar_width = width - 40
        bar_height = 20
        bar_x = 20
        bar_y = height - 40

        # Background
        cv2.rectangle(output, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)

        # Progress
        progress_width = int(bar_width * progress)
        cv2.rectangle(output, (bar_x, bar_y), (bar_x + progress_width, bar_y + bar_height), (0, 255, 0), -1)

        # Progress text
        progress_text = f"{self.current_pose_index}/{len(self.required_poses)}"
        (text_width, text_height), _ = cv2.getTextSize(progress_text, font, 0.5, 1)
        text_x = bar_x + (bar_width - text_width) // 2
        text_y = bar_y + (bar_height + text_height) // 2
        cv2.putText(output, progress_text, (text_x, text_y), font, 0.5, (255, 255, 255), 1)

        return output
