import copy
import time
import math
import numpy
from threading import Thread
import Utils as u
from Sample import Sample
from Grid import Grid
from Screen import Screen
from Fixation import Fixation
from TransitionMatrix import TransitionMatrix

class Backend:
    def __init__(self, maximumTimeBetweenFixations, maxAngleBetweenFixations,
                 screenWidth, screenHeight, screenResolutionWidth, screenResolutionHeight,
                 defaultDistanceToScreen, processingWindow, shortFixaitonThreshold,
                 imHeight, imWidth, gridWidth, gridHeight, datafile, stimuli, skip):

        self.maximumTimeBetweenFixations = maximumTimeBetweenFixations
        self.maxAngleBetweenFixations = maxAngleBetweenFixations
        self.shortFixaitonThreshold = shortFixaitonThreshold
        self.processingWindow = processingWindow
        self.fread = datafile
        self.stimuli = stimuli
        self.skipLines = skip

        self.screen = Screen(screenWidth, screenHeight, screenResolutionWidth, screenResolutionHeight, defaultDistanceToScreen)
        self.grid = Grid(screenResolutionHeight, screenResolutionWidth, imHeight, imWidth, gridWidth, gridHeight)

        self.sample = Sample()
        self.currentSample = Sample()
        self.previousSample = Sample()
        self.currentFixation = Fixation()
        self.previousFixation = Fixation()
        self.transitionMatrix = TransitionMatrix(0, [])
        self.windowTransitionMatrix = TransitionMatrix(0, [])
        self.latestFixation = Fixation()
        self.numberOfStates = self.grid.grid_width * self.grid.grid_height
        self.numberOfSamplesInAProcessingWindow = u.compute_window_size(self.processingWindow * 1000)
        self.fixation = []
        self.fixations = []
        self.states = []
        self.windowStates = []
        self.transitions = []
        self.startOfFixation = False
        self.endBackendOperations = False
        self.fixationCounter = 0
        self.totalFixationDuration = 0
        self.averageFixationDuration = 0
        self.scanPathLengthInPixels = 0
        self.scanPathLengthInCM = 0

        self.process_samples()
        self.process_fixations_offline()

        # if offline is False:
        #     self.t1 = Thread(target=self.process_fixations_cumulative)
        #     self.t1.daemon = True
        #     self.t1.start()

    def samples_to_fixation(self, fixationSamples):
        sizeOfFixation = len(fixationSamples)
        fixationDuration = int(fixationSamples[sizeOfFixation - 1].timestamp) - int(fixationSamples[0].timestamp)
        fixationSpatialDataX = []
        fixationSpatialDataY = []
        averageEyeScreenDistance = 0
        for sample in fixationSamples:
            fixationSpatialDataX.append(float(sample.filteredGazePointX))
            fixationSpatialDataY.append(float(sample.filteredGazePointY))
            averageEyeScreenDistance = averageEyeScreenDistance + sample.eyeToScreenDistance
        averageEyeScreenDistance = averageEyeScreenDistance / sizeOfFixation
        xMean = numpy.mean(fixationSpatialDataX)
        yMean = numpy.mean(fixationSpatialDataY)
        fixationAOI = self.grid.check_sample_in_grid(xMean, yMean)
        fixationObject = Fixation(0, xMean, yMean,
                                  fixationSamples[0].timestamp,
                                  fixationSamples[sizeOfFixation - 1].timestamp, fixationDuration, fixationAOI,
                                  fixationSpatialDataX, fixationSpatialDataY, fixationSamples[0],
                                  fixationSamples[sizeOfFixation - 1], averageEyeScreenDistance)
        return fixationObject

    def samples_to_fixation_offline(self, fixationSamples):
        sizeOfFixation = len(fixationSamples)
        fixationDuration = fixationSamples[0].gazeEventDuration
        xMean = fixationSamples[0].gazeEventX
        yMean = fixationSamples[0].gazeEventY
        fixationAOI = self.grid.check_sample_in_grid(xMean, yMean)
        fixationObject = Fixation(0, xMean, yMean,
                                  fixationSamples[0].timestamp,
                                  fixationSamples[sizeOfFixation - 1].timestamp, fixationDuration, fixationAOI,
                                  0, 0, fixationSamples[0],
                                  fixationSamples[sizeOfFixation - 1], 0)
        return fixationObject

    # TODO: Include in the calucaltions the x and y values of the samples in between the two fixations
    def merge_fixations(self):
        mergedFixationDuration = self.previousFixation.fixationDuration + self.currentFixation.fixationDuration
        mergedFixationSpatialDataX = numpy.concatenate([self.previousFixation.xPos, self.currentFixation.xPos])
        mergedFixationSpatialDataY = numpy.concatenate([self.previousFixation.yPos, self.currentFixation.yPos])
        xMean = numpy.mean(mergedFixationSpatialDataX)
        yMean = numpy.mean(mergedFixationSpatialDataY)
        mergedFixationAOI = self.grid.check_sample_in_grid(xMean, yMean)
        mergedFixationObject = Fixation(self.previousFixation.sequence - 1, xMean, yMean,
                                        self.previousFixation.fixationStart, self.currentFixation.fixationEnd,
                                        mergedFixationDuration, mergedFixationAOI,
                                        mergedFixationSpatialDataX, mergedFixationSpatialDataY,
                                        self.previousFixation.firstSample,
                                        self.currentFixation.lastSample,
                                        float((self.previousFixation.averageEyeDistance + self.currentFixation.averageEyeDistance) / 2))
        return mergedFixationObject

    def filter_fixation(self, fixation):
        if fixation.sequence == 1:
            self.currentFixation = copy.deepcopy(fixation)
            self.previousFixation = copy.deepcopy(self.currentFixation)
        else:
            self.currentFixation = copy.deepcopy(fixation)
            timeBetweenFixations = int(self.currentFixation.fixationStart) - int(self.previousFixation.fixationEnd)
            if timeBetweenFixations < self.maximumTimeBetweenFixations:
                dx = float(self.currentFixation.firstSample.filteredGazePointX) - float(
                    self.previousFixation.lastSample.filteredGazePointX)
                dy = float(self.currentFixation.firstSample.filteredGazePointY) - float(
                    self.previousFixation.lastSample.filteredGazePointY)
                distanceInPixels = ((dx ** 2) + (dy ** 2)) ** 0.5
                distanceInCM = distanceInPixels * self.screen.ipp
                angleBetweenFixations = u.convert_distance_to_angle(distanceInCM, fixation.averageEyeDistance)
                if angleBetweenFixations < self.maxAngleBetweenFixations:
                    fixation = self.merge_fixations()
                else:
                    fixation = copy.deepcopy(self.currentFixation)
            else:
                fixation = copy.deepcopy(self.currentFixation)
            self.previousFixation = copy.deepcopy(self.currentFixation)
        if fixation.fixationDuration > self.shortFixaitonThreshold:
            return fixation
        else:
            return None

    def process_fixations_online(self):
        while True:
            time.sleep(self.processingWindow)
            if len(self.states) > 0:
                self.transitionMatrix = TransitionMatrix(self.numberOfStates, self.states)

    def process_fixations_offline(self):
        if len(self.states) > 0:
            self.transitionMatrix = TransitionMatrix(self.numberOfStates, self.states)
        if len(self.fixations) > 0:
            for fix in self.fixations:
                self.totalFixationDuration = self.totalFixationDuration + (fix.fixationDuration/1000)

        if len(self.fixations) > 0:
            previousFixation = Fixation()
            currentFixation = Fixation()
            counter = 0
            for fix in self.fixations:
                counter = counter + 1
                if counter == 1:
                    currentFixation = fix
                    previousFixation = currentFixation
                else:
                    currentFixation = fix
                    euclideanDistanceBetweenFixations = numpy.sqrt(numpy.square((currentFixation.fixationX-previousFixation.fixationX))
                                                                + numpy.square((currentFixation.fixationY-previousFixation.fixationY)))
                    self.scanPathLengthInPixels = self.scanPathLengthInPixels + (euclideanDistanceBetweenFixations * self.screen.ipp)
                    self.scanPathLengthInCM = self.scanPathLengthInCM + (euclideanDistanceBetweenFixations * self.screen.ppi)
                    previousFixation = currentFixation

    def find_fixations_online(self, sample):
        self.sample = copy.deepcopy(sample)
        if int(sample.id) == 1:
            self.currentSample = copy.deepcopy(sample)
            self.previousSample = copy.deepcopy(self.currentSample)
        else:
            self.currentSample = copy.deepcopy(sample)

            if (self.previousSample.gazeEventType is None) and (self.currentSample.gazeEventType == "Fixation"):
                self.startOfFixation = True
                self.fixation = []
                self.fixation.append(self.currentSample)
            if (self.startOfFixation is True) and (self.previousSample.gazeEventType is "Fixation") \
                    and (self.currentSample.gazeEventType is "Fixation"):
                self.fixation.append(self.currentSample)
            if (self.startOfFixation is True) and (self.previousSample.gazeEventType is "Fixation") \
                    and (self.currentSample.gazeEventType is None):
                self.startOfFixation = False
                fixationObject = self.samples_to_fixation(self.fixation)
                self.fixationCounter = self.fixationCounter + 1
                fixationObject.sequence = self.fixationCounter
                fixationObject = self.filter_fixation(fixationObject)
                if (fixationObject is not None) and (fixationObject.fixationAOI != -1):
                    self.fixations.append(fixationObject)
                    self.states.append(fixationObject.fixationAOI)
                    self.windowStates.append(fixationObject.fixationAOI)
                    self.latestFixation = copy.deepcopy(fixationObject)
            self.previousSample = copy.deepcopy(self.currentSample)

    def find_fixations_offline(self, sample):
        self.sample = copy.deepcopy(sample)
        if int(sample.id) == 1:
            self.currentSample = copy.deepcopy(sample)
            self.previousSample = copy.deepcopy(self.currentSample)
        else:
            self.currentSample = copy.deepcopy(sample)

            if (self.previousSample.gazeEventType != "Fixation") and (self.currentSample.gazeEventType == "Fixation"):
                self.startOfFixation = True
                self.fixation = []
                self.fixation.append(self.currentSample)
            if (self.startOfFixation is True) and (self.previousSample.gazeEventType == "Fixation") \
                    and (self.currentSample.gazeEventType == "Fixation"):
                self.fixation.append(self.currentSample)
            if (self.startOfFixation is True) and (self.previousSample.gazeEventType == "Fixation") \
                    and (self.currentSample.gazeEventType != "Fixation"):
                self.startOfFixation = False
                fixationObject = self.samples_to_fixation_offline(self.fixation)
                self.fixationCounter = self.fixationCounter + 1
                fixationObject.sequence = self.fixationCounter
                if (fixationObject is not None) and (fixationObject.fixationAOI != -1):
                    self.fixations.append(fixationObject)
                    self.states.append(fixationObject.fixationAOI)
                    self.windowStates.append(fixationObject.fixationAOI)
                    self.latestFixation = copy.deepcopy(fixationObject)

            self.previousSample = copy.deepcopy(self.currentSample)

    def process_samples(self):
        skip = 0
        sampleCounter = 0
        for line in self.fread:
            skip = skip + 1
            if skip > self.skipLines:
                sampleCounter = sampleCounter + 1
                parsedMessage = line.split("\t")
                stimulusName = str(parsedMessage[6]).strip().rstrip()
                if stimulusName in self.stimuli:
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

                    sample.gazeAOI = self.grid.check_sample_in_grid(sample.filteredGazePointX, sample.filteredGazePointY)

                    self.find_fixations_offline(sample)