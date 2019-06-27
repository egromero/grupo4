#!/usr/bin/env python
from util import pi_fix, Timer
import numpy as np
import json


import rospy
from nav_msgs.msg import Odometry
from std_msgs.msg import String, Bool


def process(data,zero = [0,0,0,0]):
    new_x = np.cos(zero[3])*(data.position.x-zero[0]) + np.sin(zero[3])*(data.position.y-zero[1])
    new_y = np.cos(zero[3])*(data.position.y-zero[1]) - np.sin(zero[3])*(data.position.x-zero[0])
    new_z = data.position.z  - zero[2]
    angaux = data.orientation.w
#print('angaux = {}'.format(angaux))
    angaux2 = -2*np.arccos( angaux ) if (data.orientation.z < 0) else 2*np.arccos( angaux )
#print('angaux2 = {}'.format(angaux2))
    new_ang = pi_fix(angaux2-zero[3])

    pos = [new_x,new_y,new_z,new_ang]
    return pos

class States():
    def __init__(self):
        #First oddometry read to get references
        self.ref = True
        self.pos = [0 for i in range(4)]
        self.zero = [0 for i in range(4)]
        self.speed = [0 for i in range(4)]
        self.timer = Timer()

        ##Writer Publisher
        self.writer = rospy.Publisher('write_permit',String,queue_size =10)

        ##how much did one move publisher
        self.moved_pub = rospy.Publisher('')

        ## Subscribe to odometry
        rospy.Subscriber( 'odom', Odometry, self.Odom_read)
        ## state publisher
        self.publisher = rospy.Publisher('our_state',String,queue_size =10)
        self.change_pub = rospy.Publisher('state_change',String,queue_size =10)
	    #rospy.init_node('states',anonymous = True)
        self.r = rospy.Rate(60);
        rospy.Subscriber('reset',Bool,self.reset)
        print('Creating states node...')
        while not rospy.is_shutdown():
            self.state_dict = {'x':self.pos[0],'y':self.pos[1],'ang_pos':self.pos[3]}
            self.publisher.publish(json.dumps(self.state_dict))

            state_write = '{},{},{},{}'.format(self.pos[0],self.pos[1],self.pos[3],self.timer.time())
            #self.writer.publish(state_write)
	    #print('Posiciones : ',state_write)
            self.r.sleep()
    def reset(self,data):
        self.change_pub.publish(json.dumps(self.state_dict))
        self.ref = True

    ##Odometry message read
    def Odom_read( self, odom_data ):
        ## Sets reference if first read, else calculates new position values, speed values, and actualizes.
        pose = odom_data.pose.pose #  the x,y,z pose and quaternion orientation
        if self.ref:
            self.zero = process(pose)
            self.ref = False
            self.timer.reset()

        else:
            self.pos = process(pose,self.zero)


if __name__ =='__main__':
    rospy.init_node("states")
    handler = States()
    rospy.spin()
