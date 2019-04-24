
from geometry_msgs.msg import Twist
import rospy




## UTILITIES
def gen(vel, ang, t):
	for velocidad, angular, tiempo in zip(v,ang,t):
		yield [velocidad, angular, tiempo]

def next_action(generador):
	try:
		return next(generador)
	except StopIteration:
		return None

class Speed():

	def __init__(self):
		self.move_cmd = Twist()
		self.cmd_vel = rospy.Publisher( '/cmd_vel_mux/input/navi', Twist, queue_size=10 )
		self.rate = rospy.Rate(10);

	def aplicar_velocidad(vel_lineal, vel_angular, tiempo):
		generador = gen(vel_lineal, vel_angular, tiempo)
		current_action = next_action(generador)
		while current_action:
			lapsed_time = 0
			while (lapsed_time < current_action[2]): #and not rospy.is_shutdown():
				past_time = rospy.Time.now().to_sec()
				if not obstaculo:
					self.move(current_action[0], current_action[1])
					delta = rospy.Time.now().to_sec() - past_time
					lapsed_time += delta
				else:
					self.move(0,0)
			rospy.loginfo( "Next Instruction" )
			current_action = next_action(generador)

		self.move(0,0)

	def move(vel, ang):
		self.move_cmd.linear.x = vel
		self.move_cmd.angular.z = ang
		# publish the velocity
		self.cmd_vel.publish( self.move_cmd )
		self.rate.sleep()
