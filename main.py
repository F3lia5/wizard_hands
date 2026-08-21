import cv2
import time
import HandTrackingModule as htm

cap = cv2.VideoCapture(0)
detector = htm.HandDetector(max_hands=2)
p_time = 0

while True:
    success, img = cap.read()
    if not success:
        continue

    img = cv2.flip(img, 1)

    # 1. Detect hands and draw landmarks
    img = detector.find_hands(img, draw=True)

    # 2. Extract coordinates
    lm_list = detector.find_position(img, hand_no=0)

    # If landmarks are found, print index finger tip position (ID 8)
    if len(lm_list) != 0:
        # Each element is [ID, X, Y]
        finger_tip = lm_list[8]
        cv2.circle(img, (finger_tip[1], finger_tip[2]), 12, (0, 255, 0), cv2.FILLED)
        print(f"Tracking Index Finger at: X={finger_tip[1]}, Y={finger_tip[2]}")

    # Calculate FPS
    c_time = time.time()
    fps = 1 / (c_time - p_time)
    p_time = c_time
    cv2.putText(img, f"FPS: {int(fps)}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Main Application Window", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
