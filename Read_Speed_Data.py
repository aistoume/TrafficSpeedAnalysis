import pandas as pd
import scipy as sp
import numpy as np
import math
import os
from matplotlib import pyplot as plt
import collections
from datetime import datetime, date

# read data as array

#data_path = './Speed_data' # Test folder
data_path = './traffic_data'
save_path = './check_point'
files = os.listdir(data_path)
Speed_collection = collections.defaultdict(list) # index = 'Day_hour'
Speed_statis = []
flag = True
for file in files:
    # skip the dir file
    if os.path.isdir(file): continue

    # read speed file by pandas
    name = data_path+'/'+file
    sheet_name = 'Report Data'
    data_frame = pd.read_excel(name, sheetname=sheet_name)
    
    if flag:
        print data_frame[:5]
        flag = False
    
    # Convert date of data collected to day of week 
    collect_date = file[:-5]
    day = datetime.strptime(collect_date,'%Y%m%d').strftime('%a')
    
    # calculate average 
    time = data_frame['Time']
    location = data_frame['Postmile (Abs)']
    speed = data_frame['AggSpeed']
    location_map = set(location)
    print "Number of sensor = ",len(location_map)
    
    for i in xrange(len(time)):
        hour = time[i].split(':')[0]
        idx = day+'_'+hour+'_'+str(location[i]).zfill(7)
        
        Speed_collection[idx].append(speed[i])

# make the array of check point(mean and variance) and save it
key = sorted(Speed_collection.keys())

for idx in key:
    #Speed_statis[idx] = [np.mean(Speed_collection[idx]), np.var(Speed_collection[idx])]
    Speed_statis.append([idx, np.mean(Speed_collection[idx]), np.var(Speed_collection[idx])])


save_folder = save_path+'/average_speed.csv'
df = pd.DataFrame(Speed_statis, columns=["Index", "Mean_Speed","Variance_Speed"])    
df.to_csv(save_folder,index=False)

# plot a bar chart of speed distribution to verify whether it is Gaussian distribution
idx = key[40]
speed = Speed_collection[idx]
M = max(speed)
m = min(speed)
bins = np.linspace(math.ceil(m)-5, math.floor(M)+5,40)

plt.xlim([m-5,M+5])
plt.hist(speed, bins=bins)
plt.title('Speed Distribution '+' '.join(idx.split('_')))
plt.xlabel('Speed(MPH)')
plt.ylabel('Count')
plt.show()