import cv2
import math
from random import choice, random
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

def map_matching(g_map=None, l_map=None):
    p, local = [], []

    for i in range(8):
        for j in range(8):
            local.append([fila[j:3+j] for fila in g_map[i:3+i]])

    for angle in [0, 90, 180, 270]:
        rows, cols = l_map.shape
        M = cv2.getRotationMatrix2D(((cols-1)/2.0, (rows-1)/2.0), angle, 1)
        l_map_rtd = cv2.warpAffine(l_map, M, (cols, rows))
        corr = cv2.matchTemplate(g_map, l_map_rtd, cv2.TM_CCOEFF_NORMED)
        corr = corr[0][0] if corr[0][0] >= 0.0 else 0.0
        p.append(corr)

    return p

def easy_particles(p=None):
    l = 9
    map = [[0 for i in range(l)] for i in range(l)]
    poses = []
    for i in range(l):
        poses += [(i, j) for j in range(l)]

    if not p:
        # p = []
        poll = np.random.choice(len(poses), 70, p=[0.012345679]*len(poses))

        for n in poll:
            x, y = poses[n]
            map[x][y] = 1
        #     n = random()    # Alterar para probabilidad
        #     p.append(n)
        # print(p)
        print(np.array(map))
        # return p

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

# print(map_matching(g_map, l_map))
