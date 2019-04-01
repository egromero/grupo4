import rospy
import roslib

from sensor_msgs.msg import Image

import np as np
import cv2
from cv_bridge import CvBridge, CvBridgeError


class TurtlebotTest( object ):

    def __init__( self ):
        self.bridge = CvBridge()
        self.current_cv_depth_image = np.zeros( (1, 1, 3) )
        self.__depth_img = rospy.Subscriber( '/camera/depth/image', Image ,self.__depth_handler )
        self.raw_number = 0
    def __depth_handler( self, data ):
        try:
            self.current_cv_depth_image = np.asarray( self.bridge.imgmsg_to_cv2( data, "32FC1" ) )

            np.save('raw_{}'.format(self.raw_number,self.current_cv_depth_image))
            self.raw_number+=1

            print('showing')
            cv2.imshow('depht',self.current_cv_depth_image)
            cv2.waitkey(0)
            print('closed')
        except Exception as e:
            rospy.logerr( e )

if __name__ == '__main__':

    rospy.init_node( "turtlebot_test" )
    handler = TurtlebotTest()
    rospy.spin()
