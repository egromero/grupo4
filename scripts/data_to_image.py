import numpy as np
import matplotlib.pyplot as plt

from scipy.ndimage.interpolation import geometric_transform
path = 'Measures/'
name = 'measures_2'
sufix = '.txt'


angles = [0,180]
window = 59 # add and substract to limits of angles.
valid = [angles[0]+window,angles[1]-window]
max = 1 # max distance, set by sensor
resolution = 0.005 # resolution of generated image, bigger = more time expensive
magic_number = int(max/resolution) + 1

def remap(rmatrix,coords):
    global valid
    # print(coords)
    y,x = coords
    radius = np.sqrt(x**2 + y**2)
    if radius>=max:
        return 0.5
    else:
        try:
            theta = (np.arctan2(y,x)+np.pi/2)*360/(2*np.pi)
            # print(theta)
            if valid[0]<theta<valid[1]:
                radius_index = radius/resolution
                r1 = int(radius_index); r2 = r1+1
                t1 = int(theta); t2 = t1+1
                q1 = radius_index-r1; q2 = theta-t1
                m1 = np.array([q1,1-q1])
                m2 = np.array([q2,1-q2])
                m2.shape = (2,1)
                mr = rmatrix[r1:r2+1,t1:t2+1]
                output = m1@mr@m2
                # if output[0]>0.5:
                #     print(x,y)
                #     print(r1,r2,t1,t2,q1,q2)
                #     print(m1,m2,mr)
                #     print(output[0])
                output = output[0]
                if output>0.5:
                    output = output*1.3
                    if output>1:
                        output = 1
                return output
            else:
                return 0.5
        except ValueError:
            print(coords)
            print(r1,r2,t1,t2,q1,q2)


data = [] # file reader, wont matter later
with open (path+name+sufix) as file:
    for line in file:
        gen = map(float,line.rstrip(')\n').lstrip('(').split(','))
        data.append(list(gen))


sample = data[2]


radial_vector = np.arange(0,max+resolution,resolution)
radial_matrix = np.zeros([magic_number,angles[1]-angles[0]+1])

for i in range(angles[1]-angles[0]+1):
    binary_vector = radial_vector>sample[i]
    rolled_vector = np.roll(binary_vector,1)
    rolled_vector[0]=False

    radial_matrix[:,i] = np.transpose(binary_vector*1 - rolled_vector*0.5)
# x_array,y_array = np.mgrid[0:max+resolution:resolution,0:max+resolution:resolution]
cart_matrix = np.mgrid[-max:max+resolution:resolution,0:max+resolution:resolution].reshape(2,-1).T
#cart_matrix.shape = (401,401)

# cart_matrix = np.indices([20,20]
# xx , yy = np.meshgrid(radial_vector,radial_vector)
# cart_matrix = zeros()


end_vector = [remap(radial_matrix,item) for item in cart_matrix]
end_matrix = np.reshape(np.array(end_vector),[magic_number*2-1,magic_number])

plt.imshow(end_matrix)
plt.show()
