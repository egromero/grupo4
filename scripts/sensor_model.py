#!/usr/bin/env python
import rospy
import json
import numpy as np
from sensor_msgs.msg import Image


class Sensor(object):
	def __init__(self):

		rospy.Subscriber('/scan', Image, self.scanner_data)
		rospy.sleep(0.2)
		self.r = rospy.Rate(10)
		print("created sensor")
	def scanner_data(self, laserScan):
		data = laserScan.ranges		# Array de valores segun angulo de 90 a -90
		print(data)


if __name__ == "__main__":
    rospy.init_node( "sensor" )
    sensormodel = Sensor()
    rospy.spin()
