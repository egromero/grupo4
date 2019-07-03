#!/usr/bin/env python
import rospy
import json
import numpy as np


from std_msgs.msg import String, Bool

repeat_route = [0.5,0,None]

class Turtlebot(object):
	def __init__( self ):
		## bad joke.
		self.data_pub = rospy.Publisher('move_to',String,queue_size=10)
		rospy.Subscriber('path_to_point',String,self.path_done)
		rospy.sleep( 0.2 )

		inicio, fin = (4, 12), (20, 4)
		encoded = json.dumps([inicio, fin])
		self.data_pub.publish(encoded)
		rospy.sleep( 0.2 )

	def path_done(self, data):
		print(json.loads(data.data))


if __name__ == '__main__':
	rospy.init_node( "turtlebot_g4" )
	handler = Turtlebot()
	rospy.spin()
