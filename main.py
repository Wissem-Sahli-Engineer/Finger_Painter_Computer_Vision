import cv2
# pyrefly: ignore [missing-import]
import mediapipe as mp 
import os , time 
from Hand_Tracking_Model.utils import handDetector
from utils import get_fps , draw_fps_capsule , get_dist , handle_control_panel
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

    # preprocessing
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)

    res = detector.landmarker.detect_for_video(mp_img,timestamp_ms) 

    lmList = detector.findHands(img,res, draw =True )

    img[0:h,0:w] = controls

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
                color, brush_thickness, canvas, should_exit = handle_control_panel(
                    cx, cy, color, brush_thickness, canvas, img
                )
                if should_exit:
                    break


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