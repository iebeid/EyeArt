import math

class Screen:

    def __init__(self,screenWidthInCM=0,screenHeightInCM=0,screenResolutionWidth=0,screenResolutionHeight=0, defaultDistanceToScreen=0):
        self.screenWidthInCM = screenWidthInCM
        self.screenHeightInCM = screenHeightInCM
        self.screenResolutionWidth = screenResolutionWidth
        self.screenResolutionHeight = screenResolutionHeight
        self.defaultDistanceToScreen = defaultDistanceToScreen
        self.ipp = self.calculate_ipp()
        self.ppi = self.calculate_ppi()

    def calculate_ppi(self):
        dp = math.sqrt(math.pow(self.screenResolutionWidth, 2) + math.pow(self.screenResolutionHeight, 2))
        di = math.sqrt(math.pow(self.screenWidthInCM, 2) + math.pow(self.screenHeightInCM, 2))
        return float(dp / di)

    def calculate_ipp(self):
        dp = math.sqrt(math.pow(self.screenResolutionWidth, 2) + math.pow(self.screenResolutionHeight, 2))
        di = math.sqrt(math.pow(self.screenWidthInCM, 2) + math.pow(self.screenHeightInCM, 2))
        return float(di / dp)