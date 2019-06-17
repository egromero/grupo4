import cv2
import math
from random import choice, random, randint
import numpy as np
# import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

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
    local = np.array([np.ndarray.tolist(fila[y:3+y].astype(np.float32)) for fila in g_map[x-1:2+x]], dtype = np.uint8)

    rows, cols = l_map.shape
    M = cv2.getRotationMatrix2D(((cols-1)/2.0, (rows-1)/2.0), angle, 1)
    l_map_rtd = cv2.warpAffine(l_map, M, (cols, rows))
    corr = cv2.matchTemplate(local, l_map_rtd, cv2.TM_CCOEFF_NORMED)
    corr = corr[0][0] if corr[0][0] >= 0.0 else 0.0

    print(local)
    print(l_map_rtd)

    return corr

def easy_particles(p=None):
    l = 10
    map = [[0 for i in range(l)] for i in range(l)]
    poses = []
    for i in range(l):
        for j in range(l):
            added = randint(0, 45)
            poses += [(i, j, O + added) for O in range(0, 360, 45)]

    if not p:
        poll = np.random.choice(len(poses), 70, p=[1/len(poses)]*len(poses))

        for n in poll:
            x, y, O = poses[n]
            map[x][y] = 1
        # print(np.array(map))
        return poses, list(dict.fromkeys(poll))

    else:
        poll = np.random.choice(len(p), 70, p=p)
        for n in poll:
            x, y = poses[n]
            map[x][y] = 1
        print(np.array(map))

# map_matching()
g_map = np.array( [ [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
                    [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
                    [0.5, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.5],
                    [0.5, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.5],
                    [0.5, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.5],
                    [0.5, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.5],
                    [0.5, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.5],
                    [0.5, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.5],
                    [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
                    [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]], dtype = np.uint8 )

l_map = np.array( [ [1.0, 1.0, 1.0],
                    [1.0, 0.0, 1.0],
                    [1.0, 0.0, 1.0]], dtype = np.uint8 )

# poses, p = easy_particles()
pto = (6, 5, 54)
print(map_matching(pto, g_map, l_map))
