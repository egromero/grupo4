import numpy as np
map_name = "map.pgm"

places_to_be = [(), ()] # Psocion del cafe y de la oficina

pkg_name = 'g4p'
playfile = 'ff_fanfare2.wav'

## used by data_to_image
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

# used by particle weighting for debugging
check_max = False

## Used for initial map generation
N = 600
n_angles = 10
sigma = 2


in_pos = [4,4]
offset_pos = 120 # reduces image to show, consider when observing new initial_pos
pixel_offset = 1 # in case original map has pixel borders
initial_pos = [(in_pos[0]+pixel_offset)*ratio+magic_number,(in_pos[1]+pixel_offset)*ratio+magic_number]
radio = 35 #initial radius (particle gen)
percent = 0.8
std_target = 20
r = 20 #found oneself radius




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
