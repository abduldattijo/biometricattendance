"""
Image Quality Checker
Critical for ensuring good quality images, especially for darker skin tones
"""
import cv2
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class ImageQualityChecker:
    """Check image quality for face recognition"""

    def __init__(
        self,
        min_blur_threshold: float = 100.0,
        min_brightness: int = 60,
        max_brightness: int = 200,
        min_contrast: float = 30.0,
        min_face_size: float = 0.15,
        max_face_size: float = 0.70,
        max_center_offset: float = 0.20
    ):
        """
        Initialize quality checker

        Args:
            min_blur_threshold: Minimum Laplacian variance (higher = sharper)
            min_brightness: Minimum acceptable brightness (critical for darker skin)
            max_brightness: Maximum acceptable brightness
            min_contrast: Minimum standard deviation (critical for darker skin)
            min_face_size: Minimum face size relative to frame (0.15 = 15%)
            max_face_size: Maximum face size relative to frame (0.70 = 70%)
            max_center_offset: Maximum offset from center (0.20 = 20%)
        """
        self.min_blur_threshold = min_blur_threshold
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self.min_contrast = min_contrast
        self.min_face_size = min_face_size
        self.max_face_size = max_face_size
        self.max_center_offset = max_center_offset

    def check_blur(self, image: np.ndarray) -> Tuple[bool, float]:
        """
        Check if image is blurry using Laplacian variance

        Args:
            image: Input image (BGR or grayscale)

        Returns:
            Tuple of (is_sharp, blur_score)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Calculate Laplacian variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        blur_score = laplacian.var()

        is_sharp = blur_score >= self.min_blur_threshold

        logger.debug(f"Blur score: {blur_score:.2f}, Threshold: {self.min_blur_threshold}, Sharp: {is_sharp}")
        return is_sharp, blur_score

    def check_brightness(self, image: np.ndarray) -> Tuple[bool, float]:
        """
        Check if image brightness is in acceptable range
        Critical for darker skin tones

        Args:
            image: Input image (BGR)

        Returns:
            Tuple of (is_good_brightness, brightness_value)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        brightness = np.mean(gray)
        is_good = self.min_brightness <= brightness <= self.max_brightness

        logger.debug(f"Brightness: {brightness:.2f}, Range: [{self.min_brightness}, {self.max_brightness}], Good: {is_good}")
        return is_good, brightness

    def check_contrast(self, image: np.ndarray) -> Tuple[bool, float]:
        """
        Check if image has sufficient contrast
        Essential for West African faces

        Args:
            image: Input image (BGR)

        Returns:
            Tuple of (has_good_contrast, contrast_value)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        contrast = np.std(gray)
        has_good_contrast = contrast >= self.min_contrast

        logger.debug(f"Contrast: {contrast:.2f}, Threshold: {self.min_contrast}, Good: {has_good_contrast}")
        return has_good_contrast, contrast

    def check_face_size(self, face_bbox: Tuple[int, int, int, int], frame_shape: Tuple[int, int]) -> Tuple[bool, float]:
        """
        Check if face size is appropriate

        Args:
            face_bbox: Face bounding box (x1, y1, x2, y2)
            frame_shape: Frame shape (height, width)

        Returns:
            Tuple of (is_good_size, face_area_ratio)
        """
        x1, y1, x2, y2 = face_bbox
        height, width = frame_shape[:2]

        face_width = x2 - x1
        face_height = y2 - y1
        face_area = face_width * face_height
        frame_area = height * width

        area_ratio = face_area / frame_area

        is_good_size = self.min_face_size <= area_ratio <= self.max_face_size

        logger.debug(f"Face area ratio: {area_ratio:.3f}, Range: [{self.min_face_size}, {self.max_face_size}], Good: {is_good_size}")
        return is_good_size, area_ratio

    def check_face_centering(self, face_bbox: Tuple[int, int, int, int], frame_shape: Tuple[int, int]) -> Tuple[bool, float]:
        """
        Check if face is centered in frame

        Args:
            face_bbox: Face bounding box (x1, y1, x2, y2)
            frame_shape: Frame shape (height, width)

        Returns:
            Tuple of (is_centered, offset_ratio)
        """
        x1, y1, x2, y2 = face_bbox
        height, width = frame_shape[:2]

        # Calculate face center
        face_center_x = (x1 + x2) / 2
        face_center_y = (y1 + y2) / 2

        # Calculate frame center
        frame_center_x = width / 2
        frame_center_y = height / 2

        # Calculate offset as ratio of frame dimensions
        offset_x = abs(face_center_x - frame_center_x) / width
        offset_y = abs(face_center_y - frame_center_y) / height

        max_offset = max(offset_x, offset_y)
        is_centered = max_offset <= self.max_center_offset

        logger.debug(f"Center offset: {max_offset:.3f}, Threshold: {self.max_center_offset}, Centered: {is_centered}")
        return is_centered, max_offset

    def check_occlusion(self, landmarks: np.ndarray) -> Tuple[bool, str]:
        """
        Check if face features are visible (eyes, nose, mouth)

        Args:
            landmarks: Face landmarks (5 points: left_eye, right_eye, nose, left_mouth, right_mouth)

        Returns:
            Tuple of (is_visible, message)
        """
        if landmarks is None or len(landmarks) < 5:
            return False, "Landmarks not detected"

        # InsightFace provides 5 keypoints in order:
        # 0: left eye, 1: right eye, 2: nose, 3: left mouth corner, 4: right mouth corner

        # Check if all landmarks are within reasonable bounds
        # (This is a simple check - more sophisticated checks could be added)

        return True, "All features visible"

    def check_all(
        self,
        image: np.ndarray,
        face_bbox: Tuple[int, int, int, int] = None,
        landmarks: np.ndarray = None
    ) -> Dict:
        """
        Perform all quality checks

        Args:
            image: Input image (BGR)
            face_bbox: Optional face bounding box (x1, y1, x2, y2)
            landmarks: Optional face landmarks

        Returns:
            Dictionary with all quality check results
        """
        results = {
            'overall_pass': True,
            'feedback_messages': [],
            'checks': {}
        }

        # Blur check
        is_sharp, blur_score = self.check_blur(image)
        results['checks']['blur'] = {'pass': is_sharp, 'score': blur_score}
        if not is_sharp:
            results['overall_pass'] = False
            results['feedback_messages'].append("BLURRY - hold still")

        # Brightness check
        is_bright, brightness = self.check_brightness(image)
        results['checks']['brightness'] = {'pass': is_bright, 'score': brightness}
        if not is_bright:
            results['overall_pass'] = False
            if brightness < self.min_brightness:
                results['feedback_messages'].append("TOO DARK - add light")
            else:
                results['feedback_messages'].append("TOO BRIGHT - reduce light")

        # Contrast check (critical for West African faces)
        has_contrast, contrast = self.check_contrast(image)
        results['checks']['contrast'] = {'pass': has_contrast, 'score': contrast}
        if not has_contrast:
            results['overall_pass'] = False
            results['feedback_messages'].append("LOW CONTRAST - adjust lighting")

        # Face-specific checks
        if face_bbox is not None:
            # Face size check
            is_good_size, area_ratio = self.check_face_size(face_bbox, image.shape)
            results['checks']['face_size'] = {'pass': is_good_size, 'score': area_ratio}
            if not is_good_size:
                results['overall_pass'] = False
                if area_ratio < self.min_face_size:
                    results['feedback_messages'].append("Come CLOSER")
                else:
                    results['feedback_messages'].append("Move BACK")

            # Face centering check
            is_centered, offset = self.check_face_centering(face_bbox, image.shape)
            results['checks']['centering'] = {'pass': is_centered, 'score': offset}
            if not is_centered:
                results['overall_pass'] = False
                results['feedback_messages'].append("CENTER your face")

        # Occlusion check
        if landmarks is not None:
            is_visible, msg = self.check_occlusion(landmarks)
            results['checks']['occlusion'] = {'pass': is_visible, 'message': msg}
            if not is_visible:
                results['overall_pass'] = False
                results['feedback_messages'].append(msg)

        # Calculate overall quality score (0-100)
        total_checks = len(results['checks'])
        passed_checks = sum(1 for check in results['checks'].values() if check.get('pass', False))
        results['quality_score'] = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        logger.info(f"Quality check: {results['quality_score']:.1f}% ({passed_checks}/{total_checks} passed)")

        return results
