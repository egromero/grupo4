#!/usr/bin/env python
import rospy
import cv2
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
from Contants import *

class Pasillo():

    def __init__(self):
	self.bridge = CvBridge()
	self.current_cv_depth_image = np.zeros( (1, 1, 3) )
	self.current_cv_rgb_image = CURRENT_CV_RGB_IMAGE
    self.obstacle = OBSTACLE

    self.__depth_img = rospy.Subscriber( '/camera/depth/image', Image, self.recorrer )
	#self.__rgb_img = rospy.Subscriber( '/camera/rgb/image_color', Image, self.image )

	self.mover = rospy.Publisher( '/cmd_vel_mux/input/navi', Twist, queue_size=10 )
    self.move_cmd = Twist()

#    def image(self, data):
#	try:
#

#	except Exception as e:
      #         print('error')
      #          rospy.logerr( e )

    def recorrer( self, data ):
        try:
		self.current_cv_depth_image = np.nan_to_num(np.asarray( self.bridge.imgmsg_to_cv2( data, "32FC1" )))
		cv2.circle(self.current_cv_depth_image, (LIMIT_X, LIMIT_Y), 10, (255, 255, 255))
		cv2.circle(self.current_cv_depth_image, (640-LIMIT_X, LIMIT_Y), 10, (255, 255, 255))
		cv2.imshow("image",self.current_cv_depth_image)
		cv2.waitKey(1)

        ptoL = self.current_cv_depth_image[LIMIT_Y, LIMIT_X]
        ptoR = self.current_cv_depth_image[LIMIT_Y, 640-LIMIT_X]

		sub_imageL = self.current_cv_depth_image[LIMIT_Y : LIMIT_Y+DELTA, LIMIT_X : LIMIT_X+DELTA]
        sub_imageR = self.current_cv_depth_image[LIMIT_Y : LIMIT_Y+DELTA, 640-LIMIT_X-DELTA : 640-LIMIT_X]
        self.in_line = np.greater( ptoL-ptoR, - MARGEN ) * np.less( ptoL-ptoR, MARGEN )
		# self.in_line = ( np.greater( sub_imageL-sub_imageR, - MARGEN ) * np.less( sub_imageL-sub_imageR, MARGEN ) ).all()

        sub_image = self.current_cv_depth_image[CENTER[0]-VISION_WINDOW[0] : CENTER[0]+VISION_WINDOW[0], CENTER[1]-VISION_WINDOW[1] :CENTER[1]+VISION_WINDOW[1]]
		self.obstacle = ( np.greater( sub_image, 0.2 ) * np.less( sub_image, 0.6 ) ).any()

        if self.obstacle:
			print('obstaculo')
			self.move_cmd.linear.x = 0
            self.move_cmd.angular.z = 0

        elif self.in_line:
		    #print('in Line')
			self.move_cmd.linear.x = 0.1
            self.move_cmd.angular.z = 0
			print("Inline")

		elif ptoL == 0.0:
			self.move_cmd.linear.x = 0.1
			self.move_cmd.angular.z = 0.4
			print('Inifnite to the left')

		elif ptoR == 0.0:
			self.move_cmd.linear.x = 0.1
			self.move_cmd.angular.z = -0.4
			print('Inifnite to the left')

        else:
            error = ptoL - ptoR
            value = 0.2 + 0.15 * abs(error)
            ang_speed = -value if error < 0 else value
			print('corrigiendo',error, ang_speed)
			self.move_cmd.linear.x = 0.1
            self.move_cmd.angular.z = ang_speed

		self.mover.publish(self.move_cmd)
		#self.current_cv_rgb_image = np.nan_to_num(np.asarray( self.bridge.imgmsg_to_cv2( data, "bgr8")))
        #cv2.circle(self.current_cv_rgb_image, (LIMIT_X, LIMIT_Y), 10, (0, 0, 255))
        #cv2.circle(self.current_cv_rgb_image, (640-LIMIT_X, LIMIT_Y), 10, (0, 255, 0))
        #cv2.imshow("test", self.current_cv_rgb_image)
        #cv2.waitKey(1)
		#print(ptoL, ptoR, 'Puntos')
	except Exception as e:
		print('error')
		rospy.logerr( e )
