"""
Copyright @ 2013 Mathias Westerdahl

The fonteffects module provides commonly used base functionality for the effects.
"""

import os, logging
import numpy as np

try:
    import Image
except ImportError:
    from PIL import Image

import utils
import freetype as ft
import fontutils as fu
import fontblend as fb
from editor.properties.propertyclass import WrapPropertyClass
import editor.properties.propertytypes as prop

# good reads:
#    http://www.imagemagick.org/Usage/morphology/
#    http://stackoverflow.com/questions/5919663/how-does-photoshop-blend-two-images-together
#    http://dunnbypaul.net/blends/
#    DistanceFields: http://www.valvesoftware.com/publications/2007/SIGGRAPH2007_AlphaTestedMagnification.pdf

# TODO:
#    Bevel effect
#    Extrude effect

_CLASSES = dict()
colorfunctions = dict()
effectfunctions = dict()


def GetClassByName(name):
    return _CLASSES[name]


def GetClassType(cls):
    return cls.function_type


def ColorFunction(cls):
    """ Registers a class as a color function
    """
    assert( getattr(cls, '__call__') )
    WrapPropertyClass(cls)
    cls.function_type = 'color'
    _CLASSES[cls.__name__.lower()] = cls
    colorfunctions[cls.__name__.lower()] = cls
    logging.info( "Registered layer function %s" % cls.__name__.lower() )
    return cls


def GetColorFunction(name):
    return colorfunctions[name]




def EffectFunction(cls):
    """ Registers a class as a effect function
    """
    assert( getattr(cls, '__call__') )
    WrapPropertyClass(cls)
    cls.function_type = 'effect'
    _CLASSES[cls.__name__.lower()] = cls
    effectfunctions[cls.__name__.lower()] = cls
    logging.info( "Registered effect function %s" % cls.__name__.lower() )
    return cls

def GetEffectFunction(name):
    return effectfunctions[name]


class FontEffectException(Exception):
    """ An internal exception class used for font creator exceptions """
    pass


# ****************************************************************************************************

# Found an excellent reference here:
# http://dunnbypaul.net/blends/



# ****************************************************************************************************


def _convert_color_to_units(colors):
    """ Converts colors from 0-255 range into 0.0-1.0 range

    :param colors: A 3-tuple of integers or floats (floats in range [0.0, 1.0])
    """
    if isinstance(colors, tuple):
        if len(colors) != 3:
            raise FontEffectException("Colors should be specified with 3-tuples (float[0.0, 1.0] or int[0, 255])")
        if isinstance(colors[0], float):
            return colors
        else:
            return (colors[0] / 255.0, colors[1] / 255.0, colors[2] / 255.0)

    out = []
    for c in colors:
        if len(c) != 3:
            raise FontEffectException("Colors should be specified with 3-tuples (float[0.0, 1.0] or int[0, 255])")
        if isinstance(c[0], float):
            out.append( c )
        else:
            out.append( (c[0] / 255.0, c[1] / 255.0, c[2] / 255.0) )
    return out


# ****************************************************************************************************

@ColorFunction
class Solid(object):
    """ Creates solid fill with a single color

    :param color: A color as (r,g,b) [0,255]
    """
    color = prop.ColorProperty( (255,255,255) )

    def __init__(self, *k, **kw):
        for name, value in kw.iteritems():
            try:
                setattr(self, name, eval(value) )
            except NameError:
                setattr(self, name, value )
            except TypeError, e:
                raise fu.FontException("Solid: Error while evaluating '%s':\n%s" % (value, str(e)))
        self.color = _convert_color_to_units( self.color )
        if len(self.color) == 3:
            self.color = (self.color[0], self.color[1], self.color[2], 1.0)

    def apply(self, info, glyph, startx, starty, size, maxsize, glyphimage, previmage):
        return previmage * self.color


@ColorFunction
class Gradient(object):
    """ Creates a gradient between two or more colors.

    :param colors:       A list of colors (3 tuples) to interpolate between. [bottom color, ..., top color]
    :param angle:        The angle of rotation (in degrees)
    """
    colors = [(0,0,0), (255,255,255)]
    angle = prop.AngleProperty( 120, help='The angle of rotation (in degrees)' )

    def __init__(self, *k, **kw):
        for name, value in kw.iteritems():
            try:
                setattr(self, name, eval(value) )
            except:
                setattr(self, name, value)

        if len(self.colors) < 2:
            raise FontEffectException("Gradient must have more than one color to blend with")
        self.colors = _convert_color_to_units(self.colors)

    def set_dimensions(self, width, height):
        angle = self.angle / 180.0 * np.pi
        normal = np.array([0,-height/2.0])
        cosa = np.cos(angle)
        sina = np.sin(angle)

        rotation = np.array([[cosa, -sina], [sina, cosa]])
        normal = (rotation * normal)[:,1]
        lengthsq = np.dot(normal,normal)
        normal /= np.sqrt(lengthsq)

        # calculate the dot product with the normal
        halfextents = ( (width)/2.0, (height)/2.0 )
        origin = np.array( [np.round(halfextents[0]), np.round(halfextents[1])], float)
        maxextents = np.sqrt( halfextents[0]*halfextents[0]*np.abs(normal[0]) + halfextents[1]*halfextents[1]*np.abs(normal[1]) )
        maxextents = np.round(maxextents)

        data = np.empty((width,height,4), dtype=np.float32)
        for x in xrange(0, width):
            for y in xrange(0, height):

                v = np.array([x,y], dtype=float)
                v -= origin

                d = (np.dot(v, normal) / maxextents) / 2.0 + 0.5
                d = np.clip( d, 0.0, 1.0 )

                lenminusone = len(self.colors) - 1

                index = int(d * lenminusone)
                subunit = (d * lenminusone) % 1.0
                if index == lenminusone:
                    index -= 1
                    subunit = 1.0

                c1 = self.colors[index]
                c2 = self.colors[index+1]
                r = c1[0] + (c2[0] - c1[0]) * subunit
                g = c1[1] + (c2[1] - c1[1]) * subunit
                b = c1[2] + (c2[2] - c1[2]) * subunit
                a = 1.0

                data[x,y] = (r,g,b,a)

        self.bitmap = data

    def apply(self, info, glyph, startx, starty, size, maxsize, glyphimage, previmage):
        bm = np.array(self.bitmap[startx:startx+size[0], starty:starty+size[1]])
        assert bm.shape == previmage.shape, "Wrong sizes: %s != %s" % ( str(bm.shape), str(previmage.shape) )
        
        idx = np.where(glyphimage == 0)
        r,g,b = (bm[:,:,0], bm[:,:,1], bm[:,:,2])
        r[idx] = 0
        g[idx] = 0
        b[idx] = 0
        a = previmage[:, :, 3]
        return np.dstack((r,g,b,a))


@ColorFunction
class Stripes(object):
    """ Creates stripes with alternating colors

    :param width:        The width of the stripes
    :param offset:       The start offset of the stripes
    :param angle:        The angle of rotation (in degrees)
    :param colors:       The alternating colors of the stripes. May be more than 2
    """

    width = prop.IntProperty( 4, help='The width of the stripes' )
    offset = prop.IntProperty( 0, help='The start offset of the stripes' )
    angle = prop.AngleProperty( 0, help='The angle of rotation (in degrees)' )

    colors = [(0,0,0), (255,255,255)]

    def __init__(self, *k, **kw):
        self.width = self.__class__.width
        self.offset = self.__class__.offset
        self.angle = self.__class__.angle
        self.colors = self.__class__.colors

        for name, value in kw.iteritems():
            try:
                setattr(self, name, eval(value) )
            except NameError:
                setattr(self, name, value )
        self.colors = _convert_color_to_units( self.colors )

    def set_dimensions(self, width, height):
        angle = self.angle / 180.0 * np.pi
        normal = np.array([0,height/2.0])
        cosa = np.cos(angle)
        sina = np.sin(angle)

        rotation = np.array([[cosa, -sina], [sina, cosa]])
        normal = (rotation * normal)[:,1]

        lengthsq = np.dot(normal,normal)
        normal /= np.sqrt(lengthsq)

        # place the rotation in the middle and project a corner point
        # onto the normal. Then we can find out the max extents of the blend
        #origin = np.array([width/2.0, height/2.0])
        origin = np.array( [np.round(width/2.0), np.round(height/2.0)], float)
        maxextents = np.sqrt( np.dot( origin, origin ) )
        maxextents = np.round(maxextents)

        data = np.empty((width,height,4), dtype=np.float32)
        for x in xrange(0, width):
            for y in xrange(0, height):

                v = np.array([x,y], dtype=float)
                v -= origin

                lengthsq = np.dot(v,v)

                d = (np.dot( v, normal ) / maxextents) / 2.0 + 0.5

                unity = d

                subunit = unity
                invsubunit = 1 - subunit
                index = 0

                c1 = self.colors[index]
                c2 = self.colors[index+1]
                r = c1[0] * invsubunit + c2[0] * subunit
                g = c1[1] * invsubunit + c2[1] * subunit
                b = c1[2] * invsubunit + c2[2] * subunit

                data[x,y] = (r,g,b, 1.0)

        self.bitmap = data

    def apply(self, info, glyph, startx, starty, size, maxsize, glyphimage, previmage):
        return self.bitmap[startx:startx+size[0], starty:starty+size[1]]


@ColorFunction
class Texture(object):
    """ Applies a texture as a color function

    :param options:     The command line options
    :param name:        The texture name relative to options.datadir.
    """

    name = prop.FileProperty( default='', help='The texture name relative to options.datadir.' )

    def __init__(self, *k, **kw):
        options = k[0]
        for name, value in kw.iteritems():
            try:
                setattr(self, name, eval(value) )
            except NameError:
                setattr(self, name, value )
            except SyntaxError:
                if value and value[0] == '.':  # relative paths are ok
                    setattr(self, name, value )
                else:
                    raise

        if not os.path.exists( os.path.join(options.datadir, self.name)):
            raise fu.FontException("No such file: %s  in dir %s" % (self.name, options.datadir))

        self.bitmap = np.asarray( Image.open( os.path.join(options.datadir, self.name) ), float) / 255.0

        if self.bitmap.shape[2] == 3:
            r, g, b = fu.split_channels(self.bitmap)
            a = np.ones_like(r)
            #self.bitmap = np.dstack((r, g, b, a))
        else:
            r, g, b, a = fu.split_channels(self.bitmap)
        self.bitmap = np.dstack( (r.T, g.T, b.T, a.T) )

    def set_dimensions(self, width, height):
        # TODO: Add option to enable this wrap
        while self.bitmap.shape[0] < width:
            self.bitmap = np.concatenate( (self.bitmap, self.bitmap), axis=0)
        while self.bitmap.shape[1] < height:
            self.bitmap = np.concatenate( (self.bitmap, self.bitmap), axis=1)

    def apply(self, info, glyph, startx, starty, size, maxsize, glyphimage, previmage):
        return self.bitmap[startx:startx+size[0], starty:starty+size[1]]


@EffectFunction
class Outline(object):
    """ Creates an outline around the glyph

    :param color:   The color of the outline
    :param opacity: The opacity of the color [0,100]
    :param width:   The width of the outline
    :param spread:  The radius of the blur of the outline
    """
    color = prop.ColorProperty( (0, 0, 0) )
    opacity = prop.OpacityProperty( 100 )
    width = prop.Size1DProperty( 1 )
    spread = prop.Size1DProperty( 0 )

    def __init__(self, *k, **kw):
        """
        @param color        The color (r,g,b) of the outline
        @param width        The width of the outline
        @param opacity      The opacity of the outline (in percent)
        """

        for name, value in kw.iteritems():
            try:
                setattr(self, name, eval(value) )
            except NameError:
                setattr(self, name, value )

        self.color = [ float(x) / 255.0 for x in self.color]
        self.opacity = float(self.opacity) / 100.0
        self.kernel = fu.create_2d_circle_kernel(self.width)
        
        r = self.width + self.spread
        self.padding = (r, r, r, r)
        """ Return the amount of padding needed to fit the effect as a 4 tuple (left, top, right, bottom) """ 

    def apply(self, info, glyph, image):        
        out = utils.maximum(image, self.kernel)
        
        if self.spread:
            out = fu.blur_image(out, self.spread)

        r, g, b, a = (out[:, :, 0], out[:, :, 1], out[:, :, 2], out[:, :, 3])
        
        r[np.nonzero(r)] = self.color[0]
        g[np.nonzero(g)] = self.color[1]
        b[np.nonzero(b)] = self.color[2]
        a *= self.opacity
        
        return fu.alpha_blend(out, image)


@EffectFunction
class DropShadow(object):
    """ Applies a drop shadow to the glyphs
    """
    
    #: The color of the shadow
    color = (0, 0, 0)
    #: The opacity of the shadow (in percent)
    opacity = 100
    #: The angle of the shadow (in degrees)
    angle = 120
    #: The spread of the shadow (in pixels)
    size = 1
    #: The offset of the shadow
    distance = 3

    def __init__(self, *k, **kw):
        """
        @param color      The color (r,g,b) of the shadow. For best results, should be the same color as the background color
        @param opacity    The opacity of the shadow (in percent)
        @param angle      The lighting angle (in degrees)
        @param size       The spread of the shadow
        @param distance   The offset in the direction of the lighting angle
        """
        self.color = self.__class__.color
        self.opacity = self.__class__.opacity
        self.angle = self.__class__.angle
        self.size = self.__class__.size
        self.distance = self.__class__.distance

        for name, value in kw.iteritems():
            try:
                setattr(self, name, eval(value) )
            except NameError:
                setattr(self, name, value )

        self.color = [ float(x) / 255.0 for x in self.color]
        self.opacity = float(self.opacity) / 100.0
        self.angle = float(self.angle)

        self.offsetx = -np.cos( self.angle * np.pi/180.0 ) * float(self.distance)
        self.offsety = -np.sin( self.angle * np.pi/180.0 ) * float(self.distance)

    @property
    def padding(self):
        """ Return the amount of padding needed to fit the effect as a 4 tuple (left, top, right, bottom) """
        left = -self.size + self.offsetx
        right = self.size + self.offsetx
        top = self.size + self.offsety
        bottom = -self.size + self.offsety
        left = abs(left) if left < 0.0 else 0.0
        right = right if right > 0.0 else 0.0
        top = top if top > 0.0 else 0.0
        bottom = abs(bottom) if bottom < 0.0 else 0.0

        t = [left, top, right, bottom]
        t = map(int, t)
        return t

    def apply(self, info, glyph, image):
        x = int(self.offsetx)
        y = -int(self.offsety)

        shadowbitmap = np.copy( image )
        shadowbitmap = np.roll(shadowbitmap, x, axis = 0)
        shadowbitmap = np.roll(shadowbitmap, y, axis = 1)

        # replace the color
        r, g, b, a = fu.split_channels(shadowbitmap)

        shadowbitmap = np.dstack( (r, g, b, a) ) * (self.color[0], self.color[1], self.color[2], self.opacity)

        shadowbitmap = fu.blur_image(shadowbitmap, self.size)

        topbitmap = np.zeros_like( shadowbitmap )
        topbitmap[:image.shape[0], :image.shape[1], :] = image

        return fu.alpha_blend(shadowbitmap, topbitmap)


@EffectFunction
class GaussianBlur(object):
    """ Applies a gaussian blur to the glyph
    """
    
    #: The radius (in pixels) of the kernel
    size = 1

    def __init__(self, *k, **kw):
        """
        @param size    The size of the blur kernel
        """
        self.size = self.__class__.size

        for name, value in kw.iteritems():
            try:
                setattr(self, name, eval(value) )
            except NameError:
                setattr(self, name, value )
                
        self.padding = (self.size, self.size, self.size, self.size)

    def apply(self, info, glyph, image):
        return fu.blur_image(image, self.size)


@EffectFunction
class KernelBlur(object):
    """ Applies a simple box filter where the middle element has value 'strength'
    """
    #: The radius of the kernel (in pixels). The kernel size is `radius*2+1`
    size = 1
    #: The center value of the kernel
    strength = 1

    def __init__(self, *k, **kw):
        """
        @param size        The size of the kernel
        @param strength    The strength of the middle element
        """
        self.size = self.__class__.size

        for name, value in kw.iteritems():
            try:
                setattr(self, name, eval(value) )
            except NameError:
                setattr(self, name, value )

        self.kernel = np.ones( self.size*2+1, dtype=np.float32 )
        self.kernel[self.size] = self.strength
        self.kernel /= np.sum(self.kernel)
        
        self.padding = (self.size, self.size, self.size, self.size)

    def apply(self, info, glyph, image):
        return fu.blur_image_kernel1D(image, self.kernel)

@ColorFunction
class DistanceField(object):
    """ Calculates a distance field for each glyph
    """
    
    #: The spread of the "blur" that is applied to the glyphs
    size = 16
    #: The number of times the glyph is enlarged before the glyph is rendered.
    factor = 4

    def __init__(self, *k, **kw):
        self.size = self.__class__.size

        for name, value in kw.iteritems():
            try:
                setattr(self, name, eval(value) )
            except NameError:
                setattr(self, name, value )
        
        padding = self.size/self.factor
        self.padding = (padding, padding, padding, padding)
    
    def set_dimensions(self, width, height):
        self.max_dim = (width, height)

    def apply(self, info, glyph, startx, starty, size, maxsize, glyphimage, previmage):
        factor = self.factor
        face = info.face
        flags = ft.LOAD_RENDER | ft.LOAD_TARGET_MONO
        
        face.set_char_size( width=0, height=(info.size*factor)*64, hres=info.dpi, vres=info.dpi )
        face.load_char( glyph.unicode, flags )

        bitmap = fu.make_array_from_bitmap(face.glyph.contents.bitmap) * 255
        
        metrics = face.glyph.contents.metrics
        bearingY = (metrics.horiBearingY >> 6) + info.internalpadding[1]*factor + info.extrapadding[1]*factor
        
        # Due to the down scaling, we need to make sure that the bitmap start at the correct pixels
        offset_y = bearingY - glyph.bearingY * factor
        
        bitmap = fu.pad_bitmap(bitmap, info.extrapadding[0]*factor, info.extrapadding[1]*factor - offset_y, info.extrapadding[2]*factor, info.extrapadding[3]*factor + offset_y, 0, debug=glyph.unicode=='r')
        
        # TODO: Work out how to eliminate this issue
        e = np.empty( bitmap.shape, bitmap.dtype, order='F' )
        e[:, :] = bitmap
        bitmap = e
        
        i = utils.calculate_sedt(bitmap, self.size)
        #i = bitmap
        
        while factor > 1:
            i = utils.half_size(i)
            factor /= 2
        
        i = i.astype(np.float64) / 255.0
        
        a = np.zeros_like(i)
        a[i > 0] = 1.0
        
        return np.dstack( (i, i, i, a) )


@EffectFunction
class Halfsize(object):
    """ Down scales the glyph by a factor, using bilinear factoring
    """
    factor = prop.IntProperty( 1, help='The number of times the image should be minified' )
    
    def __init__(self, *k, **kw):
        for name, value in kw.iteritems():
            try:
                setattr(self, name, eval(value) )
            except NameError:
                setattr(self, name, value )

    def apply(self, glyph, info, image):
        for n in xrange(self.factor):
            out = utils.half_size(image)
            image = out

        return out


#To be used as a mask for each layer
class DefaultMask(object):
    idx = None

    def apply(self, info, glyph, image):
        try:
            image[DefaultMask.idx] = 0
            return image
        except:
            print "image", image.shape
            raise


class Layer(object):
    """ A class that helps applying layers on top of each other
    """
    def __init__(self, **kw):
        self.opacity = 1.0
        self.blend = fb.blendnormal
        self.effects = []

        self.mask = DefaultMask()

        for name, value in kw.iteritems():
            try:
                setattr(self, name, eval(value) )
            except (TypeError, NameError):
                setattr(self, name, value )

        if isinstance(self.opacity, int):
            self.opacity = self.opacity / 255.0
    
    @property
    def padding(self):
        zero = (0,0,0,0)
        layerpadding = getattr(self.color, 'padding', zero)
        
        for effect in self.effects:
            layerpadding = np.add(layerpadding, getattr(effect, 'padding', zero) )
            
        return layerpadding

            
    def set_info(self, glyph, info):
        self.glyph = glyph
        self.info = info
    
    def _verify(self, fn, image):
        assert image.shape[0] != 0, "Bad image generated by " + fn.__class__.__name__
        assert image.shape[1] != 0, "Bad image generated by " + fn.__class__.__name__

    def apply_color(self, *k, **kw):
        image = self.color.apply( self.info, self.glyph, *k, **kw )
        self._verify(self.color, image)
        return image
        
    def apply_effects(self, image):
        for effect in self.effects:
            image = effect.apply( self.info, self.glyph, image )
            self._verify(effect, image)
        return image
    
    def apply_mask(self, image):
        if self.mask is not None:
            image = self.mask.apply( self.info, self.glyph, image.copy() )
            self._verify(self.mask, image)
            return image
        return image
    
    def apply_blend(self, glyphimage, previmage, image):
        if self.blend is not None:
            image = np.clip( image, 0.0, 1.0 )
            image = self.blend(base=previmage, blend=image)
            image = fu.alpha_blend(previmage, image * self.opacity)
            self._verify(self.blend, image)
        return image





# ****************************************************************************************************
