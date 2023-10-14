import os
from PIL import ImageGrab
from PIL import Image
from Grid import Grid
from Screen import Screen
import Utils as u
from Sample import Sample
from Classifier import Classifier
from Filter import MovingAverageFilter
from Velocity import VelocityKernel
from Backend import Backend

#input (user,viewing) --> output (temporal matlibplot of entropy)

def temporal_entropy(user,viewing):
    stimuliDistorted = ["S01-a-L", "S01-a-M", "S01-a-S",
                        "S02-a-L", "S02-a-M", "S02-a-S",
                        "S03-a-L", "S03-a-M", "S03-a-S",
                        "S04-a-L", "S04-a-M", "S04-a-S",
                        "S05-a-L", "S05-a-M", "S05-a-S",
                        "S06-a-L", "S06-a-M", "S06-a-S",
                        "S07-a-L", "S07-a-M", "S07-a-S",
                        "S08-a-L", "S08-a-M", "S08-a-S",
                        "S09-a-L", "S09-a-M", "S09-a-S",
                        "S10-a-L", "S10-a-M", "S10-a-S",
                        "S11-a-L", "S11-a-M", "S11-a-S",
                        "S13-a-L", "S13-a-M", "S13-a-S",
                        "S14-a-L", "S14-a-M", "S14-a-S",
                        "S15-a-L", "S15-a-M", "S15-a-S",
                        "S16-a-L", "S16-a-M", "S16-a-S",
                        "S18-a-L", "S18-a-M", "S18-a-S"]
    filename = "D:/Box Sync/Summer2018/EyeArt/Data/Study/AllRespondents_20180428_175418.txt"
    fread = open(filename,"r")
    print("Filesize: " + str(os.stat(filename).st_size))
    screen = Screen(float("60.9"), float("40.9"), int("1920"), int("1080"), float("60.0"))
    screen.ppi = u.calculate_ppi(screen)
    screen.ipp = u.calculate_ipp(screen)
    maFilterX = MovingAverageFilter(5)
    maFilterY = MovingAverageFilter(5)
    classifier = Classifier(screen, "30.0", "1.5", "75.0")
    velocityKernel = VelocityKernel(screen.ipp, 3)
    offlineBackendFirst = 0
    onlineBackendFirst = 0
    offlineBackendSecond = 0
    onlineBackendSecond = 0
    gridSize = int("8")
    previousUser = ""
    currentUser = ""
    previousStimulus = ""
    currentStimulus = ""
    userCounter = 0
    stimulusCounter = 0
    newUser = False
    newStimulus = False
    grid = 0
    onlineCounter = 0
    offlineCounter = 0
    useInterpolation = True
    imWidth = 0
    imHeight = 0
    timePassed = 0
    recognized = "No"
    recordCounter = 0
    for line in fread:
        parsedMessage = line.split("\t")
        if (len(parsedMessage) > 8) and ((str(parsedMessage[8]).strip().rstrip() == str("ET|UI"))
                    or (str(parsedMessage[8]).strip().rstrip() == str("ET"))):
            name = str(parsedMessage[2]).strip().rstrip()
            age = str(parsedMessage[3]).strip().rstrip()
            gender = str(parsedMessage[4]).strip().rstrip()
            stimulusName = str(parsedMessage[6]).strip().rstrip()
            if userCounter == 0:
                currentUser = name
                userCounter = userCounter + 1
                newUser = True
                recognized = "No"
                priorKnowledge = "No"
                stimulusCounter = 0
                newStimulus = False
                previousUser = currentUser
            else:
                currentUser = name
                if currentUser != previousUser:
                    userCounter = userCounter + 1
                    newUser = True
                    recognized = "No"
                    priorKnowledge = "No"
                    stimulusCounter = 0
                    newStimulus = False
                previousUser = currentUser
            if newUser:
                if stimulusCounter == 0:
                    currentStimulus = stimulusName
                    if (str(parsedMessage[6]).strip().rstrip() in stimuliDistorted):
                        stimulusCounter = stimulusCounter + 1
                        newStimulus = True
                        onlineCounter = 0
                        offlineCounter = 0
                        timePassed = 0
                        im = Image.open("D:/Box Sync/Summer2018/EyeArt/Stimuli/StudyStimuli/" + str(stimulusName) + ".jpg")
                        imWidth, imHeight = im.size
                        grid = Grid(screen.screenResolutionHeight, screen.screenResolutionWidth, imHeight, imWidth, gridSize)
                        onlineBackendFirst = Backend(grid, 75, 0.5, screen, 7.0, 100)
                        offlineBackendFirst = Backend(grid, 75, 0.5, screen, 7.0, 100)
                    previousStimulus = currentStimulus
                else:
                    currentStimulus = stimulusName
                    if currentStimulus != previousStimulus:
                        if (str(parsedMessage[6]).strip().rstrip() in stimuliDistorted):
                            stimulusCounter = stimulusCounter + 1
                            newStimulus = True
                            onlineCounter = 0
                            offlineCounter = 0
                            timePassed = 0
                            im = Image.open("D:/Box Sync/Summer2018/EyeArt/Stimuli/StudyStimuli/" + str(stimulusName) + ".jpg")
                            imWidth, imHeight = im.size
                            grid = Grid(screen.screenResolutionHeight, screen.screenResolutionWidth, imHeight, imWidth,
                                        gridSize)
                            onlineBackendFirst = Backend(grid, 75, 0.5, screen, 10.0, 100)
                            offlineBackendFirst = Backend(grid, 75, 0.5, screen, 10.0, 100)
                    previousStimulus = currentStimulus

            if newStimulus:
                if (str(parsedMessage[6]).strip().rstrip() in stimuliDistorted):
                    keystroke = parsedMessage[49]
                    if keystroke == "Up":
                        recognized = "Yes"
                    validityLeft = int(str(parsedMessage[24]).strip().rstrip())
                    validityRight = int(str(parsedMessage[25]).strip().rstrip())
                    if (validityLeft in range(0, 4)) and (validityRight in range(0, 4)):
                        onlineCounter = onlineCounter + 1
                        offlineCounter = offlineCounter + 1
                        timestamp = int(parsedMessage[11].strip().rstrip())
                        gazeLeftX = float(parsedMessage[12].strip().rstrip())
                        gazeLeftY = float(parsedMessage[13].strip().rstrip())
                        gazeRightX = float(parsedMessage[14].strip().rstrip())
                        gazeRightY = float(parsedMessage[15].strip().rstrip())
                        leftPupilDiameter = float(parsedMessage[16].strip().rstrip())
                        rightPupilDiameter = float(parsedMessage[17].strip().rstrip())
                        leftEyeDistance = float(parsedMessage[18].strip().rstrip())
                        rightEyeDistance = float(parsedMessage[19].strip().rstrip())
                        onlineSample = Sample(onlineCounter, stimulusName, timestamp, gazeLeftX, gazeLeftY, gazeRightX, gazeRightY,
                                        leftPupilDiameter, rightPupilDiameter, leftEyeDistance, rightEyeDistance)
                        #Online
                        onlineSample.compute_gaze(screen.screenResolutionHeight, screen.screenResolutionWidth, imHeight, imWidth)
                        onlineSample.find_eye_to_screen_distance()
                        onlineSample.filteredGazePointX = maFilterX.run(onlineSample.gazePointX)
                        onlineSample.filteredGazePointY = maFilterY.run(onlineSample.gazePointY)
                        onlineSample.gazeAOI = grid.check_sample_in_grid(onlineSample.filteredGazePointX, onlineSample.filteredGazePointY)
                        onlineSample = classifier.compute_velocity(onlineSample)
                        timePassed = timePassed + onlineSample.interSampleTimestampDifference
                        onlineSample.timePassed = timePassed
                        onlineSample.filteredInterSampleVelocity = velocityKernel.run(onlineSample)
                        onlineSample.gazeEventType = classifier.classify(onlineSample)
                        onlineBackendFirst.find_fixations_cumulative(onlineSample)
                        #Offline
                        offlineSample = Sample(offlineCounter, stimulusName, timestamp, gazeLeftX, gazeLeftY, gazeRightX, gazeRightY,
                                        leftPupilDiameter, rightPupilDiameter, leftEyeDistance, rightEyeDistance)
                        if parsedMessage[26]:
                            offlineSample.gazePointX = float(parsedMessage[26])
                        else:
                            offlineSample.gazePointX = 0.0

                        if parsedMessage[27]:
                            offlineSample.gazePointY = float(parsedMessage[27])
                        else:
                            offlineSample.gazePointY = 0.0

                        offlineSample.leftEyeDistance = float(parsedMessage[18].strip().rstrip())
                        offlineSample.rightEyeDistance = float(parsedMessage[19].strip().rstrip())
                        offlineSample.find_eye_to_screen_distance()
                        if parsedMessage[29]:
                            offlineSample.filteredGazePointX = float(parsedMessage[29])
                        else:
                            offlineSample.filteredGazePointX = 0.0

                        if parsedMessage[30]:
                            offlineSample.filteredGazePointY = float(parsedMessage[30])
                        else:
                            offlineSample.filteredGazePointY = 0.0

                        if parsedMessage[32]:
                            offlineSample.filteredInterSampleVelocity = float(parsedMessage[32])
                        else:
                            offlineSample.filteredInterSampleVelocity = 0.0

                        offlineSample.gazeAOI = grid.check_sample_in_grid(offlineSample.filteredGazePointX, offlineSample.filteredGazePointY)
                        offlineSample.gazeEventType = str(parsedMessage[31].strip().rstrip())
                        if parsedMessage[40]:
                            offlineSample.gazeEventDuration = float(parsedMessage[40].strip().rstrip())
                        else:
                            offlineSample.gazeEventDuration = 0

                        if parsedMessage[37]:
                            offlineSample.gazeEventX = float(parsedMessage[37].strip().rstrip())
                        else:
                            offlineSample.gazeEventX = 0

                        if parsedMessage[38]:
                            offlineSample.gazeEventY = float(parsedMessage[38].strip().rstrip())
                        else:
                            offlineSample.gazeEventY = 0

                        offlineBackendFirst.find_fixations_offline(offlineSample)

                    if timePassed > 10.0:
                        recordCounter = recordCounter + 1
                        newStimulus = False
                        onlineBackendFirst.process_fixations_cumulative_offline()
                        offlineBackendFirst.process_fixations_cumulative_offline()
                        print(str(recordCounter)+", Online E: "+str(onlineBackendFirst.transitionMatrix.transitionMatrixEntropy)+", Online SD: "
                              +str(onlineBackendFirst.transitionMatrix.stationaryDistributionEntropy)+", Online T: "
                              +str(len(onlineBackendFirst.transitionMatrix.transitions))+", Offline E: "
                              +str(offlineBackendFirst.transitionMatrix.transitionMatrixEntropy)+", Offline SD: "
                              +str(offlineBackendFirst.transitionMatrix.stationaryDistributionEntropy)+", Offline T: "
                              +str(len(offlineBackendFirst.transitionMatrix.transitions)))

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

if __name__ == "__main__":
    # user = 12
    # viewing = 1
    # temporal_entropy(user,viewing)
    messageSizes = [6,8,10,11,18,150]
    user = "P12"
    userList = get_immediate_subdirectories("D:/Box Sync/Summer2018/EyeArt/Data/Study")
    if user in userList:
        for u in userList:
            if user == u:
                filename = "D:/Box Sync/Summer2018/EyeArt/Data/Study/"+u+"/data.txt"
                fread = open(filename, "r")
                print("Filesize: " + str(os.stat(filename).st_size))
                for line in fread:
                    parsedMessage = line.split(";")
                    if int(len(parsedMessage)) in messageSizes:
                        eventSource = parsedMessage[1].strip().rstrip()
                        sampleName = parsedMessage[2].strip().rstrip()

                        if (str(eventSource) == str("EyeTracker")) and (
                                str(sampleName) == str("GazeCalibrationResult")):
                            calibrationPoints = parsedMessage[5].strip().rstrip()
                            calibrationQuality = parsedMessage[6].strip().rstrip()
                            calibrationResult = parsedMessage[7].strip().rstrip()
                            errorMean = parsedMessage[8].strip().rstrip()
                            errorStandardDeviation = parsedMessage[9].strip().rstrip()
                            print("Number of calibration points: " + str(calibrationPoints))
                            print("Calibration quality: " + str(calibrationQuality))
                            print("Calibration result: " + str(calibrationResult))
                            print("Mean of error: " + str(errorMean))
                            print("Standard deviation of error: " + str(errorStandardDeviation))
                            continue

                        if (str(eventSource) == str("AttentionTool")) and (
                                str(sampleName) == str("SlideStart")):
                            imagePath = str(dataPath) + str(parsedMessage[6].strip().rstrip()) + str(
                                ".jpg")
                            imageName = str(parsedMessage[6].strip().rstrip()) + str(".jpg")
                            interslide = parsedMessage[7].strip().rstrip()
                            if (str(interslide) == str("TestImage")):
                                maFilterX = MovingAverageFilter(5)
                                maFilterY = MovingAverageFilter(5)
                                classifier = Classifier(screen, fixationVelocityThreshold,
                                                            fixationDegreesThreshold, fixationTimeThreshold)
                                velocityKernel = VelocityKernel(screen.ipp, 3)
                                if "Question" not in str(imageName):
                                    im = Image.open(imagePath)
                                else:
                                    im = ImageGrab.grab()
                                imWidth,  imHeight =  im.size
                                 grid = Grid( screen.screenResolutionHeight,  screen.screenResolutionWidth,
                                                  imHeight,  imWidth,  gridSize)
                                 backend = Backend( grid, 75, 0.5,  screen, 1.0, 100)
                                 start = True
                                 trialNumber =  trialNumber + 1
                                continue

                        if (str( eventSource) == str("AttentionTool")) and (
                                str( sampleName) == str("SlideEnd")):
                            if (str( interslide) == str("TestImage")):
                                 reset()
                                 backend.endBackendOperations = True
                                break

                        if ( start is True) and (str( eventSource) == str("EyeTracker")) and (
                                str( sampleName) == str("EyeData")):
                             counter =  counter + 1
                             timestamp =  parsedMessage[5].strip().rstrip()
                             gazeLeftX = float( parsedMessage[6].strip().rstrip())
                             gazeLeftY = float( parsedMessage[7].strip().rstrip())
                             gazeRightX = float( parsedMessage[8].strip().rstrip())
                             gazeRightY = float( parsedMessage[9].strip().rstrip())
                             leftPupilDiameter = float( parsedMessage[10].strip().rstrip())
                             rightPupilDiameter = float( parsedMessage[11].strip().rstrip())
                             leftEyeDistance = float( parsedMessage[12].strip().rstrip()) / 10
                             rightEyeDistance = float( parsedMessage[13].strip().rstrip()) / 10
                            # TODO: Compute sample to sample data from normalized screen coordinates
                            #  leftEyePositionX = float( parsedMessage[14])
                            #  leftEyePositionY = float( parsedMessage[15])
                            #  rightEyePositionX = float( parsedMessage[16])
                            #  rightEyePositionY = float( parsedMessage[17])
                             leftEyePositionX = 0.0
                             leftEyePositionY = 0.0
                             rightEyePositionX = 0.0
                             rightEyePositionY = 0.0

                            sample = Sample( counter,  trialNumber,  imageName,  timestamp,
                                             gazeLeftX,
                                             gazeLeftY,  gazeRightX,  gazeRightY,  leftPupilDiameter,
                                             rightPupilDiameter,
                                             leftEyeDistance,  rightEyeDistance,  leftEyePositionX,
                                             leftEyePositionY,
                                             rightEyePositionX,  rightEyePositionY)
                            sample.compute_gaze( screen.screenResolutionHeight,  screen.screenResolutionWidth,
                                                 imHeight,  imWidth)
                            sample.find_eye_to_screen_distance()
                            sample.filteredGazePointX =  maFilterX.run(sample.gazePointX)
                            sample.filteredGazePointY =  maFilterY.run(sample.gazePointY)
                            sample.gazeAOI =  grid.check_sample_in_grid(sample.filteredGazePointX,
                                                                            sample.filteredGazePointY)
                            sample =  classifier.compute_velocity(sample)
                            timePassed =  timePassed + sample.interSampleTimestampDifference
                            sample.timePassed =  timePassed
                            sample.filteredInterSampleVelocity =  velocityKernel.run(sample)
                            sample.gazeEventType =  classifier.classify(sample)
                             backend.find_fixations_cumulative(sample)
                             backend.visualize()
                             backend.process_fixations_window()
                            continue