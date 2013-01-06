import os
import logging
import Image
import numpy as np

def write(options, info, image):
    """ Writes the image to disc
    """
    
    image = (image * 255.0).astype(np.uint8)

    # transpose
    r, g, b, a = image.T
    
    if info.texturechannels == 'RGBA':
        image = np.dstack((r,g,b,a))
    elif info.texturechannels == 'RGB':
        image = np.dstack((r,g,b))
    elif info.texturechannels in ('R', 'L'):
        image = r
    elif info.texturechannels == 'G':
        image = g
    elif info.texturechannels == 'B':
        image = b
    elif info.texturechannels in 'A':
        image = a
    else:
        assert False, "Unknown channel format: '%s'" % (info.texturechannels)
        
    path = os.path.splitext(options.output)[0] + info.textureformat
    pilimage = Image.fromarray( image )
    pilimage.save( path )
    logging.debug("Wrote %s" % path)
