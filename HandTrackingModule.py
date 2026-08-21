import cv2
import mediapipe as mp
import time

class HandDetector:
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_con=0.5):
        """
        Initializes the MediaPipe Hands model configurations.
        """
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        # Initialize MediaPipe Hands pipeline
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        """
        Processes the image to detect hands and optionally draws landmarks and connections.
        """
        # Convert the image from BGR (OpenCV standard) to RGB (MediaPipe requirement)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        # Draw hand skeletons if hands are detected
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_position(self, img, hand_no=0, draw=True):
        """
        Extracts the pixel coordinate list of all 21 hand landmarks for a specific hand.
        """
        lm_list = []
        if self.results.multi_hand_landmarks:
            # Select the specified hand (default: first hand detected)
            my_hand = self.results.multi_hand_landmarks[hand_no]

            for id, lm in enumerate(my_hand.landmark):
                # Convert normalized coordinates (0.0 to 1.0) to pixel positions
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])

                # Optional: Highlight the tip of the thumb/fingers with a larger circle
                if draw and id == 8:  # 8 is the index finger tip
                    cv2.circle(img, (cx, cy), 12, (255, 0, 255), cv2.FILLED)

        return lm_list

# Fallback script to test the module independently
def main():
    p_time = 0
    cap = cv2.VideoCapture(0) # Open default webcam
    detector = HandDetector()

    while True:
        success, img = cap.read()
        if not success:
            break

        img = detector.find_hands(img)
        lm_list = detector.find_position(img)

        if len(lm_list) != 0:
            print(f"Index Finger Tip Position: {lm_list[8]}") # Prints ID and X, Y coordinates

        # Calculate Frames Per Second (FPS)
        c_time = time.time()
        fps = 1 / (c_time - p_time)
        p_time = c_time
        cv2.putText(img, f"FPS: {int(fps)}", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        cv2.imshow("Hand Tracking Module", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
