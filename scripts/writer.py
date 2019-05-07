#!/usr/bin/env python

import rospy
from std_msgs.msg import String
file_counter = 'number.txt'
file_start = 'measures'

## Publisher
# self.write_pub = rosy.publisher('write_permit',String)

class Writer():
    def __init__(self):
        try:
            open(file_counter) as fl:
                file_number = int(fl.readline().rstrip('\n'))
            open(file_counter,'w') as fl:
                fl.write(str(file_number+1))
        except FileNotFoundError:
            file_number = 0
            open(file_counter,'w') as fl:
                fl.write(str(file_number+1))
        self.filename = file_start + '_' + filenumber + '.txt'
        ## create file
        with open(self.filename,'w') as fl:
            pass
        rospy.subcsriber('write_permit',String,self.write_callback)

    def write_callback(self,data):
        with open(self.filename,'a') as fl:
            fl.write(data)
