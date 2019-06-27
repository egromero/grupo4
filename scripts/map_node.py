#!/usr/bin/env python
import rospy
import numpy as np
import matplotlib.pyplot as plt
import json

from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool,String
from data_to_image import *
from particles import *



class Map():
    def __init__(self):
        self.f, (self.ax1,self.ax2) = plt.subplots(2)
        self.data = None
        self.new_data_flag = False
        self.take_data_flag = False
	self.on = False
        self.move_data_flag = False
        self.image_done_pub = rospy.Publisher('image_done',Bool,queue_size = 1)
	rospy.Subscriber('main_on',Bool,self.on_callback)
        self.move_allowed_pub = rospy.Publisher('move_allowed',Bool,queue_size=1)

        ## Process map and initial particles, and then send flag for initial movements
	while (not self.on and not rospy.is_shutdown()):
	    rospy.sleep(1)
        tic = time.time()
        self.global_map = image_preprocess()
        self.particles = original_particles_gen(N,n_angles,self.global_map)
        toc = time.time()-tic
        print('Time for image preprocessing + origin particles: ',toc)
        self.image_done_pub.publish(True)

        ## take new data sub, and move particle data sub
        rospy.Subscriber('/scan',LaserScan,self.scanner_data)
        rospy.Subscriber('image_take',Bool,self.take_data)
        rospy.Subscriber('state_change',String,self.move_particles)

        while not rospy.is_shutdown():
            while not self.new_data_flag:
                rospy.sleep(1)

            cartesian_matrix = generate_cartesian_matrix(self.data)
	    print('cartesian matrix complete')
            self.new_data_flag = False
            self.ax1.imshow(cartesian_matrix)
            weights = get_weights(self.particles,cartesian_matrix,self.global_map,'ccoeff_norm')
            self.particles = redistribute(self.particles,weights)
	    print('weighting and redistribution complete')
            self.image_done_pub.publish(True)

            while not self.move_data_flag:
                rospy.sleep(1)

            self.particles = desplazar_particulas(self.particles,self.data[0],self.data[1])
            self.move_data_flag = False

            self.show_image()
	    self.move_allowed_pub.publish(True)
    def on_callback(self,data):
	self.on = True


    def show_image(self):
            copy_n = np.copy(self.global_map)
	    #x_mean = 0
	    #y_mean = 0
	    #angle_mean = 0
	    #length = len(self.particles)
            for particle in self.particles:
                copy_n[particle[0][0],particle[0][1]] = 2
		#x_mean+= particle[0][0]/lenght
	    length = float(len(self.particles))
            x_mean = int(np.sum([particle[0][0]/length for particle in self.particles]))
            y_mean = int(np.sum([particle[0][1]/length for particle in self.particles]))
            angle_mean = np.sum([(particle[1]-360)/len(self.particles) for particle in self.particles])
	    print(x_mean,y_mean,angle_mean)
            self.ax2.imshow(copy_n)
            plt.arrow(x_mean,y_mean,np.cos(angle_mean/360*2*np.pi)*20,-np.sin(angle_mean/360*2*np.pi)*20,width = 0.3)
            plt.show()

    def take_data(self,data):
        self.take_data_flag = True

    def scanner_data(self, laserScan):
        if self.take_data_flag:
            self.data = laserScan.ranges
            self.new_data_flag = True
            self.take_data_flag = False

    def move_particles(self,data):
        self.data = json.loads(data.data)
        self.move_data_flag = True



if __name__ == '__main__':
	rospy.init_node( "map_node" )
	handler = Map()
	rospy.spin()

#
# ## Compute origin particles
# particles = np.array(original_particle_gen(N,global_map))
# # print(particles[0])
#
# ## paint particle in global image
# ## note: should make a copy of global map for this
# for i in range(10):
#     tic = time.time()
#     weights = get_weights(particles, cartesian_matrix, global_map,'ccoeff_norm')
#     weights = weights/np.sum(weights)
#     toc = time.time()-tic
#     print('Time for getting weight of all particles: ',toc)
#
#     tic = time.time()
#     particles = redistribute(particles, weights)
#     toc = time.time()-tic
#     print('Time for getting new distribution of all particles: ',toc)
#
#
#
