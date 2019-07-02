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

        self.r = rospy.Rate(rate*5)

        while not rospy.is_shutdown():
            self.flag = True
            self.r.sleep()

    def scanner_data(self, laserScan):
        if self.flag:
            data = laserScan.ranges
            valid_values = np.array(data[valid[0]+20:valid[1]-20])
            #print(valid_values)
            boolean_data = np.any(valid_values<obstacle_distance)
            boolean_2 = np.any(valid_values==20.0)

            self.publisher.publish(boolean_data or boolean_2)
            #print(boolean_data or boolean_2)
            self.flag = False


if __name__ == '__main__':
	rospy.init_node( "obstacle" )
	handler = Obstacle()
	rospy.spin()
