import rospy
import numpy as np
from util import pi_fix,Timer
from std_msgs.msg import Float64



class Control():
    speed_dict = {'linear':0.3,'angular':0.7}
    accel_dict = {'linear':0.5,'angular':0.5}
    def __init__(self,type,ref):
        self.timer = Timer()
        rospy.Subscriber('our_state',dict,self.get_state)
        self.lin_speed = 0
        self.ang_speed = 0

        #hijos
        ## Son llamados en el callback de odom para que escupan las velocidades que el controlador dice. Falta aplicar threshold
        self.lin_controller = Lin_controller()
        self.ang_controller = Ang_controller()
        self.ref = [0,0,0]
    ## actuacion subcsriber

    def threshold(self):
        accel = (self.pre_speed-self.speed)/self.time

        self.speed = ALGO.

    ## odom subscriber callback
    def get_state(self, data ):

        x = data['x']
        y = data['y']
        ang = data['ang']

        ## Darle a los controladores el objetivo
        ## Objetivo = hacer alguna distancia 0.
        ## Recordatorio: Kp debe ser negativo
        self.lin_controller.run(target_lin)
        self.ang_controller.run(targen_ang)
