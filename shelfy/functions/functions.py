import numpy as np
import matplotlib.pyplot as plt





class Spine(object):
    def __init__(self, words):

        ys = np.array([word.bounding_box.Center()[1] for word in words])
        ordered_words = [words[i] for i in np.argsort(ys)]

        self.words = ordered_words










class Word(object):
    '''
    Simple Word class consisting of the word"s value ('string') and the bounding box ('bounding_box')
    containing the word
    '''

    def __init__(self, string, bounding_box):
        self.string = string
        self.bounding_box = bounding_box

    def FromGoogleText(google_text):
        '''
        Converts a google text_annotation into a simpler Word format
        args:
            google_text: the google text_annotation object
        '''

        string = google_text.description
        bounding_box = BoundingBox.FromGoogleBoundingPoly(google_text.bounding_poly)

        return Word(string, bounding_box)


class BoundingBox(object):
    def __init__(self, xs, ys):
        self.xs = xs
        self.ys = ys

    def Center(self):
        '''
        Returns the center of the bounding box object
        '''
        xc = (self.xs[0] + self.xs[1] + self.xs[2] + self.xs[3])/4.
        yc = (self.ys[0] + self.ys[1] + self.ys[2] + self.ys[3])/4.

        return xc, yc


    def ImageToBoundingBoxCoordinateTransformation(self, x, y):
        '''
        The coordinate frame of the bounding box is defined by its center (the origin), the long-axis
        (x-axis, or along the spine usually), and the short-axis (y-axis, lateral to spine direction usually)
        This takes coordinates
        '''
        #long_axis_angle = self.LongAxisAngle()
        long_axis_angle = self.VerticalAxisAngle()
        xc, yc = self.Center()

        xp = np.cos(long_axis_angle)*(x-xc) + np.sin(long_axis_angle)*(y-yc)
        yp = -np.sin(long_axis_angle)*(x-xc) + np.cos(long_axis_angle)*(y-yc)

        return (xp, yp)

    def FitLine(self):
        '''
        Gets the line in the form y=mx+b (returns slope and y-intercept) of the bounding box object.
        Does this by finding the long axis angle and center
        Returned as a tuple
        '''

        center = self.Center()
        x = center[0]
        y = center[1]

        m = np.tan(self.LongAxisAngle())
        b = y-m*x

        return (m, b)

    def LongAxisAngle(self):
        '''
        Returns the long axis angle of the bounding box object
        '''

        l1 = (self.ys[1]-self.ys[0])**2. + (self.xs[1]-self.xs[0])**2.
        l2 = (self.ys[2]-self.ys[1])**2. + (self.xs[2]-self.xs[1])**2.


        if l1 >= l2:
            return np.arctan2(self.ys[1]-self.ys[0], self.xs[1]-self.xs[0])
        else:
            return np.arctan2(self.ys[2]-self.ys[1], self.xs[2]-self.xs[1])

    def VerticalAxisAngle(self):
        '''
        Returns ShortAxisAngle or LongAxisAngle; whichever happens to align vertically with the image
        '''

        long_axis_angle = self.LongAxisAngle()
        short_axis_angle = self.ShortAxisAngle()

        if np.abs(np.sin(long_axis_angle)) > np.abs(np.sin(short_axis_angle)):
            return long_axis_angle
        else:
            return short_axis_angle



    def ShortAxisAngle(self):
        '''
        Returns the short axis of the bounding box object
        '''

        l1 = (self.ys[1]-self.ys[0])**2. + (self.xs[1]-self.xs[0])**2.
        l2 = (self.ys[2]-self.ys[1])**2. + (self.xs[2]-self.xs[1])**2.


        if l1 <= l2:
            return np.arctan2(self.ys[1]-self.ys[0], self.xs[1]-self.xs[0])
        else:
            return np.arctan2(self.ys[2]-self.ys[1], self.xs[2]-self.xs[1])



    def FromGoogleBoundingPoly(bounding_poly):
        '''
        Factory function for creating a vertex from a bounding poly
        args:
            bounding_poly: the bounding_poly object
        '''

        xs = []
        ys = []
        for vertex in bounding_poly.vertices:
            xs.append(vertex.x)
            ys.append(vertex.y)

        return BoundingBox(xs, ys)



def GoogleBoundingPolyToVertices(bounding_poly):
    '''
    Converts the vertices in a bounding_poly object to a list of tuples (more convenient
    to work with)
    args:
        bounding_poly: The bounding_poly object
    '''

    for vertex in bounding_poly.vertices:
        x = vertex.x
        y = vertex.y
        vertices.append((x,y))

    return vertices

def PlotBoxedImage(img, words):
    if type(words) == 'text_annotations':
        PlotBoxedImage_GoogleCloudVision()
    elif type(words) == '__main__.Words':
        PlotBoxedImage_Words()

def PlotBoxedImage_Words(img, words, color = 'red', show = True):
    '''
    Plots an image alongside all of the bounding boxes found by the GoogleCloudVision
    document_text_detection() function
    args:
        img: the img, should be in normal numpy format
        texts: the text_annotations object returned by the GoogleCloudVision api
    '''

    for word in words:
        if color == 'random':
            color = np.random.rand(3)*1.
        bb = word.bounding_box
        plt.plot([bb.xs[0], bb.xs[1]], [bb.ys[0], bb.ys[1]], lw = 3, c = color)
        plt.plot([bb.xs[1], bb.xs[2]], [bb.ys[1], bb.ys[2]], lw = 3, c = color)
        plt.plot([bb.xs[2], bb.xs[3]], [bb.ys[2], bb.ys[3]], lw = 3, c = color)
        plt.plot([bb.xs[3], bb.xs[0]], [bb.ys[3], bb.ys[0]], lw = 3, c = color)

    plt.imshow(img, cmap = 'gray')

    if show:
        plt.show()

def PlotAnnotatedImage_Words(img, words, color = 'red', show = True):
    '''
    Plots the boxed words, but also labels them
    '''
    PlotBoxedImage_Words(img, words, color = color, show = False)

    for word in words:
        bounding_box = word.bounding_box
        x0 = (word.bounding_box.xs[0] + word.bounding_box.xs[1])/2.
        x1 = (word.bounding_box.xs[1] + word.bounding_box.xs[2])/2.
        x2 = (word.bounding_box.xs[2] + word.bounding_box.xs[3])/2.
        x3 = (word.bounding_box.xs[3] + word.bounding_box.xs[0])/2.

        text_x = np.max(np.array([x0,x1,x2,x3]))
        text_y = word.bounding_box.Center()[1]

        angle = word.bounding_box.LongAxisAngle()
        plt.text(text_x, text_y, word.string, size = 18, ha = 'left', va = 'center', rotation = -angle*180./np.pi, color = 'red', fontweight = 'bold')

    if show:
        plt.show()


def SaveSpines(spines, file_path):
    '''
    Save the words along each spine to the specified file path.
    '''
    with open(file_path, 'w') as file_handle:
        writer = csv.writer(file_handle, delimiter = ',')
        for spine in spines:
            writer.writerow([word.string for word in spine.words])



def PlotAnnotatedImage_GoogleCloudVision(img, texts):
    '''
    Plots an image alongside all of the bounding boxes found by the GoogleCloudVision
    document_text_detection() function
    args:
        img: the img, should be in normal numpy format
        texts: the text_annotations object returned by the GoogleCloudVision api
    '''



    for text in texts:
        bb = BoundingBox.FromGoogleBoundingPoly(text.bounding_poly)
        plt.plot([bb.xs[0], bb.xs[1]], [bb.ys[0], bb.ys[1]], lw = 3, c = 'r')
        plt.plot([bb.xs[1], bb.xs[2]], [bb.ys[1], bb.ys[2]], lw = 3, c = 'r')
        plt.plot([bb.xs[2], bb.xs[3]], [bb.ys[2], bb.ys[3]], lw = 3, c = 'r')
        plt.plot([bb.xs[3], bb.xs[0]], [bb.ys[3], bb.ys[0]], lw = 3, c = 'r')

    plt.imshow(img, cmap = 'gray')

    plt.show()
