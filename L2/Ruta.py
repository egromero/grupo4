import rospy
import numpy as np
import time as tm
from Constans import coef, delta_lin, delta_ang

def pi_fix(angle_in):
    if angle_in < -np.pi:
        sub = angle_in + 2*np.pi
    elif angle_in > np.pi:
        sub = angle_in - 2*np.pi
    else:
        sub = angle_in
    return sub

class PlanRuta():

    def __init__(self, movement, nueva, original, ang):
        self.new = nueva
        self.original = original
        self.ang = ang
        self.movement = movement

    def aplicar_velocidad(self, vel_lineal, vel_angular, time):
        vel_lineal, vel_angular, time = iter(vel_lineal), iter(vel_angular), iter(time)
        current_action = (next(vel_lineal, None), next(vel_angular,None), next(time, None))
        
        while current_action[2]:
            lapsed_time = 0
            lineal, angular = 0, 0
            
            # Durante el tiempo de accion current_action[2]
            while (lapsed_time < current_action[2]+0.2) and not rospy.is_shutdown():
                past_time = rospy.Time.now().to_sec()
                
                if not self.movement.obstacle:
                    delta = delta_ang if current_action[0] == 0 else delta_lin
                    v = current_action[1] if current_action[0] == 0 else current_action[0]
                    delta_time = v/delta

                    if lapsed_time >= (current_action[2] - delta_time):
                        lineal -= 0 if current_action[0] == 0 else delta
                        angular -= 0 if current_action[1] == 0 else delta
                    elif lapsed_time <= delta_time:
                        lineal += 0 if current_action[0] == 0 else delta
                        angular += 0 if current_action[1] == 0 else delta
                    else:
                        lineal, angular = current_action[0], current_action[1]

                    # Mover turtlebot
                    self.movement.move(lineal, angular)

                    # Avanzar tiempo
                    delta = rospy.Time.now().to_sec() - past_time
                    lapsed_time += delta
                
                else: # Frenar por obstaculo
                    self.movement.move(0,0)
                    tm.sleep(0.2)
            
            # Get next action
            current_action = (next(vel_lineal, None), next(vel_angular,None), next(time, None))

        self.movement.move(0,0)
