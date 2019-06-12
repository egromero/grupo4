#!/usr/bin/env python

import rospy
from std_msgs.msg import String


## Publisher
self.write_pub = rospy.Publisher('write_permit',String)

global_dir = '/home/group4/catkin_ws/src/grupo4/scripts/'
file_counter = global_dir + 'number.txt'
file_start = global_dir +'Measures/measures'

class Writer():
    def __init__(self):
        self.file_number = 0

        try:
            with open(file_counter) as fl:
                medium = fl.readline().rstrip('\n')
                print(medium)
		self.file_number = int(medium)
            with open(file_counter,'w') as fl:
                fl.write(str(self.file_number+1))
        except IOError:
            self.file_number = 0
            with open(file_counter,'w') as fl:
                fl.write(str(self.file_number+1))
        self.filename = file_start + '_' + str(self.file_number) + '.txt'
        ## create file
        self.file = open(self.filename,'w')
        rospy.Subscriber('write_permit',String,self.write_callback)

    def write_callback(self,data):
        if data.data == 'END':
            self.file.close()
        else:
            self.file.write(data.data + '\n')

if __name__ =='__main__':
    rospy.init_node("writer")
    handler = Writer()
    rospy.spin()
