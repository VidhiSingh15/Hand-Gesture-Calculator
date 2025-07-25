# hand_detector.py
import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, maxHands=1):
        self.hands = mp.solutions.hands.Hands(max_num_hands=maxHands)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(imgRGB)
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, handLms, mp.solutions.hands.HAND_CONNECTIONS)
        return img, results
