# parse_phidget_1046.py

# Scripts to parse phidget load cell data

# Author: Blair Thornton
# Date: 18/10/2017

import os
from datetime import datetime
import calendar
import sys, math, time

import json, glob
#http://www.json.org/

#sys.path.append("..")
# add libraries needed here, e.g.
# from <folder>.<function> import <function_name_used_to_call_it>
# if you need to go back in folder structure preceed with
# sys.path.os("..")
# on the line above

class parse_phidget_1046:
	def __init__(self, filepath, filename, category, timezone, timeoffset, date, start_time, finish_time, outpath, fileoutname, fileout):

		class_string = 'measurement'
		sensor_string = 'phidget_1046'

		# read in timezone
		if isinstance(timezone, str):			
			if timezone == 'utc' or  timezone == 'UTC':
				timezone_offset = 0			
			elif timezone == 'jst' or  timezone == 'JST':
				timezone_offset = 9;
			else:
				try:
					timezone_offset=float(timezone)
				except ValueError:
					print('Error: timezone', timezone, 'in data.yaml not recognised, please enter value from UTC in hours')
					return

		# convert to seconds from utc
		timeoffset = -timezone_offset*60*60 + timeoffset 

		# setup the time window
		yyyy = int(date[0:4])
		mm =  int(date[5:7])
		dd =  int(date[8:10])
				
		hours = int(start_time[0:2])
		mins = int(start_time[2:4])
		secs = int(start_time[4:6])			
		
		dt_obj = datetime(yyyy,mm,dd,hours,mins,secs)		
		time_tuple = dt_obj.utctimetuple()
		epoch_start_time = calendar.timegm(time_tuple) 
		
		hours = int(finish_time[0:2])
		mins = int(finish_time[2:4])
		secs = int(finish_time[4:6])		

		dt_obj = datetime(yyyy,mm,dd,hours,mins,secs)
		time_tuple = dt_obj.utctimetuple()
		epoch_finish_time = calendar.timegm(time_tuple) 
				
		path_sensehat = filepath + filename


		print('Parsing phidget_1046 standard data')
		data_list=[]
		with open(path_sensehat) as phidget_1046:				
			
			#read in data line by line			
			for line in phidget_1046.readlines():
							
				#initialise timestamp flag
				flag_got_time=False

			  	#find a relevant line
				if category in line:
					
					packet = line.split(',')
					header = packet[0].split(':')		

					if header[0] == "'epoch_time'":
				  		epoch_timestamp = float(header[1]) + timeoffset
				  		flag_got_time=True


					#print(epoch_timestamp,epoch_finish_time, epoch_timestamp <= epoch_finish_time)
					
					if epoch_timestamp >= epoch_start_time and epoch_timestamp <= epoch_finish_time:
						#parse data, isolate the values of interest												
						data=packet[1].split(':')
							
						if category in data[0]:
							strain = float(data[1])								
							#reset flag for next data
							
						flag_got_time = False
								
						# write out in the required format interlace at end
						
						frame_string = 'body'					

						data = {'epoch_timestamp': float(epoch_timestamp),'class': class_string,'sensor':sensor_string,'frame':frame_string,'category': category,'data': [{'strain':float(strain),'strain_std':'unknown'}]}							
						data_list.append(data)
						

		fileout.close()
		for filein in glob.glob(outpath + '/' + fileoutname):
			try:
				with open(filein, 'rb') as json_file:					
					data_in=json.load(json_file)						
					for i in range(len(data_in)):
						data_list.insert(0,data_in[len(data_in)-i-1])				        
						
			except ValueError:					
				print('Initialising JSON file')

			with open(outpath + '/' + fileoutname,'w') as fileout:
				json.dump(data_list, fileout)	
				del data_list
