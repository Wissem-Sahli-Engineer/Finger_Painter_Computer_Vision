import time , math
import cv2
# pyrefly: ignore [missing-import]
import numpy as np

# init " pTime = time.time() " before the While loop
def get_fps(cap, pTime,type='default'):
    if type == "default":
        cTime = time.time()
        fps = 1/(cTime - pTime)
        pTime = cTime
        return fps, pTime

    elif type =="cap":
        fps= cap.get(cv2.CAP_PROP_FPS)
        if fps<= 0:
            return 30, pTime
        return fps, pTime
    else:
        return 30, pTime

def draw_fps_capsule(img, fps):
    """
    Draws a clean modern capsule for the frame-rate in the top-left corner.
    """
    fps_overlay = img.copy()
    cv2.rectangle(fps_overlay, (1175, 15), (1315, 55), (0, 0, 0), cv2.FILLED)
    cv2.addWeighted(fps_overlay, 0.5, img, 0.5, 0, img)
    cv2.putText(img, f"FPS: {int(fps)}", (1200, 42), cv2.FONT_HERSHEY_SIMPLEX, 
                0.55, (0, 255, 255), 1, cv2.LINE_AA)


def get_dist(point1,point2):
    return math.hypot(point1[1]-point2[1],point1[2]-point2[2])


def handle_control_panel(cx, cy, color, brush_thickness, canvas, img):
    """
    Handles menu selections on the left control panel when the user is hovering.
    
    Returns:
        tuple: (color, brush_thickness, canvas, should_exit)
    """
    should_exit = False
    
    # --------------------------------------------
    # ROW 1: COLOR SELECTION (TOP ROW)
    # --------------------------------------------
    if 180 < cy < 250:
        if 15 < cx < 65:
            color = (255, 0, 0)      # RGB Red
            print("Selected: RED")
        elif 95 < cx < 145:
            color = (0, 255, 0)      # RGB Green
            print("Selected: GREEN")
        elif 175 < cx < 225:
            color = (0, 0, 255)      # RGB Blue
            print("Selected: BLUE")
        elif 255 < cx < 305:
            color = (255, 255, 0)    # RGB Yellow
            print("Selected: YELLOW")

    # --------------------------------------------
    # ROW 2: COLOR SELECTION (MIDDLE ROW)
    # --------------------------------------------
    elif 300 < cy < 370:
        if 15 < cx < 65:
            color = (255, 0, 255)    # RGB Purple
            print("Selected: PURPLE")
        elif 95 < cx < 145:
            color = (255, 165, 0)    # RGB Orange
            print("Selected: ORANGE")
        elif 175 < cx < 225:
            color = (255, 255, 255)  # RGB White
            print("Selected: WHITE")
        elif 255 < cx < 305:
            color = (1, 1, 1)        # RGB Near-Black (so it draws black instead of being transparent)
            print("Selected: BLACK")

    # --------------------------------------------
    # ROW 3: UTILITIES (BRUSH SIZE, ERASER, CLEAR, THICKNESS)
    # --------------------------------------------
    elif 425 < cy < 525:
        # Decrease Brush Size
        if 15 < cx < 65:
            brush_thickness = max(2, brush_thickness - 2)
            print(f"Brush Size Decreased to: {brush_thickness}")
            time.sleep(0.15)  # Small delay to prevent rapid continuous firing
        
        # Eraser Mode (Paint black with a very thick brush)
        elif 95 < cx < 145:
            color = (0, 0, 0)
            brush_thickness = 50
            print("ERASER MODE Activated")
        
        # Clear Canvas
        elif 175 < cx < 225:
            canvas = np.zeros_like(img)
            print("CANVAS CLEARED!")
            time.sleep(0.2)  # Delay so it doesn't double trigger
        
        # Increase Brush Size
        elif 255 < cx < 305:
            brush_thickness = min(100, brush_thickness + 5)
            print(f"Brush Size Increased to: {brush_thickness}")
            time.sleep(0.15)  # Delay

    # --------------------------------------------
    # ROW 4: SYSTEM CONTROL (EXIT)
    # --------------------------------------------
    elif 580 < cy < 680:
        if 120 < cx < 200:
            print("Exiting application...")
            should_exit = True
            
    return color, brush_thickness, canvas, should_exit


