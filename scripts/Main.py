import rospy

import numpy as np
from control import Control

route = [(0,1),(1,1),(1,0),(0,0)]

class Turtlebot(object):

	def __init__( self ):
		## bad joke.
		# self.control = None
		self.control = Control()
		for item in route:
			self.control.new_target(item)
			while not self.control.done:
				rospy.sleep(0.05)



if __name__ == '__main__':

	rospy.init_node( "turtlebot_g4" )
	handler = TurtlebotTest()
	rospy.spin()
