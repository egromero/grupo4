#!/usr/bin/env python

import rospy
import numpy as np
import json
from util import pi_fix,Timer
from std_msgs.msg import Float64, String , Bool
from geometry_msgs.msg import Twist



class Generic_Controller():
    def __init__(self,directory):
        ## Si se usa 'error' como objetivo, el target siempre sera 0. Por ende no es necesario cambiar nunca el settpoint
        self.target = 0
        self.output = 0
        self.ready = False
        self.enabled = True

        ##init de controlador

    	## Setpoint publisher
        self.setpoint_pub = rospy.Publisher( '/'+directory+'/setpoint', Float64, queue_size = 1 )
        while self.setpoint_pub.get_num_connections() == 0 and not rospy.is_shutdown():
            rospy.sleep( 0.2 )


        ## Enable publisher (publishes to enable or disable controller)
        self.enable_pub = rospy.Publisher('/'+directory+'/pid_enable',Bool,queue_size=10)
        while self.enable_pub.get_num_connections() == 0 and not rospy.is_shutdown():
           rospy.sleep( 0.2 )

        ## Ready publisher (publishes to change a flag - interrupt like working instead of polling)
        self.ready_pub = rospy.Publisher('/'+directory+'/ready',Bool,queue_size=10)
        while self.enable_pub.get_num_connections() == 0 and not rospy.is_shutdown():
           rospy.sleep( 0.2 )


    	## publish current state to controller
        self.state_pub = rospy.Publisher( '/'+directory+'/state', Float64, queue_size = 10 )
        while self.state_pub.get_num_connections() == 0 and not rospy.is_shutdown():
            rospy.sleep( 0.2 )

    	## Creates subscriber that recieves output once ready
        self.output_sub = rospy.Subscriber( '/'+directory+'/control_effort', Float64, self.response )



        #Inicializacion de target = 0
        self.setpoint_pub.publish(0)

    ## input = Boolean
    def enable(self,input):
        self.enable_pub.publish(input)
        self.enabled = input

    ## input = newstate (numeric)
    def new_state(self,input):
        ##generico
        self.ready = False
        self.state_pub.publish(input)

    ## controller output is ready callback
    def response(self,data):
        self.output = data
        self.ready = True
        self.ready_pub.publish(True)


class Control():
    ## maximum values for threshold
    speed_dict = {'linear':0.3,'angular':0.7}
    accel_dict = {'linear':0.2,'angular':0.3}
    stop_dict = {'linear':0.04,'angular':0.1}
    def __init__(self):

        ##Lista de objetivos y estado. Ahora es solo un x,y
        self.rate = 60
        self.target = [0,0,None]
        self.done = False
        self.counter = 0


        ##odom subs
        self.flag1 = False
        self.old_speed = [0,0]

        ##booleans for applying speed
        self.angular_only = False
        self.new_info = False
        self.ready = False

        ## linear and angular controllers
        print('creating controllers')
        self.lin_controller = Generic_Controller('lin_control')
        self.ang_controller = Generic_Controller('ang_control')

        ## data ready subscriber
        rospy.Subscriber('/lin_control/ready',Bool,self.controller_ready)
        rospy.Subscriber('/ang_control/ready',Bool,self.controller_ready)

        ##Movement publisher and message
        print('Creating movement publisher')
        self.mover = rospy.Publisher( '/cmd_vel_mux/input/navi', Twist, queue_size=10 )
        self.move_cmd = Twist()
        self.r = rospy.Rate(self.rate)

	##Controller ready publisher and controller setpoint sub
        self.target_reached_pub = rospy.Publisher('target_reached',Bool,queue_size=10)
        rospy.sleep( 0.2 )

        self.writer = rospy.Publisher('write_permit',String,queue_size =10)
        rospy.sleep(0.2)

        rospy.Subscriber('new_target', String , self.new_target)
        rospy.sleep( 0.2 )

        rospy.Subscriber('our_state',String,self.get_state)
        rospy.sleep( 0.2 )


        self.timer = Timer()
        self.timer.reset()

        ##Actuation
        while not rospy.is_shutdown():

            if self.flag1:
                [lin_value,ang_value] = self.threshold(self.lin_controller.output.data,self.ang_controller.output.data)
                if self.angular_only:
		    #print(lin_value/((abs(0.17-abs(ang_value))/0.17+1)**3))
                    lin_value = 0
                    self.move_cmd.linear.x = lin_value
                    self.move_cmd.angular.z = ang_value
                else:

                    self.move_cmd.linear.x = lin_value
                    self.move_cmd.angular.z = ang_value
		#print(lin_value)
		#print(ang_value)
                self.old_speed = [lin_value,ang_value]
                #self.writer.publish('Actuacion(lineal,angular) = {},{}'.format(lin_value,ang_value))
                self.mover.publish(self.move_cmd)
                self.new_info = False
            else:
                pass
            self.r.sleep()


    def controller_ready(self,input):
        self.flag1 = self.lin_controller.ready and self.ang_controller.ready


    ## Should be changed into a node with with a sub-callback function. For now just create an object of this class in main and use this method
    def new_target(self,data):
        inc_list = json.loads(data.data)
        if len(inc_list)!= 3:
            raise IndexError('Length doesn\'t match')
        self.target = inc_list
        print(self.target)
	print(self.target)
        self.done = False

    ## actuacion subcsriber
    def threshold(self,lin_speed,ang_speed):
        lin_splimit = self.speed_dict['linear']
        lin_aclimit = self.accel_dict['linear']

        ang_splimit = self.speed_dict['angular']
        ang_aclimit = self.accel_dict['angular']

        old_lin_val = self.old_speed[0]
        old_ang_val = self.old_speed[1]

        ## get accel
        lin_accel = (lin_val - old_lin_val)/time_delta
        ang_accel = (ang_val - old_ang_val)/time_delta

        ## compare maximum acc with supposed acc
        lin_val = lin_speed if abs(lin_accel)<lin_aclimit else old_lin_val+ np.sign(lin_accel)*lin_aclimit*1/self.rate
        ang_val = ang_speed if abs(ang_accel)<ang_aclimit else old_ang_val+ np.sign(ang_accel)*ang_aclimit*1/self.rate


        ## Max velocity check
        lin_val = lin_speed if abs(lin_speed)<lin_splimit else lin_splimit*np.sign(lin_speed)

        ang_val = ang_speed if abs(ang_speed)<ang_splimit else ang_splimit*np.sign(ang_speed)

        return [lin_val,ang_val]


    ## odom subscriber callback
    def get_state(self, data ):
        inc_dict = json.loads(data.data)
        x = inc_dict['x']
        y = inc_dict['y']
        ang = inc_dict['ang_pos']

        ## euclidean distance
        if self.target[2]== None:
            target_lin = np.sqrt(np.power(self.target[0]-x,2) +np.power(self.target[1]-y,2))

                	## desired angle - actual angle
            target_ang = pi_fix(np.arctan2((self.target[1]-y),(self.target[0]-x))-ang)
        		#np.arctan2((self.target[1]-y),(self.target[0]-x))
        else:
            target_lin = 0
            target_ang = pi_fix(self.target[2]-ang)

        ## angular movement only boolean
        self.angular_only = True if (abs(target_ang)>0.17 or self.target[2]!=None) else False

        if self.angular_only and self.lin_controller.enabled:
            self.lin_controller.enable(False)
        elif not self.angular_only and not self.lin_controller.enabled:
            self.lin_controller.enable(True)
        self.lin_controller.new_state(target_lin)
        self.ang_controller.new_state(target_ang)
        ## send flag saying we got new parameters

        ## stop mechanic
	    #print('linear distance = {}. Angular distance = {}'.format(target_lin,target_ang))
        # print('linear value = {}. Angular value = {}'.format(self.old_lin_val,self.old_ang_val))
        if (abs(target_lin)<self.stop_dict['linear'] and self.target[2]==None) or (self.target[2]!=None and abs(target_ang)<self.stop_dict['angular']):
            self.done = True
            self.target_reached_pub.publish(True)
    	# self.counter+=1
if __name__ == '__main__':
	rospy.init_node( "controller" )
	handler = Control()
	rospy.spin()
