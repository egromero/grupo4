import numpy as np
import matplotlib.pyplot as plt
from random import uniform
import time
from data_to_image import image_preprocess,generate_cartesian_matrix,rotate_and_center,nothing_value
from corr_functions import *



def original_particles_gen(N,n_angles,image):
    angles = [360*i/n_angles for i in range(n_angles)]
    rows,cols = image.shape
    image_vector = image.reshape(1,rows*cols)
    binary_index = np.where(image_vector<nothing_value)[1]
    possible_locations = [(index//cols,index%cols) for index in binary_index]


    origin_particles = [(possible_locations[np.random.choice(len(possible_locations))],angle) for i in range(N) for angle in angles+np.random.rand(1)*360/n_angles]


    return np.array(origin_particles)

def get_weights(particles,cartesian_matrix,global_map,operation='ccoeff_norm'):
    check_max = True
    index = 0
    weights = np.zeros([len(particles)])
    if check_max:
        max = 0
    for i,particle in enumerate(particles):
        coord,angle = particle
        y,x = coord

        ## new matrix is what the robot 'sees' given an angle
        new_matrix, new_center = rotate_and_center(cartesian_matrix,angle)
        rows,cols = new_matrix.shape

        ## fake center reprecents the [0,0] of the window
        fake_center = (y-new_center[0],x-new_center[1])

        ##window is the matching part of global map to what the robot sees given an angle.
        window = global_map[fake_center[0]:fake_center[0]+rows,fake_center[1]:fake_center[1]+cols]
        ## correlation calculacion
        w = matrix_corr(window,new_matrix,operation)
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

    # return [weighted_choice(poses, p) for i in range(N)]
