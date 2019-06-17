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

def map_matching():
    global_map = np.array( [ [1, 1, 1], [0, 0, 0], [0, 0, 0] ], dtype = np.uint8 )
    local_map = np.array( [ [0, 0, 1], [0, 0, 1], [0, 0, 1]], dtype = np.uint8 )
    for angle in [0, 90, 180, 270]:
        rows, cols = local_map.shape
        M = cv2.getRotationMatrix2D( ((cols-1)/2.0, (rows-1)/2.0), angle, 1 )
        local_map_rtd = cv2.warpAffine(local_map, M, (cols, rows))
        print(global_map)
        print(local_map_rtd)
        corr = cv2.matchTemplate(global_map, local_map_rtd, cv2.TM_CCOEFF_NORMED)
        # Si son =s corr=1, si son opuestos corr=-1
        print("correlation matrix: %s"%(corr[0][0]))
        print("----------------------------")

def dist_to_map():
    z_max, res = 20, 0.1
    dist = [20,  1.33, 0.2, 1.33, 20]
    d = {-np.pi/2: 0.5, -np.pi/3: 0.5, -np.pi/4: 0.5, -np.pi/5: 0.5,
         -np.pi/8: 0.5, 0: 0.5, np.pi/8: 0.5, np.pi/5: 0.5, np.pi/4: 0.5,
         np.pi/3: 0.5, np.pi/2: 0.5}
    map = [[0 for i in range(9)] for i in range(9)]
    center = (4, 0)
    map[-1][4] = 8

    for key in d.keys():
        if d[key] < 20:
            y_prim = int(d[key] * np.cos(key) / res)
            x_prim = int(d[key] * np.sin(key) / res)
            x = center[0] + x_prim
            y = center[1] + y_prim
            if x >= 0 and x < 9 and y >= 0 and y < 9:
                map[-y][x] = 1
                for i in range(y+1, 10):
                    map[-i][x] = 0.5
            # print("{}: x: {}, y: {}".format(key, x, y))
    print(np.array(map))

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

map_matching()
