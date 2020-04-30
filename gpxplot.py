# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 2020, 15:44:01
@author: Daan Wielens

/--------------------------------------\
|           GPX Plotter                |
|           Version 1.0                |
|           D.H. Wielens               |
\--------------------------------------/

"""

# Step 1: Build functional GUI

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qt import *
from gpxparse import *
import os

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# Change the working directory to the QTMtoolbox directory (where the script itself should be)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Matplotlib Canvas
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=10, height=10, dpi=300):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_axes([0, 0, 1, 1]) # Use this to fully utilize the plot window (i.e. no margins)
        self.fig.patch.set_facecolor('black')
        self.ax.set_facecolor('black')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        super(MplCanvas, self).__init__(self.fig)


# Main window
class MainWindow(QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.setWindowTitle('GPXplot v0.4 (2020-04-25)')
        
    # --- Define layout --- 
        # Main layout: horizontal structure
        layMain = QHBoxLayout()
        layMain.setContentsMargins(8,8,8,8)
        layMain.setSpacing(10)
        
        # Left layer: toolbar, data selector, settings
        layLeft = QVBoxLayout()
        
        # Tools menu
        layTools = QHBoxLayout()

        refreshplot = QPushButton('', self)
        refreshplot.setIcon(QIcon('arrow-circle-double.png'))
        refreshplot.setIconSize(QSize(16, 16))
        refreshplot.clicked.connect(self.refreshPlot)
        refreshplot.setToolTip('Refresh plot according to the Data selector')
        layTools.addWidget(refreshplot)
        
        filebtn = QPushButton('', self)
        filebtn.setIcon(QIcon('folder-horizontal-open.png'))
        filebtn.setIconSize(QSize(16, 16))
        filebtn.clicked.connect(self.loadFolder)
        filebtn.setToolTip('Choose a different data folder')
        layTools.addWidget(filebtn)
        layLeft.addLayout(layTools)
        
        # Data selector
        layDataGroup = QGroupBox('Data selector')
        layData = QFormLayout()
        self.listview = QListView()
        self.listview.setFixedWidth(250)
        self.listview.setFixedHeight(380)
        self.model = QStandardItemModel()
        layData.addRow(self.listview)
        layDataGroup.setLayout(layData)
        layLeft.addWidget(layDataGroup)
        
        # Line property section:
        laySetGroup = QGroupBox('Edit line properties')
        laySet = QFormLayout()
                
        self.setcbox = QComboBox()
        self.setcbox.setFixedWidth(175)
        self.setcbox.activated.connect(self.cboxindex)
        self.setcbox.setToolTip('Choose what data set should be affected by the settings')
        laySet.addRow(QLabel('Data set:'), self.setcbox)
        
        self.setcolor = QComboBox()
        self.setcolor.setFixedWidth(175)
        self.setcolor.activated.connect(self.colorindex)
        self.setcolor.addItems(['White', 'Red', 'Blue', 'Green', 'Yellow'])
        self.setcolor.setToolTip('Change the color of the line(s)')
        laySet.addRow(QLabel('Line color:'), self.setcolor)
        
        self.setalpha = QDoubleSpinBox()
        self.setalpha.setRange(0, 1)
        self.setalpha.setFixedWidth(175)
        self.setalpha.setToolTip('Set the opacity of the line(s) [0-1]')
        laySet.addRow(QLabel('Line alpha:'), self.setalpha)
        
        self.setlinewidth = QDoubleSpinBox()
        self.setlinewidth.setRange(0, 10)
        self.setlinewidth.setFixedWidth(175)
        self.setlinewidth.setToolTip('Change the width of the line(s) [0-10]')
        laySet.addRow(QLabel('Line width:'), self.setlinewidth)
        
        setbtn = QPushButton('', self)
        setbtn.setText('Apply')
        setbtn.setFixedWidth(70)
        setbtn.setToolTip('Apply the parameters to the selected data set')
        setbtn.clicked.connect(self.ApplySettings)        
        laySet.addRow(QLabel(), setbtn) # Add spacer here!
        
        laySetGroup.setLayout(laySet)
        layLeft.addWidget(laySetGroup)
        
        # Plot settings
        laySetPlot = QGroupBox('Plot options')
        laySetP = QFormLayout()
        
        sqbtn = QPushButton('', self)
        sqbtn.setText('Fix aspect ratio')
        sqbtn.setFixedWidth(250)
        sqbtn.clicked.connect(self.fixAspectRatio)
        sqbtn.setToolTip('Change the limits of the axes to be the same to prevent images from looking distorted after zooming in')
        laySetP.addRow(sqbtn)
        
        laySetPlot.setLayout(laySetP)
        layLeft.addWidget(laySetPlot)
        
        # Right layer: plot canvas
        layPlotGroup = QGroupBox('Plot window')
        layPlot = QVBoxLayout()
        self.sc = MplCanvas(self, width=30, height=30, dpi=300)
        toolbar = NavigationToolbar(self.sc, self)
        layPlot.addWidget(toolbar)
        layPlot.addWidget(self.sc)
        self.sc.setFixedHeight(600)
        self.sc.setFixedWidth(600)
        self.show()
        layPlotGroup.setLayout(layPlot)

        # Add groups to main
        layMain.addLayout(layLeft)
        layMain.addWidget(layPlotGroup)
        
        # Final layout
        widget = QWidget()
        widget.setLayout(layMain)
        self.setCentralWidget(widget)
        
        # Load initial data set , set default settings
        self.loadData()
        self.cb_index = 0
        self.color_index = 0
        self.setalpha.setValue(0.2)
        self.setlinewidth.setValue(0.5)
                        
    # --- Add signals and slots
    def dummy(self):
        print('Triggered.')
        
    def loadData(self, folder=None):
        self.gpxlist = []
        self.model.clear()
        # Add all files to the gpxlist
        if folder == None:
            for file in os.listdir(os.getcwd()):
                if '.gpx' in file:
                    gpxact = parseGPX(file)
                    self.gpxlist.append(gpxact)
        else:
            for file in os.listdir(folder):
                if '.gpx' in file:
                    gpxact = parseGPX(os.path.join(folder, file))
                    self.gpxlist.append(gpxact)
                
        # Update QListView
        self.setcbox.clear()
        self.setcbox.addItem('All files')
        for i in range(len(self.gpxlist)):
            # Add the items to the listview here. See 
            string = self.gpxlist[i].filename
            item = QStandardItem(string)
            item.setToolTip(self.gpxlist[i].act_name + ' | ' + self.gpxlist[i].act_time)
            item.setCheckable(True)
            item.setCheckState(Qt.Checked)
            self.model.appendRow(item)
            # Add the items to the settings selector as well
            self.setcbox.addItem(self.gpxlist[i].filename)

        self.listview.setModel(self.model)
        # Plot all data (since all files will be "Qt.Checked")
        for i in range(len(self.gpxlist)):
            self.sc.ax.plot(self.gpxlist[i].xdata, self.gpxlist[i].ydata, color='White', alpha=0.2, linewidth=0.5)
            
        self.refreshPlot()
            
    def cboxindex(self, i):
        self.cb_index = i
        
    def colorindex(self, i):
        self.color_index = i
        
    def refreshPlot(self):
        # Get list of checked items only
        self.choices = [self.model.item(i).index().row() for i in 
                        range(self.model.rowCount())
                        if self.model.item(i).checkState()
                        == Qt.Checked]
        # Update gpxlist attributes (gpxlist[i].show)
        for i in range(len(self.gpxlist)):
            if i not in self.choices:
                self.gpxlist[i].show = False
            else:
                self.gpxlist[i].show = True
        
        lines = self.sc.ax.get_lines()
        for i in range(len(self.gpxlist)):
            if self.gpxlist[i].show == True:
               lines[i].set_linestyle('solid')
            else:
               lines[i].set_linestyle('None')

        self.sc.draw()
        
    def ApplySettings(self):
        lines = self.sc.ax.get_lines()
        if not self.cb_index == 0:
            lines[self.cb_index-1].set_color(str(self.setcolor.currentText()))
            lines[self.cb_index-1].set_alpha(self.setalpha.value())
            lines[self.cb_index-1].set_linewidth(self.setlinewidth.value())
        else:
            for line in lines:
                line.set_color(str(self.setcolor.currentText()))
                line.set_alpha(self.setalpha.value())
                line.set_linewidth(self.setlinewidth.value())
        
        self.sc.draw()
        
    def fixAspectRatio(self):
        xlims = self.sc.ax.get_xlim()
        ylims = self.sc.ax.get_ylim()
        xdiff = xlims[1] - xlims[0]
        ydiff = ylims[1] - ylims[0]
        xymax = max([xdiff, ydiff])
        if xdiff > ydiff:
            newylims = [-xymax/2, xymax/2] + (ylims[0]+ylims[1])/2
            self.sc.ax.set_ylim(newylims)
        else:
            newxlims = [-xymax/2, xymax/2] + (xlims[0]+xlims[1])/2
            self.sc.ax.set_xlim(newxlims)        
        
        self.sc.draw()        
        
    def loadFolder(self):
        options = QFileDialog.Options()
        folderName = QFileDialog.getExistingDirectory(self, 'Open a folder containing GPX files')
        if folderName:
            self.loadData(folder=folderName)
        
    # Fix to make PyQt5 close correctly in Spyder    
    def closeEvent(self,event):
        QApplication.quit()       

# Run main code
app = QApplication.instance()
window = MainWindow()
window.show()
app.exec_()