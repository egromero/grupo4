from util import pi_fix, Timer
import numpy as np
from classes import State


import rospy
from nav_msgs.msg import Odometry


class States():

    def __init__(self):
        self.state_dict = {'x':0,'y':0,'ang_pos':0}
        self.timer = Timer()
        ## 0 = xpos, 1 =  ypos, 2 = zpos, 3 = angular pos
        self.zero = [0 for i in range(4)]
        ## 0 = xpos, 1 = ypos, 2 = zpos, 3 = ang pos.
        self.pos = [0 for i in range(4)]
        self.speed = [0 for i in range(4)]
        #First oddometry read to get references
        self.ref = True



        ## Subscribe to odometry
        rospy.Subscriber( 'odom', Odometry, self.Odom_read)
        self.publisher = rospy.Publisher('our_state',State)

        rospy.on_shutdown( self.shutdown )
        self.r = rospy.Rate(30);
        while not rospy.is_shutdown:
            self.state_dict = {'x':self.pos[0],'y':self.pos[1],'ang_pos':self.pos[3]}
            self.publisher.publish(self.state_dict)


    ##Odometry message read
    def Odom_read( self, odom_data ):
        ## Sets reference if first read, else calculates new position values, speed values, and actualizes.

        pose = odom_data.pose.pose #  the x,y,z pose and quaternion orientation

        if self.ref:
            print('got')
            self.zero[0] = odom_data.pose.pose.position.x
            self.zero[1] = odom_data.pose.pose.position.y
            self.zero[2] = odom_data.pose.pose.position.z
            angaux = odom_data.pose.pose.orientation.w


            self.zero[3] = 2*np.arccos( angaux ) if (odom_data.pose.pose.orientation.w < 0) else -2*np.arccos( angaux )
            self.ref = False
            self.timer.reset()



        ##Calculate new values
        new_x = np.cos(self.zero[3])*(odom_data.pose.pose.position.x-self.zero[0]) + np.sin(self.zero[3])*(odom_data.pose.pose.position.y-self.zero[1])

        new_y = np.cos(self.zero[3])*(odom_data.pose.pose.position.y-self.zero[1]) - np.sin(self.zero[3])*(odom_data.pose.pose.position.x-self.zero[0])

        new_z = odom_data.pose.pose.position.z  - self.zero[2]

        angaux = odom_data.pose.pose.orientation.w
        angaux2 = -2*np.arccos( angaux ) if (odom_data.pose.pose.orientation.z < 0) else 2*np.arccos( angaux )
        new_ang = pi_fix(angaux2-self.zero[3])


        ## Calculate speeds
        if self.timer.time()>10:
            x_speed = 1000*(new_x - self.pos[0])/self.timer.time()
            y_speed = 1000*(new_y - self.pos[1])/self.timer.time()
            z_speed = 1000*(new_z - self.pos[2])/self.timer.time()
            ang_speed = 1000*(new_ang - self.pos[3])/self.timer.time()
            self.timer.reset()

            ##Actualize new speeds
            self.speed[0] = x_speed
            self.speed[1] = y_speed
            self.speed[2] = z_speed
            self.speed[3] = ang_speed

        ##Actualize new values
        self.pos[0] = new_x
        self.pos[1] = new_y
        self.pos[2] = new_z
        self.pos[3] = new_ang

if __name__ ='__main__':
    rospy.init_node("state_node")
    handler = States()
    rospy.spin()
