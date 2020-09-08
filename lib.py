import numpy as np

## Constants
PI = np.pi


def polar2cartesian(r, theta):
    '''
        Returns nx2 shaped array (n is points) with each row is x-y pair.
    '''
    return  r * np.array([np.cos(theta), np.sin(theta)]).transpose()

def polar2cartesian_np(r, theta):
    '''
        r and theta must be 1D arrays.
        Returns nx2 shaped array (n is points) with each row is x-y pair.
    '''
    if r.ndim != 1 or theta.ndim != 1:
        raise 'r and theta must be 1D arrays.'
    r = np.expand_dims(r, axis=1)
    return  r * np.array([np.cos(theta), np.sin(theta)]).transpose()