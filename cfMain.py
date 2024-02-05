import cv2
import time
from cfUtil_WOD import WOD
from cfUtil_Bar import BarDetectorDL
from cfUtil_Time import TimeModule

# Static Variables
# This is used to control the flow of the program
#       'Module' : [Mode Activation, Mode Draw/Text]
mode = { 'Timeseries': [0, 0], 'BarDL': [0, 1],
        'Watch': [1, 1], 'FPS':  [0, 0], 'Save':  [1, 0]}
watch = {'ft': 0, 'amrap': 0, 'emom': 0}

scale = 0.7    # Scaling the image displayed
single = False # Used for singel stepping the frames
ss = 90        # Used to label screenshots and give them unique names
n = 0          # n is used to skip frames when using a video file as input to the program
skip = 1       # skip is used to skip frames when using a video file as input to the program
wodActive = 0  # used to indicate if a WOD is currently on-going
screen = 0     # Used to swith between which frame is being displayed during run-time

# The video file captured in the cap object. By inputting 0 insted og the video file, the program will use the web-cam
# on the computer instead.
cap = cv2.VideoCapture("VideoM/WOD_DL_Cl_Sn_Pr_ToLorGP.MP4")

# Extrapt a frame from the capture to get the dimensions
ret, frame = cap.read()
shape = frame.shape
h, w, c = shape

# Make the WOD and the TimeModule objects
wod = WOD(shape)
t = TimeModule()

# Load trained model
if mode['BarDL'][0]:
    barDL = BarDetectorDL('model/modelWw80h40_16.xml')
    barModel = barDL.model

# Create the Video Writer object to save the products of the program into a video
if mode['Save'][0]:
    h, w = cap.get(cv2.CAP_PROP_FRAME_HEIGHT), cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    fps = 15
    # Get time and date to time stamp label the video
    l = str(time.ctime()).split()
    s = f"{l[1]}{l[2]}-{l[3][0:2]}{l[3][3:5]}{l[3][6:8]}"
    videoWriter = cv2.VideoWriter(f"Exp_Video/MP_Video_{s}.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (int(w), int(h)))

# To skip a into the video. When 0 nothing happens, replasing with "k", the program will tak k frames from the
# image capture and the program will then effectivly jump k frames into the video before starting the processing
for _ in range(0):
    ret, frame = cap.read()

# Loop through the video feed´s or file´s frames
while True:
    # Read Frame from file or stream
    _, frame = cap.read()

    # Detect end of video file or video stream.
    if frame is None:
        break

    # Mechanism to not process every "skip"(int variable) number of frames.
    # To increase program speed when processing a video file.
    n += 1
    if n % skip != 0:
        continue

    # Copy the frame
    displayFrame = frame.copy()

    # Check if WOD is on-going and foreward image to processing
    if wodActive:
        wodActive, mask = wod.ExecuteWOD(displayFrame, frame)
    else:
        # This is used during deveopment to bypass the WOD module and go straight to the image processing
        mask = wod.timeseries.TimeseriesMain(frame)

    # Calculate Frame Rate
    if mode['FPS'][0]:
        t.GetFps(frame, draw=mode['FPS'][1])

    # ! Side Project !
    # Detect Barbell with Machine Learning using the self trained model
    # using OpenCVs Cascade Classifier
    if mode['BarDL'][0]:
        # Detect object in image frame
        barPositions = barModel.detectMultiScale(frame)
        # Draw rectangles on detected objects
        barDL.BarDrawRectangle(frame, barPositions, False)
    # ! Side Project End !

    # Watch Control flow
    if mode['Watch'][0]:
        if watch['ft']:
            watch['ft'] = t.FT(displayFrame, 1, text=mode['Watch'][0])
        if watch['amrap']:
            watch['amrap'] = t.AMRAP(displayFrame, 1, text=mode['Watch'][0])
        if watch['emom']:
            watch['emom'] = t.EMOM(displayFrame, 1, 3, text=mode['Watch'][0])

    # The screen variablen lets the user/deveoper swith between which frame is shown during run-time by pressing 'b'
    # Re-size and show Frames in display windows
    # Re-sizes the window using a scaling factor "scale"
    if screen == 0:
        # Save Video using OpenCV
        if mode['Save'][0]:
            videoWriter.write(displayFrame)
        if scale != 1:
            displayFrame = cv2.resize(displayFrame, (0,0), fx=scale, fy=scale)
        cv2.imshow('Display', displayFrame)
    elif screen == 1:
        # Save Video using OpenCV
        if mode['Save'][0]:
            videoWriter.write(frame)
        if scale != 1:
            frame = cv2.resize(frame, (0,0), fx=scale, fy=scale)
        cv2.imshow('Display', frame)
    elif screen == 2:
        # Save Video using OpenCV
        if mode['Save'][0]:
            videoWriter.write(mask)
        if scale != 1:
            mask = cv2.resize(mask, (0, 0), fx=scale, fy=scale)
        cv2.imshow('Display', mask)


    # Keyboard command unit
    # Takes keyboard reading and stores in "push"
    # Then evaluate the entered keys and execute specified command
    # Capable of pausing program (p), single step frames (p, while paused), calibrate body parametrics of athlete (c)
    # start the three different clocks (f, a, e), screenshot displays (s) and abort program (q).

    # Pause and single stepping
    if not single:
        push = cv2.waitKey(1)
    if push == ord('p') or single:
        push = cv2.waitKey(0)
        if push == ord('p') or push == ord('b') or push == ord('s'):
            single = True
        else:
            single = False

    # Calibration
    if push == ord('c'):
        wod.timeseries.sm.pose.CalibrateBodyParametrics()

    # Switch display screen between front-end, back-end and the masked image frame
    if push == ord('b'):
        screen += 1
        if screen > 2:
            screen = 0

    # Clocks
    if push == ord('f'):
        watch['ft'] = 1
    if push == ord('a'):
        watch['amrap'] = 1
    if push == ord('e'):
        watch['emom'] = 1

    # Screenshot mechanism
    if push == ord('s'):
        ss += 1
        #l = str(time.ctime()).split()
        #s = f"{l[1]}{l[2]}-{l[3][0:2]}{l[3][3:5]}{l[3][6:8]}"
        cv2.imwrite(f"Screenshots/{ss}_2_Back.png", frame)
        cv2.imwrite(f"Screenshots/{ss}_1_Front.png", displayFrame)
        #cv2.imwrite(f"Screenshots/{ss}_8_Mask.png", mask)
        #cv2.imwrite(f"Screenshots/{ss}_7_Bar.png", bb)
        #cv2.imwrite(f"Screenshots/{ss}_3_vertex.png", vrtx)
        #cv2.imwrite(f"Screenshots/{ss}_4_branch.png", bch)
        #cv2.imwrite(f"Screenshots/{ss}_6_Height.png", hgt)
        #cv2.imwrite(f"Screenshots/{ss}_5_Angle.png", ang)

    # WOD Commands
    # Input WOD sequence
    if push == ord("i"):
        wod.InputWOD()
    # Load the WOD into the program
    if push == ord("l"):
        wod.LoadWOD()
    # Start the WOD
    if push == ord("w"):
        wodActive = 1

    # Abort program
    if push == ord('q'):
        break

# Release video file or video feed
cap.release()

# Save Video and export to file directory
if mode['Save'][0]:
    videoWriter.release()

# Export the logged data into a .csv file
if mode['Timeseries'][0]:
    wod.timeseries.ExportTimeseries()

# Close display windows
cv2.destroyAllWindows()

