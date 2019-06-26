#!/usr/bin/env python
import rospy
import json
import numpy as np

from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
from parameters import *
class Obstacle():
    def __init__():
        print('creating obstacle checker class...')
        self.publisher = rospy.Publisher('obstacle',Bool,queue_size=1)

        rospy.Subscriber('/scan',LaserScan,self.scanner_data)

	def scanner_data(self, laserScan):
		data = laserScan.ranges
        boolean_data = np.any(data[valid]<obstacle_distance)
        print(boolean_data)
        self.publisher.publish(boolean_data)
