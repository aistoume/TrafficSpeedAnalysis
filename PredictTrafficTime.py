import pandas as pd
import scipy as sp
import numpy as np
import math
import os
from matplotlib import pyplot as plt
import collections
from datetime import datetime, date
from scipy.stats import norm

# read data to pandas.DataFrame
speed_file = './check_point/average_speed.csv'
map_file = './check_point/distance_map.csv'
speed_frame = pd.read_csv(speed_file)
map_frame = pd.read_csv(map_file)

# Mapping sensor location to index
location_map = collections.defaultdict(int)
for i,loc in enumerate(map_frame['Postmile']):
    location_map[str(loc).zfill(7)] = i

# calculate the distance for each sensor
distance = [(float(map_frame['Postmile'][i+1]) - float(map_frame['Postmile'][i])) for i in xrange(186)]
distance.append(0)
time_cost = collections.defaultdict(list)
    
# Strategy 1 Heatmap of average speed to find the best time to start trip
speed_map = collections.defaultdict(list)
speed_var = collections.defaultdict(list)

day_list = ["Mon", "Tue","Wed","Thu","Fri", "Sat","Sun"]
hour_list = [str(i).zfill(2) for i in xrange(24)]
sensor_list = [str(i).zfill(3) for i in xrange(187)]
label_idx = speed_frame['Index'] 
speed_buff = [None]*187
sp_variance_buff = [None]*187

for i,idx in enumerate(label_idx):
    [day, hour, sensor] = idx.split('_')
    #sensor = double(sensor)
    loc_idx = location_map[sensor]
    hour = int(hour)
    if speed_frame['Mean_Speed'][i]>0:
        speed_buff[loc_idx] = speed_frame['Mean_Speed'][i]
        sp_variance_buff[loc_idx] = speed_frame['Variance_Speed'][i]
    else:
        speed_buff[loc_idx] = 60 
        sp_variance_buff[loc_idx] = 5
    if loc_idx == 186:
        speed_map[day].append(speed_buff)
        speed_var[day].append(sp_variance_buff)
        time_cost[day].append([d*1.0/s for d,s in zip(distance,speed_buff)])
        speed_buff = [None]*187
        sp_variance_buff = [None]*187
        
def SpeedHeatMap(day):
    data = np.array(speed_map[day])
    fig1 = plt.figure()
    ax = fig1.add_subplot(111)
    cax = ax.imshow(data, aspect='auto',cmap = 'plasma')
    
    # Show all ticks...
    sensor_label = [28+5.4*i for i in xrange(19)]
    #ax.set_xticks(np.arange(len(sensor_label)*10))
    ax.set_xticks(xrange(0,187,10))
    ax.set_yticks(np.arange(len(hour_list)))

    # ... and label them with the respective list entries
    ax.set_xticklabels(sensor_label)
    ax.set_yticklabels(hour_list)
    plt.title('Average Speed From San Diego to Los Angeles on '+day)
    plt.xlabel('Postmile (mile)')
    plt.ylabel('Time (hour)')
    fig1.colorbar(cax)
    plt.show()

SpeedHeatMap('Mon')


# Estimate the trip time by summing all the time_cost 
def EstimateTime(time_cost, target=187, time_start=0, time_end=24, day_start=0, day_end=7):
    estimate_time = collections.defaultdict(list)
    day_list = ["Mon", "Tue","Wed","Thu","Fri", "Sat","Sun"]
    hour_list = [str(i).zfill(2) for i in xrange(24)]
    for d in xrange(day_start, day_end):
        for h in xrange(time_start, time_end):
            cumulate_time = 0
            for pos in xrange(target):
                hour = h+int(cumulate_time//1)
                day = day_list[(d+hour//24)%7]
                cumulate_time += time_cost[day][hour%24][pos]
            estimate_time[day_list[d]].append(cumulate_time)

    travel_time = []
    min_time = 99
    min_day = 'Fri'
    min_hour = 23
    for day in day_list:
        travel_time.append(estimate_time[day])
        m = min(estimate_time[day])
        if m<min_time:
            min_time = m
            min_day = day
            min_hour = estimate_time[day].index(m)
    print 'The trip to Los Angeles with lowest time is '+str(min_hour)+':00 '+min_day+';'
    print 'The lowest estimate time to LA is '+ str(min_time)+' (hours).'
    
    time = np.array(travel_time) #python array
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111)
    cax2 = ax2.imshow(time, aspect='auto',cmap = 'plasma')
    ax2.set_xticks(np.arange(len(hour_list[time_start:time_end])))
    ax2.set_yticks(np.arange(len(day_list[day_start:day_end])))
    ax2.set_xticklabels(hour_list[time_start:time_end])
    ax2.set_yticklabels(day_list[day_start:day_end])
    fig2.colorbar(cax2)
    plt.title('Expected Time From San Diego to Los Angeles')
    plt.xlabel('Time (hour)')
    plt.show()
    
    return travel_time

expected_time = EstimateTime(time_cost, 187, 0, 24, 0, 7)


def DelayProbability(expected_time, speed_var, time=0, day='Sun', thres = 15):
    day_list = ["Mon", "Tue","Wed","Thu","Fri", "Sat","Sun"]
    
    hour_list = [str(i).zfill(2) for i in xrange(24)]
    d = day_list.index(day)
    time_exp = expected_time[d][time]
    time_delay = time_exp+thres/60.0
    
    vari_in_mean = sum(speed_var[day][time])/(len(speed_var[day][time])-1)
    cumulate_var = 0 
    speed_low = (131-28.0)/time_delay
    speed_mean = (131-28.0)/time_exp
    d_speed = speed_low-speed_mean
    z = d_speed/(vari_in_mean**0.5)
    p = norm.cdf(z)
    print 'The probability that you would delay more than '+str(thres)+' mins is '+str(p)+'.'
    
DelayProbability(expected_time, speed_var, 0, 'Sun', 15)
