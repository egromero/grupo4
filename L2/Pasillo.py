from cv_bridge import CvBridge, CvBridgeError
import numpy as np
from Constants import *

class Pasillo():

    def __init__(self, mover):
        self.mover = mover
		self.bridge = CvBridge()
		self.current_cv_depth_image = np.zeros( (1, 1, 3) )
        self.obstacle = OBSTACLE

        self.__depth_img = rospy.Subscriber( '/camera/depth/image', Image, self.recorrer )

    def recorrer( self ):
        try:
			self.current_cv_depth_image = np.nan_to_num(np.asarray( self.bridge.imgmsg_to_cv2( data, "32FC1" )))

            sub_imageL = self.current_cv_depth_image[LIMIT_X[0] : LIMIT_X[1], LIMIT_Y[0] : LIMIT_Y[0]+DELTA]
            sub_imageR = self.current_cv_depth_image[LIMIT_X[0] : LIMIT_X[1], LIMIT_Y[1]-DELTA : LIMIT_Y[1]]
            self.in_line = ( np.greater( sub_imageL-sub_imageR, - MARGEN ) * np.less( sub_imageL-sub_imageR, MARGEN ) ).all()

            sub_image = self.current_cv_depth_image[CENTER[0]-VISION_WINDOW[0] : CENTER[0]+VISION_WINDOW[0], CENTER[1]-VISION_WINDOW[1] :CENTER[1]+VISION_WINDOW[1]]
			self.obstacle = ( np.greater( sub_image, 0.2 ) * np.less( sub_image, 0.6 ) ).any()

            if self.obstacle:
                self.mover.move( 0, 0 )

            elif self.in_line:
                self.mover.move( 0.1, 0 )

            else:
                error = np.mean( ( sub_imageL - sub_imageR ).all() )
                value = 0.3 + 0.5 * abs(error)
                ang_speed = -value if error < 0 else value
                self.mover.move( 0.1, ang_speed )

		except Exception as e:
			print('error')
			rospy.logerr( e )
