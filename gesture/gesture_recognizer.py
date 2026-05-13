import cv2
import mediapipe as mp
import numpy as np
import time
from PyQt5.QtCore import QObject, pyqtSignal

class GestureRecognizer(QObject):
    gesture_detected = pyqtSignal(str)

    def __init__(self, command_system, logger, cooldown_seconds=2.0):
        super().__init__()
        self.command_system = command_system
        self.logger = logger
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

        self.cap = None
        self.is_recognizing = False

        self.cooldown_seconds = cooldown_seconds
        self.last_execution_time = 0

        try:
            self.cap = cv2.VideoCapture(0)
            self.logger.info("摄像头初始化成功")
        except Exception as e:
            self.logger.error(f"摄像头初始化失败: {str(e)}")

    def recognize_gesture(self, landmarks):
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]

        thumb_mcp = landmarks[2]
        index_mcp = landmarks[5]
        middle_mcp = landmarks[9]
        ring_mcp = landmarks[13]
        pinky_mcp = landmarks[17]

        wrist = landmarks[0]
        is_right_hand = index_mcp.x > wrist.x

        if is_right_hand:
            thumb_open = thumb_tip.x < thumb_mcp.x - 0.05
        else:
            thumb_open = thumb_tip.x > thumb_mcp.x + 0.05

        finger_threshold = 0.08

        index_open = (index_tip.y - index_mcp.y) < -finger_threshold
        middle_open = (middle_tip.y - middle_mcp.y) < -finger_threshold
        ring_open = (ring_tip.y - ring_mcp.y) < -finger_threshold
        pinky_open = (pinky_tip.y - pinky_mcp.y) < -finger_threshold

        fingers_open = sum([index_open, middle_open, ring_open, pinky_open])

        if fingers_open == 1 and index_open:
            return 'one'
        elif fingers_open == 2 and index_open and middle_open:
            return 'two'
        elif fingers_open == 3 and index_open and middle_open and ring_open:
            return 'three'
        elif fingers_open == 4 and thumb_open:
            return 'four'
        elif fingers_open == 4 and not thumb_open:
            return 'five'
        elif fingers_open == 5:
            return 'five'

        return None

    def is_in_cooldown(self):
        current_time = time.time()
        return (current_time - self.last_execution_time) < self.cooldown_seconds

    def start_recognizing(self):
        if not self.cap or not self.cap.isOpened():
            self.logger.error("摄像头不可用")
            return

        self.is_recognizing = True
        self.logger.info(f"手势识别服务已启动，冷却时间: {self.cooldown_seconds}秒")
        last_gesture = None
        gesture_counter = 0

        while self.is_recognizing:
            success, frame = self.cap.read()
            if not success:
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)

            gesture = None

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                        self.mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                    )

                    landmarks = []
                    for lm in hand_landmarks.landmark:
                        landmarks.append(lm)

                    gesture = self.recognize_gesture(landmarks)

            if gesture == last_gesture and gesture:
                gesture_counter += 1
                if gesture_counter >= 10:
                    if not self.is_in_cooldown():
                        self.logger.info(f"识别到手势: {gesture}")
                        self.gesture_detected.emit(gesture)
                        self.command_system.execute_gesture_command(gesture)
                        self.last_execution_time = time.time()
                        gesture_counter = 0
                    else:
                        gesture_counter = 0
            else:
                last_gesture = gesture
                gesture_counter = 0

        self.cap.release()

    def stop_recognizing(self):
        self.is_recognizing = False
        self.logger.info("手势识别服务已停止")