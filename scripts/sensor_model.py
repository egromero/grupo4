#!/usr/bin/env python
import rospy
import json
import numpy as np
#from scipy import spatial
#from scipy.optimize import curve_fit
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
#from Constantes import K, z_max, z_hit, z_random, O_hit


class Sensor(object):
	def __init__(self):
		print('huehue2')
		self.r = rospy.Rate(10)
		rospy.Subscriber('/scan', LaserScan, self.scanner_data)
		rospy.sleep(0.2)
		print("created sensor")
		while True:
			self.flag = True
			self.r.sleep()

	def scanner_data(self, laserScan):
		if self.flag:
			data = laserScan.ranges		# Array de valores segun angulo de 90 a -90
			print(data[90])


if __name__ == "__main__":
    rospy.init_node( "sensor" )
    sensormodel = Sensor()
    rospy.spin()
