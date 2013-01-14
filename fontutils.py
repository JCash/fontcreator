import math
import numpy as np
import utils


class FontException(Exception):
    pass


def split_channels(image):
    """ Takes a numpy array and splits its' channels into a 3 or 4 tuple (views)

    :return: A 3 or 4 tuple, with each element containing the corresponding color channel
    """
    if image.shape[2] == 3:
        return (image[:, :, 0], image[:, :, 1], image[:, :, 2])
    elif image.shape[2] == 4:
        return (image[:, :, 0], image[:, :, 1], image[:, :, 2], image[:, :, 3])
    assert False, "Wrong shape: %s" % str(image.shape)


def multiply_color(image, color):
    ir, ig, ib, ia = split_channels(image)
    cr, cg, cb, ca = color
    ir *= cr
    ig *= cg
    ib *= cb
    ia *= ca
    return image


def pre_multiply_alpha(image):
    r,g,b,a = split_channels(image)
    r *= a
    g *= a
    b *= a
    return image


def alpha_blend(bottom, top):
    """ Creates a new copy by alpha blending top onto bottom
    """
    br, bg, bb, ba = split_channels(bottom)
    tr, tg, tb, ta = split_channels(top)

    r = br + (tr-br) * ta
    g = bg + (tg-bg) * ta
    b = bb + (tb-bb) * ta
    a = np.maximum(ba, ta)
    return np.clip(np.dstack((r, g, b, a)), 0.0, 1.0)


def pad_bitmap(bitmap, left, top, right, bottom, value):
    """ Pads a bitmap with x pixels in width, and y pixels in height
    The new elements gets the 'value'
    @bitmap         A numpy array
    @param left     The number of pixels that should be added to the left
    @param top      The number of pixels that should be added to the top
    @param right    The number of pixels that should be added to the right
    @param bottom   The number of pixels that should be added to the bottom
    @param value    A float
    """
    s = bitmap.shape
    if len(s) == 2:
        left = np.array([value] * (left*s[1]), float ).reshape(-1, s[1])
        right = np.array([value] * (right*s[1]), float ).reshape(-1, s[1])
    elif len(s) == 3:
        left = np.array([value] * (left*s[1]*s[2]), float ).reshape(-1, s[1], s[2])
        right = np.array([value] * (right*s[1]*s[2]), float ).reshape(-1, s[1], s[2])

    bm = np.concatenate( (left, bitmap, right), axis=0 )
    s = bm.shape

    if len(s) == 2:
        top = np.array([value] * (top*s[0]), float ).reshape(s[0], -1)
        bottom = np.array([value] * (bottom*s[0]), float ).reshape(s[0], -1)
    elif len(s) == 3:
        top = np.array([value] * (top*s[0]*s[2]), float ).reshape(s[0], -1, s[2])
        bottom = np.array([value] * (bottom*s[0]*s[2]), float ).reshape(s[0], -1, s[2])

    bm = np.concatenate( (top, bm, bottom), axis=1 )

    return bm


def create_1d_lanczos_kernel(radius):
    # formula taken from http://en.wikipedia.org/wiki/Gaussian_blur
    def calc(x): return 0 if abs(x) > radius else (1 if x == 0 else sin(x*np.pi)/x)
    k = np.array( map(calc, range(-radius,radius+1)) )
    return k / np.sum(k)



def create_1d_gaussian_kernel(radius, sigma=None):
    """ Creates a 1D gaussian kernel given a radius and a constant
    Implementation taken from http://en.wikipedia.org/wiki/Gaussian_blur
    
    :param radius: The radius of the kernel
    :param a:    A constant that controls the shape of the bell curve
    :return:     A 1D numpy.array with shape (radius*2+1,)
    """
    if sigma is None:
        vert = radius + 1.0;
        sigma = math.sqrt( -(vert * vert) / -3);
    
    f = 1.0 / ( sigma * np.sqrt(2.0 * np.pi) )
    sigma2 = sigma**2
    def calc(x):
        return f * np.exp( -(x**2 / (2.0 * sigma2)) )
    k = np.array( [calc(i) for i in range(-radius,radius+1)], dtype=np.float32 )
    k /= np.sum(k)
    return k


def create_2d_circle_kernel(radius):
    """ Creates a kernel where the cells within the radius gets a value of 1.0
    
    :param radius: The radius of the kernel
    :return: A numpy.array with shape (radius*2+1, radius*2+1) 
    """
    return np.array([ np.sqrt( x * x + y * y ) <= float(radius) for y in xrange(-radius, radius+1) for x in xrange(-radius, radius+1)], dtype=np.float32).reshape( radius*2+1, radius*2+1 )


def blur_image(image, radius):
    k = create_1d_gaussian_kernel(radius)
    blurred = utils.convolve1d(image, k, axis=0)
    blurred = utils.convolve1d(blurred, k, axis=1)
    return blurred

def blur_image_kernel1D(image, kernel):
    blurred = utils.convolve1d(image, kernel, axis=0)
    blurred = utils.convolve1d(blurred, kernel, axis=1)
    return blurred


def print_ascii(bitmap, char=None, replace=['.', '@']):
    """ For debugging the contents of a numpy bitmap
    @param bitmap    A 2-D numpy bitmap of dimensions (e.g. bitmap.shape == (X,Y))
    @param char      A CharacterInfo
    @param replace   A 2 element array that lets you replace the bitmap values with better suited ascii characters.
                     Rule: replace[1] if bitmap[x,y] else replace[0]
                     Can be None, then the original values will be printed
    """
    if char:
        print "(utf-8, unicode) =", (hex(char.character), char.unicode)

    bm = bitmap

    xformat = "%" + str( len(str(bm.shape[0]-1) ) ) + "d"
    yformat = "%" + str( len(str(bm.shape[1]-1) ) ) + "d: "

    print " " * ( len(str(bm.shape[1])) + 1) + "X",
    print " ".join([xformat % x for x in xrange(bm.shape[0])])
    print " " * ( len(str(bm.shape[1])) -1) + "Y"

    for y in xrange(bm.shape[1]):
        print yformat % y,
        for x in xrange(bm.shape[0]):
            if replace:
                print replace[ 1 if bm[x,y] else 0 ].rjust( len(str(bm.shape[0]-1) ) ),
            else:
                print xformat % int( bm[x,y]*255 ),
        print ""
    print ""
    

if __name__ == '__main__':
    import Image
    
    """
    im = Image.open('/Users/mawe/Pictures/flower.jpg')
    image = np.array(im.getdata(), np.uint8).reshape(im.size[1], im.size[0], 3)
    
    kernel = create_1d_gaussian_kernel(5)
    #kernel = [1,2,3,5,3,2,1]
    #kernel = [1,1,1,1,1]
    #s = float(sum(kernel))
    #kernel = np.array([x / s for x in kernel], dtype=np.float32)
    
    out = utils.convolve1d(image, kernel, 0)
    out = utils.convolve1d(out, kernel, 1)
    
    outim = Image.fromarray(out)
    outim.save('/Users/mawe/Pictures/out.png')
    
    
    im = Image.open('/Users/mawe/Pictures/lena.jpg')
    image = np.array(im.getdata(), np.uint8).reshape(im.size[1], im.size[0], 3)
    
    kernel = create_2d_circle_kernel(3)
    out = utils.maximum(image, kernel)
    
    outim = Image.fromarray(out)
    outim.save('/Users/mawe/Pictures/lena_maximum.png')
    
    out = utils.minimum(image, kernel)
    
    outim = Image.fromarray(out)
    outim.save('/Users/mawe/Pictures/lena_minimum.png')

    im = Image.open('/Users/mawe/Pictures/a.png')
    image = np.array(im.getdata(), np.uint8).reshape(im.size[1], im.size[0], 4)
    
    r, g, b, a = (image[:, :, 0], image[:, :, 1], image[:, :, 2], image[:, :, 3])
    image = np.dstack((r, g, b, a))
    
    kernel = create_2d_circle_kernel(5)
    out = utils.maximum(image, kernel)
    
    outim = Image.fromarray(out)
    outim.save('/Users/mawe/Pictures/a_outline.png')
    
    out = blur_image(image, 10)
    
    outim = Image.fromarray(out)
    outim.save('/Users/mawe/Pictures/a_blur.png')
    
    """
    
    im = Image.open('/Users/mawe/Pictures/a.png')
    image = np.array(im.getdata(), np.uint8).reshape(im.size[1], im.size[0], 4)
    
    image = np.dstack((image[:, :, 0],))
    
    out = utils.calculate_sedt(image, 14)
    

    outim = Image.fromarray( np.dstack( (out, out, out, np.ones_like(out)*255 ) ) )
    #outim = Image.fromarray( out )
    outim.save('build/a_sed.png')
    
    # http://code.google.com/p/freetype-gl/

