import numpy as np
import matplotlib.pyplot as plt
import sys


class QuarticPolynomial:
    def __init__(self, pts1, pts2, pts3, pts4):
        k = 0.5;
        self.a = -k * pts1 + (2 - k) * pts2 + (-2 + k) * pts3 + k * pts4;
        self.b = 2 * k * pts1 + (-3 + k) * pts2 + (3 - 2 * k) * pts3 - k * pts4;
        self.c = -k * pts1 + k * pts3;
        self.d = pts2;

    def __str__(self):
        return(str(self.a) +" t^3 +"+ str(self.b) + " t^2 + "+ str(self.c) +" t +" + str(self.d))

    def __call__(self, t):
        return(self.a * t**3 + self.b * t**2 + self.c * t + self.d)

#Define Catmull Rom Spline Class
class CatmullRomSpline:
    __handleRadius = 0.5
    __controlPoints={}
    __controlPointsCircles={}
    __controlPointsLines=None
    __curves=None

    #map from matplotlib-artists to some object that can change data
    __artistToControlPointIndex={}

    def __init__(self, p0, p1, p2, p3):
        #Default control points
        self.setControlPoint(0, p0)
        self.setControlPoint(1, p1)
        self.setControlPoint(2, p2)
        self.setControlPoint(3, p3)
        
        self.xfunc = QuarticPolynomial(p0[0], p1[0], p2[0], p3[0])
        print(self.xfunc)
        print(self.xfunc(0.5))

        self.yfunc = QuarticPolynomial(p0[1], p1[1], p2[1], p3[1])
        print(self.yfunc)
        print(self.yfunc(0.5))
        
    
    def setControlPoint(self, index, coordinates):
        #Set control point with the give index (start at zero)
        global __controlPoints
        self.__controlPoints[index] = coordinates
        if index in self.__controlPointsCircles.keys():
            self.__controlPointsCircles[index].center = coordinates

        #connecting lines
        if self.__controlPointsLines is not None:
            xy = self.getXYCoordinatList()
            self.__controlPointsLines[0].set_xdata(xy[0])
            self.__controlPointsLines[0].set_ydata(xy[1])

        #update the quartic polynomial
        if(self.__controlPoints.has_key(0) and
           self.__controlPoints.has_key(1) and
           self.__controlPoints.has_key(2) and
           self.__controlPoints.has_key(3)): #Only recalc when it's possible 
            p0 = self.__controlPoints[0]
            p1 = self.__controlPoints[1]
            p2 = self.__controlPoints[2]
            p3 = self.__controlPoints[3]
            self.xfunc = QuarticPolynomial(p0[0], p1[0], p2[0], p3[0])
            self.yfunc = QuarticPolynomial(p0[1], p1[1], p2[1], p3[1])        

            #and connecting curves
            if self.__curves is not None:
                tValues = np.arange(0,1.1,0.1)
                xValues = [self.xfunc(t) for t in tValues]
                yValues = [self.yfunc(t) for t in tValues]
                self.__curves[0].set_xdata(xValues)
                self.__curves[0].set_ydata(yValues)

    def getControlPointsDict(self):
        return (self.__controlPoints)

    def getXYCoordinatList(self):
        xList = []; yList = []
        for p in self.__controlPoints.values():
            xList.append(p[0])
            yList.append(p[1])  
        return (xList, yList)
    
    #Drawing
    def setupDrawing(self, figure):
        figure.gca().set_xlim(-3, 17)
        figure.gca().set_ylim(-3, 7 )

        #Prepare for picking events
        for i,p in self.__controlPoints.iteritems():    
            centerX, centerY = p[0], p[1] 
            circle = plt.Circle((centerX,centerY), self.__handleRadius,fc=np.random.random(3),picker=True, alpha=0.5)
            self.__controlPointsCircles[i]=circle             
            figure.gca().add_patch(circle)
            #Prepare for picking events
            self.__artistToControlPointIndex[circle]=i

        #connecting lines
        xy = self.getXYCoordinatList()
        self.__controlPointsLines = figure.gca().plot(xy[0], xy[1])

        #connecting curves
        tValues = np.arange(-1,2,0.1)
        xValues = [self.xfunc(t) for t in tValues]
        yValues = [self.yfunc(t) for t in tValues]
        self.__curves = figure.gca().plot(xValues, yValues)
       
    #Picking logic
    def selectControlPoint(self, artist):
        if(artist in self.__artistToControlPointIndex):
            controlIndex = self.__artistToControlPointIndex[artist]
            return(controlIndex)


#Plot
plt.ion()
figure = plt.figure('Spline tool')
figure.gca().set_aspect('equal')

#Just plot some stuff for reference
##x = np.linspace(0, 10, 1000)
##line, = ax.plot(x, np.sin(x))

#make a Catmull Rom spline object and plot it
spline = CatmullRomSpline(np.array([0.01,3.1]), np.array([4.01,0.01]), np.array([7.1,4.1]),np.array([13.1,1.1]))
spline.setupDrawing(figure)

#Setup the keyboard key press event
def on_key_press(event):    
    global index
    global figure
    if event.key == 'escape':    
        exit() #NB has no effect with IPython
    elif event.key == 'control':
        index=None
    print("event.key="+event.key)

figure.canvas.mpl_connect('key_press_event', on_key_press)

#Setup picker event
index = None #spline controle point index

def on_pick(event):
    global index
    index = spline.selectControlPoint(event.artist)

def motion_notify_event(event):
    global figure
    if index is not None:
        spline.setControlPoint(index, np.array([event.xdata, event.ydata]))   
    figure.canvas.draw()

def button_press_event(event):
    pass

def button_release_event(event):
    global index
    index = None

figure.canvas.mpl_connect('pick_event', on_pick)
figure.canvas.mpl_connect('motion_notify_event', motion_notify_event)
figure.canvas.mpl_connect('button_press_event', button_press_event)
figure.canvas.mpl_connect('button_release_event', button_release_event)


#Disable default keys on the plot e.g. 'k' is logaritmic scale
"""figure.canvas.mpl_disconnect(figure.canvas.manager.key_press_handler_id)"""

#Display the figures on screen

plt.show(block=True) #keep the window open
