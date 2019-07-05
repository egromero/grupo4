import numpy as np
import matplotlib.pyplot as plt
import time
import cv2
import rospkg
from parameters import *



## Bilinear interpolation for radial_matrix -> cartesian matrix transformation
def pseudo_equal(m,value):
    return np.greater(m,value-threshold)*np.less(m,value+threshold)

def remap(rmatrix,coords):
    #rmatrix n x m array
    #coords is (y,x) coords of new array
    global valid, multiplier,max_r
    # print(coords)
    y,x = coords
    radius = np.sqrt(x**2 + y**2)
    if radius>=max_r:
        return nothing_value
    else:
        try:
            theta = (np.arctan2(-y,x)+np.pi/2)*360/(2*np.pi)
            # print(theta)
            if valid[0]<theta<valid[1]:  #bIlineal interpolation
                radius_index = radius/resolution
                r1 = int(radius_index); r2 = r1+1
                t1 = int(theta); t2 = t1+1
                q1 = radius_index-r1; q2 = theta-t1
                m1 = np.array([1-q1,q1])
                m2 = np.array([1-q2,q2])
                m2.shape = (2,1)
                mr = rmatrix[r1:r2+1,t1:t2+1]
                output = np.dot(np.dot(m1,mr),m2)
                # if output[0]>0.5:
                #     print(x,y)
                #     print(r1,r2,t1,t2,q1,q2)
                #     print(m1,m2,mr)
                #     print(output[0])
                output = output[0]
                if output>nothing_value+threshold:
                    output = output*multiplier ## augment with saturation
                    if output>1:
                        output = 1
                return output
            else:
                return nothing_value
        except ValueError:
            print(coords)
            print(r1,r2,t1,t2,q1,q2)
## Generate radial matrix
def generate_radial_matrix(data):
    global resolution,max_r,magic_number,angles
    radial_vector = np.arange(0,max_r+resolution,resolution)
    radial_matrix = np.zeros([magic_number+1,angles[1]-angles[0]+1])
    for i in range(angles[1]-angles[0]+1):
        binary_vector = radial_vector>data[i]
        rolled_vector = np.roll(binary_vector,3)
        rolled_vector[0:rolled]=False

        radial_matrix[:,i] = np.transpose(binary_vector*1 - rolled_vector*(1-nothing_value ))
    # plt.imshow(radial_matrix)
    # plt.show()
    return radial_matrix

## Generate cartesian matrix
def generate_cartesian_matrix(data):
    global max_r,resolution,magic_number
    if radius_filter(data):
	    radial_matrix = generate_radial_matrix(data)
	    cart_matrix = np.mgrid[-max_r:max_r+resolution:resolution,0:max_r+resolution:resolution].reshape(2,-1).T
	    end_vector = [remap(radial_matrix,item) for item in cart_matrix]
	    end_matrix = np.reshape(np.array(end_vector),[(magic_number+1)*2-1,magic_number+1])

	    rows,cols = end_matrix.shape
	    extra_matrix = np.ones([rows,cols-1])*nothing_value
	    end_matrix = np.concatenate((extra_matrix,end_matrix),axis=1)
	
	    return end_matrix
    else:
	return None

## Preprocess image for map matching
def image_preprocess():
    global ratio,magic_number, gaussian_size
    file_name = our_path + map_name
    #print(file_name)
    img = cv2.imread(file_name,0)

    ## change into 0-1 values	

    img = (img == 0)*1 + (img==205)*nothing_value
    #print(img.shape)
	
    ## resize into correct resolution
    rows,cols = img.shape
    img = cv2.resize(img,(int(cols*ratio),int(rows*ratio)))
    
    ## gaussian blur
    if gaussian_flag:
        img = cv2.GaussianBlur(img,(gaussian_size,gaussian_size),0)

    ## make a bigger image so the windows never go out of bounds
    rows,cols = img.shape

    new_img = np.ones([rows+2*magic_number,cols+2*magic_number])*nothing_value

    rows,cols = new_img.shape
    new_img[magic_number:rows-magic_number,magic_number:cols-magic_number] = img
    #plt.imshow(new_img)
    #plt.show()

    return new_img

## rotates the cartesian matrix to a given angle, and proceeds to cut it to it's minimum size giving it's viewing center (from where the particle should see)
def rotate_and_center(inc_matrix,angle):
    global magic_number

    ## Reduce cartsian matrix
    rows,cols = inc_matrix.shape
    M = cv2.getRotationMatrix2D((cols/2,rows/2),angle,1)
    inc_matrix = cv2.warpAffine(inc_matrix,M,(cols,rows),borderValue=nothing_value,flags =cv2.INTER_NEAREST)
    original_center =  np.array([magic_number ,magic_number])
    if gaussian_flag:
        inc_matrix = cv2.GaussianBlur(inc_matrix,(gaussian_size,gaussian_size),0)

    # plt.imshow(inc_matrix)
    # plt.show()

    ## compute the minimum sized image
    boolean_matrix1 = 1-pseudo_equal(inc_matrix,nothing_value)

    boolean_vector1 = np.any(boolean_matrix1,axis=1)
    boolean_index1 = np.nonzero(boolean_vector1)

    boolean_vector2 = np.any(boolean_matrix1,axis=0)
    boolean_index2 = np.nonzero(boolean_vector2);

    zero_min1 = boolean_index1[0][0]; zero_max1 = boolean_index1[0][-1]
    zero_min2 = boolean_index2[0][0]; zero_max2 = boolean_index2[0][-1]

    new_center = original_center - np.array([zero_min1,zero_min2])

    inc_matrix = inc_matrix[zero_min1:zero_max1,zero_min2:zero_max2]

    # f,(ax1,ax2,ax3) = plt.subplots(1,3)
    # ax1.imshow(boolean_matrix1)
    # ax2.imshow(inc_matrix)
    # ax3.imshow(inc_matrix)
    # plt.show()
    ## gaussian blur

    return [inc_matrix,new_center]
