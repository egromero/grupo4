import numpy as np
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


## takes two matrices of same size and calculates a certain correlation. Can be changed via argument operation
def matrix_corr(m1,m2,operation='corr_norm'):
    function_dict = {'corr':corr, 'corr_norm':corr_norm,'sq_diff':sq_diff,'sq_diff_norm':sq_diff_norm,'ccoeff_norm':ccoeff_norm,'ccoeff':ccoeff}
    return function_dict[operation](m1,m2)
