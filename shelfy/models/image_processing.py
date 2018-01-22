

class Line(object):
    '''
    Simple class that holds the information related to a line;
    i.e., the slope, y-intercept, and center point along the line
    '''

    vertical_threshold = 30

    def __init__(self, m, b, center):
        '''
        m: slope
        b: y-intercept
        center: center point along the line (tuple)
        '''

        self.m = m
        self.b = b
        self.center = center


    def y(x):
        '''
        Returns the y-value of the line at position x.
        If the line is vertical (i.e., slope is close to infinity), the y-value
        will be returned as np.inf
        '''

        if self.m > self.vertical_threshold:
            return


def downsample(img, num_downsamples, debug = False):
    '''
    Downsamples an image by 50% num_downsamples times.
    This effectively reduces image size and resolution.
    '''
    for i in range(num_downsamples):
        proc_img = scipy.ndimage.interpolation.zoom(img,.5)

        if debug:
            print('downsample', i)
            plot_img(proc_img, show = True)

    return proc_img

def sobel_x_squared(img, debug = False):
    '''
    Calculates the sobel_x transformation (x-gradient) squared.
    '''

    proc_img = cv2.Sobel(img, cv2.CV_8UC1, 1, 0, ksize = -1)**2.

    if debug:
        print('sobel x')
        plot_img(proc_img)

    return proc_img

def standardize(img, debug = False):
    '''
    Standardizes the image via img = (img - min/(max-min), where max and min
    are the maxima and minima pixel intensities present in the image
    '''
    proc_img = (img - np.min(img))/(np.max(img) - np.min(img))

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

def binarize(img, debug = False):
    '''
    Binarizes an image by setting intensity of any pixel value with intensity
    not equal to zero to equal one.
    Final image has pixel intensities [0,1].
    '''

    img[img == np.min(img)] = 0
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

    structure = np.ones((3,3))*structure_length

    proc_img = img - scipy.ndimage.morphology.binary_erosion(img, structure, 1)

    if debug:
        print('erode subtract')
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
        print('morpho dilate')
        plot_img(proc_img, show = True)

    return proc_img

def connected_components(img, debug = False):
    '''
    Finds all connected components in a binary image and assigns all connections
    within a component to a unique value for that component.
    Returns the processed image, and the values of the unique components.

    '''
    proc_img, unique_values = scipy.ndimage.label(img, structure = np.ones((3,3)))
    unique_values = list(range(unique_values))


    if debug:
        print('find connected components')
        plot_img(proc_img, show = True)

    return proc_img, unique_values


def remove_short_clusters(img, levels, debug = False):
    '''
    Given an image that has been labeled with connected components (see above),
    calculates the vertical height of each component and filters those that
    are too short.
    This is used to remove short vertical lines.
    '''

    drop_values = []
    threshold = img.shape[0]*.35
    for level in levels:
        bright_pixels = np.where(img == level)
        ptp = np.ptp(bright_pixels[0])

        if(ptp < threshold):
            drop_values.append(unique_value)

        for drop_value in drop_values:
            img[img == drop_value] = 0

    if debug:
        print('remove short clusters')
        plot_img(img, show = True)

    return img

def dilate(img, structure_length, debug = False):
    '''
    Dilates the image once using a structuring element with length
    structure_length
    '''

    structure_length = 3
    structure = np.array([[1,1,1],[1,1,1],[1,1,1]])*structure_length
    proc_img = scipy.ndimage.morphology.binary_dilation(img, structure, 1)

    if debug:
        print('dilate')
        plot_img(proc_img, show = True)

    return proc_img

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

def get_lines_from_img(img, debug = False):
    '''
    Finds the equations for all of the lines in a binary image,
    and returns as a list of Line objects (see above class definition)
    '''

    lines = []
    for unique_value in unique_values:
        line = np.where(img == unique_value)
        xs = line[1]
        ys = line[0]


        m, b, r, p, std = scipy.stats.linregress(xs,ys)
        center = [np.mean(xs), np.mean(ys)]

        line = Line(m, b, center)
        lines.append(line)

    # Sort the lines by their center x positions
    lines.sort(key = lambda line: line.center[0])

    return lines






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

    # Horizontal erosion and subtraction
    structure_length = 5
    proc_img = erode_subtract(proc_img, structure_length, debug = debug)

    # Vertical erode
    structure_length = 200
    iterations = 3
    proc_img = vertical_erode(proc_img, structure_length, iterations, debug = debug)

    # Vertical dilate
    structure_length = 3
    iterations = 3
    proc_img = vertical_dilate(proc_img, structure_length, iterations, debug = debug)

    # Connected components
    proc_img, levels = connected_components(proc_img, debug = debug)

    # Remove short clusters
    proc_img = remove_short_clusters(proc_img, levels, debug = debug)

    # Re-binarize
    proc_img = binarize(proc_img, debug = debug)

    # Dilate
    structure_length = 3
    proc_img = dilate(proc_img, structure_length, debug = debug)

    # Up sample
    upsample_factor = 2**num_downsamples
    proc_img = upsample(proc_img, debug = debug)

    # Connected components
    proc_img, unique_values = connected_components(proc_img, debug = debug)

    # Lines
    lines = get_lines(proc_img, debug = False)


    # Plot the result
    if debug:
        new_img = np.empty((img.shape[0], img.shape[1], 3))
        new_img[:,:,0] = img
        new_img[:,:,1] = img
        new_img[:,:,2] = img

        new_img[proc_img != 0,:] = [0,255,128]

        plot_img(new_img, show = False)
        plt.show()

    return lines
