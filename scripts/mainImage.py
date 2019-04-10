#!/usr/bin/env python
import rospy
import roslib

from sensor_msgs.msg import Image

import numpy as np
import cv2
from cv_bridge import CvBridge, CvBridgeError
import os

center = [240,320]
windows = [100,80]
threshold = [0.1,0.7]


number = 0
dir_path = os.path.dirname(os.path.realpath(__file__))
filename = dir_path + '/raw_{}'.format(number)

class TurtlebotTest( object ):

    def __init__( self ):
        self.bridge = CvBridge()

        self.current_cv_depth_image = np.zeros( (1, 1, 3) )
        print('a')
        self.__depth_img = rospy.Subscriber( '/camera/depth/image', Image ,self.__depth_handler )
        print('b')
    def __depth_handler( self, data ):
        try:
            print('in')
            self.current_cv_depth_image = np.nan_to_num(np.asarray( self.bridge.imgmsg_to_cv2( data, "32FC1" )))
            sub_image = self.current_cv_depth_image[center[0]-windows[0] : center[0]+windows[0], center[1]-windows[1] :
            center[1]+windows[1]]
            #np.save(filename,self.current_cv_depth_image)
            print((np.greater(sub_image,threshold[0]) * np.less(sub_image ,threshold[1])).any())
            print((sub_image==0).all())
            
            #print(np.nan_to_num(self.current_cv_depth_image[239:241,319:321]))

            #print('showing')
            cv2.imshow('depht',np.nan_to_num(self.current_cv_depth_image[center[0]-windows[0] : center[0]+windows[0] , center[1] - windows[1] : center[1] + windows[1]]))
            cv2.waitKey(0)
            print('closed')
        except Exception as e:
            print('error')
            rospy.logerr( e )

if __name__ == '__main__':

    rospy.init_node( "turtlebot_test" )
    handler = TurtlebotTest()
    rospy.spin()
