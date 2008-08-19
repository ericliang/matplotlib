#!/usr/bin/env python
"""Image denoising example using 2-dimensional FFT."""

XXX = None # a sentinel for missing pieces

import numpy as np
from matplotlib import pyplot as plt

def mag_phase(F):
    """Return magnitude and phase components of spectrum F."""

    # XXX Look at the absolute and angle functions in numpy...

def plot_spectrum(F, amplify=1000):
    """Normalise, amplify and plot an amplitude spectrum."""

    M = XXX # use mag_phase to get the magnitude...

    # XXX Now, rescale M by amplify/maximum_of_M.  Numpy arrays can be scaled
    # in-place with ARR *= number.  For the max of an array, look for its max
    # method.

    # XXX Next, clip all values larger than one to one.  You can set all
    # elements of an array which satisfy a given condition with array indexing
    # syntax: ARR[ARR<VALUE] = NEWVALUE, for example.


    # Display: this one already works, if you did everything right with M
    plt.imshow(M, plt.cm.Blues)


if __name__ == '__main__':

    im = XXX # make an image array from the file 'moonlanding.png', using the
         # pylab imread() function.  You will need to just extract the red
         # channel from the MxNx4 RGBA matrix to represent the grayscale
         # intensities

    F = XXX # Compute the 2d FFT of the input image.  Look for a 2-d FFT in
            # np.fft.

    # Define the fraction of coefficients (in each direction) we keep
    keep_fraction = 0.1

    # XXX Call ff a copy of the original transform.  Numpy arrays have a copy
    # method for this purpose.

    # XXX Set r and c to be the number of rows and columns of the array.  Look
    # for the shape attribute...

    # Set to zero all rows with indices between r*keep_fraction and
    # r*(1-keep_fraction):

    # Similarly with the columns:


    # Reconstruct the denoised image from the filtered spectrum.  There's an
    # inverse 2d fft in the dft module as well. Call the result im_new

    # Show the results.

    # The code below already works, if you did everything above right.
    plt.figure()

    plt.subplot(221)
    plt.title('Original image')
    plt.imshow(im, plt.cm.gray)

    plt.subplot(222)
    plt.title('Fourier transform')
    plot_spectrum(F)

    plt.subplot(224)
    plt.title('Filtered Spectrum')
    plot_spectrum(ff)

    plt.subplot(223)
    plt.title('Reconstructed Image')
    plt.imshow(im_new, plt.cm.gray)

    # Adjust the spacing between subplots for readability
    plt.subplots_adjust(hspace=0.32)
    plt.show()
