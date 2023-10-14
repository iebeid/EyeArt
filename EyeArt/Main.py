import os
from Sample import Sample
from Grid import Grid
from Screen import Screen
import Utils as u
from Backend import Backend
import datetime
import pandas
import numpy as np

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

if __name__ == "__main__":
    dataDirectory = "D:/Box Sync/Work/Fall2018/HighPriority/StatisticalModelling/Data/Raw/"
    analysisDirectory = "D:/Box Sync/Work/Fall2018/HighPriority/StatisticalModelling/Data/Analysis/"
    usersFile = "UserResponses.csv"
    usersFileDataFrame = pandas.read_csv(analysisDirectory+usersFile, sep=',', na_values='.')

    userList = get_immediate_subdirectories(dataDirectory)
    # stimuli = ["S01-a-L", "S01-a-M", "S01-a-S",
    #            "S02-a-L", "S02-a-M", "S02-a-S",
    #            "S03-a-L", "S03-a-M", "S03-a-S",
    #            "S04-a-L", "S04-a-M", "S04-a-S",
    #                     "S05-a-L", "S05-a-M", "S05-a-S",
    #                     "S06-a-L", "S06-a-M", "S06-a-S",
    #                     "S07-a-L", "S07-a-M", "S07-a-S",
    #                     "S08-a-L", "S08-a-M", "S08-a-S",
    #                     "S09-a-L", "S09-a-M", "S09-a-S",
    #                     "S10-a-L", "S10-a-M", "S10-a-S",
    #                     "S11-a-L", "S11-a-M", "S11-a-S",
    #                     "S13-a-L", "S13-a-M", "S13-a-S",
    #                     "S14-a-L", "S14-a-M", "S14-a-S",
    #                     "S15-a-L", "S15-a-M", "S15-a-S",
    #                     "S16-a-L", "S16-a-M", "S16-a-S",
    #                     "S18-a-L", "S18-a-M", "S18-a-S"]
    # stimuliMain = ["S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S13","S14","S15","S16","S18"]
    stimuli = ["S01-a-L", "S01-a-M", "S01-a-S"]
    stimuliMain = ["S01"]
    screen = Screen(float("60.9"), float("40.9"), int("1920"), int("1080"), float("60.0"))
    screen.ppi = u.calculate_ppi(screen)
    screen.ipp = u.calculate_ipp(screen)
    imWidth = 1920
    imHeight = 1080
    gridWidth = 2
    gridHeight = 2
    forbiddenUsers = ["P02","P06"]

    # for index, row in usersFileDataFrame.iterrows():
    #     user = row['Participant']
    #     gender = row['Gender']
    #     stimulus = row['Stimulus']
    #     recognized = row['Recognized']

    userCount = 1
    maleUserID = 1
    femaleUserID = 1
    data = []
    for user in userList:
        if user not in forbiddenUsers:
            # print("User: " + user)
            grid = Grid(screen.screenResolutionHeight, screen.screenResolutionWidth, imHeight, imWidth, gridWidth,
                        gridHeight)
            backend = Backend(75, 0.5, screen, 10.0, 100, grid)
            filename = dataDirectory + user + "/offline.txt"
            fread = open(filename, "r")
            sampleCounter = 0
            skip = 0
            skipLines = 200
            for line in fread:
                skip = skip + 1
                if skip > skipLines:
                    parsedMessage = line.split("\t")
                    stimulusName = str(parsedMessage[6]).strip().rstrip()
                    if stimulusName in stimuli:
                        sampleCounter = sampleCounter + 1
                        timestamp = int(parsedMessage[12])
                        gazeLeftX = float(parsedMessage[13].strip().rstrip())
                        gazeLeftY = float(parsedMessage[14].strip().rstrip())
                        gazeRightX = float(parsedMessage[15].strip().rstrip())
                        gazeRightY = float(parsedMessage[16].strip().rstrip())
                        leftPupilDiameter = float(parsedMessage[17].strip().rstrip())
                        rightPupilDiameter = float(parsedMessage[18].strip().rstrip())
                        leftEyeDistance = float(parsedMessage[19].strip().rstrip())
                        rightEyeDistance = float(parsedMessage[20].strip().rstrip())
                        sample = Sample(sampleCounter, stimulusName,
                                        timestamp, gazeLeftX, gazeLeftY,
                                        gazeRightX, gazeRightY, leftPupilDiameter,
                                        rightPupilDiameter, leftEyeDistance, rightEyeDistance)
                        if parsedMessage[27]:
                            sample.gazePointX = float(parsedMessage[27])
                        else:
                            sample.gazePointX = 0.0

                        if parsedMessage[28]:
                            sample.gazePointY = float(parsedMessage[28])
                        else:
                            sample.gazePointY = 0.0

                            sample.leftEyeDistance = leftEyeDistance
                            sample.rightEyeDistance = rightEyeDistance
                            sample.find_eye_to_screen_distance()
                        if parsedMessage[30]:
                            sample.filteredGazePointX = float(parsedMessage[30])
                        else:
                            sample.filteredGazePointX = 0.0

                        if parsedMessage[31]:
                            sample.filteredGazePointY = float(parsedMessage[31])
                        else:
                            sample.filteredGazePointY = 0.0

                        if parsedMessage[32]:
                            sample.gazeEventType = str(parsedMessage[32].strip().rstrip())
                        else:
                            sample.gazeEventType = ""

                        if parsedMessage[33]:
                            sample.filteredInterSampleVelocity = float(parsedMessage[33])
                        else:
                            sample.filteredInterSampleVelocity = 0.0

                        if parsedMessage[41]:
                            sample.gazeEventDuration = float(parsedMessage[41].strip().rstrip())
                        else:
                            sample.gazeEventDuration = 0

                        if parsedMessage[38]:
                            sample.gazeEventX = float(parsedMessage[38].strip().rstrip())
                        else:
                            sample.gazeEventX = 0

                        if parsedMessage[39]:
                            sample.gazeEventY = float(parsedMessage[39].strip().rstrip())
                        else:
                            sample.gazeEventY = 0

                        sample.gazeAOI = grid.check_sample_in_grid(sample.filteredGazePointX,
                                                                   sample.filteredGazePointY)

                        backend.find_fixations_offline(sample)

            backend.process_fixations_offline()
            states = np.array(backend.states)
            print(userCount)
            print(states)
            gender = 0
            recognized = 0
            genderdf = ""
            recognizeddf = ""
            for index, row in usersFileDataFrame.iterrows():
                userdf = row['Participant']
                stimulusdf = row['Stimulus']
                if (str(userdf) == str(user)) and (str(stimulusdf) == stimuliMain):
                    recognizeddf = row['Recognized']
                    genderdf = row['Gender']


            if genderdf == "Female":
                gender = 1
                femaleUserID = femaleUserID + 1
            else:
                gender = 2
                maleUserID = maleUserID + 1

            if recognizeddf == "Yes":
                recognized = 1
            else:
                recognized = 2

            stateCounter = 0
            previousState = 0
            currentState = 0
            datarow = []
            for state in backend.states:
                stateCounter = stateCounter + 1
                if stateCounter == 1:
                    currentState = state
                    previousState = currentState
                else:
                    currentState = state
                    # if gender == 1:
                    #     datarow = [femaleUserID, gender, recognized, previousState, currentState]
                    # if gender == 2:
                    # datarow = [userCount, gender, recognized, previousState, currentState]
                    datarow = [userCount, recognized, previousState, currentState]
                    data.append(datarow)
                    previousState = currentState

            userCount = userCount + 1

    # print(data)
    df = pandas.DataFrame.from_records(data)
    dataFrameFile = "D:/Box Sync/Work/Fall2018/HighPriority/StatisticalModelling/Code/Reference/Data_Set.csv"
    df.to_csv(dataFrameFile, sep=',', encoding='utf-8', index=False, header=False)
    # todays_date = datetime.datetime.now().date()
    # index = pandas.date_range(todays_date - datetime.timedelta(10), periods=10, freq='D')
    # columns = ['UserID', 'Recognized', 'Gender', 'Ytminus1', 'Yt']
    # newDataFrame = pandas.DataFrame(index=index, columns=columns)
    # newDataFrame = newDataFrame.fillna(0)  # with 0s rather than NaNs
    # for index, row in newDataFrame.iterrows():
    #     print(row['UserID'])