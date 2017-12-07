# sess6072_lab
 
# Author: Blair Thornton
# Date: 17/10/2017

""" 
    Parsers for raw sensor data for the Vector Node ASV platform to generate a nav_standard.json file containinng the data you specify when you call the function.
    
    The code expect to find a data.yaml file in the specified path to load instructions for data analysis.

        Usage:
            sess6072_lab.py <options>
                where <options> are 
                    -i <path to data_format.yaml>
                    -s <start time in local time> hhmmss 
                    -f <end time in local time> hhmmss

            eg.
            python3 asv_nav.py -i ../raw/2017/example/20171017_151455_VNA00_SESS6072_lab_001 -s 153000 -f 160000

        data_format.yaml example:
            
            #YAML 1.0
            metadata:
                platform: VNA02
                mission: SESS6072
                date: 2017/08/17

            orientation:
                format: sensehat
                filepath: navigation/
                filename: imu.txt
                timezone: utc
                timoffset: 0.00

            acceleration:
                format: sensehat
                filepath: navigation/
                filename: imu.txt
                timezone: utc
                timoffset: 0.0
            
            strain:
                format: phidget_1046
                filepath: strain/
                filename: strain.txt
                timezone: utc
                timoffset: 0.0

        Returns:
            
            Returns:
            interleaved navigation and imaging data with output options:

                nav_standard.json
                    [{"epoch_timestamp": 1501974125.926, "epoch_timestamp_dvl": 1501974125.875, "class": "measurement", "sensor": "phins", "frame": "body", "category": "velocity", "data": [{"x_velocity": -0.075, "x_velocity_std": 0.200075}, {"y_velocity": 0.024, "y_velocity_std": 0.200024}, {"z_velocity": -0.316, "z_velocity_std": 0.20031600000000002}]},
                    {"epoch_timestamp": 1501974002.1, "class": "measurement", "sensor": "phins", "frame": "inertial", "category": "orientation", "data": [{"heading": 243.777, "heading_std": 2.0}, {"roll": 4.595, "roll_std": 0.1}, {"pitch": 0.165, "pitch_std": 0.1}]},
                    {"epoch_timestamp": 1501974125.926, "epoch_timestamp_dvl": 1501974125.875, "class": "measurement", "sensor": "phins", "frame": "body", "category": "altitude", "data": [{"altitude": 31.53, "altitude_std": 0.3153}, {"sound_velocity": 1546.0, "sound_velocity_correction": 0.0}]},
                    {"epoch_timestamp": 1501974002.7, "epoch_timestamp_depth": 1501974002.674, "class": "measurement", "sensor": "phins", "frame": "inertial", "category": "depth", "data": [{"depth": -0.958, "depth_std": -9.58e-05}]},
                    {"epoch_timestamp": 1502840568.204, "class": "measurement", "sensor": "gaps", "frame": "inertial", "category": "usbl", "data_ship": [{"latitude": 26.66935735000014, "longitude": 127.86623359499968}, {"northings": -526.0556603025898, "eastings": -181.08730736724087}, {"heading": 174.0588800058365}], "data_target": [{"latitude": 26.669344833333334, "latitude_std": -1.7801748803947248e-06}, {"longitude": 127.86607166666667, "longitude_std": -1.992112444781924e-06}, {"northings": -527.4487693247576, "northings_std": 0.19816816183128352}, {"eastings": -197.19537408743128, "eastings_std": 0.19816816183128352}, {"depth": 28.8}]},{"epoch_timestamp": 1501983409.56, "class": "measurement", "sensor": "unagi", "frame": "body", "category": "image", "camera1": [{"epoch_timestamp": 1501983409.56, "filename": "PR_20170816_023649_560_LC16.tif"}], "camera2": [{"epoch_timestamp": 1501983409.56, "filename": "PR_20170816_023649_560_RC16.tif"}]}
                    ]

            These are stored in a mirrored file location where the input raw data is stored as follows with the paths to raw data as defined in data.yaml
            e.g. 
                raw     /<YEAR> /<SESSION>   /<PLATFORM_TYPE> / configuration / data.yaml
                                                              / nav/ imu.txt
                                                        
            For this example, the outputs would be stored in the following location, where folders will be automatically generated                                                    

                processed   /<YEAR> /<SESSION>   /<PLATFORM_TYPE> / <start_time end_time > / nav_standard.json   


    """

# Import librarys
import sys, os, math
import yaml, json
# import other libraries here
# e.g. import csv, json

# import other selfmade libraries here
from lib_coordinates.body_to_inertial import body_to_inertial
from lib_sensors.parse_sensehat import parse_sensehat
from lib_sensors.parse_interlacer import parse_interlacer
from lib_sensors.parse_phidget_1046 import parse_phidget_1046

# add libraries needed here, e.g.
# from <folder>.<function> import <function_name_used_to_call_it>
# if you need to go back in folder structure preceed with
# sys.path.os("..")
# on the line above

# constants used
gravity = 9.81 # acceleration due to gravity in m/s^2
deg_to_rad = 3.141592654/180 


def parse_data(filepath,start_time,finish_time):


    # specify the name of the output file, we use a generic format and filename
    filename = 'nav_standard.json'

    # initiate data and processing flags
    proc_flag = 0   
    metadata_flag=0
    orientation_flag=0
    acceleration_flag=0    
    strain_flag =0


    print('Loading data_format.yaml')    
    data_file = filepath+ '/' + 'data_format.yaml'
    with open(data_file,'r') as stream:
        load_data = yaml.load(stream)        
    
    for i in range(0,len(load_data)): 
        if 'metadata' in load_data:
            metadata_flag=1
            platform_name = load_data['metadata']['platform']
            mission_name = load_data['metadata']['mission']
            date = load_data['metadata']['date']            
        
        if 'orientation' in load_data:
            orientation_flag=1                    
            orientation_format = load_data['orientation']['format']
            orientation_filepath = load_data['orientation']['filepath']
            orientation_filename = load_data['orientation']['filename']
            orientation_timezone = load_data['orientation']['timezone']
            orientation_timeoffset = load_data['orientation']['timeoffset']

        if 'acceleration' in load_data:
            acceleration_flag=1
            acceleration_format = load_data['acceleration']['format']
            acceleration_filepath = load_data['acceleration']['filepath']
            acceleration_filename = load_data['acceleration']['filename']
            acceleration_timezone = load_data['acceleration']['timezone']
            acceleration_timeoffset = load_data['acceleration']['timeoffset']

        if 'strain' in load_data:
            strain_flag=1                    
            strain_format = load_data['strain']['format']
            strain_filepath = load_data['strain']['filepath']
            strain_filename = load_data['strain']['filename']
            strain_timezone = load_data['strain']['timezone']
            strain_timeoffset = load_data['strain']['timeoffset']
    
            print('Loading calibration.yaml')    
            data_file = filepath+ '/' + 'calibration.yaml'
            strain_calibration_force=[]
            strain_calibration_value=[]
            with open(data_file,'r') as stream:
                load_data = yaml.load(stream)  
                number_of_points = load_data['number_of_points']
                for i in range(0,len(load_data)-1): 
                    value_label= 'value_' + str(i)            
                    strain_calibration_force.append(load_data[value_label]['mass']*gravity)
                    strain_calibration_value.append(load_data[value_label]['value'])

    # generate output path
    print('Generating output paths')    
    sub_path = filepath.split('/')        
    sub_out=sub_path
    outpath=sub_out[0]
    
    sub_path.append(start_time + '_' + finish_time)
    for i in range(1,len(sub_path)):
        if sub_path[i]=='raw':
            sub_out[i] = 'processed'
            proc_flag = 1
        else:
            sub_out[i] = sub_path[i]
        
        outpath = outpath +'/' + sub_out[i]
        # make the new directories after 'processed' if it doesnt already exist 
        if proc_flag == 1:
            #at end of folder structure, add folder for the specified timestamp range            
            if os.path.isdir(outpath) == 0:
                try:
                    os.mkdir(outpath)                    
                except Exception as e:
                    print("Warning:",e) 



    
    # generate file with parsed data (overwrite if exists)
    with open(outpath + '/' + filename,'w') as fileout:
        print('Loading raw data')

        # read in, parse data and write data
        if orientation_flag == 1:             
            if orientation_format == "sensehat":
                parse_sensehat(filepath + '/' + orientation_filepath,orientation_filename,'orientation',orientation_timezone,orientation_timeoffset,date,start_time,finish_time,outpath,filename,fileout)
                
        if acceleration_flag == 1:                
            if acceleration_format == "sensehat":
                parse_sensehat(filepath + '/' + acceleration_filepath,acceleration_filename,'acceleration',acceleration_timezone,acceleration_timeoffset,date,start_time,finish_time,outpath,filename,fileout)

        if strain_flag == 1:
            if strain_format == "phidget_1046":
                parse_phidget_1046(filepath + '/' + strain_filepath,strain_filename,'strain',strain_timezone,strain_timeoffset,date,start_time,finish_time,outpath,filename,fileout)

    fileout.close()
    
    #interlace the data based on timestamps
    print('Interlacing data')
    parse_interlacer('oplab',outpath,filename)
    print('Output saved to ' + outpath + '/' + filename)   

    # load data
    print('Loading json file ' + outpath + '/' + filename)
    with open(outpath + '/' + filename) as nav_standard:                
        parsed_json_data = json.load(nav_standard)


    
    # initialise lists you will need (hint, you need to add the new lists you will use)
    strain_time=[]
    strain_data=[]

    acceleration_time=[]
    acceleration_x=[]
    acceleration_y=[]
    acceleration_z=[]

    orientation_time=[]
    orientation_roll=[]
    orientation_pitch=[]
    orientation_yaw=[]

    # i here is the number of the data packet
    for i in range(len(parsed_json_data)):
        
        # if you look at the json file loaded in line 208, the header category is one of the following options
        # parsed_json_data[i]['category'] looks for the i'th instant of the header 'category' and returns the value that has the label category
        # which is specified according to the standard json format, i.e. {some data , "category" : "the thing being specified", some more data}
        
        # similarly parsed_json_data[i]['epoch_timestamp']
        # i.e. {some data , "epoch_timestamp" : <a numerical value>, some more data}
        # will return the value of time. 

        # json standards allow you to have nested data, so e.g. 
        # parsed_json_data[i]['data'][1]['acceleration_x']
        # looks for a header 'data' and looks for the 2nd subheader ([0] would be the 1st), which should be 'acceleration_x' and returns it
        if 'strain' in parsed_json_data[i]['category']:
            strain_time.append(parsed_json_data[i]['epoch_timestamp'])
            strain_data.append(parsed_json_data[i]['data'][0]['strain'])
            
        if 'acceleration' in parsed_json_data[i]['category']:
            acceleration_time.append(parsed_json_data[i]['epoch_timestamp'])
            acceleration_x.append(parsed_json_data[i]['data'][1]['acceleration_x']*gravity)
            acceleration_y.append(parsed_json_data[i]['data'][2]['acceleration_y']*gravity)
            acceleration_z.append(parsed_json_data[i]['data'][0]['acceleration_z']*gravity)
        
        if 'orientation' in parsed_json_data[i]['category']:
            orientation_time.append(parsed_json_data[i]['epoch_timestamp'])
            orientation_roll.append(parsed_json_data[i]['data'][1]['roll']*deg_to_rad)
            orientation_pitch.append(parsed_json_data[i]['data'][2]['pitch']*deg_to_rad)
            orientation_yaw.append(parsed_json_data[i]['data'][0]['heading']*deg_to_rad)
            
    
    # perform coordinate transformation to calculate the 
    acceleration_north=[]
    acceleration_east=[]
    acceleration_down=[]    

    for i in range(len(acceleration_time)):        
        [north,east,down] = body_to_inertial(orientation_roll[i], orientation_pitch[i], orientation_yaw[i], acceleration_x[i], acceleration_y[i], acceleration_z[i])
        acceleration_north.append(north)
        acceleration_east.append(east)
        acceleration_down.append(down)
    

    # Task 1
    # 1.1 Plot the amplitude, plot the fft of this acceleration in the horizontal and vertical directions for each wave condition
    
    # uncomment these to write the values out to a csv file if you prefer
    with open(outpath + '/acceleration.csv' ,'w') as fileout:
       fileout.write('epoch_time, acceleration_north, acceleration_east, acceleration_down \n')
    for i in range(len(acceleration_time)):        
       with open(outpath + '/acceleration.csv' ,'a') as fileout:
           fileout.write(str(acceleration_time[i])+','+str(acceleration_north[i])+','+str(acceleration_east[i])+','+str(acceleration_down[i])+'\n')
           fileout.close()

    with open(outpath + '/orientation.csv' ,'w') as fileout:
       fileout.write('epoch_time, roll, pitch, yaw \n')
    for i in range(len(orientation_time)):        
       with open(outpath + '/orientation.csv' ,'a') as fileout:
           fileout.write(str(orientation_time[i])+','+str(orientation_roll[i])+','+str(orientation_pitch[i])+','+str(orientation_yaw[i])+'\n')
           fileout.close()

    with open(outpath + '/strain.csv' ,'w') as fileout:
       fileout.write('epoch_time, strain \n')
    for i in range(len(strain_time)):        
       with open(outpath + '/strain.csv' ,'a') as fileout:
           fileout.write(str(strain_time[i])+','+str(strain_data[i])+'\n')
           fileout.close()
    # Task 2
    # 2.1 Apply the calibration values to the strain gauge readings to compute force in N
    # 2.2 Plot the amplitude, plot the fft of this the strain in N for each wave condition

    # uncomment these to see the values
    #print(strain_calibration_value) # the strain gauge reading corresponding to the calibration force
    #print(strain_calibration_force) # the mass * gravity applied to the strain gauge corresponding to values above
    #print(strain_time) # the time stamp of the strain data taken during the experiments in th specified time window
    #print(strain_data) # the strain gauge values taken during the experiments in th specified time window        


    print('Complete')



    

def syntax_error():
# incorrect usage message
    print("     pythom3 sess6072_lab.py <options>")
    print("         -i <path to data_format.yaml>")
    print("         -s <start time in utc time> hhmmss")
    print("         -f <finish time in utc time> hhmmss")
    print("     eg.")
    print("     python3 sess6072_lab.py -i ../raw/2017/example/20171017_151455_VNA00_SESS6072_lab_001 -s 153000 -f 160000")
    return -1

                

            

    

if __name__ == '__main__':

    # initialise flags
    flag_i=0    
    
    # take the whole day
    start_time='000000'
    finish_time='235959'

    # check number of input variables
    if (int((len(sys.argv)))) <= 2:
        print('Error: not enough arguments')
        syntax_error()
    else:   
        # read in filepath, start time and finish time from function call
        for i in range(math.ceil(len(sys.argv)/2)):

            option=option=sys.argv[2*i-1]
            value=sys.argv[2*i]                 

            if option == "-i":
                filepath=value
                flag_i=1
            if option == "-s":
                start_time=value                
            if option == "-f":
                finish_time=value               

        if (flag_i ==1):
            sys.exit(parse_data(filepath,start_time,finish_time))            
        else:
            syntax_error()
            
        