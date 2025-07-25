import cv2
import mediapipe as mp
import time

# Setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)
expression = ""
last_action_time = 0
prev_count = -1

# Define button UI structure
button_map = {
    1: "1",
    2: "2",
    3: "3",
    4: "+",
    5: "-",
    99: "=",   # Two-finger V gesture (custom)
    0: "C"     # Fist to Clear
}

def count_fingers(lm_list):
    fingers = []
    if lm_list[4][1] < lm_list[3][1]:  # Thumb
        fingers.append(1)
    else:
        fingers.append(0)
    for tip in [8, 12, 16, 20]:
        if lm_list[tip][2] < lm_list[tip - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

def get_action_from_fingers(fingers):
    total = sum(fingers)
    if total == 2 and fingers[1:3] == [1, 1]:
        return 99  # "="
    return total

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)
    h, w, _ = img.shape

    # Draw calculator box
    cv2.rectangle(img, (20, 20), (620, 100), (0, 0, 0), -1)
    cv2.putText(img, expression, (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            lm_list = [(id, int(lm.x * w), int(lm.y * h)) for id, lm in enumerate(handLms.landmark)]
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            fingers = count_fingers(lm_list)
            action = get_action_from_fingers(fingers)
            now = time.time()

            if action != prev_count and now - last_action_time > 1:
                if action in button_map:
                    symbol = button_map[action]
                    if symbol == "=":
                        try:
                            expression = str(eval(expression))
                        except:
                            expression = "Error"
                    elif symbol == "C":
                        expression = ""
                    else:
                        expression += symbol

                    last_action_time = now
                    prev_count = action

    cv2.imshow("Gesture Calculator", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
