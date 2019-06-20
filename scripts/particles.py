import numpy as np
import matplotlib.pyplot as plt
from random import uniform
import time
from data_to_image import image_preprocess,generate_cartesian_matrix,rotate_and_center
from corr_functions import *

# before = "/Users/noemiisabocrosbyconget/Desktop/RoboticaMovil/grupo4/scripts/"
path = 'Measures/'
name = 'measures_2'
sufix = '.txt'


N = 2000
n_angles = 16
angles = [360*i/n_angles for i in range(n_angles)]


def original_particle_gen(N,image):
    rows,cols = image.shape
    image_vector = image.reshape(1,rows*cols)
    binary_index = np.where(image_vector<=0.4)[1]
    possible_locations = [(index//cols,index%cols) for index in binary_index]


    origin_particles = [(possible_locations[np.random.choice(len(possible_locations))],angle) for i in range(N) for angle in angles+np.random.rand(1)*360/n_angles]


    return origin_particles

def get_weights(particles,cartesian_matrix,global_map,operation):
    max = 0
    index = 0
    weights = np.zeros([len(particles)])
    for i,particle in enumerate(particles):
        coord,angle = particle
        y,x = coord

        ## new matrix is what the robot 'sees' given an angle
        new_matrix, new_center = rotate_and_center(cartesian_matrix,angle)
        rows,cols = new_matrix.shape

        ## fake center reprecents the [0,0] of the window
        fake_center = (particle[0]-new_center[0],particle[1]-new_center[1])[0]

        ##window is the matching part of global map to what the robot sees given an angle.
        window = global_map[fake_center[0]:fake_center[0]+rows,fake_center[1]:fake_center[1]+cols]

        #w for weight
        print(fake_center)
        print(rows,cols)
        print(window.shape)
        w = matrix_corr(window,new_matrix,operation)
        weights[i] = w

        f,(ax1,ax2) = plt.subplots(1,2)
        ax1.imshow(window)
        ax2.imshow(new_matrix)
        plt.show()

        if w>max:
            print(w,max)
            max = w
            favorite_image1 = window
            favorite_image2 = new_matrix

    print(max,np.sum(weights)/len(weights))
    f,(ax1,ax2) = plt.subplots(1,2)
    ax1.imshow(window)
    ax2.imshow(new_matrix)
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
    pre =    np.random.choice(len(poses),len(poses),p=p)
    # print(type(pre[0]))
    return poses[pre]

    # return [weighted_choice(poses, p) for i in range(N)]

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
print(particles[0])

## paint particle in global image
## note: should make a copy of global map for this
for i in range(5):
    tic = time.time()
    weights = get_weights(particles, cartesian_matrix, global_map,'ccoeff_norm')
    weights = weights/np.sum(weights)
    toc = time.time()-tic
    print('Time for getting weight of all particles: ',toc)

    tic = time.time()
    particles = redistribute(particles, weights)
    toc = time.time()-tic
    print('Time for getting new distribution of all particles: ',toc)
    copy_n = np.copy(global_map)
    for particle in particles:
        copy_n[particle[0][0],particle[0][1]] = 2

    # plt.imshow(copy_n)
    # plt.show()
