import time
import cv2

class TimeModule:
    def __init__(self):
        self.pTime = 0
        self.ftWatchMode = 0
        self.amWatchMode = 0
        self.emWatchMode = 0
        self.emRound = 1

    def GetFps(self, img, draw=True):
        cTime = time.time()
        fps = 1 / (cTime - self.pTime)
        self.pTime = cTime
        if draw:
            cv2.putText(img, str(int(fps)), (50, 100), cv2.FONT_HERSHEY_PLAIN,
                        2, (255, 0, 0), 2)

    def FT(self, img, tCap=10, text=True):
        # Static Variables
        cTime = time.time()

        # If clock is off then initiate start sequence
        if self.ftWatchMode == 0:
            self.hi, self.w, self.c = img.shape
            self.ftStartTime = time.time()
            self.ftWatchMode = 1

        # If start countdown mode
        if self.ftWatchMode == 1:
            self.ftSec = int(11 - (cTime - self.ftStartTime))

            cv2.putText(img, f"FT {tCap}:", (int(self.w*0.35), int(self.hi*0.1) ),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(img, f"{self.ftSec}", (int(self.w * 0.55), int(self.hi * 0.1)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            if self.ftSec <= 0:
                self.ftWatchMode = 2
                self.ftStartTime = time.time()

        # If clock running mode
        if self.ftWatchMode == 2:
            tDiff = cTime - self.ftStartTime

            if tDiff >= 60*tCap:
                self.ftWatchMode = 0
                return False

            self.ftSec = int(tDiff %  60)
            self.ftMin = int(tDiff // 60)

            # Text Format
            if self.ftMin < 10:
                if self.ftSec < 10:
                    txt = f'0{self.ftMin}:0{self.ftSec}'
                else:
                    txt = f'0{self.ftMin}:{self.ftSec}'
            else:
                if self.ftSec < 10:
                    txt = f'{self.ftMin}:0{self.ftSec}'
                else:
                    txt = f'{self.ftMin}:{self.ftSec}'

            cv2.putText(img, txt, (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        return True

    def AMRAP(self, img, tCap, text=True):
        # Static Variables
        cTime = time.time()

        # If clock is off then initiate start sequence
        if self.amWatchMode == 0:
            self.hi, self.w, self.c = img.shape
            self.amStartTime = time.time()
            self.amWatchMode = 1

        # If start countdown mode
        if self.amWatchMode == 1:
            self.amSec = int(11 - (cTime - self.amStartTime))

            cv2.putText(img, f"AMRAP {tCap}:", (int(self.w*0.35), int(self.hi*0.15) ), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(img, f"{self.amSec}", (int(self.w * 0.55), int(self.hi * 0.15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            if self.amSec <= 0:
                self.amWatchMode = 2
                self.amStartTime = time.time()

        # If clock running mode
        if self.amWatchMode == 2:
            tRemain = 60*tCap - (cTime - self.amStartTime)

            if tRemain <= 0:
                self.amWatchMode = 0
                return False

            self.amSec = int(tRemain % 60)
            self.amMin = int(tRemain // 60)

            # Text Format
            if self.amMin < 10:
                if self.amSec< 10:
                    txt = f'0{self.amMin}:0{self.amSec}'
                else:
                    txt = f'0{self.amMin}:{self.amSec}'
            else:
                if self.amSec < 10:
                    txt = f'{self.amMin}:0{self.amSec}'
                else:
                    txt = f'{self.amMin}:{self.amSec}'

            cv2.putText(img, txt, (self.w - 150, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        return True

    def EMOM(self, img, interval=1, rounds=10, text=True):
        # Static Variables
        cTime = time.time()

        # If clock is off then initiate start sequence
        if self.emWatchMode == 0:
            self.hi, self.w, self.c = img.shape

            self.emStartTime = time.time()
            self.emWatchMode = 1

        # If start countdown mode
        if self.emWatchMode == 1:
            self.emSec = int(11 - (cTime - self.emStartTime))

            if interval != 1:
                cv2.putText(img, f"E{interval}MOM:", (int(self.w * 0.35), int(self.hi * 0.20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(img, f"{self.emSec}", (int(self.w * 0.55), int(self.hi * 0.20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(img, f"EMOM:", (int(self.w * 0.35), int(self.hi * 0.20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(img, f"{self.emSec}", (int(self.w * 0.55), int(self.hi * 0.20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if self.emSec <= 0:
                self.emWatchMode = 2
                self.emStartTime = time.time()

        # If clock running mode
        if self.emWatchMode == 2:
            tRemain = 60 * interval * self.emRound - (cTime - self.emStartTime)

            if tRemain <= 0:
                self.emRound += 1
                if self.emRound > rounds:
                    self.emRound = 1
                    self.emWatchMode = 0
                    return False
                return True

            self.emSec = int(tRemain % 60)
            self.emMin = int(tRemain // 60)

            # Text Format
            if self.emMin < 10:
                if self.emSec < 10:
                    txt = f'0{self.emMin}:0{self.emSec}'
                else:
                    txt = f'0{self.emMin}:{self.emSec}'
            else:
                if self.emSec < 10:
                    txt = f'{self.emMin}:0{self.emSec}'
                else:
                    txt = f'{self.emMin}:{self.emSec}'

            if interval != 1:
                cv2.putText(img, f"E{interval}MOM: {self.emRound}", (self.w - 400, 75), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                cv2.putText(img, txt, (self.w - 150, 75), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            else:
                cv2.putText(img, str(self.emRound), (self.w - 180, 75), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                cv2.putText(img, txt, (self.w - 150, 75), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        return True



