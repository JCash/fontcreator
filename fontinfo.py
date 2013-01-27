""" The font info reads the .fontinfo and creates the layers, effects, and blends

.. py:attribute:: name = ''

    The path of the font file. Relative paths are relative to the .fontinfo file. Supports .ttf files.
    For a complete list of supported formats, see `Freetype2 <http://www.freetype.org/freetype2/index.html>`_

.. py:attribute:: size = 32

    The size of the font (in pixels)

.. py:attribute:: bitmapsize = None

    The size (in pixels) of the font when it should be rendered.
    This is useful when you wish to render the glyph much larger and later on scale it back down.
    It is used when generating distance field fonts.
    If set to None, the *size* will be used. Defaults to None.

.. py:attribute:: dpi = 72

    The resolution of the font when being rendered.

.. py:attribute:: padding = 0

    The amount of padding that is inserted between two glyphs when rendered to the bitmap.

.. py:attribute:: internalpadding = 0, 0

    The amount of padding (x, y) that is added *internally* for a glyph.
    E.g. making room for manual fixup in a image editing program.

.. py:attribute:: useadvanceaswidth = 0

    For japanese fonts, the space in the glyph is important.
    Therefore, this flag was introduced to respect the space of a glyph.
    Set to 1 for Japanese fonts.
    
.. py:attribute:: usepairkernings = 1

    Enables the collecting of the pair kernings table.

.. py:attribute:: letters = 20-7e

    Specifies what letters should be included in the font. It can hold these formats:
    
    #. A list of hexadecimal digits. The list is comma separated and can specify ranges with the '-' character::
    
        letters = 20-7c,7d,7e
        
    #. A filename. The file contains the actual letters.

.. py:attribute:: bgcolor = 0, 0, 0

    The background color of the texture

.. py:attribute:: fgcolor = 1, 1, 1
    
    The color of the glyph
        
.. py:attribute:: antialias = normal

    Enables antialiasing for the glyph rendering (the first pass).
    Possible values are **'none', 'light' and 'normal'**.
    
.. py:attribute:: texturerender = fonttex_bitmap
    
    A path to the module that renders the glyphs to the texture. Must implement a *image = render(info)* function.
    The default is :doc:`fonttex_bitmap`

.. py:attribute:: texturewriter = fonttexout_pil

    A path to the module that writes the texture to disc. Must implement a *write(options, info, image)* function.
    The default is :doc:`fonttexout_pil`

.. py:attribute:: writer = fontout_json
    
    A path to the module that writes the glyph info. Must implement a *write(options, info, pairkernings)* function.
    The default is :doc:`fontout_json`
    
.. py:attribute:: layers = ''

    A list of layers (:py:class:`fonteffects.Layer`) that will be applied in order.
        
.. py:attribute:: effects = ''

    A list of post effects that will be applied in order, after the layers have been rendered.


"""
import os, sys, struct
from ConfigParser import SafeConfigParser
from fontutils import FontException
import fontblend
import fonteffects


def GetDefaultOptions():
    defaults = dict()
    defaults['name'] = 'not set'
    defaults['size'] = '32'
    defaults['bitmapsize'] = None
    defaults['dpi'] = '72'
    defaults['padding'] = '0'
    defaults['internalpadding'] = '0, 0'
    defaults['useadvanceaswidth'] = '0'  # E.g. set to 1 for japanese fonts
    defaults['usepairkernings'] = '1'
    
    defaults['letters'] = '20-7e'
    defaults['bgcolor'] = '0, 0, 0'
    defaults['fgcolor'] = '1, 1, 1'
    defaults['antialias'] = 'normal'

    defaults['writer'] = 'fontout_json'
    
    defaults['texturerender'] = 'fonttex_bitmap'
    defaults['texturesize'] = '512, 512'
    defaults['textureoffset'] = '0, 0'
    defaults['usepremultipliedalpha'] = '0'
    
    defaults['texturewriter'] = 'fonttexout_pil'
    defaults['textureformat'] = '.png'
    defaults['texturechannels'] = 'RGBA'
    
    defaults['layers'] = ''
    defaults['posteffects'] = ''
    return defaults


class SFontInfo(object):
    """ The input format (.fontinfo)
    """
    
    def __init__(self, options):
        """ Reads the font info and converts the info into usable members in this struct """
        defaults = GetDefaultOptions()

        cfg = SafeConfigParser()
        cfg.read(options.input)

        for name in defaults.iterkeys():
            if cfg.has_option('default', name):
                setattr(self, name, cfg.get('default', name) )
            else:
                setattr(self, name, defaults[name] )

        self.functionlist = dict()

        for section in cfg.sections():
            if section in ['default']:
                continue

            vars = dict(cfg.items(section))
            vars['section'] = section

            typename = vars.get('type', None)
            if typename is None:
                raise FontException("%s: There is no type specified" % section)
            try:
                cls = fonteffects.GetClassByName(typename)
            except KeyError:
                raise FontException("%s: There is no function type named %s" % (section, typename))

            self.functionlist[section] = cls(options, **vars)
            self.functionlist[section].name = section

        d = dict()
        d.update( self.functionlist )
        d.update( fontblend.BLENDFUNCTIONS )
        d['Layer'] = fonteffects.Layer

        if not cfg.has_option('default', 'layers'):
            raise FontException("A font must have at least one layer")

        self.layers = eval( cfg.get("default", "layers"), d, d )
        if cfg.has_option('default', 'posteffects'):
            self.posteffects = eval( cfg.get("default", "posteffects"), d, d )
        else:
            self.posteffects = []

        if not os.path.isabs(self.name):
            self.name = os.path.join( os.path.dirname(options.input), self.name )

        self.size = int(eval(self.size))
        if self.bitmapsize is None:
            self.bitmapsize = self.size
        else:
            self.bitmapsize = int(eval(self.bitmapsize))
        self.dpi = int(self.dpi)
        self.texturesize = tuple( map( int, self.texturesize.split(',') ) )
        self.textureoffset = tuple( map( int, self.textureoffset.split(',') ) )

        texturerender = __import__(self.texturerender)
        texturerender = getattr(texturerender, 'render', None)
        if not texturerender:
            raise FontException("The module %s doesn't implement render()" % self.texturerender)
        self.texturerender = texturerender
        
        texturewriter = __import__(self.texturewriter)
        texturewriter = getattr(texturewriter, 'write', None)
        if not texturewriter:
            raise FontException("The module %s doesn't implement write()" % self.texturewriter)
        self.texturewriter = texturewriter

        basedir, basename = os.path.split(self.writer)
        if basedir and not basedir in sys.path:
            sys.path.append(basedir)
        basename, ext = os.path.splitext(basename)
        writer = __import__(basename)
        if not getattr(writer, 'write', None):
            raise FontException("The module %s doesn't implement write()" % self.writer)
        self.writer = writer

        self.padding = int(self.padding)
        self.internalpadding = tuple( map( int, self.internalpadding.split(',') ) )
        self.useadvanceaswidth = int(self.useadvanceaswidth)
        self.usepairkernings = int(self.usepairkernings)
        self.usepremultipliedalpha = int(self.usepremultipliedalpha)

        self.bgcolor = eval(self.bgcolor)
        self.fgcolor = eval(self.fgcolor)
        self.bgcolor = map( lambda x: float(x)/255.0 if isinstance(x, int) else x, self.bgcolor )
        self.fgcolor = map( lambda x: float(x)/255.0 if isinstance(x, int) else x, self.fgcolor )

        if os.path.exists(self.letters):
            with open(self.letters, 'rb') as f:
                data = f.read()
            
            data = data.replace('\n', '').replace('\r', '')
            if not data:
                raise f.FontException("The file '%s' was empty" % self.letters)
            
            try:
                letters = [ ord(c) for c in str(data) ]
            except UnicodeEncodeError, e:
                letters = [ ord(c) for c in unicode(data) ] 
        else:
            letters = []
            for token in self.letters.split(','):
                if not token:
                    continue
                limits = token.split('-')
                if len(limits) == 1:
                    letters.append( int(limits[0], 16) )
                else:
                    letters += range( int(limits[0], 16), int(limits[1], 16) + 1 )

        self.letters = letters
        if not self.letters:
            raise FontException("There were no letters specified!")


def ReadFormat(f, format):
    return struct.unpack(format, f.read( struct.calcsize(format) ) )


class SPackedFontInfo(object):
    def __init__(self, texturename='', info=None):
        self.texture = texturename
        if info:
            self.name = info.name
            self.sizepixels = info.size     # the size in pixels
            self.sizefont = info.fontsize   # the size of the font
            self.spacing = info.padding
            self.texturesize = info.texturesize
            self.ascender = info.ascender
            self.descender = info.descender
            self.maxsize = info.maxsize
        else:
            self.name = ''
            self.texturesize = [0, 0]
            self.sizepixels = 0
            self.sizefont = 0
            self.spacing = 0
            self.ascender = 0
            self.descender = 0
            self.maxsize = [0, 0]

    def __str__(self):
        s = ''
        for n, v in self.__dict__.iteritems():
            if n.startswith('_'):
                continue
            s += '%s = %s\n' % (n, str(v))
        return s

    def write(self, f, endian):
        s = struct.pack(endian + '64s256s', self.name, self.texture )

        # 16 bytes
        s += struct.pack(endian + 'BBBBbBBxHHxxxx',
                                             self.sizepixels,
                                             self.sizefont,
                                             self.spacing,
                                             self.ascender,
                                             self.descender,
                                             self.maxsize[0],
                                             self.maxsize[1],
                                             self.texturesize[0],
                                             self.texturesize[1]
                                              )
        f.write( s )

    def read(self, f, endian):

        self.name, self.texture = ReadFormat(f, endian + '64s256s')

        self.name = self.name[:self.name.find('\0')]
        self.texture = self.texture[:self.texture.find('\0')]

        self.size, self.fontsize, self.spacing, self.ascender, self.descender, self.maxsize[0], self.maxsize[1], self.texturesize[0], self.texturesize[1] = ReadFormat(f, endian + 'BBBBbBBxHHxxxx')


class SFontChar(object):
    format = 'HHBBbb'

    def __init__(self, glyph=None):
        if glyph:
            self.x, self.y, self.width, self.height = getattr(glyph, 'bitmapbox', (0, 0, 0, 0) )
            self.utf8 = glyph.utf8
            self.advanceX = glyph.info.advance
            self.bearingY = glyph.info.bearingY
        else:
            assert( False )
            self.utf8 = 0
            self.x = 0
            self.y = 0
            self.width = 0
            self.height = 0
            self.advanceX = 0
            self.bearingY = 0

    def __str__(self):
        s = ''
        for n, v in self.__dict__.iteritems():
            if n.startswith('_'):
                continue
            s += '%s = %s\n' % (n, v)
        return s

    def write(self, f, endian):
        s = struct.pack( endian + SFontChar.format,
                                                self.x,
                                                self.y,
                                                self.width,
                                                self.height,
                                                self.advanceX,
                                                self.bearingY
                                                )
        f.write( s )

    def read(self, f, endian='='):
        self.x, self.y, self.width, self.height, self.advanceX, self.bearingY = ReadFormat(f, endian + SFontChar.format)


class SFont(object):
    def __init__(self, texture='', info=None, glyphs=None, kernings=None):
        if texture and info is not None:
            self.info = SPackedFontInfo(texture, info)
        if glyphs is not None:
            self.chars = [ SFontChar(glyph) for glyph in glyphs ]
        self.kernings = kernings if kernings else []

    def __str__(self):
        s = ''
        for n, v in self.__dict__.iteritems():
            if n.startswith('_'):
                continue
            s += '%s = %s\n' % (n, v)
        return s

    def write(self, f, endian):
        self.info.write( f, endian )

        s = struct.pack( endian + 'HH', len(self.chars), len(self.kernings) )
        f.write( s )

        pointeroffset_chars = f.tell() + struct.calcsize('IIII')
        pointeroffset_chars_glyphs = pointeroffset_chars + struct.calcsize('H') * len(self.chars)
        pointeroffset_kerning_chars = pointeroffset_chars_glyphs + struct.calcsize(SFontChar.format) * len(self.chars)
        pointeroffset_kerning_values = pointeroffset_kerning_chars + struct.calcsize('I') * len(self.kernings)

        #print self.info.texture, pointeroffset_chars, pointeroffset_chars_glyphs, pointeroffset_kerning_chars, pointeroffset_kerning_values

        s = struct.pack( endian + 'IIII', pointeroffset_chars, pointeroffset_chars_glyphs, pointeroffset_kerning_chars, pointeroffset_kerning_values )
        f.write( s )

        chars, glyphs = zip( *[ (c.utf8, c) for c in self.chars] )

        s = ''
        for char in chars:
            s += struct.pack( endian + 'H', char )
        f.write( s )

        for glyph in glyphs:
            glyph.write( f, endian )

        if self.kernings:
            chars, kernings = zip(*sorted(self.kernings.items()))
            s = ''
            for char in chars:
                s += struct.pack( endian + 'I', char )

            for kerning in kernings:
                s += struct.pack( endian + 'i', kerning )

            f.write( s )

    def read(self, f, endian='='):
        """ Reads a font from a .fntb file.
        This implementation is very Python specific, do not use it in your c/c++ code.
        Instead, do a single read of the file into a sufficient char* buffer, and then cast the buffer into a SFont object.
        Next, you should patch the pointers (to the glyphs and kerning chars/values)
        """

        self.info = SPackedFontInfo()
        self.info.read( f, endian )

        len_chars, len_kernings = ReadFormat(f, endian + 'HH')

        pointeroffset_chars, pointeroffset_chars_glyphs, pointeroffset_kerning_chars, pointeroffset_kerning_values = ReadFormat(f, endian + 'IIII')

        chars = [0] * len_chars
        for i in xrange(len_chars):
            chars[i] = ReadFormat(f, endian + 'H')[0]

        glyphs = []
        for i in xrange(len_chars):
            char = SFontChar()
            char.read(f, endian)
            glyphs.append(char)

        """
        print self.info.name
        for index, (char, glyph) in enumerate( zip(chars, glyphs) ):
            print "%d: char %c %d  x,y: %d, %d  w,h: %d, %d  adv: %d" % ( index, char, int(char), glyph.x, glyph.y, glyph.width, glyph.height, glyph.advanceX )
        print ""
        print ""
        """

        self.chars = dict( zip(chars, glyphs) )

        kerning_chars = list( ReadFormat(f, endian + 'I' * len_kernings))
        kerning_values = list( ReadFormat(f, endian + 'i' * len_kernings))
        self.kernings = dict( zip(kerning_chars, kerning_values) )


def Extension():
    return '.fntb'


def Write(options, info, glyphs, pairkernings):
    font = SFont( options.texturename, info, glyphs, pairkernings )
    f = open( options.output, 'wb')
    font.write( f, options.endian )
    f.close()
    return 0


