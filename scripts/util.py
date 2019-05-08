    #!/usr/bin/env python

import numpy as np
import rospy

def pi_fix(angle_in):
    if angle_in<-np.pi:
        sub = angle_in+2*np.pi
    elif angle_in>np.pi:
        sub = angle_in-2*np.pi
    else:
        sub = angle_in
    return sub


class Timer():
    def __init__(self):
        self.ref = rospy.Time.now().to_sec()

    def reset(self):
        self.ref = rospy.Time.now().to_sec()

    def time(self):
        return rospy.Time.now().to_sec() - ref

# class Angle():
#     def __init__(self):
#         self._value = 0
#
#
#
#
#     def self.value():
#         doc = "The  property."
#         def fget(self):
#             return self._value
#         def fset(self, value):
#             self._value = value
#         def fdel(self):
#             del self
#         return locals()
#      = property(**())
