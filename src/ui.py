import cv2
import numpy as np 

class UIManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # BGR values
        self.colours = {
            "red": (0, 0, 255),
            "blue": (230, 180, 40),
            "green": (20, 180, 50),
            "yellow": (0, 255, 255),
            "white": (255, 255, 255)
        }
        
        self.box_size = 120
        self.margin = 20
        self.selected_colour = "red"  # Default red
        
        # Create colour boxes
        self.colour_boxes = {}
        y_pos = self.margin
        x_pos = self.width - self.box_size - self.margin
        
        for colour_name in self.colours:
            self.colour_boxes[colour_name] = (x_pos, y_pos, self.box_size, self.box_size)
            y_pos += self.box_size + self.margin

    def draw(self, frame):
        # Draw colour boxes
        for colour_name, (x, y, w, h) in self.colour_boxes.items():
            cv2.rectangle(frame, (x, y), (x + w, y + h), 
                         self.colours[colour_name], -1)
            
            # Highlight selected colour
            if colour_name == self.selected_colour:
                cv2.rectangle(frame, (x-3, y-3), (x + w+3, y + h+3), (255, 255, 255), 2)
        
        # Draw current colour indicator
        cv2.rectangle(frame, (10, 10), (50, 50), 
                     self.colours[self.selected_colour], -1)
        cv2.rectangle(frame, (10, 10), (50, 50), (255, 255, 255), 2)
    
    def handle_selection(self, point):
        for colour_name, (x, y, w, h) in self.colour_boxes.items():
            if (x <= point[0] <= x + w) and (y <= point[1] <= y + h):
                self.selected_colour = colour_name
                return True, colour_name
        return False, None