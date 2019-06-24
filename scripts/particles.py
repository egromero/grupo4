import numpy as np
import matplotlib.pyplot as plt
from random import uniform
import time
from data_to_image import image_preprocess,generate_cartesian_matrix,rotate_and_center,nothing_value
from corr_functions import *

path = 'Measures/'
name = 'measures_3'
sufix = '.txt'


N = 800
n_angles = 12
angles = [360*i/n_angles for i in range(n_angles)]
mu_ang, sigma_ang = 360*2/n_angles, 0.1


def original_particle_gen(N,image):
    rows,cols = image.shape
    image_vector = image.reshape(1,rows*cols)
    binary_index = np.where(image_vector<nothing_value)[1]
    possible_locations = [(index//cols,index%cols) for index in binary_index]


    origin_particles = [(possible_locations[np.random.choice(len(possible_locations))],angle) for i in range(N) for angle in angles+np.random.rand(1)*360/n_angles]


    return origin_particles

def get_weights(particles,cartesian_matrix,global_map,operation):
    index = 0
    weights = np.zeros([len(particles)])
    # max = 0
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
        # if w>max:
        #     max = w
        #     favorite_window = window
        #     favorite_image = new_matrix
    ##Favorite plot
    # f,(ax1,ax2) = plt.subplots(1,2)
    # ax1.imshow(favorite_window)
    # ax2.imshow(favorite_image)
    # plt.show()
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
    # print(type(pre[0]))
    return poses[pre]

    # return [weighted_choice(poses, p) for i in range(N)]

def desplazar_particulas(particles, mu, sigma):
    for particle in particles: # particle = [(x, y), angle]
        new_angle = np.random.normal(mu, sigma, 1)[0]
        r = np.random.normal(0, 0.1, 1)[0]
        x_var, y_var = r*np.cos(new_angle), r*np.sin(new_angle)

        particle[0][0] += x_var
        particle[0][1] += y_var
        particle[1] += new_angle
    return particles

def get_position(sample, N):
    # get local map
    tic = time.time()
    cartesian_matrix = generate_cartesian_matrix(sample)
    toc = time.time()-tic
    print('Time for cartesian full matrix generation: ', toc)

    # get global map
    tic = time.time()
    global_map = image_preprocess()
    toc = time.time()-tic
    print('Time for image preprocessing: ', toc)

    # get original particles
    particles = np.array(original_particle_gen(N, global_map))

    # get weights
    tic = time.time()
    weights = get_weights(particles, cartesian_matrix, global_map, 'ccoeff_norm')
    weights = weights/np.sum(weights)
    toc = time.time()-tic
    print('Time for getting weight of all particles: ', toc)

    # redistribute particles
    tic = time.time()
    particles = redistribute(particles, weights)
    toc = time.time()-tic
    print('Time for getting new distribution of all particles: ', toc)

    # move bot and particles
    particles = desplazar_particulas(particles, mu_ang, sigma_ang)

    return


"""
##open sample data
data = [] # file reader, wont matter later
with open(path+name+sufix) as file:
    for line in file:
        gen = map(float,line.rstrip(')\n').lstrip('(').split(','))
        data.append(list(gen))
sample = data[2]

##preprocess image
tic = time.time()
global_map = image_preprocess()
toc = time.time()-tic
print('Time for image preprocessing: ',toc)


##generate cartesian matrix
tic = time.time()
cartesian_matrix = generate_cartesian_matrix(sample)
# plt.figure()
# plt.imshow(cartesian_matrix)

toc = time.time()-tic
print('Time for cartesian full matrix generation: ',toc)

## Compute origin particles
particles = np.array(original_particle_gen(N,global_map))
# print(particles[0])

## paint particle in global image
for i in range(1):
    tic = time.time()
    weights = get_weights(particles, cartesian_matrix, global_map,'ccoeff_norm')
    weights = weights/np.sum(weights)
    toc = time.time()-tic
    print('Time for getting weight of all particles: ',toc)

    tic = time.time()
    particles = redistribute(particles, weights)
    toc = time.time()-tic
    print('Time for getting new distribution of all particles: ',toc)

    copy_n = np.copy(global_map) # make a copy of global map for this
    for particle in particles:
        copy_n[particle[0][0],particle[0][1]] = 2

plt.imshow(copy_n)
plt.show()
"""
