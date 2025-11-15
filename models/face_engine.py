"""
Face Recognition Engine using InsightFace
Optimized for West African faces using buffalo_l model
"""
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class FaceRecognitionEngine:
    """Face recognition engine using InsightFace"""

    def __init__(self, model_name: str = 'buffalo_l', detection_threshold: float = 0.5):
        """
        Initialize face recognition engine

        Args:
            model_name: InsightFace model name (buffalo_l recommended for diverse faces)
            detection_threshold: Face detection confidence threshold
        """
        self.model_name = model_name
        self.detection_threshold = detection_threshold
        self.app = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize InsightFace model"""
        try:
            logger.info(f"Initializing InsightFace model: {self.model_name}")
            self.app = FaceAnalysis(name=self.model_name, providers=['CPUExecutionProvider'])
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            logger.info("Face recognition model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize face recognition model: {e}")
            raise

    def detect_faces(self, image: np.ndarray) -> List:
        """
        Detect faces in an image

        Args:
            image: Input image as numpy array (BGR format)

        Returns:
            List of detected faces with embeddings and landmarks
        """
        if image is None or image.size == 0:
            logger.warning("Empty image provided for face detection")
            return []

        try:
            faces = self.app.get(image)
            # Filter by detection threshold
            faces = [face for face in faces if face.det_score >= self.detection_threshold]
            logger.debug(f"Detected {len(faces)} faces")
            return faces
        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return []

    def get_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face embedding from image

        Args:
            image: Input image as numpy array (BGR format)

        Returns:
            512-dimensional face embedding or None if no face detected
        """
        faces = self.detect_faces(image)

        if len(faces) == 0:
            logger.warning("No face detected in image")
            return None

        if len(faces) > 1:
            logger.warning(f"Multiple faces detected ({len(faces)}), using largest face")
            # Use the face with largest bounding box
            faces = sorted(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]), reverse=True)

        # Get embedding (already normalized by InsightFace)
        embedding = faces[0].embedding
        return embedding

    def get_face_with_landmarks(self, image: np.ndarray) -> Optional[Dict]:
        """
        Get face embedding along with landmarks and bounding box

        Args:
            image: Input image as numpy array (BGR format)

        Returns:
            Dictionary with embedding, landmarks, bbox, and detection score
        """
        faces = self.detect_faces(image)

        if len(faces) == 0:
            return None

        if len(faces) > 1:
            # Use the face with largest bounding box
            faces = sorted(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]), reverse=True)

        face = faces[0]
        return {
            'embedding': face.embedding,
            'landmarks': face.kps,  # 5 keypoints: eyes, nose, mouth corners
            'bbox': face.bbox,
            'det_score': face.det_score,
            'pose': face.pose if hasattr(face, 'pose') else None
        }

    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First face embedding
            embedding2: Second face embedding

        Returns:
            Cosine similarity score (0 to 1, higher is more similar)
        """
        # Ensure embeddings are 2D for sklearn
        emb1 = embedding1.reshape(1, -1)
        emb2 = embedding2.reshape(1, -1)

        # Calculate cosine similarity
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)

    def recognize_face(
        self,
        image: np.ndarray,
        known_embeddings: List[np.ndarray],
        known_ids: List[str],
        threshold: float = 0.30
    ) -> Tuple[Optional[str], float]:
        """
        Recognize a face by comparing with known embeddings

        Args:
            image: Input image to recognize
            known_embeddings: List of known face embeddings
            known_ids: List of employee IDs corresponding to embeddings
            threshold: Similarity threshold for recognition (0.25-0.30 for West African faces)

        Returns:
            Tuple of (employee_id, confidence) or (None, 0.0) if not recognized
        """
        if not known_embeddings or not known_ids:
            logger.warning("No known embeddings provided for recognition")
            return None, 0.0

        # Get embedding from input image
        query_embedding = self.get_embedding(image)
        if query_embedding is None:
            logger.warning("No face detected in query image")
            return None, 0.0

        # Calculate similarities with all known faces
        similarities = []
        for known_emb in known_embeddings:
            sim = self.calculate_similarity(query_embedding, known_emb)
            similarities.append(sim)

        # Find best match
        max_similarity = max(similarities)
        best_match_idx = similarities.index(max_similarity)

        logger.info(f"Best match similarity: {max_similarity:.3f}, Threshold: {threshold}")

        if max_similarity >= threshold:
            employee_id = known_ids[best_match_idx]
            logger.info(f"Face recognized as {employee_id} with confidence {max_similarity:.3f}")
            return employee_id, max_similarity
        else:
            logger.info(f"No match found (max similarity: {max_similarity:.3f})")
            return None, max_similarity

    def get_average_embedding(self, embeddings: List[np.ndarray]) -> np.ndarray:
        """
        Calculate average embedding from multiple embeddings

        Args:
            embeddings: List of face embeddings

        Returns:
            Average normalized embedding
        """
        if not embeddings:
            raise ValueError("No embeddings provided")

        # Stack and average
        avg_embedding = np.mean(embeddings, axis=0)

        # Normalize
        norm = np.linalg.norm(avg_embedding)
        if norm > 0:
            avg_embedding = avg_embedding / norm

        return avg_embedding
