import rospy
import numpy as np
import time as tm
from Constans import * 

def pi_fix(angle_in):
    if angle_in < -np.pi:
        sub = angle_in + 2*np.pi
    elif angle_in > np.pi:
        sub = angle_in - 2*np.pi
    else:
        sub = angle_in
    return sub

class PlanRuta():

    def __init__(self, nueva, original, ang):
        self.new = nueva
        self.original = original
        self.ang = ang
        self.obstacle = None

    def plan(self):
        if abs((self.new[0]-self.original[0]))<0.00000000001:
            dif = 0.000000000001
        else:
            dif = self.new[0]-self.original[0]

        ##  Absolute angle of target
        aim_angle = np.arctan((self.new[1]-self.original[1])/dif)

        if dif < 0:
            aim_angle = pi_fix(aim_angle + np.pi)

        ## Relative angle of target
        delta_angle = pi_fix(aim_angle - self.ang)

        ## Distance between target and acutal self.newition
        module =  np.sqrt(np.power((self.new[1]-self.original[1]),2) + np.power((self.new[0]-self.original[0]),2))

        ## Set values with corresponding sign

        angular_speed = 0.8 if delta_angle > 0 else -0.8
        real_speed = 0.34 if delta_angle > 0 else -0.34
        delta_pos = 0.26 if delta_angle > 0 else -0.26
        linear = [0,0.2]
        angular = [angular_speed,0]

        ## the 0.8 and 0.26 values are a kind of a fix.
        angular_time = (delta_angle-delta_pos)/real_speed + 0.8 if (abs(delta_angle)>0.26) else 0.00000001

        time = [angular_time, module/(0.2*coef) + 0.000001]
        return linear,angular,time
    
    def aplicar_velocidad(self, vel_lineal, vel_angular, time):
        vel_lineal, vel_angular, time = iter(vel_lineal), iter(vel_angular), iter(time)
        current_action = (next(vel_lineal, None), next(vel_angular, None), next(time, None))

        while current_action[2]:
            lapsed_time = 0
            while (lapsed_time < current_action[2]+0.2) and not rospy.is_shutdown():
                past_time = rospy.Time.now().to_sec()

                if not self.obstacle:
                    # Movimiento abrupto
                    # self.move(current_action[0], current_action[1])
                    delta = rospy.Time.now().to_sec() - past_time
                    lapsed_time += delta
                else:
                    # Freno abrupto
                    # self.move(0,0)
                    tm.sleep(0.2)
                    #past_time = rospy.Time.now().to_sec()

        current_action = (next(vel_lineal, None), next(vel_angular,None), next(time, None))

        # self.move(0,0)