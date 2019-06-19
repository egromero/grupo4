import numpy as np
import matplotlib.pyplot as plt
import time
import cv2

path = 'Measures/'
name = 'measures_3'
sufix = '.txt'


angles = [0,180]
window = 59 # add and substract to limits of angles.
valid = [angles[0]+window,angles[1]-window]
max = 1 # max distance, set by sensor
resolution = 0.005 # resolution of generated image, bigger = more time expensive
original_res = 0.1
ratio = original_res/resolution
magic_number = int(max/resolution)
offset = 90
multiplier = 10

## Bilinear interpolation for radial_matrix -> cartesian matrix transformation
def remap(rmatrix,coords):
    #rmatrix n x m array
    #coords is (y,x) coords of new array
    global valid, multiplier
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
                m1 = np.array([1-q1,q1])
                m2 = np.array([1-q2,q2])
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
                    output = output*multiplier ## augment with saturation
                    if output>1:
                        output = 1
                return output
            else:
                return 0.5
        except ValueError:
            print(coords)
            print(r1,r2,t1,t2,q1,q2)
## Generate radial matrix
def generate_radial_matrix(data):
    global resolution,max,magic_number,angles
    radial_vector = np.arange(0,max+resolution,resolution)
    radial_matrix = np.zeros([magic_number+1,angles[1]-angles[0]+1])


    for i in range(angles[1]-angles[0]+1):
        binary_vector = radial_vector>sample[i]
        rolled_vector = np.roll(binary_vector,1)
        rolled_vector[0]=False

        radial_matrix[:,i] = np.transpose(binary_vector*1 - rolled_vector*0.5)
    return radial_matrix

## Generate cartesian matrix
def generate_cartesian_matrix(data):
    global max,resolution,magic_number

    radial_matrix = generate_radial_matrix(data)
    cart_matrix = np.mgrid[-max:max+resolution:resolution,0:max+resolution:resolution].reshape(2,-1).T
    end_vector = [remap(radial_matrix,item) for item in cart_matrix]
    end_matrix = np.reshape(np.array(end_vector),[(magic_number+1)*2-1,magic_number+1])

    rows,cols = end_matrix.shape
    extra_matrix = np.ones([rows,cols-1])*0.5
    end_matrix = np.concatenate((extra_matrix,end_matrix),axis=1)

    return end_matrix

## Preprocess image for map matching
def image_preprocess():
    global ratio,magic_number
    file = 'map.pgm'
    img = cv2.imread(file,0)
    ## change into 0-1 values
    img = (img == 0)*1 + (img==205)*0.5

    ## resize into correct resolution
    rows,cols = img.shape
    img = cv2.resize(img,(int(rows*ratio),int(cols*ratio)))

    ## make a bigger image so the windows never go out of bounds
    rows,cols = img.shape
    new_img = np.ones([rows+2*magic_number,cols+2*magic_number])*0.5

    rows,cols = new_img.shape
    new_img[magic_number:rows-magic_number,magic_number:cols-magic_number] = img

    return new_img

## rotates the cartesian matrix to a given angle, and proceeds to cut it to it's minimum size giving it's viewing center (from where the particle should see)
def rotate_and_center(inc_matrix,angle):
    global magic_number
    rows,cols = inc_matrix.shape
    M = cv2.getRotationMatrix2D((cols/2,rows/2),angle,1)
    inc_matrix = cv2.warpAffine(inc_matrix,M,(cols,rows),borderValue=0.5)

    ## Reduce cartsian matrix

    original_center =  np.array([magic_number ,magic_number ])
    boolean_matrix1 = inc_matrix!=0.5
    boolean_vector1 = [np.sum(item) for item in boolean_matrix1]
    boolean_index1 = np.nonzero(boolean_vector1);
    zero_min1 = boolean_index1[0][0]; zero_max1 = boolean_index1[0][-1]

    boolean_matrix2 = inc_matrix.transpose()!=0.5
    boolean_vector2 = [np.sum(item) for item in boolean_matrix2]
    boolean_index2 = np.nonzero(boolean_vector2);
    zero_min2 = boolean_index2[0][0]; zero_max2 = boolean_index2[0][-1]

    new_center = original_center - np.array([zero_min1,zero_min2])
    new_matrix = inc_matrix[zero_min1:zero_max1,zero_min2:zero_max2]
    return [new_matrix,new_center]

## takes two matrices of same size and calculates a certain correlation. Can be changed via argument operation
def norm(m1,m2):
    m1_sum = np.sum(m1**2)
    m2_sum = np.sum(m2**2)
    return np.sqrt(m1_sum*m2_sum)

def sq_diff(m1,m2):
    return np.sum((m1-m2)**2)

def sq_diff_norm(m1,m2):
    num = sq_diff(m1,m2)
    den = norm(m1,m2)
    return num/den

def corr(m1,m2):
    return np.sum((m1*m2))

def corr_norm(m1,m2):
    num = corr(m1,m2)
    den = norm(m1,m2)
    return num/den

def ccoeff(m1,m2): ## Not quite
    return np.sum(m1*m2)

def ccoeff_norm(m1,m2):
    num = ccoeff(m1,m2)
    den = norm(m1,m2)
    return num/den
def matrix_corr(m1,m2,operation='corr_norm'):
    function_dict = {'corr':corr, 'corr_norm':corr_norm,'sq_diff':sq_diff,'sq_diff_norm':sq_diff_norm,'ccoeff_norm':ccoeff_norm,'ccoeff':ccoeff}
    return function_dict[operation](m1,m2)


    return 0

data = [] # file reader, wont matter later
with open (path+name+sufix) as file:
    for line in file:
        gen = map(float,line.rstrip(')\n').lstrip('(').split(','))
        data.append(list(gen))
sample = data[2]


tic = time.time()
end_matrix = generate_cartesian_matrix(sample)
toc = time.time()-tic
print('Time for cartesian full matrix generation: ',toc)
# M = np.float32([[1,0,new_center[0]],[0,1,new_center[1]]])
# dst = cv2.warpAffine(new_matrix,M,(cols,rows),borderValue=0.5)



## Open original image with corresponding resolution and extra 'zeros'

tic = time.time()
new_img = image_preprocess()
toc = time.time()-tic
print('Time for image preprocessing: ',toc)
# obtain piece of or_image corresponding a certain x,y,angle particle.
sample_particle = (480,440,45)
# f,subplt = plt.subplots(2,2)
tic = time.time()
for i,angle in enumerate(range(3)):
    new_matrix,new_center = rotate_and_center(end_matrix,angle)
    rows,cols = new_matrix.shape
    fake_center = (sample_particle[0]-new_center[0],sample_particle[1]-new_center[1])
    window = new_img[fake_center[0]:fake_center[0]+rows,fake_center[1]:fake_center[1]+cols]
    out = cv2.matchTemplate(new_img,window,cv2.TM_CCOEFF_NORMED)
    # plt.figure()
    # plt.imshow(window*new_matrix)
    # # print(np.sum(window*new_matrix))
    # a= matrix_corr(window,new_matrix,operation='corr_norm')
    # print(matrix_corr(window,new_matrix,operation='sq_diff_norm'))
    # print(matrix_corr(window,new_matrix,operation='ccoeff_norm'))
#
#     # subplt[i//2,i%2].imshow(window)
toc = time.time()-tic
print('Time for getting 1 window: ',toc)
# plt.figure()
# plt.imshow(new_img)
# plt.figure()
# plt.imshow(end_matrix)
plt.show()
