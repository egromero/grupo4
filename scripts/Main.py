import rospy
from Evadir import Evation


class Turtlebot(object):

	def __init__( self ):
		self.evacion = Evation()
		rospy.sleep(1)


if __name__ == '__main__':

	rospy.init_node( "turtlebot_g4" )
	handler = Turtlebot()
	rospy.spin()
