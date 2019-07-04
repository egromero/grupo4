#!/usr/bin/env python
import rospy
import numpy as np
from scipy import spatial
import matplotlib.pyplot as plt
import json

from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool,String
from data_to_image import *
from particles import *
from parameters import *


class Map():
    def __init__(self):
        self.data = None
        self.move_data = None

        self.new_data_flag = False
        self.take_data_flag = False
        self.on = False ##main program is running
        self.move_data_flag = False
        self.localized = False ## localized flag

        self.image_done_pub = rospy.Publisher('image_done',Bool,queue_size = 1)
        rospy.Subscriber('main_on',Bool,self.on_callback)
        self.move_allowed_pub = rospy.Publisher('move_allowed',Bool,queue_size=1)

        ## localized publisher
        self.localized_pub = rospy.Publisher('localized',Bool,queue_size=1)

        ## take new data sub, and move particle data sub
        rospy.Subscriber('/scan',LaserScan,self.scanner_data)
        rospy.Subscriber('image_take',Bool,self.take_data)
        rospy.Subscriber('state_change',String,self.move_particles)

        # Conect to Main
        self.initial_pub = rospy.Publisher('initial_pos',String,queue_size=10)
        rospy.Subscriber('ask_beginning',Bool,self.get_x_y)

        ## Process map and initial particles, and then send flag for initial movements
    	while (not self.on and not rospy.is_shutdown()):
    	    rospy.sleep(1)

        tic = time.time()
        self.global_map = image_preprocess()
        self.particles = original_particles_gen(N,n_angles,self.global_map,initial_pos)
        toc = time.time()-tic
        print('Time for image preprocessing + origin particles: ',toc)
        self.image_done_pub.publish(True)
        self.show_image()

        while not rospy.is_shutdown():
            while not self.new_data_flag:
                rospy.sleep(1)
            print('got data')
            cartesian_matrix = generate_cartesian_matrix(self.data)
            print('cartesian matrix complete')
            self.new_data_flag = False
            print('pre_imshow1')
            plt.figure()
            plt.imshow(cartesian_matrix)
            print('pre_weights')
            weights = get_weights(self.particles,cartesian_matrix,self.global_map,'ccoeff_norm')
            self.particles = redistribute(self.particles,weights)
            print('weighting and redistribution complete')
            self.image_done_pub.publish(True)
            if self.found_place(self.particles, r):
                self.show_image()
                print("Localizado en:", self.x_mean_loc, self.y_mean_loc)
                if not self.localized:
                    self.localized = True
                    self.localized_pub.publish(True)


            while not self.move_data_flag:
                rospy.sleep(1)

            self.particles = desplazar_particulas(self.particles,self.move_data[0],self.move_data[1]*360/(2*np.pi))

            self.move_data_flag = False

            self.show_image()
            self.move_allowed_pub.publish(True)

    def on_callback(self,data):
        self.on = True

    def found_place(self, particles, radio):
        length = float(len(self.particles))
        self.x_mean_loc = int(np.sum([(particle[0][1]-offset_pos)/length for particle in self.particles]))
        self.y_mean_loc = int(np.sum([(particle[0][0]-offset_pos)/length for particle in self.particles]))
        pos_mean = (self.y_mean_loc+offset_pos, self.x_mean_loc+offset_pos)
	coords = [cord for cord,angle in particles]
        tree = spatial.KDTree(coords)
        in_place = tree.query_ball_point(pos_mean, radio)
        angles = [particles[i] for i in in_place]
        std_dev = np.std(angles)

        if (len(in_place)/len(particles) >= percent) and std_dev<std_target:
            return True

    def get_x_y(self, data):
        self.x_mean_loc = int(np.sum([(particle[0][1])/length for particle in self.particles]))
        self.y_mean_loc = int(np.sum([(particle[0][0])/length for particle in self.particles]))
        angle_mean = np.sum([(particle[1])/len(self.particles) for particle in self.particles])
        pos_mean = (self.x_mean_loc, self.y_mean_loc, angle_mean)
        encoded = json.dumps(pos_mean)
        self.initial_pub.publish(encoded)

    def show_image(self):
        copy_n = np.copy(self.global_map)
	    #x_mean = 0
	    #y_mean = 0
	    #angle_mean = 0
	    #length = len(self.particles)
        for particle in self.particles:
            copy_n[particle[0][0],particle[0][1]] = 2
	    rows,cols = copy_n.shape
		#x_mean+= particle[0][0]/lenght
	    length = float(len(self.particles))
        x_mean = int(np.sum([(particle[0][1]-offset_pos)/length for particle in self.particles]))
        y_mean = int(np.sum([(particle[0][0]-offset_pos)/length for particle in self.particles]))
        angle_mean = np.sum([(particle[1])/len(self.particles) for particle in self.particles])

        plt.figure()
    	plt.imshow(copy_n[offset_pos:rows-offset_pos,offset_pos:rows-offset_pos])
        plt.arrow(x_mean,y_mean,np.cos(angle_mean/360*2*np.pi)*20,-np.sin(angle_mean/360*2*np.pi)*20,width = 0.3)
        plt.show()

    def take_data(self,data):
        self.take_data_flag = True

    def scanner_data(self, laserScan):
        if self.take_data_flag:
            self.data = laserScan.ranges
            self.new_data_flag = True
            self.take_data_flag = False
            self.image_done_pub.publish(True)

    def move_particles(self,data):
        self.move_data = json.loads(data.data)
	print('recieve data :'  ,self.move_data)
        self.move_data_flag = True



if __name__ == '__main__':
	rospy.init_node( "map_node" )
	handler = Map()
	rospy.spin()
