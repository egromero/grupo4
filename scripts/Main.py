#!/usr/bin/env python
import rospy
import json
import numpy as np


from std_msgs.msg import String, Bool

route = [[1,0,None],[0,0,None],[0,0,0]]


class Turtlebot(object):
	def __init__( self ):
		## item are main targets, subroutes are if obstacles are detected, allows nesting (obsacle in first obstacle route)
		self.item = None
		self.sub_route = []
		self.target_publisher = rospy.Publisher('new_target',String,queue_size=10)
		rospy.sleep( 0.2 )
		# self.obstacle = False


		rospy.Subscriber('target_reached',Bool,self.target_reached_callback)
		rospy.Subscriber('route_obstacle', String, self.new_route_recieved)
		rospy.sleep( 0.2 )

		self.target_reached_flag = True
		self.r = rospy.Rate(5)
		for item in route:
			## Allows for better progaming, instead of nesting with if, a smarter choice would choose between publishing main targets or secondary targets
			self.item = item

			encoded = json.dumps(item)
			self.target_publisher.publish(encoded)

			print('Sent {}'.format(encoded))

			self.target_reached_flag = False
			## Only move through main targets if all subroute targets have been cleared
			self.item_ready = self.target_reached_flag and (len(self.sub_route)==0)

			while not self.item_ready and not rospy.is_shutdown():
				#print('Actual flag' ,self.flag)

				## if target reached and there still are sub_route targets, get a new one
				if self.target_reached and (len(self.sub_route)!=0):
					instruction = self.sub_route.pop(0)
					encoded = json.dumps(instruction)
					self.target_publisher.publish(encoded)
					print('Sent {}'.format(encoded))

					self.target_reached = False
				self.r.sleep()
				# if self.obstacle:
				# 	print('Obstaculo')
				# 	while len(self.new_route) >= 1:
				# 		instruction = self.new_route.pop(0)
				# 		encoded = json.dumps(instruction)
				# 		self.target_publisher.publish(encoded)
				# 		print('Sent {}'.format(encoded))
				# 		self.flag = False
				# 		while not self.flag and not rospy.is_shutdown():
				# 			print('Esquivando')
				# 			print("actual flag: ",self.flag)
				# 			self.r.sleep()
				# 	self.obstacle = False
				# self.r.sleep()

	def target_reached_callback(self,data):
		self.target_reached_flag = data.data
		#print('incoming flag :',data.data)
	# def new_route_recieved(self, data):
	# 	if not self.obstacle:
	# 		self.new_route = json.loads(data.data)
	# 		self.obstacle = True
	def new_route_recieved(self, data):
		self.sub_route =  json.loads(data.data).append(self.item)

if __name__ == '__main__':
	rospy.init_node( "turtlebot_g4" )
	handler = Turtlebot()
	rospy.spin()
