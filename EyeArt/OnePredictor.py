import os
from Sample import Sample
from Grid import Grid
from Screen import Screen
import Utils as u
from Backend import Backend
import pandas
import numpy

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def process_sample(line,stimuli,sampleCounter,grid,backend):
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
    return backend

def find_users_data(user,analysisDirectory):
    usersStimuliFile = "UsersStimuli.csv"
    usersStimuliFileDataFrame = pandas.read_csv(analysisDirectory + usersStimuliFile, sep=',', na_values='.')
    recognition = 0
    for index, row in usersStimuliFileDataFrame.iterrows():
        participant = row['Participant']
        gender = row['Gender']
        stimulus = row['Stimulus']
        recognized = row['Recognized']
        correctly = row['Correctly']
        if (user == participant) and (stimulus == "S01"):
            if (recognized == "Yes") and (correctly == "Yes"):
                recognition = 1
            else:
                recognition = 2
    return recognition

if __name__ == "__main__":
    dataDirectory = "D:/Box Sync/Work/Fall2018/HighPriority/StatisticalModelling/Data/Raw/"
    analysisDirectory = "D:/Box Sync/Work/Fall2018/HighPriority/StatisticalModelling/Data/Analysis/"
    usersFile = "Users.csv"
    usersFileDataFrame = pandas.read_csv(analysisDirectory + usersFile, sep=',', na_values='.')
    userData = get_immediate_subdirectories(dataDirectory)
    forbiddenUsers = ["P02", "P06"]
    stimuli = ["S01-a-L", "S01-a-M", "S01-a-S"]
    genderCode = 0
    maleCode = 0
    femaleCode = 0
    data = []
    screen = Screen(float("60.9"), float("40.9"), int("1920"), int("1080"), float("60.0"))
    screen.ppi = u.calculate_ppi(screen)
    screen.ipp = u.calculate_ipp(screen)
    imWidth = 1920
    imHeight = 1080
    gridWidth = 2
    gridHeight = 2

    for index, row in usersFileDataFrame.iterrows():
        user = row['ID']
        age = row['Age']
        gender = row['Gender']
        if user not in forbiddenUsers:
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
                    sampleCounter = sampleCounter + 1
                    backend = process_sample(line,stimuli,sampleCounter,grid,backend)
            backend.process_fixations_offline()
            genderCode = 1
            femaleCode = femaleCode + 1
            recognition = find_users_data(user,analysisDirectory)
            datarow = []
            stateCounter = 0
            currentState = 0
            previousState = 0
            for state in backend.states:
                stateCounter = stateCounter + 1
                if stateCounter == 1:
                    currentState = state
                    previousState = currentState
                else:
                    currentState = state
                    datarow = [femaleCode, recognition, previousState, currentState]
                    data.append(datarow)
                    previousState = currentState

    print(data)
    df = pandas.DataFrame.from_records(data)
    dataFrameFile = "D:/Box Sync/Work/Fall2018/HighPriority/StatisticalModelling/Code/Reference/Data_Set_Single_Predictor.csv"
    df.to_csv(dataFrameFile, sep=',', encoding='utf-8', index=False, header=False)