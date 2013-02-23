"""

@COPYRIGHT 2013 MATHIAS WESTERDAHL

"""


import sys, os, logging
from optparse import OptionParser
import itertools

try:
    from PIL import Image
except ImportError:
    import Image

def _patch_numpy():
    """ When chasing optimizations, numpy's excessive imports actually amounted to
    times that were not insignificant compared to the other functions in the font creator.
    """
    class FooModule(object):
        __all__ = []
    class FooObject(object):
        def __getattr__(self,*k,**kw): pass

    # Timings went from 0.675 to 0.609 (~9.5%)
    # Saved 0.01s out of 0.067s by not including all the documentation
    sys.modules['numpy.add_newdocs'] = True
    # Saved 0.002s out of 0,066s
    #sys.modules['numpy.fft'] = True # needed by numpy.numarray
    # Saved 0.016s from 0.658s
    sys.modules['numpy.polynomial'] = True
    # Saved 0.01s from 0.064s
    sys.modules['numpy.ma'] = True
    # Saved 0,01s from 0.63s
    #sys.modules['numpy.random'] = True # needed by numpy.numarray
    # Save 0.016s from 0.625s
    sys.modules['numpy.testing'] = FooModule()
    sys.modules['numpy.testing'].__dict__['Tester'] = FooObject

    sys.modules['numpy.core.records'] = FooModule()
    sys.modules['numpy.core.financial'] = FooModule()
    
    sys.modules['numpy.lib.triu'] = FooModule()

_patch_numpy()
import numpy as np

import freetype as ft
import fontutils as fu

from fontinfo import SFontInfo
import fonteffects

"""
for n in sorted(sys.modules.keys()):
    if 'numpy' in n:
        print n, sys.modules[n]
"""


"""
http://www.freetype.org/freetype2/docs/reference/ft2-index.html
http://www.freetype.org/freetype2/docs/glyphs/glyphs-3.html
http://code.google.com/p/freetype-py/source/browse/trunk/
http://dunnbypaul.net/blends/
http://www.catenary.com/howto/emboss.html
http://www.scipy.org/Numpy_Example_List#head-6a18109f2befe2d8e7bdc599e1834a8b3453f5ef

http://www.russellcottrell.com/greek/utilities/UnicodeRanges.htm
"""




class LogStream(object):
    def __init__(self, path):
        self.log = open(path, 'wb')
        self.stdout = sys.stdout

    def __del__(self):
        self.log.close()
        self.log = None

    def write(self, s):
        self.stdout.write(s)
        self.log.write(s)

    def flush(self):
        self.stdout.flush()
        self.log.flush()


def _apply_layer(glyph, info, layer, character, previmage, glyphimage):
    # The max y should be the same for all characters in the same row
    # This is necessary for having the same "space" during calculations
    maxsize = info.maxsize

    starty = info.maxbearingY - character.bearingY

    layer.set_info( glyph, info )
    image = layer.apply_color( 0, starty, character.bitmap.shape, maxsize, glyphimage, previmage )
    image = layer.apply_effects( image )
    image = layer.apply_mask( image )
    image = layer.apply_blend( glyphimage, previmage, image )

    assert image != None
    return image


def _apply_layers(info):
    
    bbox = np.array( [0, 0] )
    max_bearing_y = 0
    for glyph in info.glyphs:
        if glyph.bitmap is None:
            continue
        bbox = np.maximum( bbox, glyph.bitmap.shape )
        max_bearing_y = max(max_bearing_y, glyph.bearingY)
    
    bbox[0] += info.extrapadding[0] + info.extrapadding[2]
    bbox[1] += info.extrapadding[1] + info.extrapadding[3]
    
    info.maxsize = bbox
    info.maxbearingY = max_bearing_y

    elements = []
    for layer in info.layers:
        elements.append(layer)
        elements.append(layer.color)
    for element in elements + info.posteffects:
        if hasattr(element, 'set_dimensions'):
            element.set_dimensions(info.maxsize[0], info.maxsize[1])

    for glyph in info.glyphs:
        
        if glyph.bitmap is None:
            continue

        glyphimage = glyph.bitmap

        # ????
        fonteffects.DefaultMask.idx = np.where(glyphimage == 0)
        
        previmage = np.dstack((glyphimage, glyphimage, glyphimage, glyphimage))

        previmage = _apply_layer(glyph, info, info.layers[0], glyph, previmage, glyphimage)

        for layer in info.layers[1:]:
            previmage = _apply_layer(glyph, info, layer, glyph, previmage, glyphimage)

        for effect in info.posteffects:
            previmage = effect.apply(glyph, info, previmage)
        
        bgimage = np.ones( previmage.shape, float) * (info.bgcolor[0], info.bgcolor[1], info.bgcolor[2], 0.0)
        
        previmage = fu.alpha_blend(bgimage, previmage)
        
        glyph.bitmap = previmage


def _convert_int_to_unicode(char):
    """ Converts an UTF-8 encoded integer and converts it back to a unicode character
    """
    if char <= 255:
        return chr(char)

    s = ''
    if char & 0xFF000000:
        s += '%x' % (char >> 24 & 0xFF)
    if char & 0x00FF0000:
        s += '%x' % (char >> 16 & 0xFF)
    if char & 0x0000FF00:
        s += '%x' % (char >> 8 & 0xFF)
    if char & 0x000000FF:
        s += '%x' % (char >> 0 & 0xFF)

    return s.decode('hex').decode('utf-8')


def _get_extra_padding(info):
    zero = (0,0,0,0)
    extrapadding = (0,0,0,0)
    for layer in info.layers:
        layerpadding = layer.padding
        extrapadding = np.maximum(extrapadding, layerpadding)
        
    for effect in info.posteffects:
        extrapadding = np.add(extrapadding, getattr(effect, 'padding', zero))
    return extrapadding


class Glyph(object):
    """ Holds the glyph info.
    For a detailed description of the glyph metrics, see http://www.freetype.org/freetype2/docs/tutorial/step2.html
    
    :param utf8:          The UTF-8 character code
    :param unicode:       The unicode letter
    :param bitmap:        The numpy array of shape (x, y, 4)
    :param bitmapbox:     The box in the texture where the glyph is printed.
                          A 4-tuple: (left, top, width, height)  *(In pixels)*
    :param bearingX:      The distance from the cursor to the leftmost border of the bitmap
    :param bearingY:      The distance from the baseline to the topmost border of the bitmap
    :param advance:       The distance used to increment the cursor
    """
    def __init__(self, utf8, unicode):
        self.utf8 = utf8
        self.unicode = unicode
        self.bitmap = None
        self.bitmapbox = None
        self.bearingX = 0
        self.bearingY = 0
        self.advance = 0


def _get_glyph_info(options, info, face):
    logging.debug("Fetching glyph info")
    
    face.set_char_size( width=0, height=info.size*64, hres=info.dpi, vres=info.dpi )
    
    # find out the needed extra padding on each side of each glyph
    info.extrapadding = _get_extra_padding(info)
    
    info.ascender = (face.size.ascender >> 6) + info.extrapadding[1]
    info.descender = (face.size.descender >> 6) - info.extrapadding[3]
    info.fontsize = face.height >> 6
    
    flags = ft.LOAD_NO_BITMAP
    
    all_letters = set()
    
    info.glyphs = []
    for c in info.letters:
        if c in all_letters:
            continue
        if options.writetext and not unichr(c) in options.writetext:
            continue
        all_letters.add(c)
        
        unicode = _convert_int_to_unicode(c)

        face.load_char( unicode, flags )

        metrics = face.glyph.contents.metrics

        glyph = Glyph(c, unicode)
        glyph.bearingX = (metrics.horiBearingX >> 6) + info.extrapadding[0]
        glyph.bearingY = (metrics.horiBearingY >> 6) + info.internalpadding[1] + info.extrapadding[1]
        glyph.advance = (metrics.horiAdvance >> 6) + info.extrapadding[2]
        
        info.glyphs.append( glyph )


def render(options, info, face):
    
    found = False
    for charmap in face.charmaps:
        found = found or charmap.encoding == ft.ENCODING_UNICODE
    if not found:
        logging.warning("The font %s doesn't seem to support unicode!? Continuing anyway")
    
    if options.writetext:
        info.letters = [c for c in info.letters if unichr(c) in options.writetext]

    logging.debug("Rendering %d characters" % len(info.letters))

    # find out the needed extra padding on each side of each glyph
    info.extrapadding = _get_extra_padding(info)
    
    info.face = face

    flags = ft.LOAD_RENDER
        
    antialias = getattr(info, 'antialias', 'normal')
    if antialias == 'none':
        flags |= ft.LOAD_TARGET_MONO
    elif antialias == 'light':
        flags |= ft.LOAD_TARGET_LIGHT
    elif antialias == 'normal':
        flags |= ft.LOAD_TARGET_NORMAL

    logging.debug("RENDERING %s", unicode([g.unicode for g in info.glyphs]))
    
    assert len(info.glyphs) > 0, "No glyphs to process!"
    
    # since the layers might set this, we set it back
    face.set_char_size( width=0, height=info.bitmapsize * 64, hres=info.dpi, vres=info.dpi )
    
    for glyph in info.glyphs:

        face.load_char( glyph.unicode, flags )

        if face.glyph.contents.bitmap.rows:
            glyph.bitmap = fu.make_array_from_bitmap(face.glyph.contents.bitmap)
            shape = glyph.bitmap.shape

            glyph.bitmap = fu.pad_bitmap(glyph.bitmap, info.extrapadding[0], info.extrapadding[1], info.extrapadding[2], info.extrapadding[3], 0.0)

            if info.useadvanceaswidth:
                # Pad the bitmap with the bearing width on each side
                # This is useful for file formats that doesn't carry all the glyph info into it
                padleft = glyph.bearingX
                padright = glyph.advance - shape[0] - padleft
                glyph.bitmap = fu.pad_bitmap(glyph.bitmap, 0, 0, padright, 0, 0.0)

            if antialias != 'none':
                glyph.bitmap /= 255.0

        else:
            logging.debug("char missing bitmap %X '%s'" % (glyph.utf8, glyph.unicode) )

    # Apply all layers on all the tiny bitmaps
    _apply_layers(info)
    
    max_bearing_y = 0 # the maximum extent above the baseline
    min_bearing_y = 0 # the maximum extent below the baseline
    max_width = 0

    # calculate the height/width, since the layers may increased/decreased the size
    max_width = 0
    max_height = 0
    for glyph in info.glyphs:
        if glyph.bitmap is None:
            continue
        # find the highest char
        max_bearing_y = max(max_bearing_y, glyph.bearingY)
        # find the lowest char
        min_bearing_y = min(min_bearing_y, glyph.bearingY - glyph.bitmap.shape[1])
        
        max_width = max(max_width, glyph.bitmap.shape[0])
        max_height = max(max_height, glyph.bitmap.shape[1])

    info.max_height = max(max_height, info.ascender - info.descender)
    info.max_width = max_width


def _get_pair_kernings(info, face):
    characters = set([ glyph.utf8 for glyph in info.glyphs])
    pairkernings = dict()
    for pair in itertools.product(characters, repeat=2):
        prevc, c = pair
        kerning = face.get_kerning(prevc, c)
        if kerning.x != 0:
            assert c < 0xFFFFFFFF
            assert prevc < 0xFFFFFFFF
            pairkernings[ _encode_pair(prevc, c) ] = kerning.x>>6
            
            #print "kerning %s, %s: %d" % (chr(prevc), chr(c), kerning.x>>6), '\t', '0x%016x' % _encode_pair(prevc, c)
    return pairkernings


def compile(options):

    info = SFontInfo(options)

    if not os.path.exists( info.name ):
        raise fu.FontException("Failed to find font: %s" % info.name)

    face = ft.new_face( info.name )

    # gather the glyph info
    _get_glyph_info(options, info, face)

    pairkernings = None
    if info.usepairkernings:
        pairkernings = _get_pair_kernings(info, face)
    
    # The actual compile step
    render(options, info, face)
    
    # assemble into a texture
    image = info.texturerender( info )

<<<<<<< HEAD
=======
    pairkernings = dict()
    if info.usepairkernings:
        pairkernings = _get_pair_kernings(info, face)

>>>>>>> 3eeb00c02e840fb3ffe6d0facbf7d03948aeb3f8
    if not options.writetext:
        if not os.path.exists( os.path.dirname(options.output) ):
            os.makedirs(os.path.dirname(options.output))
            
        try:
            info.texturewriter( options, info, image )
        except Exception, e:
            raise fu.FontException('Failed to write texture: %s' % str(e) )

        info.writer.write(options, info, pairkernings)

    return (info, pairkernings, image)


def _encode_pair(prevc, c):
    """ Encodes two 16 bit integers into 32 bits """
    return prevc << 32 | c


def _calc_bbox(info, characters, pairkernings, text):
    extrapadding = _get_extra_padding(info)
    maxx = 0
    x = 0
    lineheight = info.max_height + extrapadding[1] + extrapadding[3]
    y = lineheight
    prevc = 0
    for i, c in enumerate(text):
        c = ord(c)
        if c == '\n' and i < len(text)-1:
            maxx = max(x, maxx)
            x = 0
            y += lineheight
            continue

        char = characters.get( c, None )
        if not char:
            logging.warning("Character not in info.letters: '%s'" % unichr(c) )
            continue
            x += char.advance
            prevc = c
            continue

        x += pairkernings.get( _encode_pair(prevc, c), 0)
        x += char.advance
        x += extrapadding[0] + extrapadding[2]
        prevc = c

    maxx = max(x, maxx)
    return (maxx, y)


def write_text(options, info, pairkernings):
    """
    Writes the given text to an image
    """

    pairkernings = pairkernings or dict()

    # first, calculate the texture size
    if os.path.isfile(options.writetext):
        with open(options.writetext, 'rt') as f:
            options.writetext = f.read()

    cinfo = {glyph.utf8 : glyph for glyph in info.glyphs}
    
    texture_size = _calc_bbox(info, cinfo, pairkernings, options.writetext)
    texture_size = (texture_size[0]+info.padding*2+60, texture_size[1]+info.padding*2)

    ones = np.ones(texture_size, float)
    r = ones * info.bgcolor[0]
    g = ones * info.bgcolor[1]
    b = ones * info.bgcolor[2]

    zeros = np.zeros(texture_size, float)
    image = np.dstack( (r,g,b,zeros) )

    x = 0
    y = info.ascender
    prevc = 0

    found = False
    for c in options.writetext:
        c = ord(c)

        char = cinfo.get( c, None )
        if not char:
            logging.warning("Character not in info.letters: '%s'" % unichr(c))
            continue

        if char.bitmap == None:
            x += char.advance
            prevc = c
            continue

        found = True

        x += pairkernings.get( _encode_pair(prevc, c), 0)

        bw, bh, _ = char.bitmap.shape
        bx = x + char.bearingX
        by = y - char.bearingY
        
        # we must make sure that the first pixel is within range
        if bx < 0:
            x += -char.bearingX
            bx = x
            
        
        target = image[bx : bx + bw, by : by + bh ]

        try:
            image[bx : bx + bw, by : by + bh ] = fu.alpha_blend( target, char.bitmap )
        except Exception, e:
            print e
            print 'image shape', image.shape
            print 'target shape', target.shape
            print 'bitmap shape', char.bitmap.shape
            print "bx, bw", bx, bw
            print "by, bh", by, bh
            print "y", y
            print "bearingY", char.bearingY
            print "lineheight", info.max_height
            print "c:", char.utf8, char.unicode
            print ""
            print ""
            raise

        x += char.advance
        prevc = c

    if not found:
        raise fu.FontException("No characters found in font: %s" % options.writetext)

    image = (image * 255.0).astype(np.uint8)

    r,g,b,a = image.T
    image = np.dstack((r,g,b,a))

    if not os.path.exists( os.path.dirname(options.output) ):
        os.makedirs(os.path.dirname(options.output))

    Image.fromarray( image ).save( options.output )
    logging.debug("Wrote %s" % options.output)


def init():
    parser = OptionParser()
    parser.add_option('-i', '--input', metavar='FILE', help='The input font (.fontinfo)')
    parser.add_option('-o', '--output', metavar='FILE', help='The output font (.fntb)')
    parser.add_option('-d', '--datadir', default='', metavar='DIRECTORY', help='The data directory that all resource paths should be relative to')
    parser.add_option('-e', '--endian', default='little', choices=['little', 'big'], help='The endianess of the output file.')
    parser.add_option('-v', '--verbose', action='store_true', default=False, help='Specifies verbose mode')
    parser.add_option('-l', '--log', default='', help='A log file where the stdout is saved logged to.' )
    parser.add_option('-w', '--writetext', metavar='TEXT', help='When used, a .fontinfo file is used as input and the text is written into the output texture.')

    options, args = parser.parse_args()

    if options.log:
        sys.stdout = LogStream(options.log)
        sys.stderr = sys.stdout

    if not options.input:
        parser.error("You must specify an input file")
    if not options.output:
        parser.error("You must specify an output file")
    if not os.path.exists(options.input):
        parser.error("The input file doesn't exist: %s" % options.input)
    if not options.endian in ['little', 'big']:
        parser.error("Invalid endianess: %s" % options.endian)

    logging.basicConfig(level=(logging.INFO if options.verbose else logging.WARN))

    return options


if __name__ == '__main__':
    options = init()

    if options.verbose:
        logging.info("Using freetype-%d.%d.%d" % ft.version() )

    try:
        options.endian = '<' if options.endian == 'little' else '>'

        (info, pairkernings, image) = compile(options)

        if options.writetext:
            write_text(options, info, pairkernings)

    except fu.FontException, e:
        if '-v' in sys.argv:
            raise
        logging.error( "%s: %s" % (options.input, str(e)) )
        sys.exit(1)
