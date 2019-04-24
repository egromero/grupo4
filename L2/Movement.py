import rospy
import math
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
import cv2
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
import time as tm
import os
from std_msgs.msg import Float64
from Constans import * 




def pi_fix(angle_in):
    if angle_in<-np.pi:
        sub = angle_in+2*np.pi
    elif angle_in>np.pi:
        sub = angle_in-2*np.pi
    else:
        sub = angle_in
    return sub



class Movement():
	def __init__( self ):
		rospy.loginfo( "To stop TurtleBot CTRL+C" )

		self.r = rospy.Rate(10);

		self.move_cmd = Twist()
		self.pos = [0 for x in xrange(3)]
		self.ang = 0

		if self.write:
			self.file = open(dir_path+filename,'w')
			self.file.write('starting new something.\n')
		
		# What method to call when you ctrl + c
		rospy.on_shutdown( self.shutdown )

		#Publisher and Subscriber
		rospy.Subscriber( 'odom', Odometry, self.Position)

		self.cmd_vel = rospy.Publisher( '/cmd_vel_mux/input/navi', Twist, queue_size=10 )

		#PID
		
		self.dist_set_point = rospy.Publisher( '/robot_dist/setpoint', Float64, queue_size = 1 )

		while self.dist_set_point.get_num_connections() == 0 and not rospy.is_shutdown():
			rospy.sleep( 0.2 )

		self.dist_state = rospy.Publisher( '/robot_dist/state', Float64, queue_size = 1 )
		while self.dist_state.get_num_connections() == 0 and not rospy.is_shutdown():
			rospy.sleep( 0.2 )

		self.actuation = rospy.Subscriber( '/robot_dist/control_effort', Float64, self.get_speed )
		

	def get_speed( self, data ):
		self.speed = float( data.data )
		rospy.loginfo( 'speed received: %f' % ( self.speed ))
		#do something with speed

	

	def move(self,vel, ang):
		self.move_cmd.linear.x = vel
		self.move_cmd.angular.z = ang

		# publish the velocity
		self.cmd_vel.publish( self.move_cmd )
		self.r.sleep()

	def Position( self, odom_data ):
		pose = odom_data.pose.pose #  the x,y,z pose and quaternion orientation

		if self.ref:
			print('got')
			self.zero[0] = odom_data.pose.pose.position.x
			self.zero[1] = odom_data.pose.pose.position.y
			self.zero[2] = odom_data.pose.pose.position.z
			angaux = odom_data.pose.pose.orientation.w
			self.zero[3] = 2*math.acos( angaux ) if (odom_data.pose.pose.orientation.w < 0) else -2*math.acos( angaux )
			self.ref = False
			self.pos[0] = np.cos(self.zero[3])*(odom_data.pose.pose.position.x-self.zero[0]) + np.sin(self.zero[3])*(odom_data.pose.pose.position.y-self.zero[1])
			self.pos[1] = np.cos(self.zero[3])*(odom_data.pose.pose.position.y-self.zero[1]) - np.sin(self.zero[3])*(odom_data.pose.pose.position.x-self.zero[0])
			self.pos[2] = odom_data.pose.pose.position.z  - self.zero[2]
			angaux = odom_data.pose.pose.orientation.w
			angaux2 = -2*math.acos( angaux ) if (odom_data.pose.pose.orientation.z < 0) else 2*math.acos( angaux )

		if angaux2-self.zero[3]>math.pi:

			self.ang = (angaux2-self.zero[3])-2*math.pi

		elif angaux2 - self.zero[3] < -math.pi:

			self.ang = (angaux2-self.zero[3]) + 2*math.pi
		else:
			self.ang  = angaux2 - self.zero[3]

		if self.flag == 2 and self.write:

			self.file.write('X:{}, Y:{}, Z:{}, Angle:{}\n'.format(self.pos[0],self.pos[1],self.pos[2],self.ang))

		if self.flag == 3 and self.write :
			self.file.close()
			self.flag = 4
			print('Se cerro archivo')

	def aplicar_velocidad(self, vel_lineal, vel_angular, time):
		vel_lineal, vel_angular, time = iter(vel_lineal), iter(vel_angular), iter(time)
		current_action = (next(vel_lineal, None), next(vel_angular,None), next(time, None))
		while current_action[2]:
			print(current_action)
			if self.write:
				self.file.write('Nueva rutina: {}\n'.format(current_action))
			lapsed_time = 0
				while (lapsed_time < current_action[2]+0.2) and not rospy.is_shutdown():
					past_time = rospy.Time.now().to_sec()
					#print(rospy.Time.now().to_sec())
					if not self.obstacle:
						self.move(current_action[0], current_action[1])
							delta = rospy.Time.now().to_sec() - past_time
								lapsed_time += delta
					else:
						self.move(0,0)
						tm.sleep(0.2)
						#past_time = rospy.Time.now().to_sec()
					if self.flag ==2 and self.write:
						print('Time: {}\n'.format(lapsed_time))
						self.file.write('Time: {}\n'.format(lapsed_time))
			current_action = (next(vel_lineal, None), next(vel_angular,None), next(time, None))

		self.move(0,0)

	def mover_robot_goal_beta(self,pos):
		## Debug print
		#print(self.pos[0])
		#print(self.pos[1])
		#print(pos[0])
		#print(pos[1])

		## since division by 0 is not allowed, gotta improvise. FIX

		if abs((pos[0]-self.pos[0]))<0.00000000001:
			dif = 0.000000000001
		else:
			dif = pos[0]-self.pos[0]

		##  Absolute angle of target
		aim_angle = np.arctan((pos[1]-self.pos[1])/dif)

		if dif<0:
			aim_angle = pi_fix(aim_angle+np.pi)

		## Relative angle of target
		delta_angle = pi_fix(aim_angle - self.ang)
		#print(aim_angle)
		#print(delta_angle)

		## Distance between target and acutal position
		module =  np.sqrt(np.power((pos[1]-self.pos[1]),2) + np.power((pos[0]-self.pos[0]),2))


		## Set values with corresponding sign

		angular_speed = 0.8 if delta_angle>0 else -0.8
		real_speed = 0.34 if delta_angle>0 else -0.34
		delta_pos = 0.26 if delta_angle>0 else -0.26
		linear = [0,0.2]
		angular = [angular_speed,0]

		## the 0.8 and 0.26 values are a kind of a fix.
		angular_time = (delta_angle-delta_pos)/real_speed + 0.8 if (abs(delta_angle)>0.26) else 0.00000001

		time = [angular_time,module/(0.2*coef) + 0.000001]
		return linear,angular,time

	def linearecta(self, limit):

		self.flag=2
		for item in item_list:
			vl, va, t = self.mover_robot_goal_beta(item)
			#print(vl)
			#print(va)
			#print(t)
			self.aplicar_velocidad(vl,va,t)
		self.flag=3
		#print('Se termino la segunda rutina')

		## meter control bangbang
		return 0


	def shutdown( self ):
		# stop turtlebot
		rospy.loginfo( "Stopping TurtleBot" )
		# a default Twist has linear.x of 0 and angular.z of 0.  So it'll stop TurtleBot
		self.cmd_vel.publish( Twist() )
		# sleep just makes sure TurtleBot receives the stop command prior to shutting down the script
		rospy.sleep( 1 )








