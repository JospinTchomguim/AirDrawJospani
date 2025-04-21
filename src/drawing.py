import cv2
import numpy as np

class DrawingCanvas:
    def __init__(self, width, height):
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.temp_canvas = np.zeros_like(self.canvas)
        
        # MUST match UI colours exactly
        self.colours = {
            "red": (0, 0, 255),
            "blue": (230, 180, 40),
            "green": (20, 180, 50),
            "yellow": (0, 255, 255),
            "white": (255, 255, 255)
        }
        
        # Current drawing settings
        self.current_colour_name = "red"
        self.current_colour = self.colours["red"]
        self.thickness = 15
        self.eraser_thickness = 125
        self.current_tool = "pen"
        self.drawing = False
        self.start_point = None
        
    def draw(self, point):
        if not self.drawing or self.start_point is None:
            return
            
        if self.current_tool == "pen":
            # Get the actual BGR color to use
            bgr_colour = self.current_colour
            print(f"Drawing with colour: {self.current_colour_name}, BGR: {bgr_colour}")
            cv2.line(self.canvas, self.start_point, point, bgr_colour, self.thickness)
            self.start_point = point
            
        elif self.current_tool == "eraser":
            cv2.line(self.canvas, self.start_point, point, (0, 0, 0), self.eraser_thickness)
            self.start_point = point

    def start_drawing(self, point):
        self.drawing = True
        self.start_point = point
        print(f"Started drawing with: {self.current_colour_name}")
        
    def stop_drawing(self):
        self.drawing = False
        self.start_point = None

    def set_colour(self, colour_name):
        if colour_name in self.colours:
            self.current_colour_name = colour_name
            self.current_colour = self.colours[colour_name]
            print(f"Canvas colour set to: {colour_name}, BGR: {self.current_colour}")
            
    def set_tool(self, tool_name):
        if tool_name in ["pen", "eraser"]:
            self.current_tool = tool_name
            
    def get_display(self):
        return self.canvas.copy()