# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 19:39:14 2018

@author: nr6g14
"""
#========================trackbar for single motor============================#

#import os     #to communicate with the system
#import time   #importing time library to make Rpi wait
#os.system ("sudo pigpiod") #Launching GPIO library
#time.sleep(1) # to remove an error
import maestro #importing GPIO library
import cv2 as cv


max_value = 8000 #maximum speed desired for clockwise rotation
min_value = 4000  #minimum speed desired for anti-clockwise rotation

servo = maestro.Controller()
servo.setRange(0, min_value, max_value)
servo.setRange(1, min_value, max_value)
servo.setRange(2, min_value, max_value)

def nothing(x):
    pass

cv.namedWindow('controller')
cv.createTrackbar('M1', 'controller',50,100,nothing)
cv.createTrackbar('M2', 'controller',50,100,nothing)
cv.createTrackbar('M3', 'controller',50,100,nothing)

#============================initialising=====================================#
servo.setTarget(0,6000)
servo.setTarget(1,6000)
servo.setTarget(2,6000)
print ("control OR stop")

#=============================control=========================================#
def control():
    print ("Starting the motor, I hope its calibrated and armed, if not restart by giving 'x'")
    #time.sleep(1)
    tbar0 = 50
    tbar1 = 50
    tbar2 = 50
    speed0 = 6000    # center point
    speed1 = 6000
    speed2 = 6000
    print("Calibrate by controlling the trackbar")
    while True:
        #cv.imshow('controller', M1)
        if cv.waitKey(20) == 27:
            stop()
            break
        servo.setTarget(0, speed0)
        servo.setTarget(1, speed1)
        servo.setTarget(2, speed2)
        tbar0 = cv.getTrackbarPos('M1', 'controller')
        tbar1 = cv.getTrackbarPos('M2', 'controller')
        tbar2 = cv.getTrackbarPos('M3', 'controller')
        speed0 = 40*tbar0+min_value
        speed1 = 40*tbar1+min_value
        speed2 = 40*tbar2+min_value
        print(speed0,  speed1,  speed2)
        """inp = input()

        if inp == "stop":
            stop()          #going for the stop function
            break
        elif inp == "arm":
            arm()
            break
        else:
            print ("WHAT DID I SAID!! Press a,q,d or e")"""


#=================================stop========================================#
def stop(): #This will stop every action your Pi is performing for ESC ofcourse.
    servo.setTarget(0,6000)
    servo.setTarget(1,6000)
    servo.setTarget(2,6000)
    servo.close()
    print("Okay")
#=============================================================================#



inp = input()
if inp == "control":
    control()
elif inp == "stop":
    stop()
else :
    print ("Error. Restart from beginning.")

cv.destroyAllWindows()
