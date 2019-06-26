#!/usr/bin/env python
import rospy
import json
import numpy as np

from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
from parameters import *
class Obstacle():
    def __init__(self):
        print('creating obstacle checker class...')
        self.publisher = rospy.Publisher('obstacle',Bool,queue_size=1)

        rospy.Subscriber('/scan',LaserScan,self.scanner_data)

    def scanner_data(self, laserScan):
	print('something')
	data = laserScan.ranges
	valid_values = data[valid[0]:valid[1]]
    	boolean_data = np.any(valid_values<obstacle_distance)
	print(valid_values[30])
	self.publisher.publish(boolean_data)


if __name__ == '__main__':
	rospy.init_node( "obstacle" )
	handler = Obstacle()
	rospy.spin()
