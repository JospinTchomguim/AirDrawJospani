from enum import Enum
import math
import time

class GestureType(Enum):
    NONE = "none"
    DRAW = "draw"       # index + thumb pinch
    ERASE = "erase"     # open palm 
    SELECT = "select"   # index pointing
    CLEAR = "clear"     # fist with thumb out 

class GestureRecogniser:
    def __init__(self):
        self.pinch_threshold = 75
        self.current_gesture = GestureType.NONE
        # clear gesture timing
        self.clear_gesture_start = 0
        self.clear_hold_time = 3.0
        self.is_clear_gesture = False

    def recognise_gesture(self, landmark_list):
        if not landmark_list:
            # reset clear gesture state when no hand detected
            self.is_clear_gesture = False
            self.clear_gesture_start = 0
            return GestureType.NONE
        
        landmarks = dict([(id, (x, y)) for id, x, y in landmark_list])

        fingers_extended = self._check_fingers_extended(landmarks)

        # calculate pinch distance
        pinch_distance = self._calculate_distance(
            landmarks[4],
            landmarks[8]
        )

        # debug info
        print(f"Pinch distance: {pinch_distance}")
        print(f"Fingers extended: {fingers_extended}")
        
        # check for draw gesture
        if pinch_distance < self.pinch_threshold:
            return GestureType.DRAW
        
        # check for erase gesture
        fingers_extended = self._check_fingers_extended(landmarks)
        if all(fingers_extended):
            return GestureType.ERASE
        
        # check for select gesture 
        if self._is_select_gesture(landmarks, fingers_extended):
            return GestureType.SELECT
        
        # # check for clear gesture
        # if fingers_extended[0] and not any(fingers_extended[1:]):
        #     # Start timing if we just entered clear gesture
        #     if not self.is_clear_gesture:
        #         self.clear_gesture_start = time.time()
        #         self.is_clear_gesture = True
            
        #     # Check if we've held the gesture long enough
        #     if time.time() - self.clear_gesture_start >= self.clear_hold_time:
        #         return GestureType.CLEAR
        # else:
        #     # Reset clear gesture state if hand position changes
        #     self.is_clear_gesture = False
        #     self.clear_gesture_start = 0
        
        return GestureType.NONE
    
    def _is_select_gesture(self, landmarks, fingers_extended):
        index_extended = fingers_extended[1]

        other_fingers_curled = not any([fingers_extended[2], fingers_extended[3], fingers_extended[4]])

        # Check index finger angle (should be pointing upward)
        index_tip = landmarks[8]    # Index tip
        index_pip = landmarks[6]    # Index PIP (middle joint)
        
        # Calculate angle between index finger and vertical
        dx = index_tip[0] - index_pip[0]
        dy = index_tip[1] - index_pip[1]
        angle = abs(math.degrees(math.atan2(dx, -dy)))  # Negative dy because y increases downward

        # Check if index is relatively straight and vertical
        is_vertical = angle < 30  # Allow 30 degrees deviation from vertical

        # Check if index is above other fingers
        index_tip_y = landmarks[8][1]
        other_tips_y = [landmarks[i][1] for i in [12, 16, 20]]  # Middle, Ring, Pinky tips
        is_highest = all(index_tip_y < y for y in other_tips_y)
                         
        # Combined conditions for SELECT gesture
        return (index_extended and 
                other_fingers_curled and 
                is_vertical and 
                is_highest)

    def _calculate_distance(self, point1, point2):
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
    
    def _check_fingers_extended(self, landmarks):
        # get palm center 
        palm_x = sum(landmarks[i][0] for i in [0, 5, 9, 13, 17]) / 5

        thumb_extended = landmarks[4][0] < palm_x

        # Other fingers - compare y positions
        fingers = []
        for tip, mid, base in [(8,6,5), (12,10,9), (16,14,13), (20,18,17)]:  # Index to Pinky
            finger_tip_y = landmarks[tip][1]
            finger_base_y = landmarks[base][1]
            finger_mid_y = landmarks[mid][1]

            # A finger is extended if its tip is higher (smaller y) than both its mid and base points
            finger_extended = finger_tip_y < finger_mid_y < finger_base_y
            fingers.append(finger_extended)

        return [thumb_extended] + fingers
    


        
        