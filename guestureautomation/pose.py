import cv2
import mediapipe as mp
import math
from pyfirmata import Arduino, SERVO

# Connect to Arduino
board = Arduino('com10')  # Replace '/dev/ttyUSB0' with the serial port of your Arduino

# Define servo pins
servo_pin_x = 8  # Example pin for horizontal servo
servo_pin_y = 10  # Example pin for vertical servo

# Configure servo pins
board.digital[servo_pin_x].mode = SERVO
board.digital[servo_pin_y].mode = SERVO

# Initialize PWM signal for servo motors
pwm_x = board.get_pin('d:{}:s'.format(servo_pin_x))
pwm_y = board.get_pin('d:{}:s'.format(servo_pin_y))

# Load Mediapipe solutions
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

# Initialize Holistic model
holistic = mp_holistic.Holistic(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Initialize video capture
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the image to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the image to detect landmarks
    results = holistic.process(frame_rgb)

    # Draw landmarks on the image
    if results.pose_landmarks:
        # Get landmarks for right shoulder, elbow, and wrist
        right_shoulder = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_SHOULDER]
        right_elbow = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_ELBOW]
        right_wrist = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_WRIST]

        # Convert landmarks to pixel coordinates
        h, w, _ = frame.shape
        right_shoulder_px = int(right_shoulder.x * w), int(right_shoulder.y * h)
        right_elbow_px = int(right_elbow.x * w), int(right_elbow.y * h)
        right_wrist_px = int(right_wrist.x * w), int(right_wrist.y * h)

        # Draw points for right shoulder, elbow, and wrist
        cv2.circle(frame, right_shoulder_px, 5, (255, 0, 0), -1)
        cv2.circle(frame, right_elbow_px, 5, (0, 255, 0), -1)
        cv2.circle(frame, right_wrist_px, 5, (0, 0, 255), -1)

        # Draw line between right shoulder and right elbow
        cv2.line(frame, right_shoulder_px, right_elbow_px, (0, 255, 0), 2)

        # Calculate angle between right shoulder, elbow, and wrist
        shoulder_elbow_vec = (right_shoulder_px[0] - right_elbow_px[0], right_shoulder_px[1] - right_elbow_px[1])
        elbow_wrist_vec = (right_elbow_px[0] - right_wrist_px[0], right_elbow_px[1] - right_wrist_px[1])

        # Calculate angle using dot product formula
        dot_product = shoulder_elbow_vec[0] * elbow_wrist_vec[0] + shoulder_elbow_vec[1] * elbow_wrist_vec[1]
        shoulder_elbow_length = math.sqrt(shoulder_elbow_vec[0] ** 2 + shoulder_elbow_vec[1] ** 2)
        elbow_wrist_length = math.sqrt(elbow_wrist_vec[0] ** 2 + elbow_wrist_vec[1] ** 2)

        if shoulder_elbow_length != 0 and elbow_wrist_length != 0:
            angle_radians = math.acos(dot_product / (shoulder_elbow_length * elbow_wrist_length))
            angle_degrees = math.degrees(angle_radians)
            cv2.putText(frame, f'Angle: {angle_degrees:.2f} degrees', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Move servo motors based on angle
            pwm_x.write(angle_degrees)
            pwm_y.write(angle_degrees)

    # Display the resulting image
    cv2.imshow('Pose Detection and Servo Control', frame)

    # Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()