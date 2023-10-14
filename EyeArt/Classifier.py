import copy
from Screen import Screen
from Sample import Sample
import Utils as u

class Classifier:
    def __init__(self, screen=Screen(), fixationVelocityThreshold=30.0, fixationDegreesThreshold=1.5, fixationTimeThreshold=75.0):
        self.previousSample = Sample()
        self.currentSample = Sample()
        self.screen = screen
        self.counter = 0
        self.fixationStart = False
        self.fixationVelocityThreshold = fixationVelocityThreshold
        self.fixationDegreesThreshold = fixationDegreesThreshold
        self.fixationTimeThreshold = fixationTimeThreshold

    def classify(self,sample=Sample()):
        if (float(sample.filteredInterSampleVelocity) < float(self.fixationVelocityThreshold)):
            self.fixationStart = True
            return str("Fixation")

    def compute_velocity(self, sample=Sample()):
        if int(sample.id) == 1:
            self.currentSample = copy.deepcopy(sample)
            self.previousSample = copy.deepcopy(self.currentSample)
        else:
            self.currentSample = copy.deepcopy(sample)
            dx = float(self.currentSample.filteredGazePointX) - float(self.previousSample.filteredGazePointX)
            dy = float(self.currentSample.filteredGazePointY) - float(self.previousSample.filteredGazePointY)
            dt = (float(self.currentSample.timestamp) - float(self.previousSample.timestamp)) / 1000
            distanceInPixels = ((dx ** 2) + (dy ** 2)) ** 0.5
            distanceInCM = distanceInPixels * self.screen.ipp
            self.currentSample.interSampleTimestampDifference = dt
            self.currentSample.interSampleDistance = u.convert_distance_to_angle(distanceInCM, float(
                self.currentSample.eyeToScreenDistance))
            self.currentSample.interSampleVelocity = float(self.currentSample.interSampleDistance) / float(
                self.currentSample.interSampleTimestampDifference)
            dv = float(self.currentSample.interSampleVelocity) - float(self.previousSample.interSampleVelocity)
            self.currentSample.interSampleAcceleration = float(dv / float(self.currentSample.interSampleTimestampDifference))
            self.previousSample = copy.deepcopy(self.currentSample)
        sample = copy.deepcopy(self.currentSample)
        return sample