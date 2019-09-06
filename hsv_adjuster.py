import cv2
import numpy as np
import imutils
cap = cv2.VideoCapture('http://192.168.1.6:8080/video')
panel = np.zeros([100, 700], np.uint8)
cv2.namedWindow('panel')

kernelOpen = np.ones((5,5))
kernelClose = np.ones((20,20))

def nothing(x):
    pass

cv2.createTrackbar('L - h', 'panel', 0, 179, nothing)
cv2.createTrackbar('U - h', 'panel', 179, 179, nothing)
cv2.createTrackbar('L - s', 'panel', 0, 255, nothing)
cv2.createTrackbar('U - s', 'panel', 255, 255, nothing)
cv2.createTrackbar('L - v', 'panel', 0, 255, nothing)
cv2.createTrackbar('U - v', 'panel', 255, 255, nothing)



while True:
    _, frame = cap.read()
    frame = cv2.resize(frame, (640, 480))
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    l_h = cv2.getTrackbarPos('L - h', 'panel')
    u_h = cv2.getTrackbarPos('U - h', 'panel')
    l_s = cv2.getTrackbarPos('L - s', 'panel')
    u_s = cv2.getTrackbarPos('U - s', 'panel')
    l_v = cv2.getTrackbarPos('L - v', 'panel')
    u_v = cv2.getTrackbarPos('U - v', 'panel')
    lower_green = np.array([l_h, l_s, l_v])
    upper_green = np.array([u_h, u_s, u_v])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    mask = cv2.dilate(mask,(11,11), iterations=2)
    maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernelOpen)
    maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, kernelClose)
   
    cv2.imshow('maskClose', maskClose)
    cv2.imshow('panel', panel)
    cv2.imshow('frame', frame)
    if cv2.waitKey(2) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()