import numpy as np
path = 'Measures/'
name = 'measures_0'
sufix = '.txt'


N = 700
n_angles = 10
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

obstacle_distance = 0.45

rate = 60

ang_speed = 0.9
ang_acc = 0.25
ang_stop = 0.05
ang_thresh = 2/36*np.pi


lin_speed = 0.12
lin_acc = 0.08
lin_stop = 0.05

sigma_r = 0.06
sigma_ang = 0.0377


