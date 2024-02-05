import cv2
import mediapipe as mp
import time
import math
from cfUtil_Bar import BarDetectorC


class PoseMap:
    #    BodyPart, LM number,   Neighbors,      , Angle Neigh
    poseMap = [
        ["Nose",            0,  []              , []      ],
        ["LeftEyeIn",       1,  []              , []      ],
        ["LeftEye",         2,  []              , []      ],
        ["LeftEyeOut",      3,  []              , []      ],
        ["RightEyeIn",      4,  []              , []      ],
        ["RightEye",        5,  []              , []      ],
        ["RightEyeOut",     6,  []              , []      ],
        ["LeftEar",         7,  []              , []      ],
        ["RightEar",        8,  []              , []      ],
        ["MouthLeft",       9,  [10]            , []      ],
        ["MouthRight",      10, [9]             , []      ],
        ["LeftShoulder",    11, [12, 13, 23]    , [13, 23]],
        ["RightShoulder",   12, [11, 14, 24]    , [14, 24]],
        ["LeftElbow",       13, [11, 15]        , [11, 15]],
        ["RightElbow",      14, [12, 16]        , [12, 16]],
        ["LeftWrist",       15, [13, 17, 19, 21], []      ],
        ["RightWrist",      16, [14, 18, 20, 22], []      ],
        ["LeftPinky",       17, [15]            , []      ],
        ["RightPinky",      18, [16]            , []      ],
        ["LeftIndex",       19, [15]            , []      ],
        ["RightIndex",      20, [16]            , []      ],
        ["LeftThumb",       21, [15]            , []      ],
        ["RightThumb",      22, [16]            , []      ],
        ["LeftHip",         23, [11, 24, 25]    , [11, 25]],
        ["RightHip",        24, [12, 23, 26]    , [12, 26]],
        ["LeftKnee",        25, [23, 27]        , [23, 27]],
        ["RightKnee",       26, [24, 28]        , [24, 28]],
        ["LeftAnkle",       27, [25, 29, 31]    , []      ],
        ["RightAnkle",      28, [26, 30, 32]    , []      ],
        ["LeftHeel",        29, [27, 31]        , []      ],
        ["RightHeel",       30, [28, 32]        , []      ],
        ["LeftFootIndex",   31, [27, 29]        , []      ],
        ["RightFootIndex",  32, [28, 30]        , []      ]
    ]

    def __init__(self, index):
        self.bodypart =  self.poseMap[index][0]
        self.lm =        self.poseMap[index][1]
        self.neighbor =  self.poseMap[index][2]
        self.angleNeig = self.poseMap[index][3]

class PoseLandmarks:
    def __init__(self):
        self.Nose       = PoseMap(0)
        self.EyeInL     = PoseMap(1)
        self.EyeL       = PoseMap(2)
        self.EyeOutL    = PoseMap(3)
        self.EyeInR     = PoseMap(4)
        self.EyeR       = PoseMap(5)
        self.EyeOutR    = PoseMap(6)
        self.EarL       = PoseMap(7)
        self.EarR       = PoseMap(8)
        self.MouthL     = PoseMap(9)
        self.MouthR     = PoseMap(10)
        self.ShoulderL  = PoseMap(11)
        self.ShoulderR  = PoseMap(12)
        self.ElbowL     = PoseMap(13)
        self.ElbowR     = PoseMap(14)
        self.WristL     = PoseMap(15)
        self.WristR     = PoseMap(16)
        self.PinkyL     = PoseMap(17)
        self.Pinky1R    = PoseMap(18)
        self.IndexL     = PoseMap(19)
        self.IndexR     = PoseMap(20)
        self.ThumbL     = PoseMap(21)
        self.ThumbR     = PoseMap(22)
        self.HipL       = PoseMap(23)
        self.HipR       = PoseMap(24)
        self.KneeL      = PoseMap(25)
        self.KneeR      = PoseMap(26)
        self.AnkleL     = PoseMap(27)
        self.AnkleR     = PoseMap(28)
        self.HeelL      = PoseMap(29)
        self.HeelR      = PoseMap(30)
        self.FootIndexL = PoseMap(31)
        self.FootIndexR = PoseMap(32)


class PoseDetector():
    branches = { 11:[12, 13, 23], 12:[14, 24], 13:[15], 14:[16], 15:[], 16:[], 23:[24, 25], 24:[26],
                 25:[27], 26:[28], 27:[29, 31], 28:[30, 32], 29:[], 30:[], 31:[], 32:[] }

    def __init__(self, shape):
        self.shape = shape
        self.h, self.w, self.c = shape

        self.pose = mp.solutions.pose.Pose()

        # Create pose map of landmark indexes
        self.lmIdx = PoseLandmarks()


    def MapLandmarks(self, img):
        # Static Variables
        self.lmList = []
        colorVerticies = (0, 0, 255)
        colorBranch = (255, 255, 255)

        # Find Pose
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)

        # If there has been located landmarks
        if self.results.pose_landmarks:
            #print(self.results.pose_landmarks.landmark)
            # idx is lm index (0-32), lm gies x, y, z coordinates and a visibility prosentage
            for idx, lm in enumerate(self.results.pose_landmarks.landmark):

                x, y = int(lm.x * self.w), int(lm.y * self.h)
                self.lmList.append([idx, x, y])

            # Draw lines between vertices
            for v1, lv in self.branches.items():
                x1, y1 = self.lmList[v1][1], self.lmList[v1][2]
                for v2 in lv:
                    x2, y2 = self.lmList[v2][1], self.lmList[v2][2]
                    cv2.line(img, (x1, y1), (x2, y2), colorBranch, 2)

            # Vertex on mouth
            x, y = int((self.lmList[9][1] + self.lmList[10][1])/2), int((self.lmList[9][2] + self.lmList[10][2])/2)
            x1, x2, y1, y2 = self.lmList[9][1], self.lmList[10][1], self.lmList[9][2], self.lmList[10][2]
            cv2.circle(img, (int((self.lmList[9][1] + self.lmList[10][1])/2),
                                   int((self.lmList[9][2] + self.lmList[10][2])/2)),
                             6, (255, 255, 255), cv2.FILLED)


    def FindAngle(self, img, vertex, ang):
        # Get Landmarks
        _, x2, y2 = self.lmList[vertex]
        if vertex % 2 == 0:
            _, x1, y1 = self.lmList[PoseMap.poseMap[vertex][3][1]]
            _, x3, y3 = self.lmList[PoseMap.poseMap[vertex][3][0]]
        else:
            _, x1, y1 = self.lmList[PoseMap.poseMap[vertex][3][0]]
            _, x3, y3 = self.lmList[PoseMap.poseMap[vertex][3][1]]

        # Calculate Angle
        angle = int(math.degrees(math.atan2(y3-y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2)))

        if angle < 0:
            angle += 360

        # Draw
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
        cv2.line(img, (x3, y3), (x2, y2), (0, 255, 0), 3)
        cv2.circle(img, (x1, y1), 5, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 5, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x3, y3), 5, (255, 0, 0), cv2.FILLED)
        cv2.putText(img, str(angle), (x2 - 50, y2 + 50), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 1)

        # Draw
        cv2.line(ang, (x1, y1), (x2, y2), (0, 255, 0), 3)
        cv2.line(ang, (x3, y3), (x2, y2), (0, 255, 0), 3)
        cv2.circle(ang, (x1, y1), 5, (255, 0, 0), cv2.FILLED)
        cv2.circle(ang, (x2, y2), 5, (255, 0, 0), cv2.FILLED)
        cv2.circle(ang, (x3, y3), 5, (255, 0, 0), cv2.FILLED)
        cv2.putText(ang, str(angle), (x2 - 50, y2 + 50), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 1)

        return angle

    def FindCoordinates(self, img, mode, hgt):
        # Modes
        match mode:
            case 0:  # Toes = Floor
                _, xR, yR = self.lmList[self.lmIdx.FootIndexR.lm]
                _, xL, yL = self.lmList[self.lmIdx.FootIndexL.lm]
            case 1:  # Ankle
                _, xR, yR = self.lmList[self.lmIdx.AnkleR.lm]
                _, xL, yL = self.lmList[self.lmIdx.AnkleL.lm]
            case 2:  # Knee
                _, xR, yR = self.lmList[self.lmIdx.KneeR.lm]
                _, xL, yL = self.lmList[self.lmIdx.KneeL.lm]
            case 3: # Hip
                _, xR, yR = self.lmList[self.lmIdx.HipR.lm]
                _, xL, yL = self.lmList[self.lmIdx.HipL.lm]
            case 4: # Shoulder
                _, xR, yR = self.lmList[self.lmIdx.ShoulderR.lm]
                _, xL, yL = self.lmList[self.lmIdx.ShoulderL.lm]
            case 5:  # Elbow
                _, xR, yR = self.lmList[self.lmIdx.WristR.lm]
                _, xL, yL = self.lmList[self.lmIdx.WristL.lm]
            case 6:  # Wrists
                _, xR, yR = self.lmList[self.lmIdx.WristR.lm]
                _, xL, yL = self.lmList[self.lmIdx.WristL.lm]
            case 7: # Head
                _, xR, yR = self.lmList[self.lmIdx.MouthR.lm]
                _, xL, yL = self.lmList[self.lmIdx.MouthL.lm]

        # Calculate mid-point
        x, y = int((xR + xL) / 2), int(self.h - (yR + yL) / 2)

        # Draw
        cv2.putText(img, str(y), (xR - 100, yR), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 255), 1)
        cv2.putText(hgt, str(y), (xR - 100, yR), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 255), 1)

        return y, xL, xR

class Pose():
    def __init__(self, shape):
        self.shape = shape
        self.h, self.w, self.c = shape
        self.angleThreshold = 15                # Angular threshold for determining when angle is within desired range (degrees)
        self.heightThreshold = 0.02 * self.h    # Height threshold (percent of pixel height)
        self.legLength = 0
        self.detector = PoseDetector(shape)
        self.barC = BarDetectorC(shape)

        # Body Detection
        self.bodyCalibrated = False
        self.bodyCalTxt = "Not Calibrated"
        self.bodyCalColor = (0, 0, 255)
        self.bodyCalActive = False
        self.displayCal = False

        # Pose
        self.currPose = -1

    def UpdatePose(self, img):
        # Get positions of all nodes
        bb = img.copy()
        self.detector.MapLandmarks(img)
        ang, hgt = img.copy(), img.copy()

        # If list has element 10 or any at all, then landmarks are available. Extract angles between and heights of nodes.
        try:
            if self.detector.lmList[10]:
                pass
            self.lmAvail = 1
        except:
            self.lmAvail = 0

        if self.lmAvail:
            # Get angles
            self.angleElbR = self.detector.FindAngle(img, self.detector.lmIdx.ElbowR.lm, ang)
            self.angleElbL = self.detector.FindAngle(img, self.detector.lmIdx.ElbowL.lm, ang)
            self.angleKneR = self.detector.FindAngle(img, self.detector.lmIdx.KneeR.lm, ang)
            self.angleKneL = self.detector.FindAngle(img, self.detector.lmIdx.KneeL.lm, ang)
            self.angleShoR = self.detector.FindAngle(img, self.detector.lmIdx.ShoulderR.lm, ang)
            self.angleShoL = self.detector.FindAngle(img, self.detector.lmIdx.ShoulderL.lm, ang)
            self.angleHipR = self.detector.FindAngle(img, self.detector.lmIdx.HipR.lm, ang)
            self.angleHipL = self.detector.FindAngle(img, self.detector.lmIdx.HipL.lm, ang)

            # Get height
            self.heightToe, _, _ = self.detector.FindCoordinates(img, 0, hgt)
            self.heightAnk, _, _ = self.detector.FindCoordinates(img, 1, hgt)
            self.heightKne, _, _ = self.detector.FindCoordinates(img, 2, hgt)
            self.heightHip, _, _ = self.detector.FindCoordinates(img, 3, hgt)
            self.heightSho, self.widthShoL, self.widthShoR = self.detector.FindCoordinates(img, 4, hgt)
            self.heightElb, _, _ = self.detector.FindCoordinates(img, 5, hgt)
            self.heightWrst, self.widthWrstL, self.widthWrstR = self.detector.FindCoordinates(img, 6, hgt)
            self.heightHead, _, _ = self.detector.FindCoordinates(img, 7, hgt)

            # Get Length
            self.legLength = self.heightHip - self.heightAnk
            self.torsoLength = self.heightSho - self.heightHip
            self.bodyLength = self.heightSho - self.heightAnk

            # Take measurements of body
            self.CalibrationCheck(img)

        # Get Barbell Height
        self.barFound, self.barHeight, mask = self.barC.FindBar(img, bb)

        return mask


    def CalibrationCheck(self, img):
        length = self.heightHead - self.heightAnk
        if (abs(self.widthWrstL - self.widthWrstR) > 0.88 * length):
            if ((4 * (self.heightKne - self.heightAnk) < length) and (self.heightWrst < self.heightHead)):
                if not self.bodyCalActive:
                    self.bodyCalActive = True
                    self.bodyCalStart = time.time()
                else:
                    calTime = round(time.time() - self.bodyCalStart, 2)
                    cv2.putText(img, f"{calTime}", (int(0.45 * self.w), int(0.45 * self.h)),
                                cv2.FONT_HERSHEY_PLAIN, 8, (0, 255, 255), 4)
                    if calTime > 1:
                        self.CalibrateBodyParametrics()
            else:
                self.bodyCalActive = False
        else:
            self.bodyCalActive = False

        if self.displayCal:
            displayTime = time.time()
            if (displayTime < self.bodyDisplayStart + 3):
                cv2.putText(img, f"Calibrated",(int(0.35 * self.w), int(0.3 * self.h)),
                            cv2.FONT_HERSHEY_PLAIN, 8,(0, 255, 0), 6)

                self.bodyCalTxt = "Calibrated"
                self.bodyCalColor = (0, 255, 0)
            else:
                self.displayCal = False
        else:
            cv2.putText(img, self.bodyCalTxt, (int(0.05 * self.w), int(0.05 * self.h)),
                        cv2.FONT_HERSHEY_PLAIN, 3, self.bodyCalColor, 2)

    def CalibrateBodyParametrics(self):
        self.totalLegLength = self.heightHip - self.heightAnk
        self.totalTorsoLength = self.heightSho - self.heightHip
        self.totalBodyLength = self.heightSho - self.heightAnk
        self.totalArmSpan = abs(self.widthWrstL - self.widthWrstR)

        self.bodyCalActive = False
        self.bodyCalibrated = True
        self.displayCal = True
        self.bodyDisplayStart = time.time()




