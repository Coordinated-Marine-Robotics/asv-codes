# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 18:08:11 2018

@author: Syafiqah
"""

import numpy as np
import cv2 as cv

#40cm:360,212
#60cm:358,223
#80cm:355,231
#7 452 123

def laser_measurement():
	vid = cv.VideoCapture(1) #0 on desktop #1 on laptop

	#range for the laser pointer
	lower_red = np.array([0,0,245])
	upper_red = np.array([45,45,255])

	while(True):
		ret, frame = vid.read()
		hsvt = cv.cvtColor(frame,cv.COLOR_BGR2HSV)
	
		mask = cv.inRange(hsvt, lower_red, upper_red)
	
		#comparing median & Gaussian blur
		#Gaussian is more accurate
		#median = cv.medianBlur(mask,5) #remove noises
		gray = cv.GaussianBlur(mask, (3,3),0)
	
		(minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(gray)
		#(minVal2, maxVal2, minLoc2, maxLoc2) = cv.minMaxLoc(median)
	
		cv.circle(gray, maxLoc, 10, (0, 255, 0), 2)
		#cv.circle(median, maxLoc2, 10, (255,0,0), 2)
		#cv.circle(frame, maxLoc2, 10, (255,0,0), 2)
		cv.circle(frame, maxLoc, 10, (0,255,0), 2)
		cv.line(frame, (0,630), (590,0), (0,0,255),1)
		cv.imshow("ori", frame)
		#cv.imshow("median", median)
		#cv.imshow("gray", gray)
		#print(maxLoc2)
		xy_val = maxLoc
		y_val = maxLoc[0]
		x_val = maxLoc[1]
	
		#using formula theta=px*rad+ro
		#px = abs(x_val-240)
		#theta = 0.00272*px-0.0199
		#tan_theta = np.tan(theta)
		#distance = int(1.6/tan_theta)
		#print("distance: %s cm" %distance)
	
		py = abs(y_val-320)
		theta = 0.001445*py-0.034684
		tan_theta = np.tan(theta)
		distance = int(1.4/tan_theta)
		if maxLoc[0] != 0:
			print("distance: %s cm" %distance)

		if cv.waitKey(20) == 27: # 27 is ESC key
			break
	return distance
	vid.release()
	cv.destroyAllWindows()

