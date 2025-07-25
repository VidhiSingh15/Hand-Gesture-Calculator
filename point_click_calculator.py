import cv2
import mediapipe as mp
import numpy as np
import math

# Hand tracking setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width
cap.set(4, 720)   # Height

# Button class for calculator
class Button:
    def __init__(self, pos, text, size=(60, 60)):
        self.pos = pos
        self.size = size
        self.text = text

    def draw(self, img):
        x, y = self.pos
        w, h = self.size
        cv2.rectangle(img, self.pos, (x + w, y + h), (255, 255, 255), -1)
        cv2.rectangle(img, self.pos, (x + w, y + h), (0, 0, 0), 2)
        cv2.putText(img, self.text, (x + 15, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    def is_clicked(self, cursor):
        x, y = self.pos
        w, h = self.size
        return x < cursor[0] < x + w and y < cursor[1] < y + h

# Create mini calculator layout (bottom-right)
buttons = []
button_labels = [['7', '8', '9', '+'],
                 ['4', '5', '6', '-'],
                 ['1', '2', '3', '*'],
                 ['C', '0', '=', '/']]

start_x = 950
start_y = 400

for i in range(4):
    for j in range(4):
        x = start_x + j * 65
        y = start_y + i * 65
        buttons.append(Button((x, y), button_labels[i][j]))

equation = ""

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(handLms.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((cx, cy))

            # Draw hand landmarks
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            # Use tip of index finger
            if len(lm_list) > 8:
                x1, y1 = lm_list[8]  # Index tip
                x2, y2 = lm_list[12]  # Middle tip

                # Draw pointer circle
                cv2.circle(img, (x1, y1), 8, (255, 0, 255), -1)

                for button in buttons:
                    if button.is_clicked((x1, y1)):
                        # Check pinch (click simulation)
                        distance = math.hypot(x2 - x1, y2 - y1)
                        if distance < 40:
                            if button.text == "=":
                                try:
                                    equation = str(eval(equation))
                                except:
                                    equation = "Err"
                            elif button.text == "C":
                                equation = ""
                            else:
                                equation += button.text

    # Draw mini calculator background
    cv2.rectangle(img, (start_x - 10, start_y - 50), (start_x + 4 * 65 + 10, start_y + 4 * 65 + 10), (50, 50, 50), -1)
    cv2.rectangle(img, (start_x - 10, start_y - 50), (start_x + 4 * 65 + 10, start_y + 4 * 65 + 10), (0, 0, 0), 2)

    # Display current equation
    cv2.putText(img, equation, (start_x, start_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

    # Draw all buttons
    for button in buttons:
        button.draw(img)

    cv2.imshow("Gesture Calculator", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
