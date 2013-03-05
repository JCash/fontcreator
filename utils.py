"""
A set of C++ functions that help out with the image processing etc.

The Signed Euclidian Distance Transform functionality is taken from http://www.gbuffer.net/vector-textures
"""

import sys
import numpy as np
import ctypes
from ctypes import POINTER, byref, c_void_p, c_size_t, c_float, c_uint32

c_float_p = POINTER(c_float)

if sys.platform == 'darwin':
    _suffix = '.dylib'
    platformdir = 'darwin64' if sys.maxsize > 2**32 else 'darwin32'
elif sys.platform == 'win32':
    _suffix = '.dll'
    platformdir = 'win64' if sys.maxsize > 2**32 else 'win32'
elif sys.platform == 'linux2':
    _suffix = '.so'
    platformdir = 'linux64' if sys.maxsize > 2**32 else 'linux32'

try:
    path = '_utils%s' % (_suffix)
    _utils = ctypes.cdll.LoadLibrary(path)
except (OSError,):
    raise IOError("FAILED TO OPEN " + path)

LAYOUT_INTERLEAVED = 0
LAYOUT_STACKED = 1

TYPE_UINT = 0
TYPE_FLOAT = 1


class Image(ctypes.Structure):
    _fields_ = [
        ('data', c_void_p),
        ('width', c_size_t),
        ('height', c_size_t),
        ('channels', c_size_t),
        ('layout', c_uint32, 2),
        ('type', c_uint32, 2),
        ('bitdepth', c_uint32, 26),
    ]


_convolve1d = _utils.convolve1d
_convolve1d.argtypes = [POINTER(Image), c_float_p, c_size_t, c_size_t, c_void_p]

_maximum = _utils.maximum
_maximum.argtypes = [POINTER(Image), c_float_p, c_size_t, c_size_t, c_void_p]

_minimum = _utils.minimum
_minimum.argtypes = [POINTER(Image), c_float_p, c_size_t, c_size_t, c_void_p]

_half_size = _utils.half_size
_half_size.argtypes = [POINTER(Image), c_void_p]

_calculate_sedt = _utils.calculate_sedt
_calculate_sedt.argtypes = [POINTER(Image), c_float, c_void_p]


def _make_image(npimage):
    image = Image()
    image.data = npimage.ctypes.data_as(c_void_p)
    
    if len(npimage.shape) == 2:
        image.width, image.height = npimage.shape
        image.channels = 1
    else:
        image.width, image.height, image.channels = npimage.shape
        
    image.layout = LAYOUT_INTERLEAVED if npimage.flags.c_contiguous else LAYOUT_STACKED
    
    typ = npimage.dtype
    if typ in (np.ubyte, np.uint8, np.uint16, np.uint32, np.uint64):
        image.type = TYPE_UINT
    elif typ in (np.float16, np.float32, np.float64):
        image.type = TYPE_FLOAT
    
    if typ in (np.ubyte, np.uint8):
        image.bitdepth = 8
    elif typ in (np.uint16, np.float16):
        image.bitdepth = 16
    elif typ in (np.uint32, np.float32):
        image.bitdepth = 32
    elif typ in (np.uint64, np.float64):
        image.bitdepth = 64
        
    return image

def _make_kernel(kernel):
    if isinstance(kernel, list):
        kernel = np.array(kernel, dtype=np.float32)
    if kernel.dtype == np.float64:
        kernel = np.array( [x for x in kernel], dtype=np.float32)
    return kernel
    

def convolve1d(npimage, kernel, axis):
    out = np.empty_like(npimage)
    image = _make_image(npimage)
    kernel = _make_kernel(kernel)
    _convolve1d(byref(image), kernel.ctypes.data_as(c_float_p), len(kernel), axis, out.ctypes.data_as(c_void_p))
    return out


def maximum(npimage, kernel):
    out = np.empty_like(npimage)
    image = _make_image(npimage)
    kernel = _make_kernel(kernel)
    _maximum( byref(image), kernel.ctypes.data_as(c_float_p), kernel.shape[0], kernel.shape[1], out.ctypes.data_as(c_void_p))
    return out


def minimum(npimage, kernel):
    out = np.empty_like(npimage)
    image = _make_image(npimage)
    kernel = _make_kernel(kernel)
    _minimum( byref(image), kernel.ctypes.data_as(c_float_p), kernel.shape[0], kernel.shape[1], out.ctypes.data_as(c_void_p))
    return out

def half_size(npimage):
    depth = 1 if len(npimage.shape) == 2 else npimage.shape[2]
    if npimage.flags.f_contiguous:  # stacked
        empty = np.empty( (npimage.shape[0]//2, npimage.shape[1]//2), npimage.dtype )
        if depth == 1:
            out = np.dstack( (empty,) )
        elif depth == 2:
            out = np.dstack( (empty, empty) )
        elif depth == 3:
            out = np.dstack( (empty, empty, empty) )
        elif depth == 4:
            out = np.dstack( (empty, empty, empty, empty) )
    else:
        if depth == 1:
            out = np.empty( (npimage.shape[0]//2, npimage.shape[1]//2), npimage.dtype )
        else:
            out = np.empty( (npimage.shape[0]//2, npimage.shape[1]//2, depth), npimage.dtype )

    image = _make_image(npimage)
    _half_size(byref(image), out.ctypes.data_as(c_void_p))
    return out

def calculate_sedt(npimage, radius):
    assert len(npimage.shape) == 2 or npimage.shape[2] == 1, "calculate_sed only supports 1 channel bitmaps"
    out = np.empty_like(npimage)
    image = _make_image(npimage)
    _calculate_sedt( byref(image), radius, out.ctypes.data_as(c_void_p))
    return out
    
