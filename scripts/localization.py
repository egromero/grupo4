import rospy
import json



class Localizer():
    def __init__(self):
        self.scanner_data = 0
        rospy.Subscriber('/scan', LaserScan, self.scanner_data)


    #scanner callback
    def scanner_data(self, laserScan):
        # Array de valores segun angulo de 90 a -90
        if self.new_data_flag:
            self.scanner_data = laserScan.ranges
            self.new_data_flag = False




		# while self.write < 10:
		# 	print(data)
		# 	self.write_pub.publish(str(data))
		# 	self.write += 1
		# self.write_pub.publish("END")
