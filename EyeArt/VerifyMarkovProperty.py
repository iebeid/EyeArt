import random
import pandas
import numpy

if __name__ == "__main__":
    sequence = [2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 3, 1,
                2, 1, 2, 1, 1, 2, 1, 1, 2, 1, 3, 1, 2, 1, 3, 1, 2, 1, 2, 1, 3, 1, 2, 1, 3, 1, 2, 1, 3, 1,
                2, 1, 3, 1, 2, 1, 3, 1, 2, 1, 2, 1, 1]
    samples = []
    windowSize = 3
    for s in sequence:
        samples.append(s)
        if len(samples) == windowSize:
            stringOfStates = ""
            for s in samples:
                stringOfStates = stringOfStates + str(s)
            firstSample = samples[0]
            middleSample = samples[int((windowSize - 1) / 2)]
            lastSample = samples[int(windowSize - 1)]
            del samples[0]
            print(str(firstSample) + " , " + str(middleSample) + " , " + str(lastSample))