import os
from Sample import Sample
from Grid import Grid
from Screen import Screen
import Utils as u
from Backend import Backend
import pandas
import numpy
import rpy2.robjects as robjects
import re

def check_markov_property(sequence):
    r = robjects.r
    r.source("testforgeneral.r")
    # r["main(sequence)"]
    x= robjects.IntVector(sequence)
    r_test_sequence = robjects.globalenv['main']
    p_value_string=r_test_sequence(x)
    p_value_extracted = re.findall("\d+\.\d+\d+", str(p_value_string))
    # p_value = float(p_value_extracted[0])
    return p_value_extracted

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

def find_users_data(user,analysisDirectory,stimulusName):
    usersStimuliFile = "UsersStimuli.csv"
    usersStimuliFileDataFrame = pandas.read_csv(analysisDirectory + usersStimuliFile, sep=',', na_values='.')
    recognition = 0
    for index, row in usersStimuliFileDataFrame.iterrows():
        participant = row['Participant']
        gender = row['Gender']
        stimulus = row['Stimulus']
        recognized = row['Recognized']
        correctly = row['Correctly']
        if (user == participant) and (stimulus == stimulusName):
            if (recognized == "Yes") and (correctly == "Yes"):
                recognition = 1
            else:
                recognition = 2
    return recognition

def f7(states):
    seen = set()
    seen_add = seen.add
    return [x for x in states if not (x in seen or seen_add(x))]

def check_sequence_sparse(sequence,gridWidth, gridHeight):
    sequenceSparse = True
    stateSpace = gridWidth * gridHeight
    uniqueOrderedList = f7(sequence)
    fixedStates = []
    for state in sequence:
        indexOfState = uniqueOrderedList.index(state) + 1
        fixedStates.append(indexOfState)
    maximumStateInOrderedList = max(fixedStates)
    if stateSpace == maximumStateInOrderedList:
        sequenceSparse = False
    return sequenceSparse

def fix_states(states):
    print(states)
    uniqueOrderedList = f7(states)
    fixedStates = []
    for state in states:
        indexOfState = uniqueOrderedList.index(state) + 1
        fixedStates.append(indexOfState)
    return fixedStates

def generate_sequence(state,states):
    generatedSequence = []
    for s in states:
        generatedSequence.append(state)
        generatedSequence.append(s)

    return generatedSequence

def represent_states(sequence, numberOfStates):
    uniqueOrderedList = f7(sequence)
    states = numpy.arange(1, numberOfStates, 1)
    generatedSequence = []
    for s in states:
        if s not in uniqueOrderedList:
            generatedSequence = generatedSequence + generate_sequence(s,states)
    fullSequence = sequence + generatedSequence
    return fullSequence

# method to print the divisors
def findDivisors(n) :
    divisors = []
    i = 1
    while i <= n :
        if (n % i==0) :
            divisors.append(i)
        i = i + 1
    return divisors

def main():
    numpy.set_printoptions(threshold=numpy.nan)
    dataDirectory = "D:/Box Sync/Spring2019/ETRA2019/Data/Raw/"
    analysisDirectory = "D:/Box Sync/Spring2019/ETRA2019/Data/Analysis/"
    usersFile = "Users.csv"
    usersFileDataFrame = pandas.read_csv(analysisDirectory + usersFile, sep=',', na_values='.')
    userData = get_immediate_subdirectories(dataDirectory)
    # forbiddenUsers = ["P02","P06","P07","P11","P15","P17","P20"]
    forbiddenUsers = ["P02","P06"]

    stimuliFile = "EyeArt_stimulus.csv"
    stimuliDataFrame = pandas.read_csv(analysisDirectory + stimuliFile, sep=',', na_values='.')
    for index, row in stimuliDataFrame.iterrows():
        stimuliName = row['stimulus_id']
        print(stimuliName)
        stimuli = [stimuliName + "-a-L", stimuliName + "-a-M", stimuliName + "-a-S"]
        genderCode = 0
        maleCode = 0
        femaleCode = 0
        data = []
        screen = Screen(float("60.9"), float("40.9"), int("1920"), int("1080"), float("60.0"))
        screen.ppi = u.calculate_ppi(screen)
        screen.ipp = u.calculate_ipp(screen)

        imWidth = int(row['width'])
        imHeight = int(row['height'])
        gridWidth = 8
        gridHeight = 8
        maximumTimeBetweenFixations = 75
        maxAngleBetweenFixations = 0.5
        processingWindow = 3.0
        shortFixaitonThreshold = 60

        for index, row in usersFileDataFrame.iterrows():
            user = row['ID']
            age = row['Age']
            gender = row['Gender']
            if user not in forbiddenUsers:
                if gender == "Female":
                    grid = Grid(screen.screenResolutionHeight, screen.screenResolutionWidth, imHeight, imWidth, gridWidth, gridHeight)
                    backend = Backend(maximumTimeBetweenFixations, maxAngleBetweenFixations, screen, processingWindow, shortFixaitonThreshold, grid)
                    filename = dataDirectory + user + "/offline.txt"
                    fread = open(filename, "r")
                    sampleCounter = 0
                    skip = 0
                    skipLines = 200
                    for line in fread:
                        skip = skip + 1
                        if skip > skipLines:
                            sampleCounter = sampleCounter + 1
                            backend = process_sample(line, stimuli, sampleCounter, grid, backend)
                    backend.process_fixations_offline()
                    sequenceSparse = check_sequence_sparse(backend.states,gridWidth,gridHeight)
                    sequenceSparse = False
                    if not sequenceSparse:
                        genderCode = 1
                        femaleCode = femaleCode + 1
                        recognition = find_users_data(user, analysisDirectory, stimuliName)
                        datarow = []
                        stateCounter = 0
                        currentState = 0
                        previousState = 0
                        print(user)
                        print(genderCode)
                        print(str(numpy.array(backend.states)))
                        # fixedStates = fix_states(backend.states)
                        fixedStates = represent_states(backend.states,int(gridWidth*gridHeight))
                        print(str(str(numpy.array(fixedStates))))
                        print(check_markov_property(fixedStates))
                        for state in fixedStates:
                            stateCounter = stateCounter + 1
                            if stateCounter == 1:
                                currentState = state
                                previousState = currentState
                                datarow = [femaleCode, genderCode, recognition, previousState, currentState]
                                data.append(datarow)
                            else:
                                currentState = state
                                datarow = [femaleCode, genderCode, recognition, previousState, currentState]
                                data.append(datarow)
                                previousState = currentState
                    else:
                        continue

        for index, row in usersFileDataFrame.iterrows():
            user = row['ID']
            age = row['Age']
            gender = row['Gender']
            if user not in forbiddenUsers:
                if gender == "Male":
                    grid = Grid(screen.screenResolutionHeight, screen.screenResolutionWidth, imHeight, imWidth, gridWidth, gridHeight)
                    backend = Backend(maximumTimeBetweenFixations, maxAngleBetweenFixations, screen, processingWindow, shortFixaitonThreshold, grid)
                    filename = dataDirectory + user + "/offline.txt"
                    fread = open(filename, "r")
                    sampleCounter = 0
                    skip = 0
                    skipLines = 200
                    for line in fread:
                        skip = skip + 1
                        if skip > skipLines:
                            sampleCounter = sampleCounter + 1
                            backend = process_sample(line, stimuli, sampleCounter, grid, backend)
                    backend.process_fixations_offline()
                    sequenceSparse = check_sequence_sparse(backend.states,gridWidth,gridHeight)
                    sequenceSparse = False
                    if not sequenceSparse:
                        genderCode = 2
                        maleCode = maleCode + 1
                        recognition = find_users_data(user, analysisDirectory, stimuliName)
                        datarow = []
                        stateCounter = 0
                        currentState = 0
                        previousState = 0
                        print(user)
                        print(genderCode)
                        print(str(numpy.array(backend.states)))
                        # fixedStates = fix_states(backend.states)
                        fixedStates = represent_states(backend.states,int(gridWidth*gridHeight))
                        print(str(numpy.array(fixedStates)))
                        print(check_markov_property(fixedStates))
                        for state in fixedStates:
                            stateCounter = stateCounter + 1
                            if stateCounter == 1:
                                currentState = state
                                previousState = currentState
                                datarow = [maleCode, genderCode, recognition, previousState, currentState]
                                data.append(datarow)
                            else:
                                currentState = state
                                datarow = [maleCode, genderCode, recognition, previousState, currentState]
                                data.append(datarow)
                                previousState = currentState
                    else:
                        continue

        df = pandas.DataFrame.from_records(data)
        dataFrameFile = "Data_Set"+str(stimuliName)+".csv"
        df.to_csv(dataFrameFile, sep=',', encoding='utf-8', index=False, header=False)

if __name__ == "__main__":
    # list1 = findDivisors(1050)
    # print(list1)
    # print("-------------")
    # list2 = findDivisors(700)
    # print(list2)
    # print("-------------")
    # commonDivisorList = list(set(list1).intersection(list2))
    # commonDivisorList.sort()
    # print(commonDivisorList)
    # for div in commonDivisorList:
    #     print(str(700/div) + " X " + str(1050/div))
    main()