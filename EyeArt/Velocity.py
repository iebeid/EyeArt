import Utils as u

class VelocityKernel:
    def __init__(self,ipp,windowSize=None):
        self.samples = []
        self.currentValue = 0
        self.windowSize = windowSize
        if windowSize is None:
            self.windowSize = 3
        self.ipp=ipp

    def compute_velocity(self,previousSample,currentSample):
        dx = float(currentSample.filteredGazePointX) - float(previousSample.filteredGazePointX)
        dy = float(currentSample.filteredGazePointY) - float(previousSample.filteredGazePointY)
        dt = (float(currentSample.timestamp) - float(previousSample.timestamp)) / 1000
        distanceInPixels = ((dx ** 2) + (dy ** 2)) ** 0.5
        distanceInCM = distanceInPixels * self.ipp
        interSampleDistance = u.convert_distance_to_angle(distanceInCM, float(currentSample.eyeToScreenDistance))
        interSampleVelocity = float(interSampleDistance) / dt
        return interSampleVelocity

    def moving_velocity(self) :
        firstSample = self.samples[0]
        middleSample = self.samples[int((self.windowSize-1)/2)]
        lastSample = self.samples[int(self.windowSize-1)]
        firstVelocity = self.compute_velocity(firstSample, middleSample)
        lastVelocity = self.compute_velocity(middleSample, lastSample)
        return float((firstVelocity+lastVelocity)/2)

    def run(self, sample):
        if sample == -1:
            sample = 0
        self.samples.append(sample)
        if len(self.samples) == self.windowSize:
            self.currentValue = self.moving_velocity()
        if len(self.samples) == (self.windowSize+1):
            del self.samples[0]
            self.currentValue = self.moving_velocity()
        return self.currentValue