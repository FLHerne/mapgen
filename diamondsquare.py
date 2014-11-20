import numpy
from PIL import Image


def genvaluemap(mapsize, wibbledecay):
    """
    Generate a heightmap using diamond-square algorithm.
    Return square 2d array, side length 'mapsize', of floats in range 0-255.
    'mapsize' must be a power of two.
    """
    assert (mapsize & (mapsize - 1) == 0)
    maparray = numpy.empty((mapsize, mapsize), dtype=numpy.float_)
    maparray[0, 0] = 0
    stepsize = mapsize
    wibble = 100

    def wibbledmean(array):
        return array/4 + numpy.random.uniform(-wibble, wibble, array.shape)

    def fillsquares():
        """For each square of points stepsize apart,
           calculate middle value as mean of points + wibble"""
        cornerref = maparray[0:mapsize:stepsize, 0:mapsize:stepsize]
        squareaccum = cornerref + numpy.roll(cornerref, shift=-1, axis=0)
        squareaccum += numpy.roll(squareaccum, shift=-1, axis=1)
        maparray[stepsize/2:mapsize:stepsize,
                 stepsize/2:mapsize:stepsize] = wibbledmean(squareaccum)

    def filldiamonds():
        """For each diamond of points stepsize apart,
           calculate middle value as mean of points + wibble"""
        mapsize = maparray.shape[0]
        drgrid = maparray[stepsize/2:mapsize:stepsize, stepsize/2:mapsize:stepsize]
        ulgrid = maparray[0:mapsize:stepsize, 0:mapsize:stepsize]
        ldrsum = drgrid + numpy.roll(drgrid, 1, axis=0)
        lulsum = ulgrid + numpy.roll(ulgrid, -1, axis=1)
        ltsum = ldrsum+lulsum
        maparray[0:mapsize:stepsize, stepsize/2:mapsize:stepsize] = wibbledmean(ltsum)
        tdrsum = drgrid + numpy.roll(drgrid, 1, axis=1)
        tulsum = ulgrid + numpy.roll(ulgrid, -1, axis=0)
        ttsum = tdrsum+tulsum
        maparray[stepsize/2:mapsize:stepsize, 0:mapsize:stepsize] = wibbledmean(ltsum)

    while stepsize >= 2:
        fillsquares()
        filldiamonds()
        stepsize /= 2
        wibble /= wibbledecay

    maparray -= maparray.min()
    maparray *= 255.0/maparray.max()
    return maparray
