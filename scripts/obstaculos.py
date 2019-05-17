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
		print("iniciando obstaculos")
		self.bridge = CvBridge()
		self.__depth_img = rospy.Subscriber( '/camera/depth/image', Image, self.process )
		self.pub_obstacle = rospy.Publisher('route_obstacle', String, queue_size = 10)
		self.state_odom = rospy.Subscriber('our_state',String, self.data_received)

	def process(self, data):
		# New image callback
		# Looks if obstacle is on defined window.
		self.depth_image = np.nan_to_num(np.asarray( self.bridge.imgmsg_to_cv2( data, "32FC1" )))
		sub_image = self.depth_image[CENTER[0]-VISION_WINDOW[0] : CENTER[0]+VISION_WINDOW[0], CENTER[1]-VISION_WINDOW[1] :CENTER[1]+VISION_WINDOW[1]]
		self.obstacle = ( np.greater( sub_image, 0.2 ) * np.less( sub_image, 0.6 ) ).any()
		if self.obstacle:
			self.calculate_route()

	def data_received(self, data):
		## Odometry callback for rerouting planning
		inc_dict = json.loads(data.data)
        	self.x = inc_dict['x']
        	self.y = inc_dict['y']
       		self.ang = inc_dict['ang_pos']

	def calculate_route(self):
		## Create rot rot_matrix
		#	Calculate relative 0.5 x,y axis Movement
		#	applicate to old vector and publish in corresponding topic after json encoding
		rot_matrix = np.array([[np.cos(self.ang),np.sin(self.ang)],[-np.sin(self.ang),np.cos(self.ang)]])
		extra_x = np.matmul(rot_matrix,np.array([[0.5],[0]]))
		extra_y = np.matmul(rot_matrix,np.array([[0],[0.5]]))
		original_vec = np.array([[self.x],[self.y]])
		new_vectors = [original_vec + extra_y, original_vec+ extra_y + extra_x]
		new_route = [ [new_vectors[0][0],new_vectors[0][1],None] ,[new_vectors[1][0],new_vectors[1][1] ],None]
		print(new_route)
		encoded = json.dumps(new_route)
		self.pub_obstacle.publish(encoded)


if __name__ =='__main__':
    rospy.init_node("obstacles")
    handler = DetectorObstaculos()
    rospy.spin()
