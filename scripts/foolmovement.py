import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from cv_bridge import CvBridge




CENTER = [240,320]
VISION_WINDOW = [90,90]


class FoolMovement():
	def __init__(self):
		self.bridge = CvBridge()
		self.mover = rospy.Publisher( '/cmd_vel_mux/input/navi', Twist, queue_size=10 )
		self.move_cmd = Twist()
		rospy.Subscriber( '/camera/depth/image', Image, self.measure)
	
	def straight(self):
		self.move_cmd.linear.x = 0.2
		self.move_cmd.angular.z = 0
		self.mover.publish(self.move_cmd)

	def swing(self, sense):
		rot = {"RIGHT": 0.8 , 'LEFT': -0.8}
		self.move_cmd.linear.x = 0
		self.move_cmd.angular.z = rot[sense]
		self.mover.publish(self.move_cmd)

	def measure(self, data):
		self.depth_image = np.nan_to_num(np.asarray( self.bridge.imgmsg_to_cv2( data, "32FC1" )))
		sub_image = self.depth_image[CENTER[0]-VISION_WINDOW[0] : CENTER[0]+VISION_WINDOW[0], CENTER[1]-VISION_WINDOW[1] :CENTER[1]+VISION_WINDOW[1]]
		self.obstacle = (np.greater( sub_image, 0.2 ) * np.less( sub_image, 0.55)).any()

	def route(self):
		### Localizate es una flag que viene de otra parte, la idea es que mientras no esté localizado,
		### se ejecute la función.
		tm = rospy.Time.now().to_sec()
		while not localizate and not self.obstacle:
			if rospy.Time.now().to_sec()-tm < 1.5:
				self.straight()
				
		## Falta los tiempos para girar, sensar, si tengo espacio, avanzo si no me devuelvo y sigo mi camino
		## además si tiene obstaculo adelante, girar a la izquierda. 
		## Para giro usar swing("RIHT") o "LEFT"








