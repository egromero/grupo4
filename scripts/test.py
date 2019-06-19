import cv2
import math
from random import random, randint, uniform
import numpy as np
# import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Constantes
N_PARTICULAS = 50
IMAGE_X, IMAGE_Y = 2, 2
ANGULO = 45

def weighted_choice(choices, weights):
    total = sum(w for w in weights)
    r = uniform(0, total)
    upto = 0
    for c in choices:
        w = weights[choices.index(c)]
        if upto + w >= r:
             return c
        upto += w

def gaussian(x, mean, std_dev):
    a = (1/(np.sqrt(2*np.pi*std_dev**2)))
    return a * np.exp( -(x-mean)**2 / (2 * std_dev**2) )

def ajuste_funcion():
    data_x = np.linspace(-10, 10, 101)
    data_y = gaussian(data_x, 0, 10)
    init_vals = [0, 1]
    best_vals, covar = curve_fit(gaussian, data_x, data_y, p0 = init_vals)
    # best_vals: valores optimos para calsar con parametros
    # covar: covarianza
    print("best values: (mean, std_dev) = %s"%(best_vals))

def map_matching(pos=None, g_map=None, l_map=None):
    x, y, angle = pos

    mini = np.array([fila[x-IMAGE_X:x+IMAGE_X+1] for fila in g_map[y-IMAGE_Y:y+IMAGE_Y+1]])
    mini_row, mini_cols = mini.shape
    mini_M = cv2.getRotationMatrix2D(((mini_cols-1)/2.0, (mini_row-1)/2), angle, 1)
    mini_rtd = cv2.warpAffine(mini, mini_M, (mini_cols, mini_row))
    local = np.array([fila[IMAGE_X//2:IMAGE_X+IMAGE_X//2] for fila in mini_rtd[:IMAGE_Y+1]], dtype = np.float32)

    corr = cv2.matchTemplate(local, l_map, cv2.TM_CCOEFF_NORMED)
    corr = corr[0][0] if corr[0][0] >= 0.0 else 0.0
    return corr

def easy_particles(g_map, poses=None, p=None):
    l = 10
    map = [[0 for i in range(l)] for i in range(l)]

    if not poses:
        poses = []
        for i in range(l):
            for j in range(l):
                if g_map[j][i] == 0.0:
                    added = randint(0, ANGULO)
                    poses += [(i, j, O + added) for O in range(0, 360, ANGULO)]

    p = [1/len(poses)]*len(poses) if not p else p
    poll = [weighted_choice(poses, p) for i in range(N_PARTICULAS)]
    return poll

g_map = np.array( [ [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
                    [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
                    [0.5, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.5],
                    [0.5, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.5],
                    [0.5, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.5],
                    [0.5, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.5],
                    [0.5, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.5],
                    [0.5, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.5],
                    [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
                    [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]], dtype = np.float32 )

l_map = np.array( [ [1.0, 1.0, 1.0],
                    [0.0, 0.0, 1.0],
                    [0.0, 0.0, 1.0]], dtype = np.float32 )

poses = easy_particles(g_map)
new_p = []
for pose in poses:
    new_p.append(map_matching(pose, g_map, l_map))
poses = easy_particles(g_map, poses, new_p)
print(np.sum(new_p))
