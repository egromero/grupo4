import cv2
import math
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
        M = cv2.getRotationMatrix2D( (cols/2, rows/2), angle, 1 )
        local_map_rtd = cv2.warpAffine(local_map, M, (cols, rows))
        print(global_map)
        print(local_map_rtd)
        corr = cv2.matchTemplate(global_map, local_map_rtd, cv2.TM_CCOEFF_NORMED)
        # Si son =s corr=1, si son opuestos corr=-1
        print("correlation matrix: %s"%(corr))
        print("----------------------------")

z_max, res = 20, 0.1
def dist_to_map():
    dist = [20,  1.33, 0.2, 1.33, 20]
    d = {-np.pi/2: 20, -0.0558: 0.0625, 0: 0.2, 0.0558: 0.0625, np.pi/2: 20}
    map = [[0]*3]*3

    for key in d.keys():
        if d[key] < 20:
            # pos = [dist*math.cos(ang), dist*math.sin(ang)]
            a = d[key] * np.cos(key)
            b = d[key] * np.sin(key)
            print("{}: a: {}, b: {}".format(key, a, b))
