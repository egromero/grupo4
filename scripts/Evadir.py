from cv_bridge import CvBridge, CvBridgeError
import rospy
import numpy as np
from Constants import *

class Evation():

    def __init__(self):
        self.bridge = CvBridge()
        self.obstacle = OBSTACLE
        self.evadiendo = False

        self.__depth_img = rospy.Subscriber( '/camera/depth/image', Image, self.avanzar )

        self.mover = rospy.Publisher( '/cmd_vel_mux/input/navi', Twist, queue_size=10 )
        self.move_cmd = Twist()

    def avanzar(self, data):
        try:
            self.current_cv_depth_image = np.nan_to_num(np.asarray( self.bridge.imgmsg_to_cv2( data, "32FC1" )))

            sub_image = self.current_cv_depth_image[CENTER[0]-VISION_WINDOW[0] : CENTER[0]+VISION_WINDOW[0], CENTER[1]-VISION_WINDOW[1] :CENTER[1]+VISION_WINDOW[1]]
			self.obstacle = ( np.greater( sub_image, 0.2 ) * np.less( sub_image, 0.6 ) ).any()

            if self.obstacle:
                self.evadiendo = True
                self.lapsed_time = 0
                self.move(0, 0)
            else:
                self.move(0.1, 0)

            if self.evadiendo:
                if self.lapsed_time < (SPIN_TIME) and not rospy.is_shutdown():
                    past_time = rospy.Time.now().to_sec()
                    self.move(0, ANGULAR_SPEED)
                    delta = rospy.Time.now().to_sec() - past_time
					self.lapsed_time += delta

                elif self.lapsed_time < (SPIN_TIME+ROTATE_TIME) and not rospy.is_shutdown():
                    past_time = rospy.Time.now().to_sec()
                    self.move(ROTATE_LINEL, ROTATE_ANG)
                    delta = rospy.Time.now().to_sec() - past_time
					self.lapsed_time += delta

                elif self.lapsed_time < (2*SPIN_TIME+ROTATE_TIME) and not rospy.is_shutdown():
                    past_time = rospy.Time.now().to_sec()
                    self.move(0, -ANGULAR_SPEED)
                    delta = rospy.Time.now().to_sec() - past_time
					self.lapsed_time += delta

                else:
                    self.evadiendo = False
                    self.move(0, 0)

        except Exception as e:
            print('error')
			rospy.logerr( e )

    def move(self, vel, ang):
		self.move_cmd.linear.x = vel
		self.move_cmd.angular.z = ang
		self.mover.publich(self.move_cmd)
		self.r.sleep()
