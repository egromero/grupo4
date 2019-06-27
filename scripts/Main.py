#!/usr/bin/env python
import rospy
import json
import numpy as np


from std_msgs.msg import String, Bool
initial_route = [0,0,np.pi/n_angles]
repeat_route = [0.5,0,None]

class Turtlebot(object):
	def __init__( self ):
		self.flag = True
		self.absolute_obstacle_flag = False
		self.in_route = False
		self.image_flag = False

		## bad joke.
		self.target_publisher = rospy.Publisher('new_target',String,queue_size=10)
		rospy.sleep( 0.2 )

		## when obstacle is found, we need to retrieve states
		self.state_change_pub = rospy.Publisher('state_change',Bool,queue_size=10)
		rospy.sleep( 0.2 )


		self.reset_pub = rospy.Publisher('reset',Bool,queue_size=10)
		rospy.Subscriber('target_reached',Bool,self.target_reached_callback)
		rospy.sleep( 0.2 )

		##obstacle sub
		rospy.Subscriber('obstacle',Bool,self.obstacle_response)

		##Image taker pub and sub
		self.image_take_pub= rospy.Publisher('image_take',Bool,queue_size=1)
		self.image_data_pub = rospy.Publisher('image_data',String,queue_size=10)
		rospy.Subscriber('image_done',Bool,self.image_callback)



		self.r = rospy.Rate(5)
		## wait for map and initial particles
		while not self.image_flag:
			self.r.sleep()
		## initial 360 degree spin with data
		for i in range(n_angles):
			## take image and wait
			self.image_flag = False
			self.image_pub.publish(True)
			while not self.image_flag:
				self.r.sleep()
			## image done? move and send movement data to map node
			self.target_wait(initial_route)
			#note: doesnt get data from states to see what to send
			self.send_data([0,np.pi/n_angles],self.image_data_pub)

		self.absolute_obstacle_flag = True
		while not rospy.is_shutdown():
			self.image_flag = False
			self.image_pub.publish(True)
			while not self.image_flag:
				self.r.sleep()

			self.send_data(repeat_route)
			self.flag = False
			while not self.flag and not rospy.is_shutdown():
				#print('Actual flag' ,self.flag)
				self.r.sleep()
			rospy.sleep(2)
			self.in_route = False

	def image_callback(self,data):
		self.image_flag = True

	def send_data(self,item,target=self.target_publisher):
		encoded = json.dumps(data)
		target.publish(encoded)
		print('Sent {}'.format(encoded))

	## reset the state and spin the robot
	def obstacle_response(self,data):
		## abosulte flag ignores interruptions at the beginning (initial spin)
		if (data.data and not self.in_route) and self.absolute_obstacle_flag:
			print('changing angle due to obstacle')
			## before ressetting the states, see how much did everyone move
			self.state_change_pub.publish(True)
			self.reset_pub.publish(True)
			self.send_data([0,0,np.pi/3])
			self.flag = False
			self.in_route = True

	def target_wait(self,target):
		self.send_data(target)
		self.flag = False
		while not self.flag and not rospy.is_shutdown():
			#print('Actual flag' ,self.flag)
			self.r.sleep()
		rospy.sleep(2)

	def target_reached_callback(self,data):
		self.flag = data.data
		self.reset_pub.publish(True)
		print('incoming flag :',data.data)

if __name__ == '__main__':
	rospy.init_node( "turtlebot_g4" )
	handler = Turtlebot()
	rospy.spin()
