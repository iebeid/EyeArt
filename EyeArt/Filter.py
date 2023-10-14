import statistics

#TODO: The moving average filter does not resolve the case when an invalid -1 appears. According to Tobii's algorithm when an invalid sample appears the window has to be reshaped to preserve symmetry on both sides of the middle sample being averaged.
#TODO: Careful that the window sizes for both filters have to be an odd number bearing in mind that the default window sizes for both filtes is 7.

class MovingAverageFilter:
    def __init__(self,windowSize=None):
        self.samples = []
        self.currentValue = 0
        self.windowSize = windowSize
        if windowSize is None:
            self.windowSize = 7

    def moving_average(self) :
        invalidSampleCounter = 0
        sumOfArray = 0.0
        for s in self.samples:
            if s == -1:
                invalidSampleCounter = invalidSampleCounter + 1
                s = 0
            sumOfArray = sumOfArray + s
        average = 0
        if self.windowSize == invalidSampleCounter:
            average = 0.0
        else:
            average = float(sumOfArray / (self.windowSize - invalidSampleCounter))
        return average

    def run(self, sample):
        self.samples.append(sample)
        if len(self.samples) == self.windowSize:
            self.currentValue = self.moving_average()
        if len(self.samples) == (self.windowSize+1):
            del self.samples[0]
            self.currentValue = self.moving_average()
        return self.currentValue

class MovingMedianFilter:
    def __init__(self,windowSize=None):
        self.samples = []
        self.currentValue = 0
        self.windowSize = windowSize
        if windowSize is None:
            self.windowSize = 7

    def moving_median(self) :
        return statistics.median(self.samples)

    def run(self, sample):
        if sample == -1:
            sample = 0
        self.samples.append(sample)
        if len(self.samples) == self.windowSize:
            self.currentValue = self.moving_median()
        if len(self.samples) == (self.windowSize+1):
            del self.samples[0]
            self.currentValue = self.moving_median()
        return self.currentValue