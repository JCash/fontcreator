"""
Copyright @ 2013 Mathias Westerdahl

This is the default rendering of the fonts
    
.. py:attribute:: texturesize = 512, 512

    The desired size of the texture. If it's too small, the creator will fail.
  
.. py:attribute:: textureoffset = 0, 0
    
    The offset from the top left corner of the texture to the top left corner of the first glyph.
    It is used to create a border around the texture. The same border is also applied on the right/bottom sides.
    
.. py:attribute:: usepremultipliedalpha = 0

    If set, will premultiply the alpha

"""

import numpy as np
from fontutils import FontException, pre_multiply_alpha

DEBUG=False


def _guess_dimensions(glyphs):
    area = 0
    for glyph in glyphs:
        if glyph.bitmap is None:
            continue
        w, h, d = glyph.bitmap.shape
        area += w*h
    
    #area += area / 1
    
    gw = 512
    gh = 64
    guess = gw * gh
    while guess < area:
        if gh >= gw:
            gw *= 2
            gh /= 2
        else:
            gh *= 2
        guess = gw * gh
    return (gw, gh)
        

def _create_image(info, w, h):
    image = np.ones( (w, h, 4), np.float64)
    image[:, :, 0] *= info.bgcolor[0]
    image[:, :, 1] *= info.bgcolor[1]
    image[:, :, 2] *= info.bgcolor[2]
    image[:, :, 3] *= 0
    return image


def _glyph_cmp(a, b):
    if a.bitmap is None and b.bitmap is not None:
        return 1
    elif b.bitmap is None and a.bitmap is not None:
        return -1
    elif b.bitmap is None and a.bitmap is None:
        return cmp(a, b)
    
    return a.bitmap.shape[1] - b.bitmap.shape[1]


def render(info):
    """ Assuming (0,0) is at the top left corner of the image.
    
    :param info:    The settings from the fontinfo file
    :return:        The image all glyphs are rendered to
    """
    
    iw, ih = info.texturesize
    image = _create_image(info, iw, ih)

    y = info.ascender + info.textureoffset[1]
    x = info.textureoffset[0]
    
    for glyph in info.glyphs:
        if glyph.bitmap is None:
            continue
        
        w, h, d = glyph.bitmap.shape
        
        if x + w + info.padding >= iw:
            x = info.textureoffset[0]
            y += info.ascender - info.descender + info.padding
                
        top = y - glyph.bearingY
        left = x
        right = x + w
        bottom = top + h
        
        if right >= iw or bottom >= ih:
            print "glyph", glyph.unicode
            print "RECT", (left, top, right, bottom)
            raise FontException("The texture size is too small: (%d, %d) Increase the 'texturesize' property in the font info" % (info.texturesize[0], info.texturesize[1]) )

        glyph.bitmapbox = (left, top, w, h)
        
        try:
            image[ left : right, top : bottom ] = glyph.bitmap

        except Exception, e:
            print "glyph", glyph.unicode
            print "ERROR", e
            print "RECT", (left, top, right, bottom)
            
            print "image.shape", image.shape
            print "char.bitmap.shape", glyph.bitmap.shape
            raise

        #x += max(w, w2) + info.padding + info.internalpadding[0]*2
        x += info.padding + w
    
    if info.usepremultipliedalpha:
        image = pre_multiply_alpha(image)
        
    return image
        
