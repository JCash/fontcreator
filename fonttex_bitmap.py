"""
This is the default rendering of the fonts
"""
import logging
import numpy as np
from fontutils import FontException
import binpack

DEBUG=False


def _guess_dimensions(glyphs):
    area = 0
    for glyph in glyphs:
        if glyph.info.bitmap is None:
            continue
        w, h, d = glyph.info.bitmap.shape
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
    ones = np.ones( (w, h), float)
    zeros = np.zeros( (w, h), float)
    r = ones * info.bgcolor[0]
    g = ones * info.bgcolor[1]
    b = ones * info.bgcolor[2]
    return np.dstack( (r, g, b, zeros) )


def _glyph_cmp(a, b):
    if a.info.bitmap is None and b.info.bitmap is not None:
        return 1
    elif b.info.bitmap is None and a.info.bitmap is not None:
        return -1
    elif b.info.bitmap is None and a.info.bitmap is None:
        return cmp(a, b)
    
    return a.info.bitmap.shape[1] - b.info.bitmap.shape[1]


def render(info, glyphs):
    """ Assuming (0,0) is at the top left corner of the image.
    @param info            The settings from the fontinfo file
    @param glyphs          The set of glyphs to be rendered, as specified by the info.letters
    @param[in,out] image   The destination image where all glyphs are rendered to
    """
    
    # sort the glyphs
    glyphs.sort(cmp=_glyph_cmp)
    
    # Work in progress
    #iw, ih = _guess_dimensions(glyphs)
    iw, ih = info.texturesize
    #ih /= 2
    #print "guessed image size", iw, ih
    image = _create_image(info, iw, ih)
    
    textureoffset = info.textureoffset
    padding = info.padding
    
    packer = binpack.create_packer(binpack.SKYLINE_BL, iw - textureoffset[0], ih - textureoffset[1], False)
    
    # DEBUG PACK RENDERING
    if DEBUG:
        image[:, :, 0] = 1.0
        image[:, :, 3] = 1.0
    
    for glyph in glyphs:
        if glyph.info.bitmap is None:
            continue
        
        bitmap = glyph.info.bitmap
        
        w, h, d = bitmap.shape
        
        rect = binpack.pack_rect(packer, w + padding, h + padding)
        if rect.height == 0:
            raise FontException("The texture size is too small: (%d, %d) Increase the 'texturesize' property in the font info" % (info.texturesize[0], info.texturesize[1]) )
        
        rect.x += textureoffset[0]
        rect.y += textureoffset[1]
        rect.width -= padding
        rect.height -= padding
        
        glyph.bitmapbox = (rect.x, rect.y, rect.width, rect.height )
        
        # check if the glyph has been flipped
        if w != h and w == rect.height:
            bitmap = np.rot90(bitmap)
        
        try:
            image[ rect.x : rect.x + rect.width, rect.y : rect.y + rect.height ] = bitmap

            # DEBUG PACK RENDERING
            if DEBUG:
                import fontutils
                top = image[ rect.x : rect.x + rect.width, rect.y : rect.y + rect.height ]
                ones = np.ones( (top.shape[0], top.shape[1]) )
                
                from random import random
                r = random() * 0.4 + 0.6
                g = random() * 0.4 + 0.6
                b = random() * 0.4 + 0.6
                a = 1.0
                bottom = np.dstack( (ones * r, ones * g, ones * b, ones * a) )
            
                result = fontutils.alpha_blend(bottom, top)
                image[ rect.x : rect.x + rect.width, rect.y : rect.y + rect.height ] = result
        except Exception, e:
            print "ERROR", e
            print "RECT", rect
            
            #print "bmshape", (bx,by,w,h)
            print "image.shape", image.shape
            print "char.bitmap.shape", glyph.info.bitmap.shape
            raise

        #x += max(w, w2) + info.padding + info.internalpadding[0]*2
    
    logging.debug('Used %f %% of the texture', (binpack.get_occupancy(packer) * 100))
    binpack.destroy_packer(packer)
    
    if info.usepremultipliedalpha:
        image = fontutils.pre_multiply_alpha(image)
        
    return image
        
