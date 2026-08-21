import cv2
import time
import HandTrackingModule as htm


cap = cv2.VideoCapture(0)
detector = htm.HandDetector(max_hands=2)
p_time = 0

while True:
    success, img = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue


    img = cv2.flip(img, 1)


    img = detector.find_hands(img, draw=True)


    lm_list = detector.find_position(img, draw=False)

    if len(lm_list) != 0:

        thumb_x, thumb_y = lm_list[4][1], lm_list[4][2]
        index_x, index_y = lm_list[8][1], lm_list[8][2]


        cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), (0, 255, 0), 3)

    # Calculate and display FPS
    c_time = time.time()
    fps = 1 / (c_time - p_time)
    p_time = c_time
    cv2.putText(img, f"FPS: {int(fps)}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display execution window
    cv2.imshow("Main Application Window", img)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
