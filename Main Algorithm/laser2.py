# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 18:08:11 2018

@author: Syafiqah
"""

import numpy as np
import cv2 as cv


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
		gray = cv.GaussianBlur(mask, (3,3),0)
	
		(minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(gray)
		
		cv.circle(gray, maxLoc, 10, (0, 255, 0), 2)
		cv.circle(frame, maxLoc, 10, (0,255,0), 2)
		cv.line(frame, (0,630), (590,0), (0,0,255),1)
		#cv.imshow("ori", frame)
		
		xy_val = maxLoc
		y_val = maxLoc[0]
		x_val = maxLoc[1]
	
		py = abs(y_val-320)
		theta = 0.001445*py-0.034684
		tan_theta = np.tan(theta)
		distance = int(1.4/tan_theta)
		if maxLoc[0] != 0:
			return(distance)

	vid.release()
	cv.destroyAllWindows()
