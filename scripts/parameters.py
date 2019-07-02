import numpy as np
path = 'Measures/'
name = 'measures_0'
sufix = '.txt'


check_max = False

N = 300
n_angles = 12
sigma = 2
initial_pos = [150,150]
radio = 30 #initial radius (particle gen)
percent = 0.8
r = 50 #found oneself radius

offset = 120 ## reduces image to show, consider when observing new initial_pos
angles = [0,180]
window = 65 # add and substract to limits of angles.
valid = [angles[0]+window,angles[1]-window]
max_r = 2.5 # max distance, set by sensor
resolution = 0.02 # resolution of generated image, lower value (more res) = more time expensive
original_res = 0.12
ratio = original_res/resolution
magic_number = int(max_r/resolution)
offset = 90
multiplier = 10
gaussian_size = 5
gaussian_flag = True
nothing_value = 0.1
threshold = 0.001

rolled = 5

obstacle_distance = 0.45

rate = 60

ang_speed = 0.9
ang_acc = 0.25
ang_stop = 0.05
ang_thresh = 2/36*np.pi


lin_speed = 0.1
lin_acc = 0.08
lin_stop = 0.05

sigma_r = 0.1
sigma_ang = 0.1


