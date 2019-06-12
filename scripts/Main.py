#!/usr/bin/env python
import rospy
import json
from sensor_model import Sensor
from scan_from_kinect import DeepScan


from std_msgs.msg import String, Bool

class Turtlebot(object):
	def __init__( self ):
		self.scan = DeepScan()
		self.sensor = Sensor()

if __name__ == '__main__':
	rospy.init_node( "turtlebot_g4" )
	handler = Turtlebot()
	rospy.spin()
