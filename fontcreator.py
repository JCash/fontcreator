"""

@COPYRIGHT 2012 MATHIAS WESTERDAHL

"""


import sys, os, logging, math
from optparse import OptionParser
import ctypes, itertools

from PIL import Image

import freetype as ft
import fontutils as fu

from fontinfo import SFontInfo
import fonteffects


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

_patch_numpy()
import numpy as np

"""
for n in sorted(sys.modules.keys()):
    if 'numpy' in n:
        print n
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




def _make_array_from_bitmap(_bitmap, bitdepth=8):
    """ Converts a FTBitmap into a numpy array """
    bitmap = ft.Bitmap()
    ft.bitmap_convert(_bitmap, bitmap, bitdepth)

    width, rows, pitch = bitmap.width, bitmap.rows, bitmap.pitch

    # fetch all data from C to Python
    #buffer = bitmap.buffer[:]

    data = []
    for i in xrange(rows):
        data.extend( bitmap.buffer[ i * pitch : i * pitch + width ] )

    return np.array(data, np.float32).reshape(rows, width).transpose()


class CharacterInfo(object):
    """
    """
    def __init__(self, character, unicode):
        self.character = character
        self.unicode = unicode
        self.bitmap = None
        self.bearingX = 0
        self.bearingY = 0
        self.advance = 0
        self.bitmap_x = 0
        self.bitmap_y = 0


def _apply_layer(info, layer, character, previmage, glyphimage):
    # The max y should be the same for all characters in the same row
    # This is necessary for having the same "space" during calculations
    maxsize = info.maxsize

    starty = info.maxbearingY - character.bearingY

    image = layer.apply_color( 0, starty, character.bitmap.shape, maxsize, glyphimage, previmage )
    image = layer.apply_effects( image )
    image = layer.apply_mask( image )
    image = layer.apply_blend( glyphimage, previmage, image )

    assert image != None
    return image


def _apply_layers(info, characterinfos):
    bbox = [0.0, 0.0]
    for character, characterinfo in characterinfos.iteritems():
        if None == characterinfo.bitmap:
            continue
        bbox[0] = max( bbox[0], characterinfo.bitmap.shape[0] )

    bbox[0] += info.extrapadding[0] + info.extrapadding[2]

    info.maxsize = [bbox[0], info.ascender - info.descender]
    info.maxbearingY = info.ascender

    elements = []
    for layer in info.layers:
        elements.append(layer)
        elements.append(layer.color)
    for element in elements + info.posteffects:
        if hasattr(element, 'set_dimensions'):
            element.set_dimensions(info.maxsize[0], info.maxsize[1] )

    for character, characterinfo in characterinfos.iteritems():
        if None == characterinfo.bitmap:
            continue

        glyphimage = characterinfo.bitmap

        # ????
        fonteffects.DefaultMask.idx = np.where(glyphimage == 0)
        
        previmage = np.dstack((glyphimage, glyphimage, glyphimage, glyphimage))

        previmage = _apply_layer(info, info.layers[0], characterinfo, previmage, glyphimage)

        for layer in info.layers[1:]:
            previmage = _apply_layer(info, layer, characterinfo, previmage, glyphimage)

        for effect in info.posteffects:
            previmage = effect.apply(previmage)

        prevshape = (previmage.shape[0], previmage.shape[1])
        ones = np.ones( prevshape, float)
        zeros = np.zeros( prevshape, float)
        r = ones * info.bgcolor[0]
        g = ones * info.bgcolor[1]
        b = ones * info.bgcolor[2]
        bgimage = np.dstack( (r,g,b,zeros) )
        previmage = fu.alpha_blend(bgimage, previmage)

        characterinfo.alpha = previmage[:,:,3]

        characterinfo.bitmap = previmage


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

        for effect in layer.effects:
            layerpadding = np.add(layerpadding, getattr(effect, 'padding', zero) )

        extrapadding = np.maximum(extrapadding, layerpadding)
        
    for effect in info.posteffects:
        extrapadding = np.add(extrapadding, getattr(effect, 'padding', zero))
    return extrapadding


def render(options, info, face):

    antialias = getattr(info, 'antialias', 'normal')

    if info.unicode:
        found = False
        for charmap in face.charmaps:
            found = found or charmap.encoding_name == 'FT_ENCODING_UNICODE'
        if not found:
            logging.warning("The font %s doesn't seem to support unicode!? Continuing anyway")

    if options.writetext:
        info.letters = [c for c in info.letters if unichr(c) in options.writetext]

    logging.debug("Rendering %d characters" % len(info.letters))

    # find out the needed extra padding on each side of each glyph
    info.extrapadding = _get_extra_padding(info)

    max_bearing_y = 0 # the maximum extent above the baseline
    min_bearing_y = 0 # the maximum extent below the baseline
    max_width = 0

    flags = ft.LOAD_RENDER
    if antialias == 'none':
        flags |= ft.LOAD_TARGET_MONO
    elif antialias == 'light':
        flags |= ft.LOAD_TARGET_LIGHT
    elif antialias == 'normal':
        flags |= ft.LOAD_TARGET_NORMAL

    cinfolist = []
    for c in set(info.letters):
        unicode = _convert_int_to_unicode(c)

        face.load_char( unicode, flags )

        metrics = face.glyph.contents.metrics

        char = CharacterInfo(c, unicode)
        char.bearingX = (metrics.horiBearingX >> 6) + info.extrapadding[0]
        char.bearingY = (metrics.horiBearingY >> 6) + info.internalpadding[1] + info.extrapadding[1]
        char.advance = (metrics.horiAdvance >> 6) + info.extrapadding[2]


        """
        print ""
        print "(utf-8, unicode) =", (hex(char.character), char.unicode)
        print "bearing", char.bearingX, char.bearingY
        print "advance", metrics.horiAdvance >> 6, face.glyph.advance.x >> 6
        print ""
        """
        
        char.bitmap = None
        if face.glyph.contents.bitmap.rows:
            char.bitmap = _make_array_from_bitmap(face.glyph.contents.bitmap)
            shape = char.bitmap.shape

            char.bitmap = fu.pad_bitmap(char.bitmap, info.extrapadding[0], info.extrapadding[1], info.extrapadding[2], info.extrapadding[3], 0.0)

            if info.useadvanceaswidth:
                # Pad the bitmap with the bearing width on each side
                # This is useful for file formats that doesn't carry all the glyph info into it
                padleft = char.bearingX
                padright = char.advance - shape[0] - padleft
                char.bitmap = fu.pad_bitmap(char.bitmap, 0, 0, padright, 0, 0.0)

            if antialias != 'none':
                char.bitmap /= 255.0

            #char.bitmap_left = face.glyph.bitmap_left
            #char.bitmap_top = face.glyph.bitmap_top

        else:
            logging.debug("char missing bitmap %X '%s'" % (char.character, char.unicode) )

        if char.bitmap != None:
            # find the highest char
            max_bearing_y = max(max_bearing_y, char.bearingY)
            # find the lowest char
            min_bearing_y = min(min_bearing_y, char.bearingY - char.bitmap.shape[1])
            # Find the widest char
            max_width = max(max_width, char.bitmap.shape[0])

        cinfolist.append( (c, char) )

    info.fontsize = face.height >> 6
    info.ascender = max_bearing_y
    info.descender = min_bearing_y
    info.max_width = max_width
    info.max_height = info.ascender - info.descender

    cinfo = dict(cinfolist)

    # Apply all layers on all the tiny bitmaps
    _apply_layers(info, cinfo)

    # adjust the ascender/descender, since the layers may increased/decreased the size
    max_width = 0
    max_height = 0
    for c, char in cinfo.iteritems():
        if char.bitmap is None:
            continue
        max_width = max(max_width, char.bitmap.shape[0])
        max_height = max(max_height, char.bitmap.shape[1])

    ratio = float(max_height) / float(max_bearing_y - min_bearing_y)
    info.ascender = math.ceil( max_bearing_y * ratio )
    info.descender = math.floor( min_bearing_y * ratio )
    info.max_width = max_width
    info.max_height = max_height

    # Now when we've found the new ratio, adjust the glyphs
    for c, char in cinfo.iteritems():
        char.bearingX = math.ceil( char.bearingX * ratio )
        char.bearingY = math.ceil( char.bearingY * ratio )
        char.advance = math.ceil( char.advance * ratio )

    # Now, render the small bitmaps into the large bitmap

    class Glyph(object):
        def __init__(self, c, cinfo):
            self.character = c
            self.info = cinfo
            self.bitmapbox = None

    # might contain duplicates
    glyphs = [ Glyph(c, cinfo[c]) for c in info.letters ]

    return cinfo, glyphs


def _get_pair_kernings(characters, face):
    characters = set([ char.character for c, char in characters.iteritems()])
    pairkernings = dict()
    for pair in itertools.product(characters, repeat=2):
        prevc, c = pair
        kerning = face.get_kerning(prevc, c)
        if kerning.x != 0:
            assert c < 0xFFFF
            assert prevc < 0xFFFF
            pairkernings[ _encode_pair(prevc, c) ] = kerning.x>>6
    return pairkernings


def compile(options):

    info = SFontInfo(options)

    if not os.path.exists( info.name ):
        raise fu.FontException("Failed to find font: %s" % info.name)

    face = ft.new_face( info.name )
    face.set_char_size( width=0, height=info.size*64, hres=info.dpi, vres=info.dpi )

    info.ascender = face.size.ascender >> 6
    info.descender = face.size.descender >> 6

    # The actual compile step
    cinfo, glyphs = render(options, info, face)
    
    # assemble into a texture
    image = info.texturerender( info, glyphs )

    pairkernings = None
    if info.usepairkernings:
        pairkernings = _get_pair_kernings(cinfo, face)

    if not options.writetext:
        if not os.path.exists( os.path.dirname(options.output) ):
            os.makedirs(os.path.dirname(options.output))
            
        try:
            info.texturewriter( options, info, image )
        except Exception, e:
            raise fu.FontException('Failed to write texture: %s' % str(e) )

        info.writer.write(options, info, glyphs, pairkernings)

    return (info, cinfo, glyphs, pairkernings, image)


def _encode_pair(prevc, c):
    """ Encodes two 16 bit integers into 32 bits """
    return prevc << 16 | c


def _calc_bbox(info, characters, pairkernings, text):
    maxx = 0
    x = 0
    lineheight = info.ascender - info.descender
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
        prevc = c

    maxx = max(x, maxx)
    return (maxx, y)


def write_text(options, info, cinfo, glyphs, pairkernings):
    """
    Writes the given text to an image
    """

    pairkernings = pairkernings or dict()

    # first, calculate the texture size
    if os.path.isfile(options.writetext):
        with open(options.writetext, 'rt') as f:
            options.writetext = f.read()

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
            print "lineheight", info.ascender - info.descender
            print "c:", char.character, char.unicode
            print x, by, x + bw, by + bh
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

        (info, cinfo, glyphs, pairkernings, image) = compile(options)

        if options.writetext:
            write_text(options, info, cinfo, glyphs, pairkernings)

    except fu.FontException, e:
        if '-v' in sys.argv:
            raise
        logging.error( "%s: %s" % (options.input, str(e)) )
        sys.exit(1)
