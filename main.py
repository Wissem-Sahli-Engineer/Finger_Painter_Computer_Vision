import cv2
# pyrefly: ignore [missing-import]
import mediapipe as mp 
import os , time 
from Hand_Tracking_Model.utils import handDetector
from utils import get_fps , draw_fps_capsule , get_dist
# pyrefly: ignore [missing-import]
import numpy as np



##################
""" Arguments """
##################
Wcam, Hcam = 1280 , 720 

cap = cv2.VideoCapture(0)
cap.set(3,Wcam)
cap.set(4,Hcam)


detector = handDetector(model_path = "Hand_Tracking_Model/hand_landmarker.task",
                        num_hands = 1,
                        confidence = 0.6
                        )

frame_count = 0
pTime = time.time()

Alert = "Hand is not completly DETECTED ! Try to move it !"

canvas = None
px, py = 0, 0

color = (255, 0, 255)
brush_thickness = 10

while True:

    # Reading
    test , img = cap.read()
    if not test or img is None:
        break

    # fps and time
    fps , pTime = get_fps(cap, pTime)

    timestamp_ms = int((frame_count / get_fps(cap,0,type='cap')[0]) * 1000)
    frame_count += 1

    # flipping the image Y-AXIS : 
    img = cv2.flip(img,1)

    # Display controls

    controls = cv2.resize(cv2.imread("controls.png"),
                        (Wcam//4,Hcam),
                        interpolation=cv2.INTER_AREA
                        )
    h , w , c = controls.shape

    img[0:h,0:w] = controls

    # preprocessing
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)

    res = detector.landmarker.detect_for_video(mp_img,timestamp_ms) 

    lmList = detector.findHands(img,res, draw =True )

    if canvas is None:
            canvas = np.zeros_like(img)
    
    if len(lmList)!=0:
        index = lmList[0][8]
        middle = lmList[0][12]
        cx, cy = index[1], index[2]

        # Mode Selection: Index & Middle finger are together (Selection/Hover Mode)
        if get_dist(index, middle) < 40:
            px, py = 0, 0  # Reset line anchor so it doesn't jump
            cx, cy = index[1], index[2]

            # Visual indicator: draw a clean white pointer ring at your fingertips
            cv2.circle(img, (cx, cy), 15, (255, 255, 255), cv2.FILLED)

            # Check if the user is hovering over the left Control Panel (x < 320)
            if cx < 320:
                
                # --------------------------------------------
                # ROW 1: COLOR SELECTION (TOP ROW)
                # --------------------------------------------
                if 180 < cy < 250:
                    if 15 < cx < 65:
                        color = (0, 0, 255)      # BGR Red
                        print("Selected: RED")
                    elif 95 < cx < 145:
                        color = (0, 255, 0)      # BGR Green
                        print("Selected: GREEN")
                    elif 175 < cx < 225:
                        color = (255, 0, 0)      # BGR Blue
                        print("Selected: BLUE")
                    elif 255 < cx < 305:
                        color = (0, 255, 255)    # BGR Yellow
                        print("Selected: YELLOW")

                # --------------------------------------------
                # ROW 2: COLOR SELECTION (MIDDLE ROW)
                # --------------------------------------------
                elif 300 < cy < 370:
                    if 15 < cx < 65:
                        color = (255, 0, 255)    # BGR Purple
                        print("Selected: PURPLE")
                    elif 95 < cx < 145:
                        color = (0, 165, 255)    # BGR Orange
                        print("Selected: ORANGE")
                    elif 175 < cx < 225:
                        color = (255, 255, 255)  # BGR White
                        print("Selected: WHITE")
                    elif 255 < cx < 305:
                        color = (0, 0, 0)        # BGR Black (Draws black onto canvas)
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
                        break  # Breaks the main video while-loop


        else: 
            if px == 0 and py == 0:
                px, py = cx, cy

            cv2.line(canvas, (px, py), (cx, cy),color, brush_thickness)
            px, py = cx, cy

    else :
        px, py = 0, 0
        cv2.putText(img,Alert, (620,100), cv2.FONT_HERSHEY_COMPLEX,
                    1, (183,81,93) , 1
                    )
        print(Alert)

    img = cv2.add(img, canvas)

    # display 
    draw_fps_capsule(img, fps)
    
    cv2.imshow('Live',cv2.cvtColor(img,cv2.COLOR_RGB2BGR))

    if cv2.waitKey(1) & 0xFF == ord(' '):
        break

cap.release()
cv2.destroyAllWindows()