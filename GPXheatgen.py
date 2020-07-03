import numpy as np
import matplotlib.pyplot as plt
import os
import pyproj

# Read a GPX file and return the lat (y) and lon (x) coordinates as np arrays
def parseGPX(filename):
    x = np.array([])
    y = np.array([])
    with open(filename, 'r') as file:
        for line in file:
            if '<trkpt lat' in line:
                line = line.split('"')
                x = np.append(x, float(line[3]))
                y = np.append(y, float(line[1]))
                
    # Transform coordinates (take earth curvature into account)
    coord_transf = pyproj.Transformer.from_crs(4326, 3857)    
    x, y = coord_transf.transform(y, x)

    return x, y

# Plot GPX data
def plotGPX(x,y):
    plt.plot(x,y)

#------------------------------------------------------------------------------
# MAIN CODE
#------------------------------------------------------------------------------

#%% Move old plots to _prev files (for comparison)
if os.path.isfile('Heatmap_bow.png'):
    os.rename('Heatmap_bow.png', 'Heatmap_bow_prev.png')
if os.path.isfile('Heatmap_wob.png'):
    os.rename('Heatmap_wob.png', 'Heatmap_wob_prev.png')

#%% Get all GPX data
x_all = []
y_all = []
cwd = os.getcwd()
for filename in os.listdir(cwd):
    if filename.endswith('.gpx'):
        x,y = parseGPX(filename)        
        x_all.append(x)
        y_all.append(y)

#%% Plot data - normal plot (black on white), alpha < 1
nData = len(x_all)
fig, ax = plt.subplots(figsize=(10, 10))
for i in range(len(x_all)):
    plt.plot(x_all[i], y_all[i], color='black', alpha=0.2)
ax.set_xticks([])
ax.set_yticks([])

# Remove 'figure border' without destroying ALL axis' parameters:
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# Fix axis limits
xlm = ax.get_xlim()
ylm = ax.get_ylim()
xdiff = xlm[1] - xlm[0]
ydiff = ylm[1] - ylm[0]
xymax = max([xdiff, ydiff])
if xdiff > ydiff:
    newylims = [-xymax/2, xymax/2] + (ylm[0]+ylm[1])/2
    ax.set_ylim(newylims)
else:
    newxlims = [-xymax/2, xymax/2] + (xlm[0]+xlm[1])/2
    ax.set_xlim(newxlims)

# Save plot
plt.savefig('Heatmap_bow.png')

#%% Plot data - normal plot (white on black), alpha < 1
nData = len(x_all)
fig, ax = plt.subplots(figsize=(10, 10))
fig.patch.set_facecolor('black')
ax.set_facecolor('black')
for i in range(len(x_all)):
    plt.plot(x_all[i], y_all[i], color='white', alpha=0.2)
ax.set_xticks([])
ax.set_yticks([])

# Remove 'figure border' without destroying ALL axis' parameters:
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# Fix axis limits
xlm = ax.get_xlim()
ylm = ax.get_ylim()
xdiff = xlm[1] - xlm[0]
ydiff = ylm[1] - ylm[0]
xymax = max([xdiff, ydiff])
if xdiff > ydiff:
    newylims = [-xymax/2, xymax/2] + (ylm[0]+ylm[1])/2
    ax.set_ylim(newylims)
else:
    newxlims = [-xymax/2, xymax/2] + (xlm[0]+xlm[1])/2
    ax.set_xlim(newxlims)

# Save plot
plt.savefig('Heatmap_wob.png', facecolor='black')

#%% Plot data - normal plot (white on black), alpha < 1, fine line for HD
nData = len(x_all)
fig, ax = plt.subplots(figsize=(10, 10))
fig.patch.set_facecolor('black')
ax.set_facecolor('black')
for i in range(len(x_all)):
    plt.plot(x_all[i], y_all[i], color='white', alpha=0.2, linewidth=0.2)
ax.set_xticks([])
ax.set_yticks([])

# Remove 'figure border' without destroying ALL axis' parameters:
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# Fix axis limits
xlm = ax.get_xlim()
ylm = ax.get_ylim()
xdiff = xlm[1] - xlm[0]
ydiff = ylm[1] - ylm[0]
xymax = max([xdiff, ydiff])
if xdiff > ydiff:
    newylims = [-xymax/2, xymax/2] + (ylm[0]+ylm[1])/2
    ax.set_ylim(newylims)
else:
    newxlims = [-xymax/2, xymax/2] + (xlm[0]+xlm[1])/2
    ax.set_xlim(newxlims)

# Save plot
plt.savefig('Heatmap_wobHD.pdf', facecolor='black')
