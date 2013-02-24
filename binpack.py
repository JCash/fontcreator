"""
Copyright @ 2013 Mathias Westerdahl
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

SKYLINE_BL = 0
SKYLINE_MW = 1
MAXRECTS_BSSF = 2
MAXRECTS_BLSF = 3
MAXRECTS_BAF = 4
MAXRECTS_BL = 5
MAXRECTS_CP = 6


c_packer_p = c_void_p

class Rect(ctypes.Structure):
    _fields_ = [
        ('x', c_int32),
        ('y', c_int32),
        ('width', c_int32),
        ('height', c_int32),
    ]
    
    def __str__(self):
        return 'Rect(%d, %d, %d, %d)' % (self.x, self.y, self.width, self.height)

create_packer = _binpack.create_packer
create_packer.restype = c_packer_p
create_packer.argtypes = [c_int32, c_int32, c_int32, c_bool]

destroy_packer = _binpack.destroy_packer
destroy_packer.argtypes = [c_packer_p]

get_occupancy = _binpack.get_occupancy
get_occupancy.restype = c_float
get_occupancy.argtypes = [c_packer_p]

pack_rect = _binpack.pack_rect
pack_rect.restype = Rect
pack_rect.argtypes = [c_packer_p, c_int32, c_int32]


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
