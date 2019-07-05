#!/usr/bin/env python
import rospy
import json
import numpy as np

from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
from parameters import *
from data_to_image import cartesian_matrix
class Obstacle():
    def __init__(self):
        print('creating obstacle checker class...')

        rospy.Subscriber('/scan',LaserScan,self.scanner_data)

        self.r = rospy.Rate(100)

        while not rospy.is_shutdown():
            self.flag = True
            self.r.sleep()

    def scanner_data(self, laserScan):
        if self.flag:
            data = laserScan.ranges
            cart_matrix = cartesian_matrix(data)
            plt.imshow(cart_matrix)
            plt.show()
            plt.pause(1/100)


if __name__ == '__main__':
	rospy.init_node( "obstacle" )
	handler = Obstacle()
	rospy.spin()
