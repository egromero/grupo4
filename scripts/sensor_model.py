#!/usr/bin/env python
import rospy
import json
import numpy as np
from sensor_msgs.msg import Image


class Sensor(object):
	def __init__(self):

		rospy.Subscriber('/scan', Image, self.scanner_data)

	def scanner_data(self, data):
		print(data.data)


