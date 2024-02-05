import time
import cv2
from cfUtil_Timeseries import Timeseries

class WOD:
    # Exercise to Int Mapping table

    ex2Int = {
        "Airsquat": 0, "Squat": 1, "Over Head Squat" : 2, "Deadlift": 3,
        "Clean": 4, "Power Clean": 5, "Squat Clean": 6, "Hang Clean": 7,
        "Snatch": 8, "Power Snatch": 9, "Squat Snatch": 10, "Hang Snatch": 11,
        "Press": 12, "Strict Press": 13, "Push Press": 14, "Jerk": 15
    }
    int2Ex = {
        0: "Airsquat", 1: "Squat", 2: "Over Head Squat", 3: "Deadlift",
        4: "Clean", 5: "Power Clean", 6: "Squat Clean", 7: "Hang Clean",
        8: "Snatch", 9: "Power Snatch", 10: "Squat Snatch", 11: "Hang Snatch",
        12: "Press", 13: "Strict Press", 14: "Push Press", 15: "Jerk"
    }

    mode2str = {0: "FT", 1: "AMRAP", 2: "EMOM"}
    mode2int = {"FT": 0, "AMRAP": 1, "EMOM": 2}
    wod = {}
    # Execution
    repLog = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0,
              9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
    iEx, currEx = -1, -1
    rnd, wodLength, currRep, green = 0, 0, 0, 0
    reps2Go, reps2GoLast = 0, 0
    dispColor = (255, 0, 0)

    def __init__(self, shape):
        self.shape = shape
        self.h, self.w, self.c = shape
        self.timeseries = Timeseries(shape)

    def ExecuteWOD(self, dispImg, img):
        # Static Variables
        if not self.wodLength:
            self.wodLength = len(self.wod["ex"])
            if self.wodLength == 0:
                print("No WOD loaded. Press 'l' to load WOD.")
                return False

        # Update Pose Status
        # Timeseries Stata Machine
        mask = self.timeseries.TimeseriesMain(img)

        # Get Exercise (not implemented)
        #self.Exercise. ....

        # Proxy mechanism to use keyboard instead of detected exercises to test the WOD module
        # Return exercise from Exercise module
        ex = cv2.waitKey(1)
        try:
            ex = int(chr(ex))
        except:
            ex = -1

        # Update WOD rep status
        if ex in self.repLog:
            self.repLog[ex] += 1

        # Go through WOD
        if self.reps2Go <= 0:
            self.iEx += 1
            if self.iEx >= self.wodLength:
                self.rnd += 1
                self.iEx = 0
                if self.rnd >= self.wod['rounds']:
                    # take time of finish
                    self.iEx = -1
                    self.rnd = 0
                    self.wodLength = 0
                    return False
            self.currEx = self.wod["ex"][self.iEx][0]
            self.startRep = self.repLog[self.currEx]

        self.reps2Go = (self.wod["ex"][self.iEx][1] - (self.repLog[self.currEx] - self.startRep))

        if self.reps2Go != self.reps2GoLast:
            self.dispColor = (0, 255, 0)
            self.green = 1
            self.reps2GoLast = self.reps2Go
            self.greenTimer = time.time()

        if self.green and (time.time() - self.greenTimer) > 0.5:
            self.green = 0
            self.dispColor = (255, 0, 0)

        cv2.putText(dispImg, f"{self.reps2Go} {self.int2Ex[self.currEx]}", (int(0.35 * self.w), int(0.95 * self.h)),
                    cv2.FONT_HERSHEY_PLAIN, 3, self.dispColor, 4)
        return True, mask

    def LoadWOD(self):
        # Static Variables
        line = True
        found = False
        self.wod = {}
        mmry = open("WOD/wod_bank.txt", "r+")

        # Input title of WOD to load
        print("What is the title of the WOD you want to load?")
        title = input()

        while line:
            line = mmry.readline()
            try:
                line = int(line)
            except:
                continue
            if line == 11111:
                line = mmry.readline()
                lineList = line.split()
                txtTitle = ' '.join(lineList[:-2])
                if title == txtTitle:
                    found = True
                    self.wod["title"] = txtTitle
                    self.wod["mode"] = self.mode2int[lineList[-2]]
                    self.wod["tcap"] = lineList[-1]

                    line = mmry.readline()
                    lineList = line.split()
                    self.wod["rounds"] = int(lineList[0])
                    nrEx = int(lineList[1])

                    self.wod["ex"] = []
                    for i in range(nrEx):
                        line = mmry.readline()
                        lineList = line.split()
                        self.wod["ex"].append([self.ex2Int[' '.join(lineList[1:])], int(lineList[0])])
                    print(self.wod)
                    break

        mmry.close()

        if not found:
            print("WOD not found in WOD bank")

    def InputWOD(self):
        wod = {}
        count = 0

        print("New WOD")
        # WOD Title
        while True:
            try:
                print("What is the title of the WOD?")
                wod["title"] = input()

                print(f"\nSelected WOD title is " + wod["title"] + ". Is this correct? (Yes/1, No/0)")
                confirm = int(input())
                if confirm == 1:
                    break
                print("No (0) selected or Wrong input, 1 or 0 expected. Please Try again \n")
            except:
                print("Wrong input, 1 or 0 expected. Please Try again \n")

        while True:
            try:
                print("What is the WOD format? (For Time/0, AMRAP/1), EMOM/2")
                wod["mode"] = int(input())

                if wod["mode"] == 0 or wod["mode"] == 1 or wod["mode"] == 2:
                    break
                print("Wrong input, 0, 1 or 2 expected. Please Try again \n")
            except:
                print("Wrong input, 0, 1 or 2 expected. Please Try again \n")

        # For time
        if wod["mode"] == 0:
            # time cap
            while True:
                try:
                    print("\nFor Time:")
                    print("What is the time cap? (min value: 1")
                    wod["tcap"] = int(input())

                    if wod["tcap"] >= 1:
                        break
                    print("Wrong input, 1 or larger expected. Please Try again \n")
                except:
                    print("Wrong input, 1 or larger expected. Please Try again \n")

            # Rounds
            # time cap
            while True:
                try:
                    print("How many rounds? (min value: 1)")
                    wod["rounds"] = int(input())

                    if wod["rounds"] >= 1:
                        break
                    print("Wrong input, 1 or larger expected. Please Try again \n")
                except:
                    print("Wrong input, 1 or larger expected. Please Try again \n")

            # Exercises
            wod["ex"] = []
            print("\nExercise overview:")
            print(self.ex2Int)
            while True:
                try:
                    print("\nAdd exercise: (0-15 according to table)")
                    print("Enter negative value when finished")
                    ex = int(input())
                    if ex < 0:
                        break
                    if ex > 15:
                        print("Wrong input, 0-15 expected. Please Try again \n")
                        continue
                except:
                    print("Wrong input, 0-15 expected. Please Try again \n")
                    continue

                try:
                    print("How many Repetitions: (1 or larger)")
                    reps = int(input())
                    if reps < 1:
                        print("Wrong input, 1 or larger expected. Please Try again \n")
                        continue
                except:
                    print("Wrong input, 1 or larger expected. Please Try again \n")
                    continue

                wod["ex"].append([ex, reps])
                print(f"{self.int2Ex[ex]} {reps} reps has been added to the WOD")
                count += 1

        # Save WOD
        # open file for storage. a+ type is read/write functionality with a pointer at the end of the file

        mmry = open("WOD/wod_bank.txt", "a+")
        mmry.write(
            "\n11111\n" + str(wod["title"]) + " " + str(self.mode2str[wod["mode"]]) + " " + str(wod["tcap"]) + "\n"
            + str(wod["rounds"]) + " " + str(count) + "\n")
        for e, r in wod["ex"]:
            mmry.write(f"{r} {self.int2Ex[e]}\n")

        # Display Confirmation
        print("\nThe following WOD has been saved:\n")
        print(str(wod["title"]) + " " + str(self.mode2str[wod["mode"]]) + " " + str(wod["tcap"]) + "\n" + str(
                wod["rounds"]) + " " + str(count))
        for e, r in wod["ex"]:
            print(f"{r} reps {self.int2Ex[e]}")

        mmry.close()





