#!/usr/bin/env python
import rospy
import json
import numpy as np
from parameters import *

from std_msgs.msg import String, Bool
initial_route = [0,0,np.pi/3]
repeat_route = [0.5,0,None]

class Turtlebot(object):
	def __init__( self ):
		self.flag = True
		self.absolute_obstacle_flag = False
		self.in_route = True
		self.image_flag = False
		self.move_allowed_flag = False
		self.continuous_obstacle_flag1 = False
		self.continuous_obstacle_flag2 = False

		## bad joke.
		self.target_publisher = rospy.Publisher('new_target',String,queue_size=10)
		rospy.sleep( 0.2 )

		##
		self.on_pub = rospy.Publisher('main_on',Bool,queue_size=1)
		self.reset_pub = rospy.Publisher('reset',Bool,queue_size=10)
		rospy.Subscriber('target_reached',Bool,self.target_reached_callback)
		rospy.sleep( 0.2 )

		##obstacle sub
		rospy.Subscriber('obstacle',Bool,self.obstacle_response)

		##Image taker pub and sub
		self.image_take_pub= rospy.Publisher('image_take',Bool,queue_size=1)
		rospy.Subscriber('image_done',Bool,self.image_callback)
		rospy.Subscriber('move_allowed',Bool,self.move_allowed_callback)

		#control enabler/disabler publisher.
		self.control_pub = rospy.Publisher('control_enable',Bool,queue_size=1)




		self.r = rospy.Rate(5)
		## wait for map and initial particles
		self.on_pub.publish(True)
		while (not self.image_flag and not rospy.is_shutdown()):
			self.r.sleep()
		## initial 360 degree spin with data
		#for i in range(6):
			## take image and wait
			#self.image_flag = False
			#self.image_take_pub.publish(True)
			#while not self.image_flag and not rospy.is_shutdown:
			#	self.r.sleep()
			## image done? move and send movement data to map node
			#self.target_wait(initial_route)
			#print('route_done')

			#while (not self.move_allowed_flag and not rospy.is_shutdown()):
			#	self.r.sleep()
			#self.move_allowed_flag = False


		self.absolute_obstacle_flag = True
		while not rospy.is_shutdown():
			self.image_flag = False
			self.image_take_pub.publish(True)
			while (not self.image_flag and not rospy.is_shutdown()):
				self.r.sleep()


			self.send_data(repeat_route)
			self.in_route = False
			self.flag = False
			while not rospy.is_shutdown():
				while not self.flag and not rospy.is_shutdown():
				    self.r.sleep()
				self.in_route = True
				print('waiting for another iteration of obstacle')
				rospy.sleep(2)
				if self.continuous_obstacle_flag2:
				    self.in_route = False
				else:
				    break	
	
			print('out of loop')
			rospy.sleep(2)
			while (not self.move_allowed_flag and not rospy.is_shutdown()):
				self.r.sleep()
			self.move_allowed_flag = False


	def image_callback(self,data):
		self.image_flag = True

	def send_data(self,item,target=None):
		if target == None:
		    target = self.target_publisher
		encoded = json.dumps(item)
		target.publish(encoded)
		print('Sent {}'.format(encoded))

	## reset the state and spin the robot
	def obstacle_response(self,data):
		if self.absolute_obstacle_flag:
		## abosulte flag ignores interruptions at the beginning (initial spin)
			if (data.data and not self.in_route):
				print('changing angle due to obstacle')
				## before ressetting the states, see how much did everyone move
				self.control_pub.publish(False)
				print('Controller shut down')
				self.reset_pub.publish(True)	
	
				while (not self.move_allowed_flag and not rospy.is_shutdown()):
					self.r.sleep()
				self.move_allowed_flag = False	


				self.image_flag = False
				self.image_take_pub.publish(True)
				while not self.image_flag and not rospy.is_shutdown:
					self.r.sleep()
				self.send_data([0,0,np.pi/4])
				self.control_pub.publish(True)
				self.continuous_obstacle_flag1 = True
			elif (self.continuous_obstacle_flag1 and data.data):	
				print('continuous obstacle')
				self.continuous_obstacle_flag1 = False
				self.continuous_obstacle_flag2 = True
			elif (self.continuous_obstacle_flag1 and not data.data):
				self.continuous_obstacle_flag1 = False
				self.continuous_obstacle_flag2 = False
			


	def move_allowed_callback(self,data):
	    self.move_allowed_flag = True

	def target_wait(self,target):
		self.send_data(target)
		self.flag = False
		while not self.flag and not rospy.is_shutdown():
			#print('Actual flag' ,self.flag)
			self.r.sleep()
		self.in_route = True
		rospy.sleep(2)

	def target_reached_callback(self,data):
		self.flag = data.data
		self.reset_pub.publish(True)
		print('incoming flag :',data.data)

if __name__ == '__main__':
	rospy.init_node( "turtlebot_g4" )
	handler = Turtlebot()
	rospy.spin()
