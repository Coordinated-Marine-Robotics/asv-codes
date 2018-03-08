import numpy as np
import ASV_Parameters as P
import imu
import laser2
import maestro 
import time


ESC_Fwd_Max = P.ESC_Fwd_Max
ESC_Fwd_Min = P.ESC_Fwd_Min
ESC_Rev_Max = P.ESC_Rev_Max
ESC_Rev_Min = P.ESC_Rev_Min
ESC_Stop = P.ESC_Stop

T_cut_off = P.T_Cut_Off #? ## value range around 0 that don't bother turning on at all as close to 0

x1 = P.D1
x2 = P.D2
x3 = P.D3
theta = P.Theta


# def get_Communication_Data():
    # # receive data from the other ASVs:
    # # list of lists of [Name, Coordinates, camera distance]
    # # include my_data
    # # sort in ascending order of ASV name so consistent with other ASV's lists so the Pos_All code gives the same allocation list
    # return(ASV_Data)

# run programme to work out centre of object
def Initial_Setup():
	#get_Communication_Data()
	#get_Coords()
	online = P.My_Name	#Online ASV list from get_Communication_Data function
	# If distance is acquired then object is detected (will change to work with object recognition rather than distance measurement)
	# Rotates ASV untill target is detected 
	while(get_Camera_Distance() == False):
		#lastSeen = x-coordinate of target frame before ASV loses sight
		if lastSeen == None:	# When object has not yet been detected
			turnLeft(1)
		elif lastSeen > Rcentre_x:
			turnRight(1)
		elif laseSeen < Rcentre_x:
			turnLeft(1)
	# Rotates ASV base on the comparison of x-coords between target frame and camera frame
	while(get_Camera_Distance() == True):
		if Rcentre_x != Ocentre_x:
			while(Ocentre_x < Rcentre_x):
				turnLeft(0.5)
			else:
				turnRight(0.5)
	for i in range(N):
		ASV0 = online
		#ASV1 = online[1]
		heading_ASV0 = imu.iihdt
		# heading_ASV1 = imu.iihdt[1]
		# Sets the first ASV south of the target
		if heading_ASV0 != 0:	# If first asv is not facing north
			# compares the x-coordinates (from get_Coords function) of the first and second ASV so it moves in the opposite direction (avoids potential collision)
			if x_ASV0 < x_ASV1:	
				Thruster_Values(LDM = -90, Speed_PC=1)	# move to the left
			else:
				Thruster_Values(LDM = 90, Speed_PC=1)	# move to the right
		# Sets the second ASV north of the target
		#if heading_ASV1 != 180:	# if the second asv is not facing south	
		#	if x_ASV1 < x_ASV0:	
		#		Thruster_Values(LDM = -90, Speed_PC=1)	# move to the left
		#	else:
		#		Thruster_Values(LDM = 90, Speed_PC=1)	# move to the right

# def get_Coords():
    # # from GPS/Qualisys
    # return(Coords)

	
# def get_Current_Angle():
    # My_Coords = get_Coords() # from GPS/Qualisys
    # Object_Centre = get_Object_Centre() # this presumably needs to be continually updated - easy if even number of ASVs, difficult if odd
    # return(np.degrees(np.arctan2((My_Coords[0]-Object_Centre[0]),((My_Coords[1]-Object_Centre[1])))))

	
def get_Camera_Distance():
	distance = laser2.laser_measurement()
	print distance
	return distance


# Calculate the centre of target from the y-coordinates of two ASV's positioned north and south of target	
def get_Object_Centre():
	get_Coords()
	Object_Centre = ((y.ASV0 + y.ASV1)/2)
	print Object_Centre
	return Object_Centre
   


# def Communicate_Data():
    # # Broadcast data for other ASVs to collect:
    # # name, coordinates, camera distance
	# do we need camera_distance ??
	# My_Coords = get_Coords()
	# My_Camera_Dist = get_Camera_Distance()
	# My_ASV_Data = [My_Name, My_Coords, My_Camera_Dist]

# what happens if the ASV thinks it's communicating and acts accordingly but no-one else knows it's there
# or equally if they're spread out and some of them to the west don't know there's a whole other crowd to the west for example?
# probably something for the report rather than the programme


## ASV_Data = [[Name, [Coordinates], camera distance]]
def Position_Allocation(ASV_Data, Object_Centre):
	ASV_Angles_from_Positions = [[number, []] for number in range(0, len(ASV_Data))]
	for ASV in ASV_Data:
		ASV.append(np.degrees(np.arctan2((ASV[1][0]-Object_Centre[0]),((ASV[1][1]-Object_Centre[1]))))) # angle from centre
		ASV.append([])
		for i in range(len(ASV_Data)):
			angle = abs(ASV[3]-(i*360//len(ASV_Data)))
			if angle > 180:
				angle = 360 - angle
			ASV[4].append(abs(angle))
			ASV_Angles_from_Positions[i][1].append(abs(angle))
		ASV.append(ASV[4].index(min(ASV[4])))
	## ASV_Data is now a list of lists [ASV's name, coordinates, distance from camera, angle from centre, [angles from positions], closest position]
	## ASV_Angles_from_Positions is a list of list [position number, [angle of each ASV from that position]]
	ASV_Pos_Inc_Angle = sorted(ASV_Angles_from_Positions, key=lambda Position:min(Position[1]), reverse=True)
	## ASV_Pos_Inc_Angle is ASV_Angles_from_Positions sorted in descending order of the minimum distances
	ASV_Allocation = ['x' for number in range(0, len(ASV_Data))]
	while 'x' in ASV_Allocation:
		i = ASV_Pos_Inc_Angle.pop(0)
		minIndex = i[1].index(min(i[1]))
		while ASV_Data[minIndex][0] in ASV_Allocation:
			i[1][minIndex] = max(i[1]) + 1
			minIndex = i[1].index(min(i[1]))
		ASV_Allocation[i[0]] = ASV_Data[minIndex][0]
		for  p in ASV_Pos_Inc_Angle:
			p[1][minIndex] = max(p[1]) + 1
		ASV_Pos_Inc_Angle = sorted(ASV_Pos_Inc_Angle, key=lambda Position:min(Position[1]), reverse=True)
	return(ASV_Allocation) ## ASV_Allocation = List of ASV names where index = allocated position


def Thruster_Values(LDM, Speed_PC): ## Speed_PC = percentage of max speed required in direction of motion (value from 0 to 1)
    LDM = np.radians(LDM)
    a = np.array([[np.sin(LDM),-np.cos(theta-LDM),np.cos(theta+LDM)] , [np.cos(LDM),-np.sin(theta-LDM),-np.sin(theta+LDM)] , [x1,x2,x3]])
    b = np.array([1,0,0])
    T = np.linalg.solve(a, b)
    TiS = []
    for Ti in T:
        if -T_cut_off < Ti < T_cut_off:	## Check likely values close to 0
            TiS.append(ESC_Stop)
        if Ti > T_cut_off:
            TiS.append(ESC_Fwd_Min + ((ESC_Fwd_Max - ESC_Fwd_Min)*Speed_PC) * Ti / max(abs(T)))
        if Ti < -T_cut_off:
            TiS.append(ESC_Rev_Min + ((ESC_Rev_Max - ESC_Rev_Min)*Speed_PC) * -Ti / max(abs(T)))
        servo.setTarget(0, TiS)
    	servo.setTarget(1, TiS)
    	servo.setTarget(2, TiS)
    #return(TiS)

def turnLeft(Turn_Speed_PC):
    T1S = T2S = T3S = ESC_Fwd_Min + ((ESC_Fwd_Max - ESC_Fwd_Min)*Turn_Speed_PC)
    servo.setTarget(0, T1S)
    servo.setTarget(1, T2S)
    servo.setTarget(2, T3S)
    #return([T1S, T2S, T3S])

def turnRight(Turn_Speed_PC):
    T1S = T2S = T3S = ESC_Rev_Min + ((ESC_Rev_Max - ESC_Rev_Min)*Turn_Speed_PC)
    servo.setTarget(0, T1S)
    servo.setTarget(1, T2S)
    servo.setTarget(2, T3S)
    #return([T1S, T2S, T3S])