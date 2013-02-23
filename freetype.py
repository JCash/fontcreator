""" A lightweight freetype binding that suits the font creator.
If you want something more thorough, check these out instead:

http://code.google.com/p/freetype-py/source/browse/trunk/
https://github.com/leovitch/python-ft2/

"""

import sys
import ctypes
from ctypes import POINTER, byref, c_void_p, c_char_p, c_long, c_ulong, c_int, c_uint, c_uint32, c_short, c_ushort, c_ubyte, c_char

if sys.platform == 'darwin':
    _prefix = 'lib'
    _suffix = '.dylib'
elif sys.platform == 'win32':
    _prefix = ''
    _suffix = '.dll'
elif sys.platform == 'linux2':
    _prefix = 'lib'
    _suffix = '.so'

try:
    path = '%sfreetype%s' % (_prefix, _suffix)
    _freetype = ctypes.cdll.LoadLibrary(path)
except (WindowsError,):
    raise IOError("FAILED TO OPEN " + path)

c_int_p = POINTER(ctypes.c_int)
c_uint_p = POINTER(ctypes.c_uint)
c_pos = c_long
c_fixed = c_long
c_f26dot6 = c_long

class FTError(Exception):
    def __init__(self, res, msg):
        super(Exception, self).__init__(msg)
        self.res = res
        
    def __str__(self):
        return "%d: %s" % (self.res, self._msgs.get(self.res, '<unknown>'))
    
    _msgs = {
        0: 'ok',
    }


LOAD_DEFAULT                      = 0x0
LOAD_NO_SCALE                     = ( 1L << 0 )
LOAD_NO_HINTING                   = ( 1L << 1 )
LOAD_RENDER                       = ( 1L << 2 )
LOAD_NO_BITMAP                    = ( 1L << 3 )
LOAD_VERTICAL_LAYOUT              = ( 1L << 4 )
LOAD_FORCE_AUTOHINT               = ( 1L << 5 )
LOAD_CROP_BITMAP                  = ( 1L << 6 )
LOAD_PEDANTIC                     = ( 1L << 7 )
LOAD_IGNORE_GLOBAL_ADVANCE_WIDTH  = ( 1L << 9 )
LOAD_NO_RECURSE                   = ( 1L << 10 )
LOAD_IGNORE_TRANSFORM             = ( 1L << 11 )
LOAD_MONOCHROME                   = ( 1L << 12 )
LOAD_LINEAR_DESIGN                = ( 1L << 13 )
LOAD_NO_AUTOHINT                  = ( 1L << 15 )

RENDER_MODE_NORMAL   = 0
RENDER_MODE_LIGHT    = 1
RENDER_MODE_MONO     = 2
RENDER_MODE_LCD      = 3
RENDER_MODE_LCD_V    = 4
RENDER_MODE_MAX      = 5

def _LOAD_TARGET( x ):
    return ( x & 15 ) << 16

LOAD_TARGET_NORMAL  = _LOAD_TARGET( RENDER_MODE_NORMAL )
LOAD_TARGET_LIGHT   = _LOAD_TARGET( RENDER_MODE_LIGHT  )
LOAD_TARGET_MONO    = _LOAD_TARGET( RENDER_MODE_MONO   )
LOAD_TARGET_LCD     = _LOAD_TARGET( RENDER_MODE_LCD    )
LOAD_TARGET_LCD_V   = _LOAD_TARGET( RENDER_MODE_LCD_V  )

KERNING_DEFAULT  = 0
KERNING_UNFITTED = 1
KERNING_UNSCALED = 2


def _ENCODE(a, b, c, d):
    return ord(a) << 24 | ord(b) << 16 | ord(c) << 8 | ord(d)

ENCODING_NONE = 0
ENCODING_MS_SYMBOL = _ENCODE('s', 'y', 'm', 'b')
ENCODING_UNICODE = _ENCODE( 'u', 'n', 'i', 'c' )
ENCODING_SJIS = _ENCODE( 's', 'j', 'i', 's' )
ENCODING_GB2312 = _ENCODE( 'g', 'b', ' ', ' ' )
ENCODING_BIG5 = _ENCODE( 'b', 'i', 'g', '5' )
ENCODING_WANSUNG = _ENCODE( 'w', 'a', 'n', 's' )
ENCODING_JOHAB = _ENCODE( 'j', 'o', 'h', 'a' )

# for backwards compatibility
ENCODING_MS_SJIS    = ENCODING_SJIS
ENCODING_MS_GB2312  = ENCODING_GB2312
ENCODING_MS_BIG5    = ENCODING_BIG5
ENCODING_MS_WANSUNG = ENCODING_WANSUNG
ENCODING_MS_JOHAB   = ENCODING_JOHAB

ENCODING_ADOBE_STANDARD = _ENCODE( 'A', 'D', 'O', 'B' )
ENCODING_ADOBE_EXPERT = _ENCODE( 'A', 'D', 'B', 'E' )
ENCODING_ADOBE_CUSTOM = _ENCODE( 'A', 'D', 'B', 'C' )
ENCODING_ADOBE_LATIN_1 = _ENCODE( 'l', 'a', 't', '1' )
ENCODING_OLD_LATIN_2 = _ENCODE( 'l', 'a', 't', '2' )
ENCODING_APPLE_ROMAN = _ENCODE( 'a', 'r', 'm', 'n' )
    

class LibraryRec(ctypes.Structure):
    pass
LibraryPtr = POINTER(LibraryRec)


class Bitmap(ctypes.Structure):
    _fields_ = [
        ('rows', c_int),
        ('width', c_int),
        ('pitch', c_int),
        ('buffer', POINTER(c_ubyte)),
        ('num_grays', c_short),
        ('pixel_mode', c_char),
        ('palette_mode', c_char),
        ('palette', c_void_p),
    ]


class BitmapSize(ctypes.Structure):
    _fields_ = [
        ('height', c_short),
        ('width', c_short),
        ('size', c_long),
        ('x_ppem', c_long),
        ('y_ppem', c_long),
    ]

    
class CharMapRec(ctypes.Structure):
    _fields_ = [
        ('face', c_void_p),
        ('encoding', c_int),
        ('platform_id', c_ushort),
        ('encoding_id', c_ushort),
    ]
CharMap = POINTER(CharMapRec)


class Generic(ctypes.Structure):
    _fields_ = [
        ('data', c_void_p),
        ('finalizer', ctypes.CFUNCTYPE(None, c_void_p))
    ]


class BBox(ctypes.Structure):
    _fields_ = [
        ('xMin', c_long),
        ('yMin', c_long),
        ('xMax', c_long),
        ('yMax', c_long)
    ]


class Vector(ctypes.Structure):
    _fields_ = [
        ('x', c_pos),
        ('y', c_pos),
    ]


class GlyphMetrics(ctypes.Structure):
    _fields_ = [
        ('width', c_pos),
        ('height', c_pos),
        ('horiBearingX', c_pos),
        ('horiBearingY', c_pos),
        ('horiAdvance', c_pos),
        ('vertBearingX', c_pos),
        ('vertBearingY', c_pos),
        ('vertAdvance', c_pos),
    ]


class Outline(ctypes.Structure):
    _fields_ = [
        ('n_contours', c_short),
        ('n_points', c_short),
        ('points', POINTER(Vector)),
        ('tags', POINTER(c_ubyte)),  # As seen in freetype-py, for being able to access all flags
        ('points', POINTER(c_short)),
        ('flags', c_int),
    ]


class GlyphSlotRec(ctypes.Structure):
    _fields_ = [
        ('library', POINTER(LibraryRec)),
        ('face', c_void_p),
        ('next', c_void_p),
        ('reserved', c_uint),
        ('generic', Generic),
        ('metrics', GlyphMetrics),
        ('linearHoriAdvance', c_fixed),
        ('linearVertAdvance', c_fixed),
        ('advance', Vector),
        ('format', c_int),
        ('bitmap', Bitmap),
        ('bitmap_left', c_int),
        ('bitmap_top', c_int),
        
        ('outline', Outline),

        ('num_subglyphs', c_uint),
        ('subglyphs', c_void_p),
        
        ('control_data', c_void_p),
        ('control_len', c_long),
        
        ('lsb_delta', c_pos),
        ('rsb_delta', c_pos),

        ('other', c_void_p),        
        ('internal', c_void_p),
    ]


class SizeMetrics(ctypes.Structure):
    _fields_ = [
        ('x_ppem', c_ushort),
        ('y_ppem', c_ushort),
        ('x_scale', c_fixed),
        ('y_scale', c_fixed),
        ('ascender', c_pos),
        ('descender', c_pos),
        ('height', c_pos),
        ('max_advance', c_pos),
    ]


class SizeRec(ctypes.Structure):
    _fields_ = [
        ('face', c_void_p),
        ('generic', Generic),
        ('metrics', SizeMetrics),
        ('internal', c_void_p),
    ]


class FaceRec(ctypes.Structure):
    _fields_ = [
        ('num_faces', c_long),
        ('face_index', c_long),
        ('face_flags', c_long),
        ('style_flags', c_long),
        ('num_glyphs', c_long),
        
        ('family_name', c_char_p),
        ('style_name', c_char_p),
        
        ('num_fixed_sizes', c_int),
        ('available_sizes', POINTER(BitmapSize)),
        
        ('num_charmaps', c_int),
        ('_charmaps', POINTER(CharMap)),
        
        ('generic', Generic),
        
        ('bbox', BBox),
        
        ('units_per_EM', c_ushort),
        ('ascender', c_short),
        ('descender', c_short),
        ('height', c_short),
        
        ('max_advance_width', c_short),
        ('max_advance_height', c_short),
        
        ('underline_position', c_short),
        ('underline_thickness', c_short),
        
        ('glyph', POINTER(GlyphSlotRec)),
        ('_size', POINTER(SizeRec)),
        
        ('charmap', CharMap),
        
        # private members
        ('_driver', c_void_p),
        ('_memory', c_void_p),
        ('_stream', c_void_p),
        ('_sizes_list', c_void_p),
        ('_autohint', Generic),
        ('_extensions', c_void_p),
        ('_internal', c_void_p),
    ]
    
    def set_char_size(self, width=0, height=0, hres=72, vres=72):
        res = _set_char_size( byref(self), width, height, hres, vres )
        if res:
            raise FTError(res, "Failed setting the character size")
    
    def get_char_index(self, char):
        if type(char) in (str, unicode):
            char = ord(char)
        if not hasattr(self, '_cache_char_index'):
            setattr(self, '_cache_char_index', dict())
        if not char in self._cache_char_index:
            index = _get_char_index( byref(self), char )
            self._cache_char_index[char] = index
        return self._cache_char_index[char]
            
    
    def get_kerning(self, left, right, mode = KERNING_DEFAULT):
        lindex = self.get_char_index( left )
        rindex = self.get_char_index( right )
        kerning = Vector()
        res = _get_kerning(byref(self), lindex, rindex, mode, byref(kerning))
        if res:
            raise FTError(res, "Failed to get kerning for pair")
        return kerning
    
    @property
    def charmaps(self):
        return [ self._charmaps[i].contents for i in range( self.num_charmaps ) ]
    
    @property
    def size(self):
        return self._size.contents.metrics
    
    def load_char(self, char, flags = LOAD_RENDER):
        if len(char) == 1:
            char = ord(char)
        res = _load_char( byref(self), char, flags)
        if res:
            raise FTError(res, "Failed to load char: '%s'" % str(char))


_init = _freetype.FT_Init_FreeType
_init.restype = c_int
_init.argtypes = [POINTER(LibraryPtr)]


def init():
    library = LibraryPtr()
    res = _init( byref(library) )
    if res:
        raise FTError(res, "Failed initializing the library")
    return library

_library_version = _freetype.FT_Library_Version
_library_version.argtypes = [POINTER(LibraryRec), c_int_p, c_int_p, c_int_p]

def version():
    major = c_int()
    minor = c_int()
    patch = c_int()
    _freetype.FT_Library_Version(_library, byref(major), byref(minor), byref(patch))
    return (major.value, minor.value, patch.value)


_bitmap_convert = _freetype.FT_Bitmap_Convert
_bitmap_convert.restype = c_int
_bitmap_convert.argtypes = [POINTER(LibraryRec), POINTER(Bitmap), POINTER(Bitmap), c_int]

def bitmap_convert(source, target, alignment):
    res = _bitmap_convert( _library, byref(source), byref(target), alignment)
    if res:
        raise FTError(res, "Failed converting bitmap")

_new_face = _freetype.FT_New_Face
_new_face.restype = c_int
_new_face.argtypes = [POINTER(LibraryRec), c_char_p, c_int, POINTER(POINTER(FaceRec))]


def new_face(path, index = 0):
    face = POINTER(FaceRec)()
    res = _new_face( _library, path, index, byref(face))
    if res:
        raise FTError(res, "Failed loading face: %s" % path)
    return face.contents


_done_face = _freetype.FT_Done_Face
_done_face.restype = c_int
_done_face.argtypes = [POINTER(FaceRec)]


def done_face(face):
    res = _done_face( byref(face) )
    if res:
        return face
    raise FTError(res, "Failed destroying face")

_set_char_size = _freetype.FT_Set_Char_Size
_set_char_size.restype = c_int
_set_char_size.argtypes = [POINTER(FaceRec), c_f26dot6, c_f26dot6, c_uint, c_uint]

_get_char_index = _freetype.FT_Get_Char_Index
_get_char_index.restype = c_uint
_get_char_index.argtypes = [POINTER(FaceRec), c_ulong]

_load_char = _freetype.FT_Load_Char
_load_char.restype = c_uint
_load_char.argtypes = [POINTER(FaceRec), c_ulong, c_uint32]

_get_kerning = _freetype.FT_Get_Kerning
_get_kerning.restype = c_uint
_get_kerning.argtypes = [POINTER(FaceRec), c_uint, c_uint, c_uint, POINTER(Vector)]

    
# Finally, initialize the module    
_library = init()
