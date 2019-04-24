def pi_fix(angle_in):
    if angle_in<-np.pi:
        sub = angle_in+2*np.pi
    elif angle_in>np.pi:
        sub = angle_in-2*np.pi
    else:
        sub = angle_in
    return sub

class Angle():
    def __init__(self):
        self._value = 0




    def self.value():
        doc = "The  property."
        def fget(self):
            return self._value
        def fset(self, value):
            self._value = value
        def fdel(self):
            del self
        return locals()
     = property(**())
