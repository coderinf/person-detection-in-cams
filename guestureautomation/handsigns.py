import cv2
import mediapipe as mp
import serial
from pyfirmata import Arduino, util

# Open the webcam
cap = cv2.VideoCapture(0)

# Initialize MediaPipe

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Define finger coordinates and thumb coordinate
finger_coordinates = [(8, 6), (12, 10), (16, 14), (20, 18)]
thumb_coordinate = (4, 2)

# Establish serial connection with Arduino
board = Arduino('COM8')  # Replace 'COM8' with your Arduino's serial port
it = util.Iterator(board)
it.start()

# Define LED pins
red_pin = board.get_pin('d:8:o')
blue_pin = board.get_pin('d:9:o')
green_pin = board.get_pin('d:10:o')

while True:
    # Read frame from webcam
    ret, img = cap.read()
    if not ret:
        break

    # Convert the image to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Process the frame to detect hand landmarks
    results = hands.process(img_rgb)

    # Check if hand landmarks are detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks on the frame
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Extract hand points
            hand_points = []
            for idx, landmark in enumerate(hand_landmarks.landmark):
                h, w, _ = img.shape
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                hand_points.append((cx, cy))

            # Count fingers
            up_count = 0
            for coordinate in finger_coordinates:
                if hand_points[coordinate[0]][1] < hand_points[coordinate[1]][1]:
                    up_count += 1
            if hand_points[thumb_coordinate[0]][0] > hand_points[thumb_coordinate[1]][0]:
                up_count += 1

            # Send finger count to Arduino
            red_pin.write(0)
            blue_pin.write(0)
            green_pin.write(0)
            if 0 <= up_count <= 3:
                if up_count == 1:
                    red_pin.write(1)
                elif up_count == 2:
                    blue_pin.write(1)
                elif up_count == 3:
                    green_pin.write(1)
                elif up_count == 5:
                    while up_count == 5:
                        green_pin.write(1)
                        cv2.waitKey(200)
                        green_pin.write(0)
                        blue_pin.write(1)
                        cv2.waitKey(200)


    # Display the frame
    cv2.imshow('Hand Gesture Detection', img)

    # Exit loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()