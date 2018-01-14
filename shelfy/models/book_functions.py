import io

import numpy as np
import matplotlib.pyplot as plt

from google.cloud import vision
from google.cloud.vision import types



class BoundingBox(object):
    '''
    A box containing a word or multiple words.
    The BoundingBox is defined by the vertex coordinates of the box;
    from the vertex coordinate, we can get the angles of the bounding box,
    the bounding box's center position, etc.
    '''

    def __init__(self, xs, ys):
        self.xs = xs
        self.ys = ys

    @property
    def center(self):
        '''
        Returns the center of the bounding box object
        '''
        xc = (self.xs[0] + self.xs[1] + self.xs[2] + self.xs[3])/4.
        yc = (self.ys[0] + self.ys[1] + self.ys[2] + self.ys[3])/4.

        return xc, yc


    def image_to_bounding_box_coordinate_transformation(self, x, y):
        '''
        The coordinate frame of the bounding box is defined by its center (the origin), the long-axis
        (x-axis, or along the spine usually), and the short-axis (y-axis, lateral to spine direction usually)
        This takes coordinates
        '''
        long_axis_angle = self.vertical_axis_angle
        xc, yc = self.center

        xp = np.cos(long_axis_angle)*(x-xc) + np.sin(long_axis_angle)*(y-yc)
        yp = -np.sin(long_axis_angle)*(x-xc) + np.cos(long_axis_angle)*(y-yc)

        return (xp, yp)

    def fit_line(self):
        '''
        Gets the line in the form y=mx+b (returns slope and y-intercept) of the bounding box object.
        Does this by finding the long axis angle and center
        Returned as a tuple
        '''

        center = self.center
        x = center[0]
        y = center[1]

        m = np.tan(self.long_axis_angle)
        b = y-m*x

        return (m, b)

    @property
    def long_axis_angle(self):
        '''
        Returns the long axis angle of the bounding box object
        '''

        l1 = (self.ys[1]-self.ys[0])**2. + (self.xs[1]-self.xs[0])**2.
        l2 = (self.ys[2]-self.ys[1])**2. + (self.xs[2]-self.xs[1])**2.


        if l1 >= l2:
            return np.arctan2(self.ys[1]-self.ys[0], self.xs[1]-self.xs[0])
        else:
            return np.arctan2(self.ys[2]-self.ys[1], self.xs[2]-self.xs[1])

    @property
    def vertical_axis_angle(self):
        '''
        Returns ShortAxisAngle or LongAxisAngle; whichever happens to align vertically with the image
        '''

        long_axis_angle = self.long_axis_angle
        short_axis_angle = self.short_axis_angle

        if np.abs(np.sin(long_axis_angle)) > np.abs(np.sin(short_axis_angle)):
            return long_axis_angle
        else:
            return short_axis_angle


    @property
    def short_axis_angle(self):
        '''
        Returns the short axis of the bounding box object
        '''

        l1 = (self.ys[1]-self.ys[0])**2. + (self.xs[1]-self.xs[0])**2.
        l2 = (self.ys[2]-self.ys[1])**2. + (self.xs[2]-self.xs[1])**2.


        if l1 <= l2:
            return np.arctan2(self.ys[1]-self.ys[0], self.xs[1]-self.xs[0])
        else:
            return np.arctan2(self.ys[2]-self.ys[1], self.xs[2]-self.xs[1])



    def from_google_bounding_poly(bounding_poly):
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





class Word(object):
    '''
    Simple Word class consisting of the word"s value ('string') and the bounding box ('bounding_box')
    containing the word
    '''

    def __init__(self, string, bounding_box):
        self.string = string
        self.bounding_box = bounding_box

    def from_google_text(google_text):
        '''
        Converts a google text_annotation into a simpler Word format
        args:
            google_text: the google text_annotation object
        '''

        string = google_text.description
        bounding_box = BoundingBox.from_google_bounding_poly(google_text.bounding_poly)

        return Word(string, bounding_box)


class Spine(object):
    '''
    Simple struct that holds the list of words on the same spine.
    Orders the words by their y-value
    Also creates a 'sentence', a string hwere instead of storing the words
    in a list, the words are stored in a single string separated by spaces.
    '''

    def __init__(self, words):


        # Store the ordered words
        ys = np.array([word.bounding_box.center[1] for word in words])
        ordered_words = [words[i] for i in np.argsort(ys)]
        self.words = ordered_words


        # Format the words as a sentence
        sentence = ''
        for word in self.words:
            sentence += word.string + ' '
        self.sentence = sentence


class Book(object):
    '''
    An object that holds all of the relevent information for a book.
    Also holds the Spine object that the book was determined from.
    '''

    def __init__(self, book_info, spine):
        '''
        book_info is a dict of information (e.g., {'title':[title]}).
        spine is the Spine object that the book info was determined from.
        '''
        self.book_info = book_info
        self.spine = spine


    @property
    def similarity(self):
        return 0






def plot_boxed_image_words(img, words, color = 'red', show = True):
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

def plot_annotated_image_words(img, words, color = 'red', show = True):
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
        text_y = word.bounding_box.center[1]

        angle = word.bounding_box.long_axis_angle
        plt.text(text_x, text_y, word.string, size = 18, ha = 'left', va = 'center', rotation = -angle*180./np.pi, color = 'red', fontweight = 'bold')

    if show:
        plt.show()


def save_spines(spines, file_path):
    '''
    Save the words along each spine to the specified file path.
    '''
    with open(file_path, 'w') as file_handle:
        writer = csv.writer(file_handle, delimiter = ',')
        for spine in spines:
            writer.writerow([word.string for word in spine.words])



def plot_annotated_image_google(img, texts):
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




def get_spines_from_words(words):
    '''
    Matches words that belong on the same spine into a 'Spine' object
    Algorithm explanation:
        - Starts with a bounding_box object and calculates its VerticleAxisAngle();
        whichever of the two bounding_box's axis angles which is more closely
        aligned with the image vertical (i.e., whichever has a larger sin
        component)
        - This axis defines the proposed axis of a book spine
        - Calculates the position of every other bounding_box in the image
        which has not been matched yet, in the coordinate from of the first
        bounding_box object
        - bounding_boxes whose position is within a certain tolerance of the
        axis of the spine are determined to belong to the same book; all others
        are ignored
        - The matched bounding_boxes are removed from the pool of words to consider
        matching, and the process is repeated with the rest of the unmatched books
    '''

    spines = []

    xcs = []
    ycs = []
    thetas = []

    yc_tolerance = 100
    theta_tolerance = 1000

    matched_words = []
    for i, special_word in enumerate(words):
        matches = []
        # Check if word has already been matched
        if i in matched_words:
            continue

        for j, word in enumerate(words):

            # Don't match a word with itself
            if i == j:
                continue

            # Check if word has already been matched
            if j in matched_words:
                continue

            x, y = word.bounding_box.center
            xc, yc = special_word.bounding_box.ImageToBoundingBoxCoordinateTransformation(x, y)
            theta = np.abs(word.bounding_box.vertical_axis_angle - special_word.bounding_box.vertical_axis_angle)%(np.pi/2.)
            xcs.append(xc)
            ycs.append(yc)
            thetas.append(theta)



            # If the difference in y value is below tolerance, append to the list of matches
            if np.abs(yc) < yc_tolerance and np.abs(theta) < theta_tolerance:
                if i not in matched_words:
                    matched_words.append(i)
                matched_words.append(j)
                matches.append(j)

        spines.append(Spine([special_word] + [words[match] for match in matches]))


    return spines
