#!/usr/bin/env python
import rospy
import json
import numpy as np


from std_msgs.msg import String, Bool
repeat_route = [0.5,0,None]

class Turtlebot(object):
	def __init__( self ):
		## bad joke.
		self.target_publisher = rospy.Publisher('new_target',String,queue_size=10)
		rospy.sleep( 0.2 )

		self.reset_pub = rospy.Publisher('reset',Bool,queue_size=10)
		rospy.Subscriber('target_reached',Bool,self.target_reached_callback)
		rospy.sleep( 0.2 )

		##obstacle sub
		rospy.Subscriber('obstacle',Bool,obstacle_response)

		self.flag = True
		self.r = rospy.Rate(5)

		while not rospy.is_shutdown()
			self.send_route(repeat_route)
			while not self.flag and not rospy.is_shutdown():
				#print('Actual flag' ,self.flag)
				self.r.sleep()
            rospy.sleep(0.1)

	def send_route(self,route):
		encoded = json.dumps(item)
		self.target_publisher.publish(encoded)
		print('Sent {}'.format(encoded))
		self.flag = False

	## reset the state and spin the robot
	def obstacle_response(self,data):
		if data.data:
			self.reset_pub.publish(True)
			self.send_route([0,0,np.pi/2])


	def target_reached_callback(self,data):
		self.flag = data.data
		self.reset_pub.publish(True)
		print('incoming flag :',data.data)

if __name__ == '__main__':
	rospy.init_node( "turtlebot_g4" )
	handler = Turtlebot()
	rospy.spin()
