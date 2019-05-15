#!/usr/bin/env python
import rospy
import math
import roslib
#from Movement import Movement
#from ComputerVision import Vision
from Pasillo import Pasillo
#from turtlebot_audio import TurtlebotAudio
from sensor_msgs.msg import Image
from std_msgs.msg import Empty
import numpy as np
import cv2
from cv_bridge import CvBridge, CvBridgeError



class Turtlebot(object):

	def __init__( self ):
		#self.movement = Movement()
		# self.vision = Vision(self.movement)
		self.pasillo = Pasillo()
		rospy.sleep(1)




if __name__ == '__main__':

	rospy.init_node( "turtlebot_g4" )
	handler = Turtlebot()
	rospy.spin()
