import numpy as np
import matplotlib.pyplot as plt
import time
from data_to_image import image_preprocess,generate_cartesian_matrix,rotate_and_center
from corr_functions import *

path = 'Measures/'
name = 'measures_3'
sufix = '.txt'


N=1000
n_angles = 1
angles = [360*i/n_angles for i in range(n_angles)]


def original_particle_gen(N,image):
    rows,cols = image.shape
    image_vector = image.reshape(1,rows*cols)
    binary_index = np.where(image_vector<=0.4)[1]
    possible_locations = [(index//cols,index%cols) for index in binary_index]


    origin_particles = [(possible_locations[np.random.choice(len(possible_locations))],np.random.choice(angles)) for i in range(N)]


    return origin_particles

def get_weights(particles,cartesian_matrix,global_map):
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
        w = matrix_corr(window,new_matrix,operation='corr_norm')
        weights[i] = w

    return weights
##open sample data
data = [] # file reader, wont matter later
with open (path+name+sufix) as file:
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
toc = time.time()-tic
print('Time for cartesian full matrix generation: ',toc)

## Compute origin particles
origin_particles = original_particle_gen(N,global_map)

## paint particle in global image
## note: should make a copy of global map for this
tic = time.time()
weights = get_weights(origin_particles,cartesian_matrix,global_map)
toc = time.time()-tic
print('Time for getting weight of all particles: ',toc)

for particles in origin_particles:
    global_map[particles[0][0],particles[0][1]] = 2


plt.imshow(global_map)
plt.show()
