import timeit
from data_to_image import *

path = 'Measures/'
name = 'measures_2'
sufix = '.txt'
data = [] # file reader, wont matter later

with open(path+name+sufix) as file:
    for line in file:
        gen = map(float,line.rstrip(')\n').lstrip('(').split(','))
        data.append(list(gen))
sample = data[2]
map = image_preprocess()
sample_particle = [(250,250),30]
cartesian_matrix = generate_cartesian_matrix(sample)

def sub_function():
    alpha = rotate_and_center(cartesian_matrix,sample_particle[1])

print(timeit.timeit(sub_function,number=1000))
