import ASV_Parameters as P
import numpy as np

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

# def Initial_Setup():
    # # run programme to work out centre of object etc.

	
# def get_Coords():
    # # from GPS
    # return(Coords)

	
# def get_Current_Angle():
    # My_Coords = get_Coords() # from GPS
    # Object_Centre = get_Object_Centre() # this presumably needs to be continually updated - easy if even number of ASVs, difficult if odd
    # return(np.degrees(np.arctan2((My_Coords[0]-Object_Centre[0]),((My_Coords[1]-Object_Centre[1])))))

	
# def get_Camera_Distance():
    # # use Sharon's camera code
    # return(Camera_Distance)

	
# def get_Object_Centre():
    # # use geometry to calculate the centre of the object
    # return(Object_Centre)


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

# def get_Communication_Data():
    # # receive data from the other ASVs:
    # # list of lists of [Name, Coordinates, camera distance]
    # # include my_data
    # # sort in ascending order of ASV name so consistent with other ASV's lists so the Pos_All code gives the same allocation list
    # return(ASV_Data)


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
    return(TiS)

def turnLeft(Turn_Speed_PC):
    T1S = T2S = T3S = ESC_Fwd_Min + ((ESC_Fwd_Max - ESC_Fwd_Min)*Turn_Speed_PC)
    return([T1S, T2S, T3S])

def turnRight(Turn_Speed_PC):
    T1S = T2S = T3S = ESC_Rev_Min + ((ESC_Rev_Max - ESC_Rev_Min)*Turn_Speed_PC)
    return([T1S, T2S, T3S])