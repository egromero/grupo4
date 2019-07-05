import numpy as np
import matplotlib.pyplot as plt
from data_to_image import *
from particles import *
from collections import Counter
from parameters import *


not_wall = 10
too_many = 10


##open sample data
data = [] # file reader, wont matter later
with open(path+name+sufix) as file:
    for line in file:
        gen = map(float,line.rstrip(')\n').lstrip('(').split(','))
        data.append(list(gen))


sample = data[0][58:len(data[0])-56]

"""
# Filter by counting 20s
vector = np.array(sample)
a = len(np.where(vector == 20)[0])
if a >= too_many:
    print("No sirve")
else:
    print("Sirve")

"""

# Filter by comparing particles
vector = np.array(sample)
rolled_vector = np.roll(vector, 1)[1:]
rolled_vector = np.insert(rolled_vector, 0, 0)
total = np.abs(vector - rolled_vector)

a = len(np.where(total >= not_wall)[0])
if a >= too_many:
    print("No sirve")
else:
    print("Sirve")
