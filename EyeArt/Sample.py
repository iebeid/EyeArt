import copy
import Utils as u

class Sample:
    def __init__(self,id=0,trialNumber=0,imageName=0,timestamp=0,gazeLeftX=0,gazeLeftY=0,gazeRightX=0,gazeRightY=0,leftPupilDiameter=0
                 ,rightPupilDiameter=0,leftEyeDistance=0,rightEyeDistance=0,leftEyePositionX=0,leftEyePositionY=0,rightEyePositionX=0
                 ,rightEyePositionY=0,gazePointX=0,gazePointY=0,filteredGazePointX=0,filteredGazePointY=0,eyeToScreenDistance=0
                 ,gazeAOI=0,interSampleTimestampDifference=0,timePassed = 0,interSampleDistance=0,interSampleVelocity=0,filteredInterSampleVelocity=0,interSampleAcceleration=0
                 ,gazeEventType=0):

        self.id = id
        self.trialNumber = trialNumber
        self.imageName = imageName
        self.timestamp = timestamp
        self.gazeLeftX = gazeLeftX
        self.gazeLeftY = gazeLeftY
        self.gazeRightX = gazeRightX
        self.gazeRightY = gazeRightY
        self.leftPupilDiameter = leftPupilDiameter
        self.rightPupilDiameter = rightPupilDiameter
        self.leftEyeDistance = leftEyeDistance
        self.rightEyeDistance = rightEyeDistance
        self.leftEyePositionX = leftEyePositionX
        self.leftEyePositionY = leftEyePositionY
        self.rightEyePositionX = rightEyePositionX
        self.rightEyePositionY = rightEyePositionY
        self.gazePointX = gazePointX
        self.gazePointY = gazePointY
        self.filteredGazePointX = filteredGazePointX
        self.filteredGazePointY = filteredGazePointY
        self.eyeToScreenDistance = eyeToScreenDistance
        self.gazeAOI = gazeAOI
        self.interSampleTimestampDifference = interSampleTimestampDifference
        self.timePassed = timePassed
        self.interSampleDistance = interSampleDistance
        self.interSampleVelocity = interSampleVelocity
        self.filteredInterSampleVelocity = filteredInterSampleVelocity
        self.interSampleAcceleration = interSampleAcceleration
        self.gazeEventType = gazeEventType

    def __str__(self):
        toBePrinted = "ID: " + str(self.id) + " | Trial Number: " + str(self.trialNumber) + " | Timestamp: " + str(self.timestamp) \
                      + " | Gaze point: (" + str(int(self.gazePointX)) + "," + str(int(self.gazePointY)) + ") " \
                      + "/ (" + str(int(self.filteredGazePointX)) + "," + str(int(self.filteredGazePointY)) + ") " \
                      + " | Eye distance: " + str(int(self.eyeToScreenDistance)) + " | AOI: " + str(self.gazeAOI) \
                      + " | Distance: " + str(int(self.interSampleDistance)) + " | Velocity: " \
                      + str(int(self.interSampleVelocity)) + " / " + str(int(self.filteredInterSampleVelocity)) \
                      + " | Event: " + str(self.gazeEventType)
        return toBePrinted

    def compute_gaze(self,screen_height,screen_width,image_height,image_width):
        if int(self.gazeLeftX) != -1 & int(self.gazeLeftY) != -1 & int(self.gazeRightX) != -1 & int(
                self.gazeRightY) != -1:
            self.gazePointX = u.mean([float(self.gazeLeftX), float(self.gazeRightX)])
            self.gazePointY = u.mean([float(self.gazeLeftY), float(self.gazeRightY)])
        elif int(self.gazeLeftX) != -1 & int(self.gazeLeftY) != -1 & int(self.gazeRightX) == -1 & int(
                self.gazeRightY) == -1:
            self.gazePointX = self.gazeLeftX
            self.gazePointY = self.gazeLeftY
        elif int(self.gazeLeftX) == -1 & int(self.gazeLeftY) == -1 & int(self.gazeRightX) != -1 & int(
                self.gazeRightY) != -1:
            self.gazePointX = self.gazeRightX
            self.gazePointY = self.gazeRightY
        else:
            self.gazePointX = -1.0
            self.gazePointY = -1.0

        leftLimit = (screen_width / 2) - (image_width / 2)
        topLimit = (screen_height / 2) - (image_height / 2)
        rightLimit = ((screen_width / 2) - (image_width / 2)) + image_width
        bottomLimit = ((screen_height / 2) - (image_height / 2)) + image_height
        check = False
        if ((self.gazePointY > topLimit)
                or (self.gazePointY < bottomLimit)
                or (self.gazePointX > leftLimit)
                or (self.gazePointX < rightLimit)):
            check = True
        if check is False:
            self.gazePointX = -1.0
            self.gazePointY = -1.0

    def find_eye_to_screen_distance(self):
        if self.leftEyeDistance != -1 and  self.rightEyeDistance != -1:
            self.eyeToScreenDistance = (self.leftEyeDistance + self.rightEyeDistance)/2
        elif self.leftEyeDistance != -1 and  self.rightEyeDistance == -1:
            self.eyeToScreenDistance = self.leftEyeDistance
        elif self.leftEyeDistance == -1 and  self.rightEyeDistance != -1:
            self.eyeToScreenDistance = self.rightEyeDistance
        else:
            self.eyeToScreenDistance = 0.0
