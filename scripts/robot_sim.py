import numpy as np
import matplotlib.pyplot as plt
from data_to_image import *
from particles import *
from collections import Counter
from parameters import *


fig = plt.figure()

##open sample data
data = [] # file reader, wont matter later
with open(path+name+sufix) as file:
    for line in file:
        gen = map(float,line.rstrip(')\n').lstrip('(').split(','))
        data.append(list(gen))

##preprocess image
tic = time.time()
global_map = image_preprocess()
plt.imshow(global_map)
plt.show(block=False)
particles = original_particles_gen(N,n_angles,global_map)
toc = time.time()-tic
print('Time for image preprocessing + origin particles: ',toc)
for i in range(10000000):
    print(i)
plt.show()

"""
## Muestra por 1 seg y luego sigue
plt.ion()
plt.show()

##open sample data
data = [] # file reader, wont matter later
with open(path+name+sufix) as file:
    for line in file:
        gen = map(float,line.rstrip(')\n').lstrip('(').split(','))
        data.append(list(gen))

##preprocess image
tic = time.time()
global_map = image_preprocess()
plt.imshow(global_map)
plt.pause(1)
# plt.show()
particles = original_particles_gen(N,n_angles,global_map)
toc = time.time()-tic
print('Time for image preprocessing + origin particles: ',toc)
"""
