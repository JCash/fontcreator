"""
Copyright @ 2013 Mathias Westerdahl
"""
from math import sqrt
import numpy as np
import numpy.ctypeslib
import utils
import freetype as ft


class FontException(Exception):
    pass


def make_array_from_bitmap(_bitmap, bitdepth=8):
    """ Converts a FTBitmap into a numpy array """
    bitmap = ft.Bitmap()
    ft.bitmap_convert(_bitmap, bitmap, bitdepth)

    width, rows, pitch = bitmap.width, bitmap.rows, bitmap.pitch

    a = numpy.ctypeslib.as_array(bitmap.buffer, (rows, pitch) ).transpose()
    
    return a[:width,:]


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
    
    :param bottom: A numpy array of shape (x, y, 4)
    :param top:    A numpy array of shape (x, y, 4)
    :return:       Returns a new numpy.array with the same dtype as the top array
    """
    assert bottom.shape == top.shape, "Cannot blend two images of different shapes: %s != %s" % (str(bottom.shape), str(top.shape))

    if bottom.dtype != top.dtype:
        bottom = bottom.astype(top.dtype)
    """
    br, bg, bb, ba = split_channels(bottom)
    tr, tg, tb, ta = split_channels(top)

    oneminusa = 1.0 - ta
    
    out = np.empty_like(bottom)
    out[:, :, 0] = br * oneminusa + tr * ta
    out[:, :, 1] = bg * oneminusa + tg * ta
    out[:, :, 2] = bb * oneminusa + tb * ta
    out[:, :, 3] = np.maximum(ba, ta)
    #return out
    #return top
    out = top.copy()
    out[:, :, 3] = np.maximum(ba, ta)
    return out
    """

    br, bg, bb, ba = split_channels(bottom)
    tr, tg, tb, ta = split_channels(top)

    out = np.empty_like(bottom)
    out[:, :, 0] = br + (tr-br) * ta
    out[:, :, 1] = bg + (tg-bg) * ta
    out[:, :, 2] = bb + (tb-bb) * ta
    out[:, :, 3] = np.maximum(ba, ta)
    return out
    


def pad_bitmap(bitmap, left, top, right, bottom, value, debug=False):
    """ Pads a bitmap with pixels on each side. The new cells are applied the value
    
    :param bitmap:   A numpy array
    :param left:     The number of pixels that should be added to the left
    :param top:      The number of pixels that should be added to the top
    :param right:    The number of pixels that should be added to the right
    :param bottom:   The number of pixels that should be added to the bottom
    :param value:    The value to insert
    :return:         The padded numpy array
    """
    
    pl, pt, pr, pb = left, top, right, bottom
    """
    s = bitmap.shape
    if len(s) == 2:
        left = np.array([value] * (left*s[1]), bitmap.dtype ).reshape(-1, s[1])
        right = np.array([value] * (right*s[1]), bitmap.dtype ).reshape(-1, s[1])
    elif len(s) == 3:
        left = np.array([value] * (left*s[1]*s[2]), bitmap.dtype ).reshape(-1, s[1], s[2])
        right = np.array([value] * (right*s[1]*s[2]), bitmap.dtype ).reshape(-1, s[1], s[2])

    bm = np.concatenate( (left, bitmap, right), axis=0 )
    s = bm.shape

    if len(s) == 2:
        top = np.array([value] * (top*s[0]), bitmap.dtype ).reshape(s[0], -1)
        bottom = np.array([value] * (bottom*s[0]), bitmap.dtype ).reshape(s[0], -1)
    elif len(s) == 3:
        top = np.array([value] * (top*s[0]*s[2]), bitmap.dtype ).reshape(s[0], -1, s[2])
        bottom = np.array([value] * (bottom*s[0]*s[2]), bitmap.dtype ).reshape(s[0], -1, s[2])

    bm = np.concatenate( (top, bm, bottom), axis=1 )
    
    #return bm
    """
    
    left, top, right, bottom = pl, pt, pr, pb
    s = list(bitmap.shape)
    s[0] += left + right
    s[1] += top + bottom
    
    out = np.empty( tuple(s), dtype=bitmap.dtype)
    out.fill( value )
    
    right = left + bitmap.shape[0]
    bottom = top + bitmap.shape[1]
    
    if len(out.shape) > 2:
        out[left:right, top:bottom, :] = bitmap
    else:
        out[left:right, top:bottom] = bitmap.flatten().reshape( bitmap.shape )

    return out


def create_1d_lanczos_kernel(radius):
    # formula taken from http://en.wikipedia.org/wiki/Gaussian_blur
    def calc(x): return 0 if abs(x) > radius else (1 if x == 0 else np.sin(x*np.pi)/x)
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
        sigma = sqrt( -(vert * vert) / -3);
    
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
    
    :param bitmap:   A 2-D numpy bitmap of dimensions (e.g. bitmap.shape == (X,Y))
    :param char:     A CharacterInfo
    :param replace:  A 2 element array that lets you replace the bitmap values with better suited ascii characters.
                     Can be None, then the original values will be printed.
                     Rule::
                     
                         replace[1] if bitmap[x,y] else replace[0]
    """
    if char:
        print "(utf-8, unicode) =", (hex(char.utf8), char.unicode)

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


def print_ascii2(bm):
    for y in xrange(bm.shape[1]):
        s = ''
        for x in xrange(bm.shape[0]):
            v = bm[x,y]
            c = None
            if v == 0:
                c = ' '
            elif v < 64:
                c = '.'
            elif v < 128:
                c = 'o'
            elif v < 196:
                c = 'O'
            elif v <= 255:
                c = '@'
            else:
                raise Exception("Value not ok: %s" % str(v))
            s += c
        print s
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

