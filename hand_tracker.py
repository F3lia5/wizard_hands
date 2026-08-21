"""
MediaPipe Tasks HandLandmarker etrafında ince bir sarmalayıcı.

Sadece tek amaç var: verilen bir kamera frame'inden işaret parmağı
ucunun piksel koordinatını döndürmek. Gesture recognition, çoklu el,
el pozu sınıflandırma gibi hiçbir ekstra özellik içermez.
"""

import os
import time

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

INDEX_FINGER_TIP = 8
MODEL_FILENAME = "hand_landmarker.task"


class HandTracker:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), MODEL_FILENAME)

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model dosyası bulunamadı: {model_path}\n"
                "README.md içindeki model indirme komutunu çalıştırın."
            )

        base_options = mp_python.BaseOptions(model_asset_path=model_path)
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            running_mode=mp_vision.RunningMode.VIDEO,
        )
        self._detector = mp_vision.HandLandmarker.create_from_options(options)
        self._start_time = time.monotonic()

    def get_index_fingertip(self, bgr_frame):
        """BGR frame alır, işaret parmağı ucunun (x, y) piksel koordinatını
        döndürür. El algılanmadıysa None döner."""
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((time.monotonic() - self._start_time) * 1000)

        result = self._detector.detect_for_video(mp_image, timestamp_ms)

        if not result.hand_landmarks:
            return None

        tip = result.hand_landmarks[0][INDEX_FINGER_TIP]
        h, w = bgr_frame.shape[:2]
        return (int(tip.x * w), int(tip.y * h))

    def close(self):
        self._detector.close()
