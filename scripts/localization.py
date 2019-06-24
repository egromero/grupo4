#!/usr/bin/env python
import rospy
import json
import numpy as np
from std_msgs.msg import String, Bool
from sensor_msgs.msg import LaserScan

route = [[0,0,item] for item in np.arange(0,2*np.pi,np.pi/3)]

class Localizer():
    def __init__(self):
    	print('Initializing localizer')
        self.writer = rospy.Publisher('write_permit',String,queue_size =10)
    	rospy.sleep(0.2)

        self.target_publisher = rospy.Publisher('new_target',String,queue_size=10)
    	rospy.sleep( 0.2 )

    	self.new_data_flag = False
    	self.flag = True

    	rospy.Subscriber('target_reached',Bool,self.target_reached_callback)
    	rospy.sleep( 0.2 )

    	rospy.Subscriber('/scan', LaserScan, self.scanner_data)
   	rospy.sleep(0.2)


    	print('Init complete')
    	self.r = rospy.Rate(5)
    	for item in route:
    	    print(item)
    	    encoded = json.dumps(item)
    	    self.target_publisher.publish(encoded)
    	    print('Sent {}'.format(encoded))
    	    self.flag = False
    	    while not self.flag and not rospy.is_shutdown():
	    	self.r.sleep()
            self.new_data_flag = True
            while self.new_data_flag:
                rospy.sleep(0.01)

        self.writer.publish("END")
    	print('Done')


    def target_reached_callback(self,data):
	self.flag = data.data
		#print('incoming flag :',data.data)

    #scanner callback
    def scanner_data(self, laserScan):
        # Array de valores segun angulo de 90 a -90
        data = laserScan.ranges
        if self.new_data_flag:
            self.writer.publish(str(data))
            self.new_data_flag = False




if __name__ == '__main__':
	rospy.init_node( "turtlebot_g4" )
	handler = Localizer()
	rospy.spin()
