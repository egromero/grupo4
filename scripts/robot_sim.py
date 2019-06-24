import numpy as np
import matplotlib.pyplot as plt
from data_to_image import *
from particles import *
from collections import Counter

# before = "/Users/noemiisabocrosbyconget/Desktop/RoboticaMovil/grupo4/scripts/"
path = 'Measures/'
name = 'measures_27'
sufix = '.txt'



N = 800
n_angles = 12




##open sample data
data = [] # file reader, wont matter later
with open(path+name+sufix) as file:
    for line in file:
        gen = map(float,line.rstrip(')\n').lstrip('(').split(','))
        data.append(list(gen))

##preprocess image
tic = time.time()
global_map = image_preprocess()
particles = original_particles_gen(N,n_angles,global_map)
toc = time.time()-tic
print('Time for image preprocessing + origin particles: ',toc)



##generate cartesian matrix
# f,axes = plt.subplots(len(data))
print(len(data))
for i,sample in enumerate(data):
    tic = time.time()
    cartesian_matrix = generate_cartesian_matrix(sample)
    plt.imshow(cartesian_matrix)
    plt.show()
    weights = get_weights(particles,cartesian_matrix,global_map,'ccoeff_norm')
    # print(weights)
    particles = redistribute(particles,weights)
    particles = np.array([[coords,ang+60] for [coords,ang] in particles])
    copy_n = np.copy(global_map)
    for particle in particles:
        copy_n[particle[0][0],particle[0][1]] = 2



x_mean = np.sum([coords[1]/len(particles) for [coords,angle] in particles])
y_mean = np.sum([coords[0]/len(particles) for [coords,angle] in particles])
angle_mean = np.sum([(angle-360)/len(particles) for [coords,angle] in particles])
print(y_mean,x_mean,angle_mean)
plt.imshow(copy_n)
plt.arrow(x_mean,y_mean,np.cos(angle_mean/360*2*np.pi)*20,-np.sin(angle_mean/360*2*np.pi)*20,width = 3)
plt.show()
toc = time.time()-tic
print(Counter(particles))
print('Time for cartesian full matrix generation: ',toc)
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
