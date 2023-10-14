import math
import Screen
import Sample
import socket
import copy
import pygame

def mean(array):
    if array:
        a = [s for s in array if s is not None]
        return float(sum(a) / float(len(a)))

def compute_window_size(windowTimeInMilliseconds):
    return round(float(windowTimeInMilliseconds / 3))

# def calculate_ppi(screen=Screen.Screen()):
#     dp = math.sqrt(math.pow(screen.screenResolutionWidth,2)+math.pow(screen.screenResolutionHeight,2))
#     di = math.sqrt(math.pow(screen.screenWidthInCM, 2) + math.pow(screen.screenHeightInCM, 2))
#     return float(dp/di)
#
# def calculate_ipp(screen=Screen.Screen()):
#     dp = math.sqrt(math.pow(screen.screenResolutionWidth,2)+math.pow(screen.screenResolutionHeight,2))
#     di = math.sqrt(math.pow(screen.screenWidthInCM, 2) + math.pow(screen.screenHeightInCM, 2))
#     return float(di/dp)

def convert_angle_to_distance(angleInDegrees, eyeToScreenDistance):
    return float(eyeToScreenDistance * (math.tan(math.radians(angleInDegrees))))

def convert_distance_to_angle(distanceInCM, eyeToScreenDistanceInCM):
    return float(math.degrees(math.atan(distanceInCM/eyeToScreenDistanceInCM)))

def listen_and_save():
    port_number = 11000  # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_STREAM)  # Connect the socket to the port where the server is listening
    server_address = ("localhost", port_number)
    print("Connecting to %s port %s" % server_address)
    sock.connect(server_address)
    file = open('../Data/Study4/data.txt', 'w')
    while True:
        data = sock.recv(256)
        print(str(data))
        try:
            file.write(str(data.decode('utf-8')))
        finally:
            file.close()

def load_dirty_json(dirty_json):
    regex_replace = [(r"([ \{,:\[])(u)?'([^']+)'", r'\1"\3"'), (r" False([, \}\]])", r' false\1'), (r" True([, \}\]])", r' true\1')]
    for r, s in regex_replace:
        dirty_json = re.sub(r, s, dirty_json)
    clean_json = json.loads(dirty_json)
    return clean_json

def visualize_gound_truth():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    white = (255,255,255)
    screen.fill(white)
    done = False
    file = open('C:/Users/islam/Box Sync/Projects/CurrentProjects/RealtimeOculomotorFramework/Data/MADAGASCAR1/ground-truth.txt', 'r')
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        counter = 1
        for line in file:
            if counter > 1:
                if line != '\n':
                    fields = line.split("\t")
                    GazeX = fields[13]
                    GazeY = fields[14]
                    GazeEventType = fields[15]
                    # if str(GazeEventType) == "Unclassified":
                    #     pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(float(GazeX), float(GazeY), 1, 1))
                    if str(GazeEventType) == "Saccade":
                        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(float(GazeX), float(GazeY), 2, 2))
                    if str(GazeEventType) == "Fixation":
                        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(float(GazeX), float(GazeY), 2, 2))
            counter = counter + 1
        pygame.display.flip()
    file.close()