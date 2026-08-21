import cv2
import mediapipe as mp
import numpy as np

class HandDetector:
    def __init__(self, model_path="hand_landmarker.task", max_hands=2, min_detection_confidence=0.5):
        """Initializes the modern MediaPipe Tasks Hand Landmarker."""
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        # Configure the hand landmarker for video stream mode
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=min_detection_confidence
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self.timestamp = 0
        self.latest_result = None

    def find_hands(self, img, draw=True):
        """Processes a frame and caches the tracking results."""
        self.timestamp += 1
        # Convert BGR frame to MediaPipe Image format
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)

        # Send frame to the landmarker with an increasing timestamp
        self.latest_result = self.landmarker.detect_for_video(mp_image, self.timestamp)

        # Draw connecting skeleton lines manually if landmarks exist
        if draw and self.latest_result and self.latest_result.hand_landmarks:
            h, w, _ = img.shape
            for hand_landmarks in self.latest_result.hand_landmarks:
                for lm in hand_landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return img

    def find_position(self, img, hand_no=0):
        """Extracts coordinate list of all 21 landmarks for a specific hand."""
        lm_list = []
        if self.latest_result and self.latest_result.hand_landmarks:
            if hand_no < len(self.latest_result.hand_landmarks):
                my_hand = self.latest_result.hand_landmarks[hand_no]
                h, w, _ = img.shape
                for idx, lm in enumerate(my_hand):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([idx, cx, cy])
        return lm_list
