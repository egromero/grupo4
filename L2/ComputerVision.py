
import cv2
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
import time as tm
import os
from Constants import *

class Vision():

	def __init__(self, mover):
		rospy.loginfo( "Inicicializando Vision" )
		self.mover = mover
		self.bridge = CvBridge()
		self.frame_CENTER = FRAME_CENTER
		self.window_width = WINDOWS_WIDTH
		self.current_cv_depth_image = np.zeros( (1, 1, 3) )
		self.current_cv_rgb_image = CURRENT_CV_RGB_IMAGE
		self.counter = COUNTER
		self.write = WRITE
		self.flag = FLAG
		self.ref = REF
		self.obstacle = OBSTACLE
		self.zero = ZERO
		self.follow = FOLLOW

		self.__depth_img = rospy.Subscriber( '/camera/depth/image', Image ,self.depth_prossesing)
		self.__rgb_img = rospy.Subscriber( '/camera/rgb/image_color', Image ,self.rgb_prossesing)


	def depth_prossesing(self, data):
		try:

			## Get image and delete nans
			self.current_cv_depth_image = np.nan_to_num(np.asarray( self.bridge.imgmsg_to_cv2( data, "32FC1" )))

			sub_image = self.current_cv_depth_image[CENTER[0]-VISION_WINDOW[0] : CENTER[0]+windows[0], CENTER[1]-windows[1] :CENTER[1]+VISION_WINDOW[1]]

			self.obstacle1 = (np.greater(sub_image,0.2) * np.less(sub_image ,0.6)).any()

			self.muy_cerca = (sub_image == 0).all()


			one_item = (np.greater(sub_image,THRESHOLD[0]) * np.less(sub_image ,THRESHOLD[1])).any()
			all_item = (sub_image[VISION_WINDOW[0]/2-LIL_VISION_WINDOW[0] : VISION_WINDOW[0]/2+LIL_VISION_WINDOW[0],VISION_WINDOW[1]/2-LIL_VISION_WINDOW[1] : VISION_WINDOW[1]/2+LIL_VISION_WINDOW[1]  ]==0).all()

			self.obstacle = True if (one_item or all_item) else False

		except Exception as e:
			print('error')
			rospy.logerr( e )



	def rgb_prossesing(self):

		try:
			self.current_cv_rgb_image = np.nan_to_num(np.asarray(self.bridge.imgmsg_to_cv2(data,"bgr8")))

			frame_lab = cv2.cvtColor(self.current_cv_rgb_image, cv2.COLOR_BGR2HSV)

			reduced_frame = cv2.resize(frame_lab, (320,240))

			mask_blue = cv2.inRange(frame_lab, LOWER_BLUE, UPPER_BLUE)

			KERNEL = cv2.getStructuringElement(cv2.MORPH_RECT, (10,10))

			mask_close = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, KERNEL)

			mask_open = cv2.morphologyEx(mask_close, cv2.MORPH_OPEN, KERNEL)

			blue_count = np.sum(mask_open)

			momentos = cv2.moments(mask_open)

			m10 = momentos["m10"]
			m01 = momentos["m01"]
			m00 = momentos["m00"] + 1

			self.centro = (int(m10/m00), int(m01/m00))


			cv2.circle(self.current_cv_rgb_image, self.centro, 10, (0,0,255))

			cv2.putText(self.current_cv_rgb_image,"x: {0}, y: {1}".format(self.centro[0],self.centro[1]),(100,100),cv2.FONT_ITALIC, 0.5, (255,255,255))

			cv2.imshow('clse', self.current_cv_rgb_image)

			cv2.waitKey(1)

			#cv2.imshow("blue", mask_blue)


			if blue_count >THRESHOLD_COUT:
				self.follow()
			else:
				pass

		except Exception as e:
			print('error')
			rospy.logerr( e )

	def follow(self):

		if self.centro[0] == 0:
			self.mover.move(0,0)

		elif self.centro[0] in range(self.frame_center-self.window_width,self.frame_center+self.window_width):

			if not(self.obstacle1):
				self.mover.move(0.1,0)
				self.window_width=38
			else:
				self.mover.move(0,0)

		elif self.centro[0] in (range(self.frame_center-320,self.frame_center-self.window_width) + range(self.frame_center+self.window_width,self.frame_center+320)):
			error = min(abs(self.centro[0] - self.frame_center)/170,1)
			
			value = 0.3 + 0.5*error
			self.window_width = 30
			ang_speed = -value if (self.centro[0] in range(self.frame_center+self.window_width,self.frame_center+320)) else value
			self.mover.move(0,ang_speed)



