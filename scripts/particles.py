import numpy as np
import matplotlib.pyplot as plt
from random import uniform
import time
from data_to_image import image_preprocess,generate_cartesian_matrix,rotate_and_center,nothing_value,threshold
from corr_functions import *
from parameters import *

check_max = False
possible_locations = None

def in_map(particle, map):
    coords, angle = particle
    if coords in map:
        return True


def original_particles_gen(N,n_angles,image):
    global possible_locations
    angles = [360*i/n_angles for i in range(n_angles)]
    rows,cols = image.shape
    image_vector = image.reshape(1,rows*cols)
    binary_index = np.where(image_vector<=nothing_value-threshold)[1]
    possible_locations = [(index//cols,index%cols) for index in binary_index]


    origin_particles = [(possible_locations[np.random.choice(len(possible_locations))],angle) for i in range(N) for angle in angles+np.random.rand(1)*360/n_angles]


    return np.array(origin_particles)

def get_weights(particles,cartesian_matrix,global_map,operation='ccoeff_norm'):
    index = 0
    weights = np.zeros([len(particles)])
    if check_max:
        max = 0
    for i,particle in enumerate(particles):
	if i%1000 == 0:
 	    print(i)
        coord,angle = particle
        y,x = coord

        if in_map(particle, possible_locations):
            ## new matrix is what the robot 'sees' given an angle
            new_matrix, new_center = rotate_and_center(cartesian_matrix,angle)
            rows,cols = new_matrix.shape

            ## fake center reprecents the [0,0] of the window
            fake_center = (y-new_center[0],x-new_center[1])

            ##window is the matching part of global map to what the robot sees given an angle.
            window = global_map[fake_center[0]:fake_center[0]+rows,fake_center[1]:fake_center[1]+cols]
            ## correlation calculacion
            w = matrix_corr(window,new_matrix,operation)
        else:
            w = 0

        weights[i] = w


        ## check favorite to see if correlation is working
        if check_max:
            if w>max:
                max = w
                favorite_window = window
                favorite_image = new_matrix
    weights = weights/np.sum(weights)
    ##Favorite plot
    if check_max:
        f,(ax1,ax2) = plt.subplots(1,2)
        ax1.imshow(favorite_window)
        ax2.imshow(favorite_image)
        plt.show()
    return weights

def weighted_choice(choices, weights):
    total = sum(w for w in weights)
    r = uniform(0, total)
    upto = 0
    for c in choices:
        w = weights[choices.index(c)]
        if upto + w >= r:
             return c
        upto += w

def redistribute(poses, p):
    # print(type(poses))
    pre = np.random.choice(len(poses),len(poses),p=p)
    type_list = np.array([type(item) for item in pre])
    for i,item in enumerate(type_list):
        if item!= np.int64:
            print(item)
    # print(np.where(type_list!=np.int64))
    # print(type(pre[0]))
    return poses[pre]

def desplazar_particulas(particles, mu_r,mu_ang):
    print('mu\'s = :', mu_r, mu_ang)
    print('sigma\'s = :', sigma_r*mu_r, sigma_ang*mu_ang )
    for particle in particles:
        ## radial movement`
        part_angle = particle[1]
        new_radius = np.random.normal(mu_r, sigma_r*mu_r + 0.01, 1)[0] / resolution
        x_var, y_var = int(new_radius*np.cos(part_angle)), int(-new_radius*np.sin(part_angle))


        ## angle movement`
        new_angle = np.random.normal(mu_ang, sigma_ang*mu_ang + np.pi/20, 1)[0]

        particle[0] = (particle[0][0] + x_var, particle[0][1] + y_var)
        particle[1] += new_angle
    return np.array(particles)



"""
##open sample data
data = [] # file reader, wont matter later
with open(path+name+sufix) as file:
    for line in file:
        gen = map(float,line.rstrip(')\n').lstrip('(').split(','))
        data.append(list(gen))
sample = data[2]

get_position(sample, 1)

# plt.figure()
# plt.imshow(cartesian_matrix)

## paint particle in global image
copy_n = np.copy(global_map)
for particle in particles:
    copy_n[particle[0][0],particle[0][1]] = 2

plt.imshow(copy_n)
plt.show()

f, axarr = plt.subplots(2,1)
axarr[0].imshow(copy_n)
axarr[1].imshow(copy_n)
plt.show()
"""
