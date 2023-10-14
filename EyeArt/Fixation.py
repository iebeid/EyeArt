
class Fixation:
    def __init__(self,sequence=0,fixationX=0,fixationY=0,fixationStart=0,fixationEnd=0,
                 fixationDuration=0,fixationAOI=0,xPos=0,yPos=0,firstSample=0,
                 lastSample=0,averageEyeDistance=0):
        self.sequence = sequence
        self.fixationX = fixationX
        self.fixationY = fixationY
        self.fixationStart = fixationStart
        self.fixationEnd = fixationEnd
        self.fixationDuration = fixationDuration
        self.fixationAOI = fixationAOI
        self.xPos = xPos
        self.yPos = yPos
        self.firstSample = firstSample
        self.lastSample = lastSample
        self.averageEyeDistance = averageEyeDistance

    def __str__(self):
        toBePrinted = "Sequence: " + str(self.sequence) \
                      + " | Fixation point: (" + str(self.fixationX) + "," + str(self.fixationY) + ") " \
                      + " | Fixation times: (" + str(self.fixationStart) + "," + str(self.fixationEnd) + ") " \
                      + " | Fixation duration: " + str(self.fixationDuration) \
                      + " | AOI: " + str(self.fixationAOI)
        return toBePrinted

    def create_dictionary(self):
        return {"sequence":self.sequence,"fixationX":self.fixationX,
                "fixationY":self.fixationY,"fixationDuration":self.fixationDuration,
                "fixationAOI":self.fixationAOI,"averageEyeDistance":self.averageEyeDistance}