import cv2
from matplotlib import pyplot as plt
import numpy as np
from parameters import *

im = cv2.imread(map_name)

rows, colums, chanel = im.shape
map = []

## Loop inicial para ubicar los centros de las grillas.
## Genera la lista index que tiene las poses de los centros de la grilla (x,y)
for r in range(4, rows+1, 8):
	map.append([])
	for c in range(4, colums+1, 8):
		im[r, c] = [255,1,1]
		map[-1].append((r, c))

def grid_center(pose):
	x, y  = map[pose[1]//8][pose[0]//8]
	return (y, x)

def get_neighbour(pose):
	x, y = pose
	# 'go_north', 'go_south', 'go_east', 'go_west'
	neighbour = {"go_north": (x, y-8) if y-8 > 0 else None,
				 "go_south": (x, y+8) if y+8 < rows else None,
				 "go_west": (x-8, y) if x-8 > 0 else None,
				 "go_east": (x+8, y) if x+8 < colums else None}
	return neighbour

def check_wall(img, pose, objetive):
	## funcion que determina si hay o no muralla entre dos poses, esas poses corresponden
	## a los valores centrales de la grilla obtenidos anteriormente.
	orientation = tuple(np.subtract(pose, objetive))
	functions = {"(8, 0)": west, "(-8, 0)": east, "(0, 8)": north , "(0, -8)": south}
	wall = functions[str(orientation)](img, pose, objetive)
	return wall

## Funciones de callback dependentiendo el caso de orientacion entre puntos.

def north(img, pose, objetive):
	x, y = pose
	camino = img[y-4][x]
	return not np.any(camino == [0,0,0])

def south(img, pose, objetive):
	x, y = pose
	camino = img[y+4][x]
	return not np.any(camino == [0,0,0])

def west(img, pose, objetive):
	x, y = pose
	camino = img[y][x-4]
	return not np.any(camino == [0,0,0])

def east(img, pose, objetive):
	x, y = pose
	camino = img[y][x+4]
	return not np.any(camino == [0,0,0])


if __name__ == '__main__':
	# Vecinos:  {'go_north': (4, 4), 'go_south': (4, 20), 'go_west': None, 'go_east': (12, 12)}
	# inicio, fin = (4, 12), (-4, 12)
	# wall = check_wall(im, inicio, fin)
	# print("Wall: ", wall)

	im[12, 4] = [1,1,255]
	im[4, 20] = [1,1,255]
	plt.imshow(im)
	plt.show()
