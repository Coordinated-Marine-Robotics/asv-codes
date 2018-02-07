N = 3	#Number of ASV's


#Tracking of object (keeping object frame at centre of camera)
if found == 1:	#if object is detected
	if Rcentre_x != Ocentre_x:	#if reference frame is not aligned with object frame
		while(Ocentre_x<Rcentre_x):	#while the object frame is to the left of reference frame
			turnLeft()	#turn left to centralise the 
		else
			turnRight() #turn right if the object frame is to the right of the reference frame

#Keeping constant distance of 1m between ASV and object
	if distance < 100:	#distance between ASV and object, if ASV is closer than 1m to object
		reverse()	#move backwards (reverse)
	else
		forward()	#move forward if ASV is further than 1m from object

#Setting the position of first ASV as reference
	if ASV(N) = ASV(1):	#if current ASV is the first ASV (ASV 1)
		if heading != North:	#if ASV 1 is not facing North
			mvRight()	#move right until ASV 1 faces North 

#Positioning additional ASV's based on the relative angle to the first ASV
	if ASV(N) != ASV(1):	#if current ASV is not ASV 1 (ASV 2 or others)
		for i in range(1,N):	#N is number of ASV
			Dpy = y(i+1) - y(1)	#Difference in y-coordinates between ASV 1 and ASV i'th
			Dpx = x(i+1) - x(1)	#Difference in x-coordinates between ASV 1 and ASV i'th 
			angle = 180/N 	#Equal angle needed between ASV's
			phi = (N-i)*angle	#Required angle between first ASV and i'th ASV
			theta = atan2(Dpy,Dpx)	#Current angle between ASV 1 and ASV i'th based on their x-y coordinates
			if theta<phi:	#if current angle is smaller than the required angle
				mvRight()	#move right 
			else:
				mvLeft()	#move left if angle is greater than required angle 


