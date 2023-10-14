
from Backend import Backend

import os
import re
import numpy
import pandas

import rpy2.robjects as robjects

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

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

def check_markov_property(sequence):
    r = robjects.r
    r.source("testforgeneral.r")
    x = robjects.IntVector(sequence)
    r_test_sequence = robjects.globalenv['main']
    p_value_string=r_test_sequence(x)
    p_value_extracted = re.findall("\d+\.\d+\d+", str(p_value_string))
    p_value = 1.0
    if len(p_value_extracted) == 1:
        p_value = float(p_value_extracted[0])
    return p_value

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

def main():
    numpy.set_printoptions(threshold=numpy.nan)
    #Data paths
    dataDirectory = "D:/Box Sync/Spring2019/BayesianEyeTracking(Abhra)/Data/Raw/"
    analysisDirectory = "D:/Box Sync/Spring2019/BayesianEyeTracking(Abhra)/Data/Global/"
    #Load user data
    usersFile = "Users.csv"
    usersFileDataFrame = pandas.read_csv(analysisDirectory + usersFile, sep=',', na_values='.')
    userData = get_immediate_subdirectories(dataDirectory)
    forbiddenUsers = ["P02","P06"]
    #Load stimuli data
    stimuliFile = "EyeArt_stimulus.csv"
    stimuliDataFrame = pandas.read_csv(analysisDirectory + stimuliFile, sep=',', na_values='.')
    #data
    data = []
    userId = 0
    stats = []
    #Loop on users
    for index, row in usersFileDataFrame.iterrows():
        user = row['ID']
        age = row['Age']
        gender = row['Gender']
        if user not in forbiddenUsers:
            print("------------------")
            print("User: " + str(user) + " | Age: " + str(age) + " | Gender: " + str(gender))
            print("------------------")
            filename = dataDirectory + user + "/offline.txt"
            userId = userId + 1
            sparseCounter = 0
            nonMarkovianSequence = 0
            recognizedStimuliCounter = 0
            notRecognizedStimuliCounter = 0
            artworkTypeCounter = 0
            landmarkTypeCounter = 0
            trialID = 0
            for index, row in stimuliDataFrame.iterrows():
                trialID = trialID + 1
                stimuliName = row['stimulus_id']
                type = row['type']
                recognition = find_users_data(user, analysisDirectory, stimuliName)
                typeCode = 0
                if str(type) == "Artwork":
                    typeCode = 1

                if str(type) == "Landmark":
                    typeCode = 2

                print("Stimulus Name: " + str(stimuliName) + " | Trial: " + str(trialID) + " | Recognition: " + str(recognition) + " | Type: " + str(
                    type) + " | Type Code: " + str(typeCode))
                #AOI Grid and fixation settings
                maximumTimeBetweenFixations = 75
                maxAngleBetweenFixations = 0.5
                processingWindow = 3.0
                shortFixaitonThreshold = 60
                screenWidth = 60.9
                screenHeight = 40.9
                screenResolutionWidth = 1920
                screenResolutionHeight = 1080
                defaultDistanceToScreen = 60.0
                skip = 200
                imWidth = int(row['width'])
                imHeight = int(row['height'])
                gridWidth = 2
                gridHeight = 2
                pValueForFirstOrderMarkovNullHypothesis = 0.01
                stimuli = [stimuliName + "-a-L", stimuliName + "-a-M", stimuliName + "-a-S"]
                fread = open(filename, "r")
                backend = Backend(maximumTimeBetweenFixations, maxAngleBetweenFixations,
                                  screenWidth, screenHeight, screenResolutionWidth,
                                  screenResolutionHeight, defaultDistanceToScreen,
                                  processingWindow, shortFixaitonThreshold, imHeight,
                                  imWidth, gridWidth, gridHeight, fread, stimuli, skip)
                fread.close()
                print(str(numpy.array(backend.states)))
                sequenceSparse = check_sequence_sparse(backend.states, gridWidth, gridHeight)
                if not sequenceSparse:
                    sparseCounter = sparseCounter + 1
                    markovian = check_markov_property(backend.states)
                    if (markovian > pValueForFirstOrderMarkovNullHypothesis) and (markovian != 1.0):
                        if typeCode == 1:
                            artworkTypeCounter = artworkTypeCounter + 1
                        if typeCode == 2:
                            landmarkTypeCounter = landmarkTypeCounter + 1
                        if recognition == 1:
                            recognizedStimuliCounter = recognizedStimuliCounter + 1
                        if recognition == 2:
                            notRecognizedStimuliCounter = notRecognizedStimuliCounter + 1
                        print("A first order Markov chain is likely to fit the sequence")
                        nonMarkovianSequence = nonMarkovianSequence + 1
                        stateCounter = 0
                        currentState = 0
                        previousState = 0
                        for state in backend.states:
                            stateCounter = stateCounter + 1
                            if stateCounter == 1:
                                currentState = state
                                previousState = currentState
                                datarow = [userId, trialID, typeCode, recognition, previousState, currentState]
                                data.append(datarow)
                            else:
                                currentState = state
                                datarow = [userId, trialID, typeCode, recognition, previousState, currentState]
                                data.append(datarow)
                                previousState = currentState
                    else:
                        print("A higher order Markov chain is likely to fit the sequence")
                else:
                    print("Warning: Sparse sequence")
                    continue
            statsDataRow = [userId, age, gender, sparseCounter, nonMarkovianSequence, recognizedStimuliCounter, notRecognizedStimuliCounter, artworkTypeCounter, landmarkTypeCounter]
            stats.append(statsDataRow)
    df = pandas.DataFrame.from_records(data)
    dataFrameFile = "Data_Set_Normal_Trial.csv"
    df.to_csv(dataFrameFile, sep=',', encoding='utf-8', index=False, header=False)
    df = pandas.DataFrame.from_records(stats)
    statsFile = "Stats.csv"
    df.to_csv(statsFile, sep=',', encoding='utf-8', index=False, header=False)

if __name__ == "__main__":
    main()