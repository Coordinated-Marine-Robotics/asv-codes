#Things to add: Laser pointing direction. If object is not detected (found==0) when object is detected the last time..cover all loop holes
#Add MQTT communication setup

import ASV_Functions as AF
import ASV_Run as AR
import imu 
import laser2
#Coordination Code
ASV = 'ASV_0'	#Name of ASV (Vehicle configuration file)
N = 3	#Number of ASV's
target_distance=100 # SETUP FILE  (MISSION.YAML)

def list_ASV():		#list of ASV in mission
	ASV_list = []	#Creates empty array to list out the number of ASV used
	a = [str(i) for i in range(N)]	#List out each character of a string
	for j in a:
		b = ASV.replace(ASV[4],j)	#Replaces the number identity of the ASV name
		ASV_list.append(b)		#Adds name of ASV to the empty array
		print(ASV_list)
	return ASV_list


#Looking for the object
while(True):
	if found == 0:
		if lastSeen < Rcentre_x:	#If last seen of object coordinate is to the left of the reference frame
			AF.turnLeft()	#Turn left
		else:	#If the last seen of the object frame coordinate is to the right of the reference frame
			AF.turnRight()	#Turn right


	#Tracking of object (keeping object frame at centre of camera)
	if found == 1:	#if object is detected
		if Rcentre_x != Ocentre_x:	#if reference frame is not aligned with object frame
			while(Ocentre_x<Rcentre_x):	#while the object frame is to the left of reference frame
				AF.turnLeft()	#turn left to centralise the object to the middle of the camera view
			else:
				AF.turnRight() #turn right if the object frame is to the right of the reference frame

	#Keeping constant distance of 1m between ASV and object
		distance = laser2.laser_measurement()
		if distance < target_distance:	#distaince between ASV and object, if ASV is closer than 1m to object
			AF.Thruster_Values(LDM = 180, Speed_PC=1)	#move backwards (reverse)
		else:
			 AF.Thruster_Values(LDM = 0, Speed_PC=1)	#move forward if ASV is further than 1m from object

	#Setting the position of first and second ASV to find centre of object
		list_ASV()	#Calls the list function
		online = []	#Array of online ASV's
		for i in range(N):
			if ASV_list[i] == ON:	#Checks which ASV is online
				online.append(ASV_list[i])	#Adds online ASV to the array
				ASV1 = online[0]	#Set the first online ASV of the element as the first ASV 
				ASV2 = online[1]	#Set the second online ASV of the element as the second ASV
				#Sets the first ASV South of the object
				if imu.iihdt == 0:
					imu.iihdt = North
				elif imu.iihdt ==180:
					imu.iihdt = South

				if heading.ASV1 != North:	#If first ASV is not facing north
					if x.ASV1 < x.ASV2:	#Checks to see whether the second ASV is to the left or right of the first ASV
						AF.Thruster_Values(LDM = -90, Speed_PC=1) # move to the left	#and moves in the opposite direction to avoid collision
					else:
						AF.Thruster_Values(LDM = 90, Speed_PC=1)	#move to the right
				#Sets the second ASV north of the object
				if heading.ASV2 != South:	#If second ASV is not facing south (opposite of first ASV) 
					if x.ASV2 < x.ASV1:	#Checks to see whether first ASV is to the left or right of the second ASV
						AF.Thruster_Values(LDM = -90, Speed_PC=1) # move to the left	#and moves in opposite direction to avoid 
					else:
						AF.Thruster_Values(LDM = 90, Speed_PC=1)	#move to the right
				Object_Centre = ((y.ASV1 + y.ASV2)/2) 
					



#Positioning additional ASV's based on the relative angle to the first ASV
#	if ASV != online[0]:	#if current ASV is not ASV 0 (ASV 2 or others)
#		for i in online[1:]:	#N is number of ASV
#			Dpy = y(i+1) - y(1)	#Difference in y-coordinates between ASV 0 and ASV i'th
#			Dpx = x(i+1) - x(1)	#Difference in x-coordinates between ASV 0 and ASV i'th 
#			angle = 180/N 	#Equal angle needed between ASV's
#			phi = (N-i)*angle	#Required angle between first ASV and i'th ASV
#			theta = atan2(Dpy,Dpx)	#Current angle between ASV 0 and ASV i'th based on their x-y coordinates
#			if theta<phi:	#if current angle is smaller than the required angle
#				mvRight()	#move right 
#			else:
#				mvLeft()	#move left if angle is greater than required angle 


#Positioning additional ASV's based on the relative angle to the middle of object
	if ASV != online[0:2]:	#if current ASV is not ASV 0 (ASV 2 or others)
		for i in online[2:]:	#N is number of ASV
			Dpy = y(i+1) - Object_Centre	#Difference in y-coordinates between object centre and ASV i'th
			Dpx = x(i+1) - x(1)	#Difference in x-coordinates between ASV 0 and ASV i'th 
			angle = 360/N 	#Equal angle needed between ASV's
			#phi = (N-i)*angle	#Required angle between first ASV and i'th ASV
			theta = atan2(Dpy,Dpx)	#Current angle between ASV 0 and ASV i'th based on their x-y coordinates
			if theta<angle:	#if current angle is smaller than the required angle
				mvRight()	#move right 
			else:
				mvLeft()	#move left if angle is greater than required angle 




