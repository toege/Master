import numpy as np
import cv2

cap = cv2.VideoCapture(0) #"VideoM/WOD_DL_Cl_Sn_Pr_ToLorGP.MP4")

###
### Static Variables
###
ret, frame = cap.read()
h, w, c = frame.shape
print(h, w, c)
h2 = int(h/2)
w2 = int(w/2)
scale = 0.55
newFrame = True

def empty(a):
    pass

###
### Create Trackbars
###
cv2.namedWindow("Parameters")
cv2.resizeWindow("Parameters", 640, 240)
cv2.createTrackbar("Threshold1", "Parameters", 50, 255, empty)
cv2.createTrackbar("Threshold2", "Parameters", 50, 255, empty)
cv2.createTrackbar("AreaMin", "Parameters", 100, 2000, empty)
cv2.createTrackbar("AreaMax", "Parameters", 5000 , w*h, empty)
cv2.namedWindow("Color")
cv2.resizeWindow("Color", 640, 240)
cv2.createTrackbar("H-Min", "Color", 29, 255, empty)
cv2.createTrackbar("H-Max", "Color", 35, 255, empty)
cv2.createTrackbar("S-Min", "Color", 70, 255, empty)
cv2.createTrackbar("S-Max", "Color", 255, 255, empty)
cv2.createTrackbar("V-Min", "Color", 70, 255, empty)
cv2.createTrackbar("V-Max", "Color", 255, 255, empty)
cv2.createTrackbar("Height", "Color", h2, h-1, empty)
cv2.createTrackbar("Width", "Color", w2, w-1, empty)

while True:
    if newFrame:
        ret, frame = cap.read()
        oldFrame = frame.copy()
    else:
        frame = oldFrame.copy()

    ###
    ### Track Bars
    ###
    hsv_H_MaxVal = cv2.getTrackbarPos("H-Max", "Color")
    hsv_H_MinVal = cv2.getTrackbarPos("H-Min", "Color")
    hsv_S_MaxVal = cv2.getTrackbarPos("S-Max", "Color")
    hsv_S_MinVal = cv2.getTrackbarPos("S-Min", "Color")
    hsv_V_MaxVal = cv2.getTrackbarPos("V-Max", "Color")
    hsv_V_MinVal = cv2.getTrackbarPos("V-Min", "Color")
    h2 = cv2.getTrackbarPos("Height", "Color")
    w2 = cv2.getTrackbarPos("Width", "Color")
    areaMin = cv2.getTrackbarPos("AreaMin", "Parameters")
    areaMax = cv2.getTrackbarPos("AreaMax", "Parameters")

    ###
    ### Blur
    ###
    #imgBlur = cv2.GaussianBlur(frame, (7, 7), 1)

    ###
    ### Color Sampler
    ###
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv2.circle(frame, (w2, h2), 15, (0, 0, 255), 1)
    cv2.putText(frame, f"hsv: {hsv[h2][w2]} bgr: {frame[h2][w2]}", (w2+50, h2-50), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)


    ###
    ### Color masking
    ###
    lowerColor = np.array([hsv_H_MinVal, hsv_S_MinVal, hsv_V_MinVal])
    upperColor = np.array([hsv_H_MaxVal, hsv_S_MaxVal, hsv_V_MaxVal])
    mask = cv2.inRange(hsv, lowerColor, upperColor)
    imgMask = cv2.bitwise_and(frame, frame, mask=mask)

    ###
    ### Canny
    ###

    threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters")
    threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")
    #imgCanny = cv2.Canny(mask, threshold1, threshold2)

    ###
    ### Detect Object
    ###
    marks = []
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Get position and size perimeters of objects
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > areaMin and area < areaMax:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02*peri, True)
            xo, yo, wo, ho = cv2.boundingRect(approx)
            marks.append([xo, yo, wo, ho])

            # Mark object with contour line and rectangle and write specs
            cv2.drawContours(mask, contour, -1, (255, 0, 255), 7)
            cv2.rectangle(mask, (xo, yo), (xo+wo, yo+ho), (0, 0, 255), 3)
            cv2.putText(mask, "Points:" + str(len(approx)), (xo+wo+20, yo+20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2)
            cv2.putText(mask, "Area:" + str(int(area)), (xo+wo+20, yo+45), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2)

    # Draw line between the two markers
    if len(marks) == 2:
        x1, y1, x2, y2 = marks[0][0] + int(0.5*marks[0][2]), marks[0][1] + int(0.5*marks[0][3]), marks[1][0] + int(0.5*marks[1][2]), marks[1][1] + int(0.5*marks[1][3])
        cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)


    ###
    ### Display: Re-size and show
    ###
    #hsv = cv2.resize(hsv, (int(scale*w), int(scale*h)))
    #imgCanny = cv2.resize(imgCanny, (int(scale*w), int(scale*h)))
    mask = cv2.resize(mask, (int(scale*w), int(scale*h)))
    frame = cv2.resize(frame, (int(scale*w), int(scale*h)))
    #imgMask = cv2.resize(imgMask, (int(scale*w), int(scale*h)))


    #cv2.imshow('HSV', hsv)
    #cv2.imshow('Canny', imgCanny)
    #cv2.imshow('Result', imgMask)
    cv2.imshow('Mask', mask)
    cv2.imshow('Frame', frame)

    # End program
    push = cv2.waitKey(1)
    if push == ord('q'):
        break
    if push == ord('p'):
        newFrame = False
    if push == ord('c'):
        newFrame = True

cap.release()
cv2.destroyAllWindows()

