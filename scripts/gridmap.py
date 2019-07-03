import cv2
from matplotlib import pyplot as plt
import numpy as np

im = cv2.imread("maps/map.pgm")

rows, colums, chanel = im.shape
index=[]

## Loop inicial para ubicar los centros de las grillas.
## Genera la lista index que tiene las poses de los centros de la grilla (x,y)

for r in range(rows):
	if r%8 == 0 and r !=0:
		for c in range(colums):
			if c%8 == 0 and c!=0:
				im[r-4, c-4] = [255,1,1]
				index.append((r-4, c-4))

def check_wall(img,pose, objetive):
	## funcion que determina si hay o no muralla entre dos poses, esas poses corresponden
	## a los valores centrales de la grilla obtenidos anteriormente.
	orientation = tuple(np.subtract(pose, objetive))
	functions = {"(8, 0)": north, "(-8, 0)": south, "(0, 8)": west , "(0, -8)": east}
	wall = functions[str(orientation)](img, pose, objetive)
	return wall

## Funciones de callback dependentiendo el caso de orientacion entre puntos.

def north(img, pose, objetive):
	camino = img[:,pose[1]][objetive[0]:pose[0]+1]
	return np.any(camino == [0,0,0])

def south(img, pose, objetive):
	camino = img[:,pose[1]][pose[0]:objetive[0]+1]
	return np.any(camino == [0,0,0])

def west(img, pose, objetive):
	camino = img[pose[0]][objetive[1]:pose[1]+1]
	return np.any(camino == [0,0,0])
def east(img, pose, objetive):
	camino = img[pose[0]][pose[1]:objetive[1]+1]
	return np.any(camino == [0,0,0])


plt.imshow(im)
print(check_wall(im, (4,20), (4,12)))
plt.show()


