"""
binpack
=======

Copyright @ 2013 Mathias Westerdahl

Brief
------

The bin packing functions are implemented by Jukka Jylanki:

- `A thousand ways to pack the bin - A practical approach to two-dimensional rectangle bin packing <http://clb.demon.fi/files/RectangleBinPack.pdf>`_
- `RectangleBinPack.zip <http://clb.demon.fi/files/RectangleBinPack/RectangleBinPack.zip>`_ (public domain) 

An example of the Skyline Bottom Left packing algorithm which is default in the font creator
 
.. image:: binpack_skyline_bl.png

Reference
---------


"""

import sys, os
import ctypes
from ctypes import c_void_p, c_float, c_int32, c_bool


if sys.platform == 'darwin':
    _suffix = '.dylib'
elif sys.platform == 'win32':
    _suffix = '.dll'
elif sys.platform == 'linux2':
    _suffix = '.so'

_dirpath = os.path.dirname(__file__)
_binpack = ctypes.cdll.LoadLibrary(os.path.join(_dirpath, '_binpack%s' % _suffix))

#: Bottom left
SKYLINE_BL = 0
#: Min Waste
SKYLINE_MW = 1
#: Positions the rectangle against the short side of a free rectangle into which it fits the best.
MAXRECTS_BSSF = 2
#: Positions the rectangle against the long side of a free rectangle into which it fits the best.
MAXRECTS_BLSF = 3
#: Positions the rectangle into the smallest free rect into which it fits.
MAXRECTS_BAF = 4
#: Does the Tetris placement.
MAXRECTS_BL = 5
#: Chooses the placement where the rectangle touches other rects as much as possible.
MAXRECTS_CP = 6


c_packer_p = c_void_p

class Rect(ctypes.Structure):
    """ A rectangle struct (x, y, w, h) 
    """
    _fields_ = [
        ('x', c_int32),
        ('y', c_int32),
        ('width', c_int32),
        ('height', c_int32),
    ]
    
    def __str__(self):
        return 'Rect(%d, %d, %d, %d)' % (self.x, self.y, self.width, self.height)

_create_packer = _binpack.create_packer
_create_packer.restype = c_packer_p
_create_packer.argtypes = [c_int32, c_int32, c_int32, c_bool]

_destroy_packer = _binpack.destroy_packer
_destroy_packer.argtypes = [c_packer_p]

_get_occupancy = _binpack.get_occupancy
_get_occupancy.restype = c_float
_get_occupancy.argtypes = [c_packer_p]

_pack_rect = _binpack.pack_rect
_pack_rect.restype = Rect
_pack_rect.argtypes = [c_packer_p, c_int32, c_int32]


def create_packer(type, width, height, allow_rotate):
    """ Creates a packer instance for use with consecutive calls to pack_rect()
    
    :param type:         The packing algorithm. Must be one of:
    
                        - SKYLINE_BL
                        - SKYLINE_MW
                        - MAXRECTS_BSSF
                        - MAXRECTS_BLSF
                        - MAXRECTS_BAF
                        - MAXRECTS_BL
                        - MAXRECTS_CP
        
    :param width:        The width of the packing bin (won't change)
    :param height:       The height of the packing bin (won't change)
    :param allow_rotate: Tells the packer if it is allowed to rotate the rects.
    :return:             Returns the packer instance. Must be destroyed with destroy_packer()
    """
    return _create_packer(type, width, height, allow_rotate)


def destroy_packer(packer):
    """  Destroys the packer instance
    
    :param packer:   The packer instance
    """
    _destroy_packer(packer)


def get_occupancy(packer):
    """ Returns the occupancy as a value between 0.0 and 1.0
    
    :param packer:   The packer instance
    :return:         The current occupancy as a unit value
    """
    return _get_occupancy(packer)


def pack_rect(packer, w, h):
    """ Packs a rectangle in the bin.
    
    :param w:   The width of the rect
    :param h:   The height of the rect
    :return:    Returns (0, 0, 0, 0) if the bin is full
                Returns (x, y, W, H) if the rect was packed
                Returns (x, y, H, W) if the rect was packed and rotated
    """
    return _pack_rect(packer, w, h)

if __name__ == '__main__':
    import time
    import Image, ImageDraw
    from random import seed, randint
    
    data = []
    for _ in xrange(700):
        w = randint(10, 20)
        h = randint(10, 30)
    
        r = randint(100, 200)
        g = randint(100, 200)
        b = randint(100, 200)
        data.append( (w, h, r, g, b) )
    
    def _sort(a, b):
        return a[1] - b[1]  # sort by height
    data.sort(_sort)
    
    for typ, name in ( (SKYLINE_BL, 'skyline_bl'), (SKYLINE_MW, 'skyline_mw'), (MAXRECTS_BSSF, 'maxrects_bssf'), (MAXRECTS_CP, 'maxrects_cp'), (MAXRECTS_BAF, 'maxrects_baf') ):
        
        iw = 512
        ih = 512
        im = Image.new( 'RGB', (iw, ih), (0,0,0) )
        
        draw = ImageDraw.Draw(im)
        
        packer = create_packer(typ, iw, ih, False)
        
        seed(1234567)

        timestart = time.time()
        
        count = 0
        for w, h, r, g, b in data:
            
            rect = pack_rect( packer, w, h )
            if rect.height == 0:
                break
            
            draw.rectangle( (rect.x, rect.y, rect.x + rect.width, rect.y + rect.height), fill=(r,g,b) )
            count += 1
        
        print '%s: Packed %d rects in %f seconds. Filled %d %%' % ( name, count, time.time() - timestart, (get_occupancy(packer) * 100))
        destroy_packer(packer)
        
        draw.rectangle( (30,30, 50, 60), fill=(230,120,100) )
        
        im.save('build/binpack_%s.png' % name)
