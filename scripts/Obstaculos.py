#!/usr/bin/env python
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
from std_msgs.msg import String
import json


CENTER = [240,320]
VISION_WINDOW = [100,90]

class DetectorObstaculos(object):
	
	def __init__(self):
		self.bridge = CvBridge()
		self.__depth_img = rospy.Subscriber( '/camera/depth/image', Image, self.process )
		self.depth_image = np.nan_to_num(np.asarray( self.bridge.imgmsg_to_cv2( data, "32FC1" )))
		self.pub_obstacle = rospy.Publisher('route_obstacle', String, queue_size = 10)
		self.state_odom = rospy.Subscriber('our_state',String, self.data_received)

	def process(self, data):
	
		sub_image = self.depth_image[CENTER[0]-VISION_WINDOW[0] : CENTER[0]+VISION_WINDOW[0], CENTER[1]-VISION_WINDOW[1] :CENTER[1]+VISION_WINDOW[1]]
		self.obstacle = ( np.greater( sub_image, 0.2 ) * np.less( sub_image, 0.6 ) ).any()
		if self.obstacle:
			self.calculate_route()
	
	def data_received(self, data):
	
		inc_dict = json.loads(data.data)
        self.x = inc_dict['x']
        self.y = inc_dict['y']
        self.ang = inc_dict['ang_pos']

	def calculate_route(self):
		new_route = [[self.x, self.y+0.5, self.ang],[self.x+0.5, self.y+0.5, self.ang],[self.x+0.5, self.y, self.ang]]
		encoded = json.dumps(new_route)
		self.pub_obstacle(encoded)


