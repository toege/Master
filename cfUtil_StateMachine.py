import time
import cv2
from cfUtil_Pose import Pose


class StateMachine:
    mapStrToInt = {'Standing': 0, 'Crouched': 1, 'Air Squat': 2, 'Start Position': 3, 'Hip Standing': 4,
                   'Hip Crouching': 5, 'Shoulder Standing': 6, 'Shoulder Crouching': 7, 'Shoulder Squatting': 8,
                   'Over Head Standing': 9, 'Over Head Crouching': 10, 'Over Head Squatting': 11, 'Na': -1}


    mapIntToStr = {0: 'Standing', 1: 'Crouched', 2: 'Air Squat', 3: 'Start Position', 4: 'Hip Standing',
                   5: 'Hip Crouching', 6: 'Shoulder Standing', 7: 'Shoulder Crouching', 8: 'Shoulder Squatting',
                   9: 'Over Head Standing', 10: 'Over Head Crouching', 11: 'Over Head Squatting', -1: 'Na'}

    stateMachine = {0: [1], 1: [0, 2, 3], 2: [1, 3], 3: [1, 2, 4, 5], 4: [0, 1, 3, 5, 6, 7, 8],
                    5: [0, 1, 3, 4, 6, 7, 8], 6: [0, 1, 4, 5, 7, 8, 9, 10, 11], 7: [0, 1, 2, 4, 5, 6, 8],
                    8: [1, 2, 3, 4, 5, 6, 7], 9: [0, 1, 5, 6, 7, 10, 11], 10: [0, 1, 2, 5, 6, 7, 8, 9, 11],
                    11: [0, 1, 2, 5, 6, 7, 8, 10], -1: [0, 1, 3]}

    def __init__(self, shape):
        self.shape = shape
        self.h, self.w, self.c = shape

        self.pose = Pose(shape)
        self.state = -1

    def smCheck(self, stateFrom, stateTo):
        return stateTo in self.stateMachine[stateFrom]

    def GetState(self, img):
        color = (255, 0, 0)
        if self.pose.lmAvail and self.pose.bodyCalibrated:
            self.GetSubStates()

            # Default no result state is -1
            self.state = -1
            # With barbell
            if self.handOnBar:
                color = (0, 255, 0)
                # Barbell on Ground
                if self.barOnGround:
                    self.state = 3
                elif self.barHip and self.standing:
                    self.state = 4

                elif self.barShoulder:
                    if self.standing:
                        self.state = 5
                    if self.crouching:
                        self.state = 6
                    elif self.squatting:
                        self.state = 7

                elif self.barOverHead:
                    if self.standing and ((self.grip and self.armsWideStraight) or (self.armsStraight and not self.grip)):
                        self.state = 8
                    elif self.crouching and ((self.grip and self.armsWideStraight) or (self.armsStraight and not self.grip)):
                        self.state = 9
                    elif self.squatting and ((self.grip and self.armsWideStraight) or (self.armsStraight and not self.grip)):
                        self.state = 10

            # No barbell
            else:
                if self.standing:
                    self.state = 0
                elif self.crouching:
                    self.state = 1
                if self.squatting:
                    self.state = 2

        cv2.putText(img, self.mapIntToStr[self.state], (int(0.45*self.w), int(0.95*self.h)),
                    cv2.FONT_HERSHEY_PLAIN, 6, color, 4)


    def GetSubStates(self):
        # Boolean variables describing sub-states
        # Legs
        self.legsBent = self.pose.legLength < (self.pose.totalLegLength - self.pose.heightThreshold)

        self.legsStraight = (self.pose.legLength < (self.pose.totalLegLength + self.pose.heightThreshold) and
                            self.pose.legLength > (self.pose.totalLegLength - self.pose.heightThreshold) and
                           (self.pose.angleKneL < 200 and self.pose.angleKneL > 160 and self.pose.angleKneR < 200 and
                            self.pose.angleKneR > 160))

        # Hips
        self.hipUnderKnee = self.pose.heightHip < (self.pose.heightKne + self.pose.heightThreshold)

        # Torso
        self.torsoBent = self.pose.torsoLength < (self.pose.totalTorsoLength - self.pose.heightThreshold)

        self.torsoStraight = (self.pose.torsoLength < (self.pose.totalTorsoLength + self.pose.heightThreshold) and
                              self.pose.torsoLength > (self.pose.totalTorsoLength - self.pose.heightThreshold))

        # Arms
        self.leftArmStraight =  ((self.pose.angleElbL < (175 + self.pose.angleThreshold)) and
                                   (self.pose.angleElbL > (175 - self.pose.angleThreshold)))
        self.rightArmStraight = ((self.pose.angleElbR < (175 + self.pose.angleThreshold)) and
                                   (self.pose.angleElbR > (175 - self.pose.angleThreshold)))
        self.armsStraight = self.leftArmStraight and self.rightArmStraight

        self.leftArmWideStraigh = (self.pose.angleElbL < (165 + 20)) and (self.pose.angleElbL > (165 - 20))
        self.rightArmWideStraight = (self.pose.angleElbR < (165 + 20)) and (self.pose.angleElbR > (165 - 20))
        self.armsWideStraight = self.leftArmWideStraigh and self.rightArmWideStraight

        # Wrists/Hands
        self.handOnBar = ((self.pose.barHeight + 4 * self.pose.heightThreshold) > self.pose.heightWrst) and ((self.pose.barHeight - 4 * self.pose.heightThreshold) < self.pose.heightWrst)

        if self.handOnBar:
            shoulderWidth = abs(self.pose.widthShoR - self.pose.widthShoL)
            gripWidth = abs(self.pose.widthWrstR - self.pose.widthWrstL)
            if gripWidth > 2.2 * shoulderWidth:
                self.grip = 1 # Wide Grip
            else:
                self.grip = 0 # Narrow Grip

        # Body
        self.standing = self.pose.bodyLength > (self.pose.totalBodyLength - self.pose.heightThreshold)
        self.crouching = self.legsBent and not self.hipUnderKnee
        self.squatting = self.legsBent and self.hipUnderKnee

        midThightHeight = (self.pose.heightKne + self.pose.heightHip) / 2

        # Bar
        self.barOnGround = ((self.pose.heightKne + self.pose.heightAnk)/2.2) > self.pose.barHeight
        self.barHip = (self.pose.heightHip > self.pose.barHeight) and (midThightHeight < self.pose.barHeight)
        self.barShoulder = (self.pose.barHeight < (self.pose.heightSho + 2 * self.pose.heightThreshold) and
                            self.pose.barHeight > (self.pose.heightSho - 2 * self.pose.heightThreshold))
        self.barOverHead = self.pose.barHeight > self.pose.heightHead + self.pose.heightThreshold

