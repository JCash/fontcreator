"""
This module lets you choose the PIL package as texture writer.
PIL supports a range of formats such as bmp, jpg, tga, png.
PIL also allows for custom file formats. 


.. py:attribute:: texturechannels

    Designates what channels should be written out to disc.
    Possible values are any permutation of the letters R, G, B, A and L.
    L gives you the red channel
    
    Defaults to 'RGBA'

.. py:attribute:: textureformat

    The texture format that will be used. 
    Defaults to '.png'

Example::

    texturewriter = fonttexout_pil
    
    [fonttexout_pil]
    textureformat = .png
    texturechannels = 'RGBA'


"""

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
    
    channels = getattr(info, 'texturechannels', None)
    if channels is None:
        channels = 'RGBA'
    
    d = { 'R' : r, 'G' : g, 'B' : b, 'A' : a, 'L' : r }
    
    outchannels = []
    for c in channels:
        outchannels.append(d[c.upper()])
    
    if len(outchannels) > 1:
        image = np.dstack( tuple(outchannels) )
    else:
        image = outchannels[0]
            
    path = os.path.splitext(options.output)[0] + info.textureformat
    pilimage = Image.fromarray( image )
    pilimage.save( path )
    logging.debug("Wrote %s" % path)
