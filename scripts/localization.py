import rospy
import json
import numpy as np



route = [(0,0,angle) for angle in np.arange(0,2*np.pi,np.pi/3)]

class Localizer():
    def __init__(self):
        self.writer = rospy.Publisher('write_permit',String,queue_size =10)
        rospy.sleep(0.2)

        self.target_publisher = rospy.Publisher('new_target',String,queue_size=10)
		rospy.sleep( 0.2 )

		rospy.Subscriber('target_reached',Bool,self.target_reached_callback)
		rospy.sleep( 0.2 )

        self.scanner_data = 0
        rospy.Subscriber('/scan', LaserScan, self.scanner_data)
        rospy.sleep(0.2)

		self.flag = True
		self.r = rospy.Rate(5)
		for item in route:
            self.new_data_flag = True
            while self.new_data_flag:
                pass
			encoded = json.dumps(item)
			self.target_publisher.publish(encoded)
			print('Sent {}'.format(encoded))
			self.flag = False
			while not self.flag and not rospy.is_shutdown():
				#print('Actual flag' ,self.flag)
				self.r.sleep()
        self.write_pub.publish("END")
	def target_reached_callback(self,data):
		self.flag = data.data
		#print('incoming flag :',data.data)

    #scanner callback
    def scanner_data(self, laserScan):
        # Array de valores segun angulo de 90 a -90
        if self.new_data_flag:
            data = laserScan.ranges
            self.write_pub.publish(str(data))
            self.new_data_flag = False




if __name__ == '__main__':
	rospy.init_node( "turtlebot_g4" )
	handler = Turtlebot()
	rospy.spin()
