#! /usr/bin/env python

import rospy
import numpy as np
from util import pi_fix,Timer
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist


class Generic_Controller():
    def __init__(self,directory):
        ## Si se usa 'error' como objetivo, el target siempre sera 0. Por ende no es necesario cambiar nunca el settpoint
        self.target = 0
        self.output = 0
        ##init de controlador
        self.setpoint_pub = rospy.Publisher( '/'+directory+'/setpoint', Float64, queue_size = 1 )
        while self.setpoint_pub.get_num_connections() == 0 and not rospy.is_shutdown():
            rospy.sleep( 0.2 )

        self.state_pub = rospy.Publisher( '/'+directory+'/state', Float64, queue_size = 1 )
        while self.state_pub.get_num_connections() == 0 and not rospy.is_shutdown():
            rospy.sleep( 0.2 )

        self.output_sub = rospy.Subscriber( '/'+directory+'/control_effort', Float64, self.response )

        ##Movement publisher

        #Inicializacion de target = 0
        self.setpoint_pub.publish(0)

    def new_state(self,input):
        ##generico
        self.ready = False
        self.state_pub.publish(input)

    def response(self,data):
        self.output = data
        self.ready = True


class Control():
    speed_dict = {'linear':0.3,'angular':0.7}
    accel_dict = {'linear':0.5,'angular':0.5}
    def __init__(self,type,ref):

        ##Lista de objetivos y estado. Ahora es solo un x,y
        self.target = [0,0]

        self.timer = Timer()
        ##odom subs
        rospy.Subscriber('our_state',dict,self.get_state)
        self.old_lin_val = 0
        self.old_ang_val = 0

        ##booleans for applying speed
        self.new_info = False
        self.ready = False
        #hijos
        ## Son llamados en el callback de odom para que escupan las velocidades que el controlador dice. Falta aplicar threshold
        self.lin_controller = Generic_Controller('lin_control')
        self.ang_controller = Generic_Controller('ang_control')

        ##Movement publisher and message
        self.mover = rospy.Publisher( '/cmd_vel_mux/input/navi', Twist, queue_size=10 )
        self.move_cmd = Twist()

        ##Actuation
        while True:
            self.ready = (lin_controller.ready and ang_controller.ready) and self.new_info

            if self.ready:
                [lin_value,ang_value] = threshold(lin_controller.output,ang_controller.output)

                if self.angular_only:
                    self.move_cmd.linear.x = 0
                    self.move_cmd.angular.z = ang_value
                else:
                    self.move_cmd.linear.x = lin_value
                    self.move_cmd.angular.z = ang_value
                self.mover.publish(self.move_cmd)

                self.ready = False
                self.new_info = False

    ## actuacion subcsriber
    def threshold(self,lin_speed,ang_speed):
        time_delta = self.timer.time()
        self.timer.reset()

        lin_splimit = self.speed_dict['linear']
        lin_aclimit = self.accel_dict['linear']

        ang_splimit = self.speed_dict['angular']
        ang_aclimit = self.accel_dict['angular']

        old_lin_val = self.old_lin_val
        old_ang_val = self.old_ang_val

        ## Max velocity check
        lin_val = lin_speed if abs(lin_speed)<lin_splimit else
        lin_splimit*np.sign(lin_speed)

        ang_val = ang_speed if abs(ang_speed)<ang_splimit else
        ang_splimit*np.sign(ang_speed)


        ## Max accel check
        lin_val = lin_val if abs(lin_val - old_lin_val)/time_delta< lin_aclimit else old_lin_val + np.sign(lin_val)*lin_aclimit*time_delta

        ang_val = ang_val if abs(ang_val - old_ang_val)/time_delta< ang_aclimit else old_ang_val + np.sign(ang_val)*ang_aclimit*time_delta

        self.old_lin_val = lin_val
        self.old_ang_val = ang_val

        return [lin_val,ang_val]


    ## odom subscriber callback
    def get_state(self, data ):
        x = data['x']
        y = data['y']
        ang = data['ang']
        ## Darle a los controladores el objetivo
        ## Objetivo = hacer alguna distancia 0.
        ## Recordatorio: Kp debe ser negativo

        ## euclidean distance
        target_lin = np.sqrt(np.power(self.target[0]-x,2) +np.power(self.target[1]-y,2)

        ## desired angle - actual angle
        target_ang = pi_fix(np.arctan2((self.target[1]-y)/(self.targer[0]-x)) - ang)

        ## angular movement only boolean
            self.angular_only = True if abs(target_ang)>0.17 else False

        self.lin_controller.new_state(target_lin)
        self.ang_controller.new_state(targen_ang)
        ## send flag saying we got new parameters
        self.new_info = True