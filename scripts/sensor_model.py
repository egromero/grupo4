#!/usr/bin/env python
import rospy
import json
import numpy as np
#from scipy import spatial
#from scipy.optimize import curve_fit
from sensor_msgs.msg import Image
#from Constantes import K, z_max, z_hit, z_random, O_hit


class Sensor(object):
	def _init_(self):
		rospy.Subscriber('/scan', Image, self.scanner_data)
		rospy.sleep(0.2)
		self.r = rospy.Rate(10)
		self.write = 0
		self.write_pub = rospy.Publisher('write_permit', String)
		print("created sensor")

	def scanner_data(self, laserScan):
		data = laserScan.ranges		# Array de valores segun angulo de 90 a -90
		while self.write < 10:
			self.print(data)
			self.write_pub.publish(str(data))
			self.write += 1
		self.write_pub.publish("END")


if __name__ == "_main_":
    rospy.init_node( "sensor" )
    sensormodel = Sensor()
    rospy.spin()
