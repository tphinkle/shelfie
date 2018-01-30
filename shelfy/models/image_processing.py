# Imports
import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage
import scipy.stats



class Line(object):
    '''
    Simple class that holds the information related to a line;
    i.e., the slope, y-intercept, and center point along the line
    '''

    vertical_threshold = 30

    def __init__(self, m, b, center, min_x, max_x, min_y, max_y):
        '''
        m: slope
        b: y-intercept
        center: center point along the line (tuple)
        '''

        self.m = m
        self.b = b

        self.center = center

        self.min_x = min_x
        self.max_x = max_x

        self.min_y = min_y
        self.max_y = max_y


    def y(self, x):
        '''
        Returns the y-value of the line at position x.
        If the line is vertical (i.e., slope is close to infinity), the y-value
        will be returned as None
        '''

        # Line is vertical
        if self.m > self.vertical_threshold:
            return None

        else:
            return self.m*x + self.b


    def x(self, y):
        '''
        Returns the x-value of the line at posiion y.
        If the line is vertical (i.e., slope is close to infinity), will always
        return the center point of the line
        '''

        # Line is vertical
        if self.m > self.vertical_threshold:
            return self.center[0]

        # Line is not vertical
        else:
            return (y - self.b)/self.m





def plot_img(img, show = True):

    fig = plt.figure(figsize = (16,12))
    plt.imshow(img, cmap = 'gray', interpolation = 'none')
    plt.xticks([])
    plt.yticks([])
    if show:
        plt.show()

def gaussian_blur(img, sigma, debug = False):
    '''
    Blurs the image with a gaussian kernel of length sigma.
    This is usually done before line detection is performed.
    '''

    proc_img = scipy.ndimage.filters.gaussian_filter(img, sigma = (sigma, sigma))


    if debug:
        print('gaussian blur')
        plot_img(proc_img, show = True)

    return proc_img




def downsample(img, num_downsamples, debug = False):
    '''
    Downsamples an image by 50% num_downsamples times.
    This effectively reduces image size and resolution.
    '''

    proc_img = np.copy(img)
    for i in range(num_downsamples):
        proc_img = scipy.ndimage.interpolation.zoom(proc_img,.5)

        if debug:
            print('downsample', i)
            plot_img(proc_img, show = True)

    return proc_img

def sobel_x_squared(img, debug = False):
    '''
    Calculates the sobel_x transformation (x-gradient) squared.
    '''

    proc_img = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize = -1)**2.

    if debug:
        print('sobel x')
        plot_img(proc_img)

    return proc_img

def sobel_y_squared(img, debug = False):
    '''
    Calculates the sobel_x transformation (y-gradient) squared.
    '''

    proc_img = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize = -1)**2.

    if debug:
        print('sobel x')
        plot_img(proc_img)

    return proc_img


def laplace_squared(img, debug = False):
    '''
    '''
    # Laplacian (sqrt)
    sobel_x_img = sobel_x_squared(img)
    sobel_y_img = sobel_y_squared(img)
    proc_img = (sobel_x_img**2. + sobel_y_img**2.)**.5

    if debug:
        print('laplace squared')
        plot_img(proc_img)

    return proc_img

def standardize(img, debug = False):
    '''
    Standardizes the image via img = (img - min/(max-min), where max and min
    are the maxima and minima pixel intensities present in the image
    '''
    proc_img = (img - np.min(img))/(np.max(img)-np.min(img))

    if debug:
        print('standardize')
        plot_img(proc_img)

    return proc_img

def digitize(img, num_levels, debug = False):
    '''
    Digitizes the image by binning the pixel intensities.
    '''

    img_max = np.max(img)
    img_min = np.min(img)
    bins = [1.*i*(img_max-img_min)/num_levels for i in range(0, num_levels)]
    proc_img = np.digitize(img, bins)

    if debug:
        print('digitize')
        plot_img(proc_img, show = True)

    return proc_img

def binarize(img, cutoff, debug = False):
    '''
    Binarizes an image by setting intensity of any pixel value with intensity
    not equal to zero to equal one.
    Final image has pixel intensities [0,1].
    '''

    img[img > cutoff] = 1
    img[img <= cutoff] = 0


    if debug:
        print('binarize')
        plot_img(img, show = True)

    return img


def dynamic_binarize(img, cutoff, debug = False):
    '''
    Binarizes an image by setting intensity of any pixel value with intensity
    not equal to zero to equal one.
    Final image has pixel intensities [0,1].
    '''

    if debug:
        print('dynamic binarize (before)')
        plt.hist(img.flatten())
        plt.show()

    for i in range(20):
        cutoff = i*.01
        bright_pixel_ratio = len(np.where(img > cutoff)[0])/(img.shape[0]*img.shape[1])


        if bright_pixel_ratio <= 0.4:
            break

    img[img > cutoff] = 1
    img[img <= cutoff] = 0


    if debug:
        print('dynamic binarize')

        plot_img(img, show = True)


    return img


def binarize_alt(img, frac, debug = False):
    '''
    Binarizes an image by setting intensity of any pixel value with intensity
    not equal to zero to equal one.
    Final image has pixel intensities [0,1].
    '''

    img[img < frac] = 0
    img[img != 0] = 1


    if debug:
        print('binarize')
        plot_img(img, show = True)

    return img

def erode_subtract(img, structure_length, debug = False):
    '''
    Erodes an image using an isotropic structure kernel with scale structure_length,
    and subtracts the eroded image off the original image.
    This can be used to split thick vertical lines into two lines, or to break up
    horizontally-thick elements.
    '''

    #structure = np.ones((3,3))*structure_length
    structure = np.array(([0,0,0],[1,1,1],[0,0,0]))*structure_length
    proc_img = np.copy(img)

    proc_img = img - scipy.ndimage.morphology.binary_erosion(img, structure, 1)

    if debug:
        print('erode subtract')
        plot_img(proc_img, show = True)

    return proc_img


def horizontal_dilate(img, structure_length, iterations, debug = False):
    structure = np.array(([0,0,0],[1,1,1],[0,0,0]))*structure_length
    proc_img = np.copy(img)

    proc_img = scipy.ndimage.morphology.binary_dilation(img, structure, iterations)

    if debug:
        print('horizontal dilate subtract')
        plot_img(proc_img, show = True)

    return proc_img


def horizontal_dilate_subtract(img, structure_length, iterations, debug = False):
    '''
    Erodes an image using an isotropic structure kernel with scale structure_length,
    and subtracts the eroded image off the original image.
    This can be used to split thick vertical lines into two lines, or to break up
    horizontally-thick elements.
    '''

    #structure = np.ones((3,3))*structure_length
    structure = np.array(([0,0,0],[1,1,1],[0,0,0]))*structure_length
    proc_img = np.copy(img)

    proc_img = img - scipy.ndimage.morphology.binary_dilation(img, structure, iterations)
    proc_img[proc_img < 0] = 1

    if debug:
        print('horizontal dilate subtract')
        plot_img(proc_img, show = True)

    return proc_img

def erode(img, structure_length, iterations, debug = False):
    '''
    Erodes the image with a vertical structure element of length structure_length.
    Used to get rid of lines that are primarily horizontal.
    '''



    structure = np.array([[1,1,1],[1,1,1],[1,1,1]])*structure_length
    proc_img = scipy.ndimage.morphology.binary_erosion(img, structure, iterations)

    if debug:
        print('vertical erode')
        plot_img(proc_img, show = True)

    return proc_img

def vertical_erode(img, structure_length, iterations, debug = False):
    '''
    Erodes the image with a vertical structure element of length structure_length.
    Used to get rid of lines that are primarily horizontal.
    '''



    structure = np.array([[0,1,0],[0,1,0],[0,1,0]])*structure_length
    proc_img = scipy.ndimage.morphology.binary_erosion(img, structure, iterations)

    if debug:
        print('vertical erode')
        plot_img(proc_img, show = True)

    return proc_img

def vertical_dilate(img, structure_length, iterations, debug = False):
    '''
    Dilates an image in the vertical direction using a vertical structure element
    of scale structure_length.
    This is used to connect lines that are close by vertically.
    Repeats iterations times.
    '''

    structure = np.array([[0,1,0],[0,1,0],[0,1,0]])*structure_length
    proc_img = scipy.ndimage.morphology.binary_dilation(img, structure, iterations)

    if debug:
        print('vertical dilate')
        plot_img(proc_img, show = True)

    return proc_img

def dilate(img, structure_length, iterations, debug = False):
    '''
    Dilates an image in the vertical direction using a vertical structure element
    of scale structure_length.
    This is used to connect lines that are close by vertically.
    Repeats iterations times.
    '''

    structure = np.array([[1,1,1],[1,1,1],[1,1,1]])*structure_length
    proc_img = scipy.ndimage.morphology.binary_dilation(img, structure, iterations)

    if debug:
        print('dilate')
        plot_img(proc_img, show = True)

    return proc_img

def horizontal_erode(img, structure_length, iterations, debug = False):
    '''
    Erodes the image with a horizontal structure element of length structure_length.
    Used to prevent lines that are close horizontally from clustering
    '''



    structure = np.array([[0,0,0],[0,1,1],[0,0,0]])*structure_length
    proc_img = scipy.ndimage.morphology.binary_erosion(img, structure, iterations)

    if debug:
        print('horizontal erode')
        plot_img(proc_img, show = True)

    return proc_img

def horizontal_erode_dilate(img, structure_length, iterations, debug = False):
    '''
    Erodes the image with a horizontal structure element of length structure_length.
    Used to prevent lines that are close horizontally from clustering
    '''



    structure = np.array([[0,0,0],[0,1,1],[0,0,0]])*structure_length
    proc_img = scipy.ndimage.morphology.binary_erosion(img, structure, iterations)
    proc_img = scipy.ndimage.morphology.binary_dilation(proc_img, structure, iterations)

    if debug:
        print('horizontal erode/dilate')
        plot_img(proc_img, show = True)

    return proc_img

def connected_components(img, debug = False):
    '''
    Finds all connected components in a binary image and assigns all connections
    within a component to a unique value for that component.
    Returns the processed image, and the values of the unique components.

    '''
    proc_img, levels = scipy.ndimage.label(img, structure = np.ones((3,3)))
    levels = list(range(1, levels + 1))


    if debug:
        print('find connected components, levels = ', levels)
        plot_img(proc_img, show = True)

    return proc_img, levels


def remove_short_clusters_vertical(img, levels, threshold_fraction, debug = False):
    '''
    Given an image that has been labeled with connected components (see above),
    calculates the vertical height of each component and filters those that
    are too short.
    The threshold should be set as a fraction of the longest line present in the
    image.
    This is used to remove short vertical lines.

    '''

    drop_values = []
    ptps = []

    # Calculate peak-to-peak height of line
    for level in levels:
        bright_pixels = np.where(img == level)
        ptp = np.ptp(bright_pixels[0])
        ptps.append(ptp)


    # Determine which lines to drop
    threshold = np.max(ptps)/2.
    for i in range(len(ptps)):
        if ptps[i] < threshold:
            drop_values.append(levels[i])


    # Drop the lines
    for drop_value in drop_values:
        img[img == drop_value] = 0



    if debug:
        print('remove short clusters')
        plt.hist(ptps, bins = 25)
        plt.show()
        plot_img(img, show = True)

    return img



def remove_short_clusters_horizontal(img, levels, threshold_fraction, debug = False):
    '''
    Given an image that has been labeled with connected components (see above),
    calculates the vertical height of each component and filters those that
    are too short.
    The threshold should be set as a fraction of the longest line present in the
    image.
    This is used to remove short vertical lines.

    '''

    drop_values = []
    ptps = []

    # Calculate peak-to-peak height of line
    for level in levels:
        bright_pixels = np.where(img == level)
        ptp = np.ptp(bright_pixels[1])
        ptps.append(ptp)


    # Determine which lines to drop
    threshold = np.max(ptps)/2.
    for i in range(len(ptps)):
        if ptps[i] < threshold:
            drop_values.append(levels[i])


    # Drop the lines
    for drop_value in drop_values:
        img[img == drop_value] = 0



    if debug:
        print('remove short clusters')
        plt.hist(ptps, bins = 25)
        plt.show()
        plot_img(img, show = True)

    return img



def upsample(img, upsample_factor, debug = False):
    '''
    Upsamples the image, e.g. multiplies its height and width by the upsample_factor.
    This is performed to restore the image to the correct overall size that it
    was before a downsample was used in the imag eprocessing pipeline.
    '''


    proc_img = img.repeat(upsample_factor, axis = 0).repeat(upsample_factor, axis = 1)

    if debug:
        print('upsample')
        plot_img(proc_img, show = True)

    return proc_img

def invert(img, debug = False):
    '''
    Inverts a binary image
    '''

    proc_img = 1-img

    if debug:
        print('invert')
        plot_img(proc_img, show = True)

    return proc_img

def get_lines_from_img(img, levels, debug = False):
    '''
    Finds the equations for all of the lines in a binary image,
    and returns as a list of Line objects (see above class definition).
    '''

    lines = []
    for level in levels:
        line = np.where(img == level)
        xs = line[1]
        ys = line[0]
        center = [np.mean(xs), np.mean(ys)]

        min_x = np.min(xs)
        max_x = np.max(xs)
        min_y = np.min(ys)
        max_y = np.max(ys)

        #print('std ratio', np.std(ys)/np.std(xs))
        spread = (np.max(ys) - np.min(ys))/(np.max(xs) - np.min(xs))

        # Line is vertical
        #if (np.std(ys)/np.std(xs) > 10):
        if spread > 10:
            line = Line(1000, 0, center, min_x, max_x, min_y, max_y)

        # Line is not vertical
        else:
            m, b, r, p, std = scipy.stats.linregress(xs,ys)
            line = Line(m, b, center, min_x, max_x, min_y, max_y)


        lines.append(line)

    # Sort the lines by their center x positions
    lines.sort(key = lambda line: line.center[0])

    return lines



def get_shelf_lines(img, debug = False):
    # Convert to HSV
    #proc_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    proc_img = np.mean(img, axis = 2)#**2. + (proc_img[:,:,2])**2.)**.5#+proc_img[:,:,2]**2.)**.5

    # Convert to gs
    #proc_img = np.mean(img[:,:], axis = 2).astype(np.uint8)
    #proc_img = img[:,:,0]#.astype(np.uint8)

    # Blur
    sigma = 3
    proc_img = gaussian_blur(proc_img, sigma = sigma, debug = debug)

    # Down sample
    num_downsamples = 3
    proc_img = downsample(proc_img, num_downsamples, debug = debug)

    # Sobel y
    proc_img = laplace_squared(proc_img, debug = debug)


    # Standardize
    proc_img = standardize(proc_img, debug = debug)

    # Digitize
    #num_levels = 4
    #proc_img = digitize(proc_img, num_levels, debug = debug)

    #plt.hist(proc_img.flatten(), bins = 100)
    #plt.show()

    # Binarize
    cutoff = np.max(proc_img)/500.
    proc_img = binarize(proc_img, cutoff, debug = debug)


    #Vertical dilate
    structure_length = 200
    iterations = 1
    proc_img = vertical_dilate(proc_img, structure_length, iterations, debug = debug)



    # Horizontal erode
    structure_length = 200
    iterations = 50
    proc_img = horizontal_erode(proc_img, structure_length, iterations, debug = debug)


    # Connected components
    proc_img, levels = connected_components(proc_img, debug = debug)

    # Remove short clusters
    threshold_fraction = 0.10
    proc_img = remove_short_clusters_horizontal(proc_img, levels, threshold_fraction, debug = debug)

    # Up sample
    upsample_factor = 2**num_downsamples
    proc_img = upsample(proc_img, upsample_factor, debug = debug)

    # Connected components
    proc_img, levels = connected_components(proc_img, debug = debug)


    # Lines
    lines = get_lines_from_img(proc_img, levels, debug = False)



    # Plot the result
    if debug:

        new_img = np.copy(img[:,:,::-1])

        #new_img[proc_img != 0,:] = [0,255,128]

        plot_img(new_img, show = False)
        for line in lines:
            y0 = 0
            y1 = np.shape(img)[0]

            x0 = line.x(y0)
            x1 = line.x(y1)

            plt.plot([x0, x1], [y0, y1], color = 'yellow', lw = 3)

        plt.xlim(0, img.shape[1])
        plt.ylim(img.shape[0], 0)
        plt.xticks([])
        plt.yticks([])
        plt.savefig('proc_img.png', bbox_inches = 'tight', dpi = 300)

        plt.show()

    return lines



def get_book_lines(img, angles = [0], spaces = ['h'], debug = False):
    '''
    Given an image, performs a number of image processing techniques to render
    the processed image down into a series of lines that represent the edges
    of spines in the image.
    The lines are returned as a list of Line objects (see above).
    Repeats iterations times.
    '''

    # Convert to HSV
    gs_img = np.mean(img, axis = 2)
    final_img = np.zeros((gs_img.shape[0], gs_img.shape[1]))
    lines = []
    for angle in angles:

        # Rotate
        proc_img = scipy.ndimage.rotate(gs_img, angle = angle, reshape = False)



        # Convert to gs
        #proc_img = np.mean(img[:,:], axis = 2).astype(np.uint8)
        #proc_img = img[:,:,0]#.astype(np.uint8)

        # Blur
        sigma = 3
        proc_img = gaussian_blur(proc_img, sigma = sigma, debug = debug)

        # Sobel x
        proc_img = sobel_x_squared(proc_img, debug = debug)

        # Down sample
        num_downsamples = 2
        proc_img = downsample(proc_img, num_downsamples, debug = debug)







        # Standardize
        proc_img = standardize(proc_img, debug = debug)

        # Digitize
        #num_levels = 4
        #proc_img = digitize(proc_img, num_levels, debug = debug)

        #plt.hist(proc_img.flatten(), bins = 100)
        #plt.show()

        # Binarize
        cutoff = np.max(proc_img)/12.
        proc_img = dynamic_binarize(proc_img, cutoff, debug = debug)

        # Horizontal erode
        #structure_length = 1
        #iterations = 1
        #proc_img = horizontal_erode(proc_img, structure_length, iterations, debug = debug)


        # Horizaontal dilate
        #structure_length = 1
        #iterations = 1
        #proc_img = horizontal_dilate(proc_img, structure_length, iterations, debug = debug)

        # Vertical erode
        structure_length = 200
        iterations = 8
        proc_img = vertical_erode(proc_img, structure_length, iterations, debug = debug)




        # Vertical dilate
        structure_length = 500
        iterations = 10
        proc_img = vertical_dilate(proc_img, structure_length, iterations, debug = debug)




        # Connected components
        proc_img, levels = connected_components(proc_img, debug = debug)

        # Remove short clusters
        threshold_fraction = 0.10
        proc_img = remove_short_clusters_vertical(proc_img, levels, threshold_fraction, debug = debug)

        # Re-binarize
        #proc_img = binarize(proc_img, debug = debug)

        # Dilate
        #structure_length = 3
        #proc_img = dilate(proc_img, structure_length, debug = debug)

        # Up sample
        upsample_factor = 2**num_downsamples
        proc_img = upsample(proc_img, upsample_factor, debug = debug)

        # Connected components
        #proc_img, levels = connected_components(proc_img, debug = debug)


        # Un-rotate image
        proc_img = scipy.ndimage.rotate(proc_img, angle = -1*angle, reshape = False)
        proc_img.resize((img.shape[0], img.shape[1]))
        final_img = final_img + proc_img

        '''fig = plt.figure(figsize = (16,12))
        plt.imshow(proc_img, cmap = 'gray')
        plt.show()'''


    # Conver the final image to binary
    final_img[final_img > 0] = 1

    # Connect components label
    final_img, levels = connected_components(final_img)

    # Get the lines from the label
    lines = get_lines_from_img(final_img, levels, debug = False)


    #fig = plt.figure(figsize = (16,12))
    #plt.imshow(final_img, cmap = 'gray')
    #plt.show()

    # Plot the result
    if debug:

        new_img = np.copy(img)

        #new_img[proc_img != 0,:] = [0,255,128]

        plot_img(new_img, show = False)
        for line in lines:
            y0 = line.min_y
            y1 = line.max_y

            x0 = line.x(y0)
            x1 = line.x(y1)

            plt.plot([x0, x1], [y0, y1], color = np.array([0,169,55])/255., lw = 6)

        plt.xlim(0, img.shape[1])
        plt.ylim(img.shape[0], 0)
        plt.xticks([])
        plt.yticks([])
        plt.savefig('proc_img.png', bbox_inches = 'tight', dpi = 300)

        plt.show()


    return lines





"""
VERY GOOD RESULTS!
def get_book_lines(img, spaces = ['h'], debug = False):
    '''
    Given an image, performs a number of image processing techniques to render
    the processed image down into a series of lines that represent the edges
    of spines in the image.
    The lines are returned as a list of Line objects (see above).
    Repeats iterations times.
    '''


    # Convert to HSV
    proc_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    proc_img = ((proc_img[:,:,1])**2. + (proc_img[:,:,2])**2.)**.5#+proc_img[:,:,2]**2.)**.5

    # Convert to gs
    #proc_img = np.mean(img[:,:], axis = 2).astype(np.uint8)
    #proc_img = img[:,:,0]#.astype(np.uint8)

    # Down sample
    num_downsamples = 0
    proc_img = downsample(proc_img, num_downsamples, debug = debug)

    # Blur
    sigma = 3
    proc_img = gaussian_blur(proc_img, sigma = sigma, debug = debug)


    # Sobel x
    proc_img = sobel_x_squared(proc_img, debug = debug)


    # Standardize
    proc_img = standardize(proc_img, debug = debug)

    # Digitize
    #num_levels = 4
    #proc_img = digitize(proc_img, num_levels, debug = debug)

    #plt.hist(proc_img.flatten(), bins = 100)
    #plt.show()

    # Binarize
    cutoff = np.max(proc_img)/100.
    proc_img = binarize(proc_img, cutoff, debug = debug)



    # Vertical erode
    structure_length = 200
    iterations = 50
    proc_img = vertical_erode(proc_img, structure_length, iterations, debug = debug)

    '''
    # Vertical dilate
    structure_length = 500
    iterations = 200
    proc_img = vertical_dilate(proc_img, structure_length, iterations, debug = debug)
    '''

    # Connected components
    proc_img, levels = connected_components(proc_img, debug = debug)

    # Remove short clusters
    threshold_fraction = 0.10
    proc_img = remove_short_clusters(proc_img, levels, threshold_fraction, debug = debug)

    # Re-binarize
    #proc_img = binarize(proc_img, debug = debug)

    # Dilate
    #structure_length = 3
    #proc_img = dilate(proc_img, structure_length, debug = debug)

    # Up sample
    upsample_factor = 2**num_downsamples
    proc_img = upsample(proc_img, upsample_factor, debug = debug)

    # Connected components
    proc_img, levels = connected_components(proc_img, debug = debug)


    # Lines
    lines = get_lines_from_img(proc_img, levels, debug = False)

    # Plot the result
    if debug:

        new_img = np.copy(img[:,:,::-1])

        #new_img[proc_img != 0,:] = [0,255,128]

        plot_img(new_img, show = False)
        for line in lines:
            y0 = 0
            y1 = np.shape(img)[0]

            x0 = line.x(y0)
            x1 = line.x(y1)

            plt.plot([x0, x1], [y0, y1], color = 'yellow', lw = 3)

        plt.xlim(0, img.shape[1])
        plt.ylim(img.shape[0], 0)
        plt.xticks([])
        plt.yticks([])
        plt.savefig('proc_img.png', bbox_inches = 'tight', dpi = 300)

        plt.show()

    return lines

"""



"""
Current working pipeline---don't delete or change this!!!!




def get_book_lines(img, debug = False):
    '''
    Given an image, performs a number of image processing techniques to render
    the processed image down into a series of lines that represent the edges
    of spines in the image.
    The lines are returned as a list of Line objects (see above).
    Repeats iterations times.
    '''

    # Convert to gs
    proc_img = np.mean(img[:,:], axis = 2).astype(np.uint8)

    # Down sample
    num_downsamples = 3
    proc_img = downsample(proc_img, num_downsamples, debug = debug)

    # Sobel x
    proc_img = sobel_x_squared(proc_img, debug = debug)

    # Standardize
    proc_img = standardize(proc_img, debug = debug)

    # Digitize
    num_levels = 4
    proc_img = digitize(proc_img, num_levels, debug = debug)

    # Binarize
    proc_img = binarize(proc_img, debug = debug)

    # Erode subtract
    structure_length = 5
    proc_img = erode_subtract(proc_img, structure_length, debug = debug)

    # Vertical erode
    structure_length = 200
    iterations = 3
    proc_img = vertical_erode(proc_img, structure_length, iterations, debug = debug)

    # Vertical dilate
    structure_length = 50
    iterations = 5
    proc_img = vertical_dilate(proc_img, structure_length, iterations, debug = debug)

    # Connected components
    proc_img, levels = connected_components(proc_img, debug = debug)

    # Remove short clusters
    threshold_fraction = 0.10
    proc_img = remove_short_clusters(proc_img, levels, threshold_fraction, debug = debug)

    # Re-binarize
    proc_img = binarize(proc_img, debug = debug)

    # Dilate
    #structure_length = 3
    #proc_img = dilate(proc_img, structure_length, debug = debug)

    # Up sample
    upsample_factor = 2**num_downsamples
    proc_img = upsample(proc_img, upsample_factor, debug = debug)

    # Connected components
    proc_img, levels = connected_components(proc_img, debug = debug)


    # Lines
    lines = get_lines_from_img(proc_img, levels, debug = False)

    # Plot the result
    if debug:

        new_img = np.copy(img[:,:,::-1])

        #new_img[proc_img != 0,:] = [0,255,128]

        plot_img(new_img, show = False)
        for line in lines:
            y0 = 0
            y1 = np.shape(img)[0]

            x0 = line.x(y0)
            x1 = line.x(y1)

            plt.plot([x0, x1], [y0, y1], color = 'yellow', lw = 3)

        plt.xlim(0, img.shape[1])
        plt.ylim(img.shape[0], 0)
        plt.xticks([])
        plt.yticks([])
        plt.savefig('proc_img.png', bbox_inches = 'tight', dpi = 300)

        plt.show()

    return lines
"""
