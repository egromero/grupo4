from util import pi_fix
import numpy as np
import rospy

class States():

    def __init__(self):
        ## 0 = xpos, 1 =  ypos, 2 = zpos, 3 = angular pos
        self.zero = [0 for i in range(4)]
        ## 0 = xpos, 1 = ypos, 2 = zpos, 3 = ang pos.
        self.pos = [0 for i in range(4)]
        #First oddometry read to get references
        self.ref = True

        ## Subscribe to odometry
        rospy.Subscriber( 'odom', Odometry, self.Odom_read)




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



        ##Calculate new values
        new_x = np.cos(self.zero[3])*(odom_data.pose.pose.position.x-self.zero[0]) + np.sin(self.zero[3])*(odom_data.pose.pose.position.y-self.zero[1])

        new_y = np.cos(self.zero[3])*(odom_data.pose.pose.position.y-self.zero[1]) - np.sin(self.zero[3])*(odom_data.pose.pose.position.x-self.zero[0])

        new_z = odom_data.pose.pose.position.z  - self.zero[2]

        angaux = odom_data.pose.pose.orientation.w
        angaux2 = -2*np.arccos( angaux ) if (odom_data.pose.pose.orientation.z < 0) else 2*np.arccos( angaux )
        new_ang = pi_fix(angaux2-self.zero[3])


        ##Actualize new values
        self.pos[0] = new_x
        self.pos[1] = new_y
        self.pos[2] = new_z
        self.pos[3] = new_ang
