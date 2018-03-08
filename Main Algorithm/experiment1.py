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

# run programme to work out centre of object
def Initial_Setup():
	
	max_value = 2500*4 #maximum speed desired for clockwise rotation
	min_value = 500*4  #minimum speed desired for anti-clockwise rotation

	servo = maestro.Controller()
	servo.setRange(0, min_value, max_value)
	servo.setRange(1, min_value, max_value)
	servo.setRange(2, min_value, max_value)
	#Initializing motor
	servo.setTarget(0,6000)
	servo.setTarget(1,6000)
	servo.setTarget(2,6000)
	time.sleep(1)
	while(get_Camera_Distance() == False):
		turnRight(1)
	# Rotates ASV base on the comparison of x-coords between target frame and camera frame
	while(get_Camera_Distance() == True):
		if distance > 100:
			P.Thruster_Values(LDM = 0, Speed_PC=1) # move forwards
		else:
			P.Thruster_Values(LDM = 180, Speed_PC=1) # move backwards


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