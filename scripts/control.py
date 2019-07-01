#!/usr/bin/env python

import rospy
import numpy as np
import json
from util import pi_fix,Timer
from std_msgs.msg import Float64, String , Bool
from geometry_msgs.msg import Twist
from parameters import*



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
        rospy.Subscriber( '/'+directory+'/control_effort', Float64, self.response )




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
    speed_dict = {'linear':lin_speed,'angular':ang_speed}
    accel_dict = {'linear':lin_acc,'angular':ang_acc}
    stop_dict = {'linear':lin_stop,'angular':ang_stop}
    def __init__(self):

        ##Lista de objetivos y estado. Ahora es solo un x,y
        self.rate = rate
        self.target = [0,0,None]
        self.target_list=  []



        ##odom subs
        self.flag1 = False
        self.old_speed = [0,0]
        self.target_lin = 0; self.target_ang = 0;
        self.active = True
        ##booleans for applying speed
        self.angular_only = False


        ## linear and angular controllers
        print('creating controllers')
        self.lin_controller = Generic_Controller('lin_control')
        self.ang_controller = Generic_Controller('ang_control')



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


        ## shutdown subscriber
        rospy.Subscriber('control_enable',Bool,self.enable_callback)

	## data ready subscriber
        rospy.Subscriber('/lin_control/ready',Bool,self.controller_ready)
        rospy.Subscriber('/ang_control/ready',Bool,self.controller_ready)


        self.timer = Timer()
        self.timer.reset()

        ##Actuation
        while not rospy.is_shutdown():
            ## Move the robot
            if self.flag1:
                lin_value =  self.lin_controller.output.data; ang_value = self.ang_controller.output.data
                [lin_value,ang_value] = self.threshold(self.lin_controller.output.data,self.ang_controller.output.data)
                if self.angular_only:
                    lin_value = 0
                [lin_value,ang_value] = self.threshold(lin_value,ang_value)
            	self.move_cmd.linear.x = lin_value
            	self.move_cmd.angular.z = ang_value
		#print(ang_value)

		#print(lin_value)

                self.old_speed = [lin_value,ang_value]
                #self.writer.publish('Actuacion(lineal,angular) = {},{}'.format(lin_value,ang_value))
                self.mover.publish(self.move_cmd)
		self.flag1 = False


            ## Check if one should stop
	    if self.active:
            	f1 = (abs(self.target_lin)<self.stop_dict['linear'] and self.target[2]==None)
            	f2 =  (self.target[2]!=None and abs(self.target_ang)<self.stop_dict['angular'])
            	if (f1 or f2) and self.data_ready:
                    self.shutdown()
        	    self.target_reached_pub.publish(True)
            self.r.sleep()

    def shutdown(self,flag = False):
        self.lin_controller.enable(flag)
        self.ang_controller.enable(flag)
        self.flag1 = False
        self.active = flag
        rospy.sleep(0.2)

    def enable_callback(self,data):
        input = data.data
        self.shutdown(input)

    def controller_ready(self,input):
        self.flag1 = (self.lin_controller.ready and self.ang_controller.ready) or (self.ang_controller.ready and self.angular_only)


    ## Should be changed into a node with with a sub-callback function. For now just create an object of this class in main and use this method
    def new_target(self,data):
        self.shutdown()
        self.data_ready = False
        inc_list = json.loads(data.data)
        if len(inc_list)!= 3:
            raise IndexError('Length doesn\'t match')
        self.target = inc_list
        self.lin_controller.enable(True)
        self.ang_controller.enable(True)
        self.active = True
        print('got new target : ' ,self.target)



    ## actuacion subcsriber
    def threshold(self,lin_val,ang_val):
        lin_splimit = self.speed_dict['linear']
        lin_aclimit = self.accel_dict['linear']

        ang_splimit = self.speed_dict['angular']
        ang_aclimit = self.accel_dict['angular']

        old_lin_val = self.old_speed[0]
        old_ang_val = self.old_speed[1]
        time_delta = 1.0/self.rate
        ## get accel
        lin_accel = (lin_val - old_lin_val)/time_delta
        ang_accel = (ang_val - old_ang_val)/time_delta

        ## compare maximum acc with supposed acc
        lin_val = lin_val if abs(lin_accel)<lin_aclimit else old_lin_val+ np.sign(lin_accel)*lin_aclimit*time_delta
        ang_val = ang_val if abs(ang_accel)<ang_aclimit else old_ang_val+ np.sign(ang_accel)*ang_aclimit*time_delta


        ## Max velocity check
        lin_val = lin_val if abs(lin_val)<lin_splimit else lin_splimit*np.sign(lin_val)

        ang_val = ang_val if abs(ang_val)<ang_splimit else ang_splimit*np.sign(ang_val)

        return [lin_val,ang_val]


    ## odom subscriber callback
    def get_state(self, data ):
        inc_dict = json.loads(data.data)
        x = inc_dict['x']
        y = inc_dict['y']
        ang = inc_dict['ang_pos']
	#print(ang)



        if self.target[2]== None:
            self.target_lin = np.sqrt(np.power(self.target[0]-x,2) +np.power(self.target[1]-y,2))

                	## desired angle - actual angle
            self.target_ang = pi_fix(np.arctan2((self.target[1]-y),(self.target[0]-x))-ang)
        		#np.arctan2((self.target[1]-y),(self.target[0]-x))
        else:
            self.target_lin = 0
            self.target_ang = pi_fix(self.target[2]-ang)
	#print(self.target_ang)
        self.data_ready = True
        ## angular movement only boolean
        self.angular_only = True if (abs(self.target_ang)>0.25 or self.target[2]!=None) else False
        self.lin_controller.new_state(self.target_lin)
        self.ang_controller.new_state(self.target_ang)





if __name__ == '__main__':
	rospy.init_node( "controller" )
	handler = Control()
	rospy.spin()
