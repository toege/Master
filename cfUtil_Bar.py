import cv2
import numpy as np

class BarDetectorC:
    def __init__(self, shape):
        self.h, self.w, self.c = shape
        self.areaMin = 30
        self.areaMax = 500
        self.lowerColor = np.array([29, 85, 85])
        self.upperColor = np.array([38, 255, 255])

    def FindBar(self, img, bb):
        # Convert image to HSV and filter out all pixels outside desired color range

        hsv = cv2.cvtColor(bb, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lowerColor, self.upperColor)

        # Detect Object and stor position and metrics
        marks = []
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # Get position and size perimeters of objects
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.areaMin and area < self.areaMax:
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                x, y, w, h = cv2.boundingRect(approx)
                marks.append([x, y, w, h])

                # Mark object with contour line and rectangle and write specs
                cv2.drawContours(mask, contour, -1, (255, 0, 255), 7)
                cv2.rectangle(mask, (x, y), (x + w, y + h), (0, 0, 255), 3)
                cv2.putText(mask, "Points:" + str(len(approx)), (x + w + 20, y + 20), cv2.FONT_HERSHEY_PLAIN, 1,
                            (255, 255, 255), 2)
                cv2.putText(mask, "Area:" + str(int(area)), (x + w + 20, y + 45), cv2.FONT_HERSHEY_PLAIN, 1,
                            (255, 255, 255), 2)

        # Draw line between the two markers
        y = -1
        barFound = 0
        if len(marks) == 2:
            x1, y1, x2, y2 = (marks[0][0] + int(0.5 * marks[0][2]), marks[0][1] + int(0.5 * marks[0][3]),
                              marks[1][0] + int(0.5 * marks[1][2]), marks[1][1] + int(0.5 * marks[1][3]))
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

            x, y = int((x1 + x2)/2), int(self.h - ((y1+y2)/2))
            barFound = 1

            cv2.putText(img, f'{y}', (x, int((y1+y2)/2)-50), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 0, 0), 1)


            cv2.line(bb, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(bb, f'{y}', (x, int((y1+y2)/2)-50), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 0, 0), 1)

        # Change the dimensions of the mask so that it may be stores in th evideo writer object in main
        mask = cv2.cvtColor(mask, cv2.COLOR_BAYER_GR2BGR)

        return barFound, y, mask

class BarDetectorDL:
    def __init__(self, file):
        self.model = cv2.CascadeClassifier(file)

    def BarDrawRectangle(self, img, rectangle, single=False):
        # Static Variables
        color = (0, 0, 255)

        for (x, y, w, h) in rectangle:
            # Calculate corners
            p1 = (x, y)
            p2 = (x + w, y + h)

            # Draw
            cv2.rectangle(img, p1, p2, color, 2)
            if single:
                cv2.imshow('Bars', img)
                cv2.waitKey(0)
