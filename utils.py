"""
A set of C++ functions that help out with the image processing etc.

The Signed Euclidian Distance Transform functionality is taken from http://www.gbuffer.net/vector-textures
"""

import sys, os
import numpy as np
import ctypes
from ctypes import POINTER, byref, c_void_p, c_size_t, c_float, c_uint32

c_float_p = POINTER(c_float)

if sys.platform == 'darwin':
    _suffix = '.dylib'
elif sys.platform == 'win32':
    _suffix = '.dll'
elif sys.platform == 'linux2':
    _suffix = '.so'
    
_dirpath = os.path.dirname(__file__)
_utils = ctypes.cdll.LoadLibrary(os.path.join(_dirpath, '_utils%s' % _suffix))

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


def _make_image(npimage, layout):
    image = Image()
    image.data = npimage.ctypes.data_as(c_void_p)
    
    if len(npimage.shape) == 2:
        image.width, image.height = npimage.shape
        image.channels = 1
    else:
        image.width, image.height, image.channels = npimage.shape
        
    image.layout = layout
    
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
    

def convolve1d(npimage, kernel, axis, layout=LAYOUT_STACKED):
    out = np.empty_like(npimage)
    image = _make_image(npimage, layout)
    kernel = _make_kernel(kernel)
    _convolve1d(byref(image), kernel.ctypes.data_as(c_float_p), len(kernel), axis, out.ctypes.data_as(c_void_p))
    return out

def half_size(npimage, layout=LAYOUT_STACKED):
    out = np.empty( (npimage.shape[0]/2, npimage.shape[1]/2, npimage.shape[2]) )
    image = _make_image(npimage, layout)
    _half_size(byref(image), out.ctypes.data_as(c_void_p))
    return out


def maximum(npimage, kernel, layout=LAYOUT_STACKED):
    out = np.empty_like(npimage)
    image = _make_image(npimage, layout)
    kernel = _make_kernel(kernel)
    _maximum( byref(image), kernel.ctypes.data_as(c_float_p), kernel.shape[0], kernel.shape[1], out.ctypes.data_as(c_void_p))
    return out


def minimum(npimage, kernel, layout=LAYOUT_STACKED):
    out = np.empty_like(npimage)
    image = _make_image(npimage, layout)
    kernel = _make_kernel(kernel)
    _minimum( byref(image), kernel.ctypes.data_as(c_float_p), kernel.shape[0], kernel.shape[1], out.ctypes.data_as(c_void_p))
    return out

def half_size(npimage, layout=LAYOUT_STACKED):
    depth = 1 if len(npimage.shape) == 2 else npimage.shape[2]
    if layout == LAYOUT_STACKED:
        empty = np.empty( (npimage.shape[0]//2, npimage.shape[1]//2) )
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
            out = np.empty( (npimage.shape[0]//2, npimage.shape[1]//2) )
        else:
            out = np.empty( (npimage.shape[0]//2, npimage.shape[1]//2, depth) )

    image = _make_image(npimage, layout)
    _half_size(byref(image), out.ctypes.data_as(c_void_p))
    return out

def calculate_sedt(npimage, radius, layout=LAYOUT_STACKED):
    assert len(npimage.shape) == 2 or npimage.shape[2] == 1, "calculate_sed only supports 1 channel bitmaps"
    out = np.empty_like(npimage)
    image = _make_image(npimage, layout)
    _calculate_sedt( byref(image), radius, out.ctypes.data_as(c_void_p))
    return out
    

