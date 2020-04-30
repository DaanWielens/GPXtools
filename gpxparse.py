# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 17:00:07 2020

@author: Daan Wielens

Function to parse a GPX file into an object
"""

import numpy as np
import pyproj
import os

# The GPX activity will be return as a class
class activity:
    def __init__(self, x, y, act_name, act_type, act_time, filename):
        self.xdata = x
        self.ydata = y
        self.act_name = act_name
        self.act_type = act_type
        self.act_time = act_time
        self.filename = filename
        # Standard settings for plotting in GPXplot
        self.show = True
        self.color = 'white'
        self.alpha = 0.2
        self.linewidth=1
        
        
def parseGPX(filename):
    x = np.array([])
    y = np.array([])
    ts_found = 0
    with open(filename, 'r') as file:
        for line in file:
            # Read track points and add them to the x,y data sets
            if '<trkpt lat' in line:
                line = line.split('"')
                x = np.append(x, float(line[3]))
                y = np.append(y, float(line[1]))
            # Read activity name (as shown in apps such as Garmin Connect)
            if '<name>' in line:
                act_name = line.split('>')[1].split('<')[0]
            # Read activity type
            if '<type>' in line: 
                act_type = line.split('>')[1].split('<')[0]
            # Read FIRST timestamp
            if '<time>' in line and ts_found == 0: 
                act_time = line.split('>')[1].split('<')[0]
                act_time = act_time[:10] + ' at ' + act_time[11:16]
                ts_found = 1
    
    # Return filename (without folder)
    filename = os.path.split(filename)[1]   
    
    # Transform coordinates (take earth curvature into account)
    coord_transf = pyproj.Transformer.from_crs(4326, 3857)    
    x, y = coord_transf.transform(y, x)
    
    GPXact = activity(x, y, act_name, act_type, act_time, filename)
    return GPXact