# importing libraries
import cv2
import numpy as np
import imutils
import math
import time
# for controling the mouse
from pynput.mouse import Button, Controller
# camera url
url = 'http://192.168.1.6:8080/video'
cap = cv2.VideoCapture(url)

# defining the range of green color
lower_green = np.array([34, 48, 25])
upper_green = np.array([70, 255, 255])
lower_yellow = np.array([23, 120, 50])
upper_yellow = np.array([40, 255, 255])
lower_blue = np.array([100, 70, 25])
upper_blue = np.array([130, 255, 255])

# kernel used to filter the image to remove noise
kernelOpen = np.ones((5, 5))
kernelClose = np.ones((20, 20))

# mouse
mouse = Controller()
# display resolution
(screenX, screenY) = (1920, 1080)

# actions
drag = False
click = True
flag = False

Xg, Yg, Xb, Yb, Xy, Yy = 0, 0, 0, 0, 0, 0


# mask function to remove noise and dilate the object
def dilate(mask):
    # filtering the mask by opening and closing method
    # opening will remove all dots randomly
    # closing will close the small holes in the object
    mask = cv2.dilate(mask, (11, 11), iterations=2)
    maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernelOpen)
    maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, kernelClose)
    return maskClose


# function to separate the specific color
def makeInRange(img, lowerColor, upperColor):
    mask = cv2.inRange(img, lowerColor, upperColor)
    return mask


# function to find the contors
def getContours(mask):
    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    return cnts


def getDistance(x1, y1, x2, y2):
    return math.floor(math.sqrt((x2 - x1)**2 + (y2 - y1)**2))


def getScreenCorr(X, Y, shapeY, shapeX):
    return ((screenX * X) / shapeY), ((screenY * Y) / shapeX)


def performActions(x1, y1, x2, y2):
    global drag, click, flag
    d = getDistance(x1, y1, x2, y2)

    if d < 100:
        if drag is True and flag is False:
            mouse.press(Button.left)
            flag = True
            time.sleep(0.10)
        elif drag is True and flag is True:
            flag = False
            time.sleep(0.10)
            mouse.release(Button.left)
        elif drag is False and click is True:
            mouse.click(Button.left, 1)
            time.sleep(0.10)


def changeAction(x1, y1, x2, y2):
    global drag, click, flag

    d = getDistance(x1, y1, x2, y2)
    if d < 90:
        if drag is False and click is True:
            drag = True
            click = False
            time.sleep(0.10)
        elif drag is True and click is False:
            click = True
            drag = False
            time.sleep(0.10)


# main loop
while True:
    # getting frame
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    # temp frame
    frame = cv2.resize(frame, (640, 480))
    # getting the shape of the frame
    shapeX, shapeY = frame.shape[0], frame.shape[1]
    # converting to hsv
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # thresholding to get green color
    maskG = makeInRange(hsv, lower_green, upper_green)
    maskY = makeInRange(hsv, lower_yellow, upper_yellow)
    maskB = makeInRange(hsv, lower_blue, upper_blue)

    # dilate the objects
    maskG = dilate(maskG)
    maskY = dilate(maskY)
    maskB = dilate(maskB)

    # contour detection
    cntsG = getContours(maskG)
    cntsY = getContours(maskY)
    cntsB = getContours(maskB)

    if len(cntsB) and len(cntsY) and len(cntsG):
        # getting the top-left coor and height and width of the object
        xB, yB, wB, hB = cv2.boundingRect(cntsB[0])
        xY, yY, wY, hY = cv2.boundingRect(cntsY[0])
        xG, yG, wG, hG = cv2.boundingRect(cntsG[0])
        # getting the center of the object
        cxB, cyB = (xB + (wB // 2)), (yB + (hB // 2))
        cxY, cyY = (xY + (wY // 2)), (yY + (hY // 2))
        cxG, cyG = xG + (wG // 2), yG + (hG // 2)
        # calculating the coor according to 1920x1080
        Xb, Yb = getScreenCorr(cxB, cyB, shapeY, shapeX)
        Xy, Yy = getScreenCorr(cxY, cyY, shapeY, shapeX)
        Xg, Yg = getScreenCorr(cxG, cyG, shapeY, shapeX)
        # drawing a red circle on the center of the object
        cv2.circle(frame, (cxB, cyB), 5, (0, 0, 255), -1)
        cv2.circle(frame, (cxY, cyY), 5, (0, 0, 255), -1)
        cv2.circle(frame, (cxG, cyG), 5, (0, 0, 255), -1)

        # moving mouse to calculated coor
        mouse.position = (Xg, Yg)

        changeAction(Xg, Yg, Xb, Yb)

        performActions(Xb, Yb, Xy, Yy)

    print('drag = {}, click = {}, flag = {}'.format(drag, click, flag))
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
