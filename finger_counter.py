import cv2
import mediapipe as mp
import math
import time

# --- Setup ---
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

equation = ""
click_time = 0

# --- Calculator Button Class ---
class Button:
    def __init__(self, pos, text, size=[60, 60]):
        self.pos = pos
        self.text = text
        self.size = size

    def draw(self, img):
        x, y = self.pos
        w, h = self.size
        cv2.rectangle(img, (x, y), (x + w, y + h), (50, 50, 50), cv2.FILLED)
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 2)
        cv2.putText(img, self.text, (x + 20, y + 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 255), 2)

    def is_clicked(self, finger_pos):
        x, y = self.pos
        fx, fy = finger_pos
        return x < fx < x + self.size[0] and y < fy < y + self.size[1]


# --- Button Layout ---
buttons = []
keys = [['7', '8', '9', '/'],
        ['4', '5', '6', '*'],
        ['1', '2', '3', '-'],
        ['C', '0', '=', '+']]

start_x = 50
start_y = 100
for i in range(4):
    for j in range(4):
        x = start_x + j * 70
        y = start_y + i * 70
        buttons.append(Button([x, y], keys[i][j]))

# --- Main Loop ---
while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    # Draw calculator display box
    cv2.rectangle(img, (50, 30), (330, 80), (0, 0, 0), cv2.FILLED)
    cv2.putText(img, equation, (60, 65), cv2.FONT_HERSHEY_SIMPLEX,
                1.5, (0, 255, 0), 2)

    # Draw buttons
    for button in buttons:
        button.draw(img)

    # Detect hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((id, cx, cy))

            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if lm_list:
                # Tip of index and middle finger
                x1, y1 = lm_list[8][1], lm_list[8][2]
                x2, y2 = lm_list[12][1], lm_list[12][2]

                # Draw circles
                cv2.circle(img, (x1, y1), 10, (0, 255, 255), -1)
                cv2.circle(img, (x2, y2), 10, (0, 0, 255), -1)

                # Check distance
                distance = math.hypot(x2 - x1, y2 - y1)

                # If fingers are close = click
                if distance < 40 and (time.time() - click_time) > 1:
                    click_time = time.time()
                    for button in buttons:
                        if button.is_clicked((x1, y1)):
                            value = button.text
                            if value == "=":
                                try:
                                    equation = str(eval(equation))
                                except:
                                    equation = "Err"
                            elif value == "C":
                                equation = ""
                            else:
                                equation += value

    # Show window
    cv2.imshow("Gesture Calculator", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
