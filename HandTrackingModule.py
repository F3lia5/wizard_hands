import cv2
import mediapipe as mp
import numpy as np

class HandDetector:
    def __init__(self, model_path="hand_landmarker.task", max_hands=1, min_detection_confidence=0.5):
        """RAM dostu ve optimize edilmiş MediaPipe Hands başlatıcısı."""
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        # max_hands değerini 1 yaparak ve ayarları hafifleterek RAM kullanımını düşürüyoruz
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self.timestamp = 0
        self.latest_result = None

    def find_hands(self, img, draw=True):
        """Kameradan gelen görüntüyü küçülterek RAM yükünü azaltır ve işler."""
        self.timestamp += 1

        # Çözünürlüğü yarı yarıya düşürerek işlemcinin ve RAM'in rahatlamasını sağlıyoruz
        # (Yüksek çözünürlük yapay zekayı kilitler)
        img_small = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_small)

        # Modeli çalıştır
        self.latest_result = self.landmarker.detect_for_video(mp_image, self.timestamp)

        # Çizimleri orijinal büyük resim üzerine yapıyoruz
        if draw and self.latest_result and self.latest_result.hand_landmarks:
            h, w, _ = img.shape
            for hand_landmarks in self.latest_result.hand_landmarks:
                for lm in hand_landmarks:
                    # Küçültülen koordinatları ana ekrana göre geri ölçeklendiriyoruz
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return img

    def find_position(self, img, hand_no=0):
        """İşaret noktalarının piksel koordinatlarını döndürür."""
        lm_list = []
        if self.latest_result and self.latest_result.hand_landmarks:
            if hand_no < len(self.latest_result.hand_landmarks):
                my_hand = self.latest_result.hand_landmarks[hand_no]
                h, w, _ = img.shape
                for idx, lm in enumerate(my_hand):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([idx, cx, cy])
        return lm_list
