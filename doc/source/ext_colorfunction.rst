Color functions
===============

.. contents::
    :local:
    :backlinks: top

Each color function takes a gray scale glyph image as input.
Each function is actually a class that fulfills a few function(s):

- __init__  (optional)
- SetDimensions (optional)
- __call__

The class must be decorated with the ColorFunction decorator.

Example
-------

A simple example which preallocates an image and, when called, serves
out portions of that image::

    import numpy as np
    from fonteffects import ColorFunction, ConvertColorsToUnits
    
    @ColorFunction
    class SolidColor(object):
        def __init__(self, *k, **kw):
            """ A function that fills the glyph with a solid color
            :param color: A color as (r,g,b) [0,255]
            """
            for name, value in kw.iteritems():
                try:
                    setattr(self, name, eval(value) )
                except NameError:
                    setattr(self, name, value )
                except TypeError, e:
                    raise FontException("Solid: Error while evaluating '%s':\n%s" % (value, str(e)))
            self.color = ConvertColorsToUnits( self.color )
                
        def SetDimensions(self, maxwidth, maxheight):
            # Sets up a solid fill bitmap
            ones = np.ones((width, height), dtype=np.float32)
            self.bitmap = np.dstack( (ones * self.color[0], ones * self.color[1], ones * self.color[2]) )

        def __call__(self, startx, starty, size, maxsize, glyphimage):
            # Return a cut out of the solid fill image
            bm = np.array(self.bitmap[startx:startx+size[0], starty:starty+size[1]])
            
            # zero out the pixels that have alpha == 0
            idx = np.where(glyphimage == 0)
            r,g,b = (bm[:,:,0], bm[:,:,1], bm[:,:,2])
            r[idx] = 0
            g[idx] = 0
            b[idx] = 0
            a = glyphimage
            
            # return a stacked numpy array 
            return np.dstack((r,g,b,a))
        
Reference
---------

.. autofunction:: fonteffects.ColorFunction
	:noindex:


.. py:function:: cls.__call__(offsetx, offsety, glyphsize, maxglyphsize, glyphimage)
    
    ``(mandatory)``
    
    Renders a an image given the start offset, size and the glyph image.
    Returns a numpy array with shape (glyphsize[0], glyphsize[1], 4)
    
    :param offsetx:         The offset into the "max glyph image". Used with any preallocated image.
    :param offsety:         The offset into the "max glyph image". Used with any preallocated image.
    :param glyphsize:       The size of the current glyph
    :param maxglyphsize:    The max size of any glyph in the font
    :param glyphimage:      The gray scale numpy array with shape (glyphsize[0], glyphsize[1], 1)

.. py:function:: cls.__init__(self, *k, **kw)

    ``(optional)``
    
    Handle the input arguments given to the class in the font info file

.. py:function:: cls.SetDimensions(self, maxwidth, maxheight)

    ``(optional)``
    
    This call is made after init, to let the class preallocate or create data.
    Only called once per font.
    
    :param integer maxwidth: The maximum expected width of any character in the font
    :param integer maxheight: The maximum expected height of any character in the font
