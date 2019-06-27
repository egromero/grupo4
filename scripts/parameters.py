import numpy as np
path = 'Measures/'
name = 'measures_0'
sufix = '.txt'


N = 800
n_angles = 12
sigma = 2


angles = [0,180]
window = 60 # add and substract to limits of angles.
valid = [angles[0]+window,angles[1]-window]
max = 2 # max distance, set by sensor
resolution = 0.02 # resolution of generated image, lower value (more res) = more time expensive
original_res = 0.1
ratio = original_res/resolution
magic_number = int(max/resolution)
offset = 90
multiplier = 10
gaussian_size = 5
gaussian_flag = True
nothing_value = 0.05
threshold = 0.001

rolled = 5

obstacle_distance = 0.5

rate = 60

ang_speed = 0.6
ang_acc = 0.25
ang_stop = 0.1
ang_thresh = 2/36*np.pi


lin_speed = 0.2
lin_acc = 0.08
lin_stop = 0.05
