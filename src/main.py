import cv2
import numpy as np
from config import *
from hand_tracker import HandTracker
from gesture import GestureRecogniser, GestureType
from drawing import DrawingCanvas
from ui import UIManager

def initialise_camera():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

    # Getting the actual dimensions of the camera (if it ignores the above set)
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"Camera running at: {actual_width}x{actual_height}")

    return cap, actual_width, actual_height

def main():
    cap, cam_width, cam_height = initialise_camera()
    tracker = HandTracker()
    gesture_recogniser = GestureRecogniser()
    canvas = DrawingCanvas(cam_width, cam_height)
    ui_manager = UIManager(cam_width, cam_height)
    
    # Set initial colour
    canvas.set_colour(ui_manager.selected_colour)
    
    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to get frame from camera")
            break
    
        # flip frame if enabled because i look ugly mirrored
        if FLIP_CAMERA:
            frame = cv2.flip(frame, 1)

        # find and draw hands
        frame = tracker.find_hands(frame)
        landmark_list = tracker.get_hand_position(frame)

        # recognise gesture
        gesture = gesture_recogniser.recognise_gesture(landmark_list)
        index_finger = tracker.get_finger_position(frame, 8) if landmark_list else None
        
        # Handle drawing actions
        if index_finger:
            if gesture == GestureType.SELECT:
                # Reset to pen when selecting
                canvas.set_tool("pen")
                
                # Handle colour selection
                colour_selected, colour_name = ui_manager.handle_selection(index_finger)
                if colour_selected:
                    canvas.set_colour(colour_name)
                    print(f"Selected colour: {colour_name}")
                
                canvas.stop_drawing()
                    
            elif gesture == GestureType.DRAW:
                # Ensure we're using pen tool
                canvas.set_tool("pen")
                
                if not canvas.drawing:
                    canvas.start_drawing(index_finger)
                else:
                    canvas.draw(index_finger)
                    
            elif gesture == GestureType.ERASE:
                # Switch to eraser tool
                canvas.set_tool("eraser")
    
                # Draw eraser circle preview around finger
                cv2.circle(frame, 
                    index_finger, 
                    canvas.eraser_thickness // 2,  # Radius is half the thickness
                    (255, 0, 0),  # Blue circle
                    2)  # Line thickness
    
                if not canvas.drawing:
                    canvas.start_drawing(index_finger)
                else:
                    canvas.draw(index_finger)
            else:
                # Stop drawing for any other gesture
                canvas.stop_drawing()
        else:
            # No hand detected, stop drawing
            canvas.stop_drawing()
                
        # Combine canvas with camera feed
        # Draw canvas content
        drawing_display = canvas.get_display()
        # Only show camera feed where there is no drawing
        mask = cv2.cvtColor(drawing_display, cv2.COLOR_BGR2GRAY)
        mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)[1]

        # Ensure mask is uint8
        if mask.dtype != np.uint8:
            mask = mask.astype(np.uint8)

        # Ensure mask is the same size as the frame
        if mask.shape != frame.shape[:2]:
            mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
        
        # Combine the camera feed and drawing
        frame_bg = cv2.bitwise_and(frame, frame, mask=cv2.bitwise_not(mask))
        drawing_fg = cv2.bitwise_and(drawing_display, drawing_display, mask=mask)
        frame = cv2.add(frame_bg, drawing_fg)
        
        # Add UI elements
        ui_manager.draw(frame)
        
        if landmark_list:
            cv2.putText(frame, f"Gesture: {gesture.value}", (10, CAMERA_HEIGHT - 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Tool: {canvas.current_tool}", (10, CAMERA_HEIGHT - 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow('AirDraw by Jospin', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()