import numpy as np
import matplotlib.pyplot as plt
import sys

#Define Catmull Rom Spline Class
class CatmullRomSpline:
    __controlPoints={}

    #map from matplotlib-artists to some object that can change data
    __artistToControlPointIndex={}

    def __init__(self, p0, p1, p2, p3):
        #Default control points
        self.setControlPoint(0, p0)
        self.setControlPoint(1, p1)
        self.setControlPoint(2, p2)
        self.setControlPoint(3, p3)

    def setControlPoint(self, index, coordinates):
        #Set control point with the give index (start at zero)
        global __controlPoints
        self.__controlPoints[index] = coordinates

    def get__controlPointsDict(self):
        return (__controlPoints)

    def getXYCoordinatList(self):
        xList = []; yList = []
        for p in self.__controlPoints.values():
            xList.append(p[0])
            yList.append(p[1])  
        return (xList, yList)
    
    #Drawing
    def draw(self, figure):
        figure.clf()
        figure.gca().set_aspect('equal')
        self.drawControlPoints(figure)
        self.drawLinesBetween__controlPoints(figure)
        figure.gca().plot()

    def drawControlPoints(self, figure, handleRadius = 0.25):
        for i,p in self.__controlPoints.iteritems():
            centerX, centerY = p[0], p[1] 
            circle = plt.Circle((centerX,centerY),handleRadius,fc=np.random.random(3),picker=True, alpha=0.5) ##<-- make this a global variable and just set the position   
            figure.gca().add_patch(circle)
            #Prepare for picking events
            self.__artistToControlPointIndex[circle]=i
            
            
    def drawLinesBetween__controlPoints(self, figure):
        xy = self.getXYCoordinatList()
        figure.gca().plot(xy[0], xy[1])
        

    #Picking logic
    def selectControlPoint(self, artist):
        if(artist in self.__artistToControlPointIndex):
            controlIndex = self.__artistToControlPointIndex[artist]
            return(controlIndex)


#Plot
plt.ion()
figure = plt.figure('Spline tool')
##fig, ax = plt.subplots()
figure.gca().set_aspect('equal')

#Just plot some stuff for reference
##x = np.linspace(0, 10, 1000)
##line, = ax.plot(x, np.sin(x))

#make a Catmull Rom spline object and plot it
spline = CatmullRomSpline(np.array([0.01,3.1]), np.array([4.01,0.01]), np.array([7.1,4.1]),np.array([13.1,1.1])) 
spline.draw(figure)

#Setup the keyboard key press event
def on_key_press(event):    
    global index
    global figure
    if event.key == 'escape':    
        exit() #NB has no effect with IPython
    elif event.key == 'control':
        index=None
    figure.clf()
    spline.draw(figure)
    figure.canvas.draw()
    print("event.key="+event.key)

figure.canvas.mpl_connect('key_press_event', on_key_press)

#Setup picker event
###movingElement=None
index = None #spline controle point index

def on_pick(event):
    global index
    index = spline.selectControlPoint(event.artist)

figure.canvas.mpl_connect('pick_event', on_pick)


def motion_notify_event(event):
    if index is not None:
        spline.setControlPoint(index, np.array([event.xdata, event.ydata]))   
    figure.clf()
    spline.draw(figure)
    figure.canvas.draw()

figure.canvas.mpl_connect('motion_notify_event', motion_notify_event)


#Disable default keys on the plot e.g. 'k' is logaritmic scale
figure.canvas.mpl_disconnect(figure.canvas.manager.key_press_handler_id)

#Display the figures on screen

plt.show(block=True) #keep the window open
