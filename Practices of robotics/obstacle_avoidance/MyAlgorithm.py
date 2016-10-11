from sensors import sensor
import numpy as np
import threading
import jderobot
import math
from Target import Target


def absolutas2relativas(x, y, rx, ry, rt):
    # Convert to relatives
    dx = x - rx
    dy = y - ry

    # Rotate with current angle
    x = dx*math.cos(-rt) - dy*math.sin(-rt)
    y = dx*math.sin(-rt) + dy*math.cos(-rt)

    return x,y



def parse_laser_data(laser_data):
    laser = []
    for i in range(laser_data.numLaser):
        dist = laser_data.distanceData[i]/1000.0
        angle = math.radians(i)
        laser += [(dist, angle)]
    return laser


class MyAlgorithm():

    def __init__(self, sensor):
        self.sensor = sensor
        self.imageRight=None
        self.imageLeft=None
        self.lock = threading.Lock()

        # Car direction
        self.carx = 0.0
        self.cary = 0.0

        # Obstacles direction
        self.obsx = 0.0
        self.obsy = 0.0

        # Average direction
        self.avgx = 0.0
        self.avgy = 0.0

        # Current target
        self.targetx = 0.0
        self.targety = 0.0

        self.initTargets()

    def initTargets(self):
        self.targets = []
        self.targets.append(Target('target01',jderobot.Pose3DData(1,-30,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target02',jderobot.Pose3DData(-5,-41,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target03',jderobot.Pose3DData(-12,-33,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target04',jderobot.Pose3DData(-15,-14,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target05',jderobot.Pose3DData(-54,-13,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target06',jderobot.Pose3DData(-67,-29,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target07',jderobot.Pose3DData(-71,3,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target08',jderobot.Pose3DData(-49,6,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target09',jderobot.Pose3DData(-49,20,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target10',jderobot.Pose3DData(-118,20,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target11',jderobot.Pose3DData(-116,8,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target12',jderobot.Pose3DData(-106,-2,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target13',jderobot.Pose3DData(-150,-4,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target14',jderobot.Pose3DData(-150,40,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target15',jderobot.Pose3DData(-106,41,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target16',jderobot.Pose3DData(-96,29,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target17',jderobot.Pose3DData(-84,43,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target18',jderobot.Pose3DData(-46,49,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target19',jderobot.Pose3DData(-40,62,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target20',jderobot.Pose3DData(-31,45,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target21',jderobot.Pose3DData(-20,45,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target22',jderobot.Pose3DData(-17,57,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target23',jderobot.Pose3DData(-1,57,0,0,0,0,0,0),False,False))
        self.targets.append(Target('target24',jderobot.Pose3DData(0,0,0,0,0,0,0,0),False,False))

    def getNextTarget(self):
        for target in self.targets:
            if target.isReached() == False:
                return target

        return None

    def execute(self):
        # Get the next point
        self.currentTarget=self.getNextTarget()
        self.targetx = self.currentTarget.getPose().x
        self.targety = self.currentTarget.getPose().y

        # TODO
		# Get the position of the robot
        rx = self.sensor.getRobotX()
        ry = self.sensor.getRobotY()
       
        # We marked the subgoals as we go through
        if(abs(ry)<(abs(self.targety)+1) and abs(ry)>(abs(self.targety)-1)):
            self.currentTarget.setReached(True)

        # We get the orientation of the robot with respect to the map
        rt = self.sensor.getRobotTheta()

        # Get the data of the laser sensor, which consists of 180 pairs of values
        laser_data = self.sensor.getLaserData()
        laser = parse_laser_data(laser_data)
        # Convert self.targetx y self.targety to relative coordinates
        self.carx,self.cary=absolutas2relativas(self.targetx,self.targety,rx,ry,rt)

        # Laser       
        laser_vectorized = []
        for d,a in laser:
            # (4.2.1) laser into GUI reference system
            x = d * math.cos(a) * -1
            y = d * math.sin(a) * -1
            v = (x,y)
            laser_vectorized += [v]

        # Average of the 180 values of the laser
        laser_mean = np.mean(laser_vectorized, axis=0)
       # print "laser", laser_mean

        # Repulsor vector
        dist_threshold = 6
        vff_repulsor_list = []
        for d,a in laser:
            # (4.2.1) laser into GUI reference system
            if(d < dist_threshold):
                x = (d - dist_threshold) * math.cos(a) * -1
                y = (d - dist_threshold) * math.sin(a) * -1
                v = (x,y)
                vff_repulsor_list += [v]

        vff_repulsor = np.mean(vff_repulsor_list, axis=0)

        self.obsx,self.obsy = vff_repulsor
        # Calculating repulsor vector module
        mod_repulsor = pow(pow(self.obsx,2) + pow(self.obsy,2),0.5)
        if (mod_repulsor > 1.55):
            self.obsx,self.obsy = vff_repulsor * 4.5

       
        # Calculating the coordinates of the resultant vector
        self.avgx = self.carx + self.obsx
        self.avgy = self.cary + self.obsy


        # Calculating the module of the speed
        speed = pow(pow(self.avgx,2) + pow(self.avgy,2),0.5)

        # Correction
        if (abs(self.obsx) > 2):
            if (abs(self.obsx) < abs(self.carx)):
                if (self.obsx >= 0):
                    self.avgx = abs(self.avgx)
                else:
                    self.avgx = -abs(self.avgx)

        if ((self.obsx == (-self.carx)) and (self.obsy == (-self.cary))):
            self.avgx = self.obsx
            self.avgy = self.cary

        # Calculating angle
        if (speed < 1):
            # Use the tangent to avoid indeterminacy
            angle = math.atan(abs(self.avgx/self.avgy))
        else:
            angle = math.asin(abs(self.avgx/speed))
        if(self.avgy > 0):
            angle = math.pi - angle


        # Linear speed
        if ((speed < 1) or (speed > 3)):
            self.sensor.setV(3)
        else:
            self.sensor.setV(speed)

        # Angular speed
        if(self.avgx < 0):
			self.sensor.setW(angle * 0.75)
        else:
            self.sensor.setW(-angle * 0.75)

      
       
    # Gui functions
    def setRightImageFiltered(self, image):
        self.lock.acquire()
        self.imageRight=image
        self.lock.release()

    def setLeftImageFiltered(self, image):
        self.lock.acquire()
        self.imageLeft=image
        self.lock.release()

    def getRightImageFiltered(self):
        self.lock.acquire()
        tempImage=self.imageRight
        self.lock.release()
        return tempImage

    def getLeftImageFiltered(self):
        self.lock.acquire()
        tempImage=self.imageLeft
        self.lock.release()
        return tempImage

    def getCarDirection(self):
        return (self.carx, self.cary)

    def getObstaclesDirection(self):
        return (self.obsx, self.obsy)

    def getAverageDirection(self):
        return (self.avgx, self.avgy)

    def getCurrentTarget(self):
        return (self.targetx, self.targety)







        
