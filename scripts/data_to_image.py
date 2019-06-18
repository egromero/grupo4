import numpy as np
import matplotlib.pyplot as plt
import time
import cv2


from scipy.ndimage.interpolation import rotate
path = 'Measures/'
name = 'measures_3'
sufix = '.txt'


angles = [0,180]
window = 59 # add and substract to limits of angles.
valid = [angles[0]+window,angles[1]-window]
max = 1 # max distance, set by sensor
resolution = 0.005 # resolution of generated image, bigger = more time expensive
magic_number = int(max/resolution) + 1
offset = 90


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
            if valid[0]<theta<valid[1]:  #bIlineal interpolation
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
                    output = output*1.3 ## augment with saturation
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


## Generate radial matrix
tic = time.time()
radial_vector = np.arange(0,max+resolution,resolution)
radial_matrix = np.zeros([magic_number,angles[1]-angles[0]+1])


for i in range(angles[1]-angles[0]+1):
    binary_vector = radial_vector>sample[i]
    rolled_vector = np.roll(binary_vector,1)
    rolled_vector[0]=False

    radial_matrix[:,i] = np.transpose(binary_vector*1 - rolled_vector*0.5)
toc = time.time()-tic
print('Time for radial matrix generation: ',toc)

## Generate cartesian matrix
tic = time.time()
cart_matrix = np.mgrid[-max:max+resolution:resolution,0:max+resolution:resolution].reshape(2,-1).T
end_vector = [remap(radial_matrix,item) for item in cart_matrix]
end_matrix = np.reshape(np.array(end_vector),[magic_number*2-1,magic_number])

rows,cols = end_matrix.shape
extra_matrix = np.ones([rows,cols-1])*0.5
end_matrix = np.concatenate((extra_matrix,end_matrix),axis=1)

toc = time.time()-tic
print('Time for cartesian matrix generation: ',toc)

## rotate matrix
rows,cols = end_matrix.shape
M = cv2.getRotationMatrix2D((cols/2,rows/2),45,1)
end_matrix = cv2.warpAffine(end_matrix,M,(cols,rows),borderValue=0.5)

## Reduce cartsian matrix


tic = time.time()

original_center =  np.array([int(max/resolution) ,int(max/resolution) ])
boolean_matrix1 = end_matrix!=0.5
boolean_vector1 = [np.sum(item) for item in boolean_matrix1]
boolean_index1 = np.nonzero(boolean_vector1);
zero_min1 = boolean_index1[0][0]; zero_max1 = boolean_index1[0][-1]

boolean_matrix2 = end_matrix.transpose()!=0.5
boolean_vector2 = [np.sum(item) for item in boolean_matrix2]
boolean_index2 = np.nonzero(boolean_vector2);
zero_min2 = boolean_index2[0][0]; zero_max2 = boolean_index2[0][-1]

new_center = original_center - np.array([zero_min1,zero_min2])
new_matrix = end_matrix[zero_min1:zero_max1,zero_min2:zero_max2]
toc = time.time()-tic
print(new_matrix.shape)
print(new_center)
print('Time for reducing cartesian matrix: ',toc)

# M = np.float32([[1,0,new_center[0]],[0,1,new_center[1]]])
# dst = cv2.warpAffine(new_matrix,M,(cols,rows),borderValue=0.5)


# rotated_matrix = rotate(new_matrix,30)

plt.figure()
plt.imshow(end_matrix)

plt.figure()
plt.imshow(new_matrix)
plt.show()
