import cv2
import numpy as np
cap = cv2.VideoCapture('http://192.168.1.2:8080/video')

lower_red = np.array([158,85,72])
upper_red = np.array([180,255,255])
kernelOpen = np.ones((5,5))
kernelClose = np.ones((20,20))

def dilate(img):
    mask = cv2.inRange(img, lower_red, upper_red)
    mask = cv2.dilate(mask, (11,11), iterations=1)
    maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernelOpen)
    maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, kernelClose)
    return maskClose

while True:

    _, frame = cap.read()
    temp = frame
    frame = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    '''frame = cv2.resize(frame, (640, 480))
    frame = dilate(frame)
    cv2.imshow('frame', frame)'''
    cv2.imshow('temp', temp)
    if cv2.waitKey(2) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()