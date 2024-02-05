import time
import pandas as pd
from cfUtil_StateMachine import StateMachine

class Timeseries:
    def __init__(self, shape):
        self.sm = StateMachine(shape)
        self.referenceTime = time.time()

        # Data Structure
        self.stateDict = {
        'Time': [], 'PoseNr': [], 'Pose': [],
        'Bar Found': [], 'Bar Height': [], 'Bar Speed': [], 'Hand On Bar': [],
        'Angle KneeR': [], 'Angle KneeL': [], 'Angle HipR': [], 'Angle HipL': [], 'Angle ShoulderR': [],
        'Angle ShoulderL': [], 'Angle ElbowR': [], 'Angle ElbowL': [],
        'Height Toe': [], 'Height Ankle': [], 'Height Knee': [], 'Height Hip': [], 'Height Shoulder': [],
        'Height Elbow': [], 'Height Wrist': [], 'Height Head': [],
        'Width WristR': [], 'Width WristL': [],
        'Length Legs': [], 'Length Torso': [], 'Length Body': [],
        'Calibration Status': [], 'Calibration Leg Length': [], 'Calibration Torso Length': [],
        'Calibration Body Length': [], 'Landmarks': [] }

        self.poseDict = {'Time': [], 'PoseNr': [], 'Pose': []}

        # Extraction of log
        l = str(time.ctime()).split()
        self.tsFilename = f"Log/TimeSeriesLog{l[1]}{l[2]}-{l[3][0:2]}{l[3][3:5]}{l[3][6:8]}.csv"
        self.poseFilename = f"Log/PoseLog{l[1]}{l[2]}-{l[3][0:2]}{l[3][3:5]}{l[3][6:8]}.csv"

        self.n = 0

    def TimeseriesMain(self, img):
        mask = self.sm.pose.UpdatePose(img)
        self.BarEstAndSpeed()
        self.sm.GetState(img)
        self.LogTimeseries()

        try:
            if self.sm.state != -1 and self.sm.state != self.poseDict['PoseNr'][-1]:
                if self.sm.smCheck(self.sm.state, self.poseDict['PoseNr'][-1]):
                    self.LogPoseSeries()
        # At the start of the program there will be no entries. This catches and gives and initial value.
        except IndexError:
            self.LogPoseSeries()

        return mask

    def LogPoseSeries(self):
        self.poseDict['Time'].append(round(time.time() - self.referenceTime, 3))
        self.poseDict['PoseNr'].append(self.sm.state)
        self.poseDict['Pose'].append(self.sm.mapIntToStr[self.sm.state])


    def LogTimeseries(self):
        self.stateDict['Time'].append(round(time.time() - self.referenceTime, 3))
        self.stateDict['PoseNr'].append(self.sm.state)
        self.stateDict['Pose'].append(self.sm.mapIntToStr[self.sm.state])

        if self.sm.pose.lmAvail:
            # Bar
            self.stateDict['Bar Found'].append(self.sm.pose.barFound)
            self.stateDict['Bar Height'].append(self.sm.pose.barHeight)
            self.stateDict['Bar Speed'].append(self.barSpeed)
            if self.sm.pose.bodyCalibrated:
                self.stateDict['Hand On Bar'].append(self.sm.handOnBar)
            else:
                self.stateDict['Hand On Bar'].append(0)

            # Angles
            self.stateDict['Angle KneeR'].append(self.sm.pose.angleKneR)
            self.stateDict['Angle KneeL'].append(self.sm.pose.angleKneL)
            self.stateDict['Angle HipR'].append(self.sm.pose.angleHipR)
            self.stateDict['Angle HipL'].append(self.sm.pose.angleHipL)
            self.stateDict['Angle ShoulderR'].append(self.sm.pose.angleShoR)
            self.stateDict['Angle ShoulderL'].append(self.sm.pose.angleShoL)
            self.stateDict['Angle ElbowR'].append(self.sm.pose.angleElbR)
            self.stateDict['Angle ElbowL'].append(self.sm.pose.angleElbL)

            # Heights
            self.stateDict['Height Toe'].append(self.sm.pose.heightToe)
            self.stateDict['Height Ankle'].append(self.sm.pose.heightAnk)
            self.stateDict['Height Knee'].append(self.sm.pose.heightKne)
            self.stateDict['Height Hip'].append(self.sm.pose.heightHip)
            self.stateDict['Height Shoulder'].append(self.sm.pose.heightSho)
            self.stateDict['Height Elbow'].append(self.sm.pose.heightElb)
            self.stateDict['Height Wrist'].append(self.sm.pose.heightWrst)
            self.stateDict['Height Head'].append(self.sm.pose.heightHead)

            # Width
            self.stateDict['Width WristR'].append(self.sm.pose.widthWrstR)
            self.stateDict['Width WristL'].append(self.sm.pose.widthWrstL)

            # Lengths
            self.stateDict['Length Legs'].append(self.sm.pose.legLength)
            self.stateDict['Length Torso'].append(self.sm.pose.torsoLength)
            self.stateDict['Length Body'].append(self.sm.pose.bodyLength)
        else:
            self.stateDict['Bar Found'].append(0)
            self.stateDict['Bar Height'].append(-1)
            self.stateDict['Bar Speed'].append(-1)
            self.stateDict['Hand On Bar'].append(0)
            self.stateDict['Angle KneeR'].append(-1)
            self.stateDict['Angle KneeL'].append(-1)
            self.stateDict['Angle HipR'].append(-1)
            self.stateDict['Angle HipL'].append(-1)
            self.stateDict['Angle ShoulderR'].append(-1)
            self.stateDict['Angle ShoulderL'].append(-1)
            self.stateDict['Angle ElbowR'].append(-1)
            self.stateDict['Angle ElbowL'].append(-1)
            self.stateDict['Height Toe'].append(-1)
            self.stateDict['Height Ankle'].append(-1)
            self.stateDict['Height Knee'].append(-1)
            self.stateDict['Height Hip'].append(-1)
            self.stateDict['Height Shoulder'].append(-1)
            self.stateDict['Height Elbow'].append(-1)
            self.stateDict['Height Wrist'].append(-1)
            self.stateDict['Height Head'].append(-1)
            self.stateDict['Width WristR'].append(-1)
            self.stateDict['Width WristL'].append(-1)
            self.stateDict['Length Legs'].append(-1)
            self.stateDict['Length Torso'].append(-1)
            self.stateDict['Length Body'].append(-1)

        if self.sm.pose.bodyCalibrated:
            self.stateDict['Calibration Status'].append(self.sm.pose.bodyCalibrated)
            self.stateDict['Calibration Leg Length'].append(self.sm.pose.totalLegLength)
            self.stateDict['Calibration Torso Length'].append(self.sm.pose.totalTorsoLength)
            self.stateDict['Calibration Body Length'].append(self.sm.pose.totalBodyLength)
        else:
            self.stateDict['Calibration Status'].append(0)
            self.stateDict['Calibration Leg Length'].append(-1)
            self.stateDict['Calibration Torso Length'].append(-1)
            self.stateDict['Calibration Body Length'].append(-1)

        self.stateDict['Landmarks'].append(self.sm.pose.detector.lmList)


    def ExportTimeseries(self):
        tsDataFrame = pd.DataFrame.from_dict(self.stateDict)
        poseDataFrame = pd.DataFrame.from_dict(self.poseDict)

        tsDataFrame.to_csv(self.tsFilename)
        poseDataFrame.to_csv(self.poseFilename)


    def BarEstAndSpeed(self):
        # Time Parametrics and bar estimation.
        # If currently bar detected and bar was detected in the last frame
        try:
            if self.sm.pose.lmAvail:
                if (self.sm.pose.barHeight == -1) and (self.stateDict['Bar Height'][-1] > -1) and (self.stateDict['Hand On Bar'][-1]):
                    barToWrstDist = self.stateDict['Bar Height'][-1] - self.stateDict['Height Wrist'][-1]
                    self.sm.pose.barHeight = self.sm.pose.heightWrst + barToWrstDist
                elif (self.sm.pose.barHeight == -1) and (self.stateDict['Bar Height'][-1] > -1) and (self.stateDict['Bar Height'][-2] > -1):
                    self.barSpeed = self.stateDict['Bar Height'][-1] - self.stateDict['Bar Height'][-2]
                    self.sm.pose.barHeight = self.stateDict['Bar Height'][-1] + self.barSpeed

                if self.sm.pose.barHeight > -1 and self.stateDict['Bar Height'][-1] > -1:
                    # Calculate bar speed
                    self.barSpeed = self.sm.pose.barHeight - self.stateDict['Bar Height'][-1]
                else:
                    self.barSpeed = 0
        except:
            self.barSpeed = 0




