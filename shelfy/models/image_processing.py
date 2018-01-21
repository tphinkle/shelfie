def get_book_lines(img, debug = False):

    # Convert to gs
    proc_img = np.mean(img[:,:], axis = 2).astype(np.uint8)


    # Down sample
    num_downsamples = 3
    for i in range(num_downsamples):
        proc_img = scipy.ndimage.interpolation.zoom(proc_img,.5)

        if debug:
            print('downsample', i)
            plot_img(proc_img, show = True)



    ## Sobel x
    proc_img = cv2.Sobel(proc_img, cv2.CV_8UC1, 1, 0, ksize = -1)**2.


    if debug:
        print('sobel x')
        plot_img(proc_img)



    # Standardize
    proc_img = (proc_img - np.min(proc_img))/np.max(proc_img)

    if debug:
        print('standardize')
        plot_img(proc_img)


    # Digitize
    img_max = np.max(proc_img)
    img_min = np.min(proc_img)
    num_levels = 4
    bins = [1.*i*(img_max-img_min)/num_levels for i in range(0, num_levels)]
    proc_img = np.digitize(proc_img, bins)

    if debug:
        print('digitize')
        plot_img(proc_img, show = True)



    # Binarize
    proc_img[proc_img == np.min(proc_img)] = 0
    proc_img[proc_img != 0] = 1


    if debug:
        print('binarize')
        plot_img(proc_img, show = True)


    # Horizontal erosion and subtraction
    for i in range(1):
        structure_length = 5*(i+1)
        #structure = np.ones((3,3))*structure_length
        structure = np.ones((3,3))*structure_length
        old_proc_img = np.copy(proc_img)
        proc_img = proc_img - scipy.ndimage.morphology.binary_erosion(proc_img, structure, 1)

        if debug:
            print('erode/subtract')
            plot_img(proc_img, show = True)


    # Vertical open close
    for i in range(1):
        structure_length = 200
        #structure = np.array([[0,1,0],[0,1,0],[0,1,0]])*structure_length
        structure = np.array([[0,1,0],[0,1,0],[0,1,0]])*structure_length
        proc_img = scipy.ndimage.morphology.binary_erosion(proc_img, structure, 3)

        if debug:
            print('morpho erode')
            plot_img(proc_img, show = True)

    # Vertical open
    for i in range(1):
        structure_length = 3
        #structure = np.array([[0,1,0],[0,1,0],[0,1,0]])*structure_length
        structure = np.array([[0,1,0],[0,1,0],[0,1,0]])*structure_length
        proc_img = scipy.ndimage.morphology.binary_dilation(proc_img, structure, 3)

        if debug:
            print('morpho dilate')
            plot_img(proc_img, show = True)





    # Connected components
    proc_img, unique_values = scipy.ndimage.label(proc_img, structure = np.ones((3,3)))

    unique_values = list(range(unique_values))





    if debug:
        for unique_value in unique_values:

            # Get slope and length of each connect component
            bright_pixels = np.where(proc_img == unique_value)
            points = np.hstack((bright_pixels[0].reshape(-1,1), bright_pixels[1].reshape(-1,1)))

            dx = np.max(points[:,0]) - np.min(points[:,0])
            dy = np.max(points[:,1]) - np.min(points[:,1])


    # Remove clusters too small
    drop_values = []
    threshold = proc_img.shape[0]*.35
    for unique_value in unique_values:
        bright_pixels = np.where(proc_img == unique_value)
        ptp = np.ptp(bright_pixels[0])



        if(ptp < threshold):
            drop_values.append(unique_value)

    for drop_value in drop_values:
        proc_img[proc_img == drop_value] = 0

    if debug:
        print('Remove clusters that are too small')
        plot_img(proc_img, show = True)


    # Re-binarize
    proc_img[proc_img != 0] = 1

    if debug:
        print('Binarize')
        plot_img(proc_img, show = True)


    # Horizontal dilate
    for i in range(1):
        structure_length = 3
        #structure = np.array([[0,1,0],[0,1,0],[0,1,0]])*structure_length
        structure = np.array([[1,1,1],[1,1,1],[1,1,1]])*structure_length
        proc_img = scipy.ndimage.morphology.binary_dilation(proc_img, structure, 1)

        if debug:
            print('morpho dilate')
            plot_img(proc_img, show = True)


    # Up sample
    proc_img = proc_img.repeat(8, axis = 0).repeat(8, axis = 1)


    # Connected components
    proc_img, unique_values = scipy.ndimage.label(proc_img, structure = np.ones((3,3)))
    unique_values = list(range(unique_values))

    # Lines
    ms = []
    bs = []
    for unique_value in unique_values:
        line = np.where(proc_img == unique_value)
        xs = line[1]
        ys = line[0]


        m, b, r, p, std = scipy.stats.linregress(xs,ys)
        ms.append(m)
        bs.append(b)




    if debug:
        new_img = np.empty((img.shape[0], img.shape[1], 3))
        new_img[:,:,0] = img
        new_img[:,:,1] = img
        new_img[:,:,2] = img

        new_img[proc_img != 0,:] = [0,255,128]

        plot_img(new_img, show = False)
        plt.show()

    return ms, bs
