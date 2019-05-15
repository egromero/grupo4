#!/usr/bin/env python
import rospy
import json
import numpy as np


from std_msgs.msg import String, Bool

route = [[1,0,None],[0,0,None],[0,0,0]]

class Turtlebot(object):
	def __init__( self ):
		## bad joke.
		self.target_publisher = rospy.Publisher('new_target',String,queue_size=10)
		rospy.sleep( 0.2 )
		self.obstacle = False

		rospy.Subscriber('target_reached',Bool,self.target_reached_callback)
		rospy.Subscriber('route_obstacle', String, self.new_route_recieved)
		rospy.sleep( 0.2 )

		self.flag = True
		self.r = rospy.Rate(5)
		for item in route:
			encoded = json.dumps(item)
			self.target_publisher.publish(encoded)
			print('Sent {}'.format(encoded))
			self.flag = False

			while not self.flag and not rospy.is_shutdown():
				#print('Actual flag' ,self.flag)
				if self.obstacle:
					print('Obstaculo')
					while len(self.new_route) >= 1:
						instruction = self.new_route.pop(0)
						encoded = json.dumps(instruction)
						self.target_publisher.publish(encoded)
						print('Sent {}'.format(encoded))
						self.flag = False
						while not self.flag and not rospy.is_shutdown():
							print('Esquivando')
							print("actual flag: ",self.flag)
							self.r.sleep()
					self.obstacle = False
				self.r.sleep()

	def target_reached_callback(self,data):
		self.flag = data.data
		#print('incoming flag :',data.data)
	def new_route_recieved(self, data):
		if not self.obstacle:
			self.new_route = json.loads(data.data)
			self.obstacle = True

		
if __name__ == '__main__':
	rospy.init_node( "turtlebot_g4" )
	handler = Turtlebot()
	rospy.spin()
