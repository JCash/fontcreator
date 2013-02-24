Color functions
===============

.. contents::
    :local:
    :backlinks: top

Each color function takes an image from the previous layer as input and
returns an altered image as result.
Each function is actually a class that implements a few function(s):

- __init__  (optional)
- set_dimensions (optional)
- apply

The class must be decorated with the ColorFunction decorator.

Example
-------

A simple example which preallocates an image and, when called, serves
out portions of that image:

.. code-block:: python

	import numpy as np
	from fonteffects import ColorFunction, ConvertColorsToUnits
	import editor.properties as prop
	
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


Reference
---------

.. autofunction:: fonteffects.ColorFunction
	:noindex:


.. py:function:: cls.apply(self, info, glyph, startx, starty, size, maxsize, glyphimage, previmage)
    
    ``(mandatory)``
    
    Renders a an image given the start offset, size and the glyph image.
    Returns a numpy array with same shape as the ``previmage.shape``
    
    :param SFontInfo info:	The info struct for the current font
    :param SGlyph glyph:	The current glyph being rendered
    :param integer startx:  The offset into the "max glyph image". Used with any preallocated image.
    :param integer starty:  The offset into the "max glyph image". Used with any preallocated image.
    :param 2-tuple size:    The size of the current glyph
    :param 2-tuple maxsize: 	 The max size of any glyph in the font
    :param np.array glyphimage:  The gray scale numpy array with shape (1 channel)
    :param np.array previmage:   The image rendered by the previous layer. If this color function is the first, the previmage \
    								is the composite of the glyphimage. (4 channels)
    :return:	(np.array) The rendered image with same shape as previmage

.. py:function:: cls.__init__(self, *k, **kw)

    ``(optional)``
    
    Handle the input arguments given to the function in the font info file
    
    :param k:  -not used-
    :param kw: The named attributes found in the function's section in the font info file

.. py:function:: cls.set_dimensions(self, maxwidth, maxheight)

    ``(optional)``
    
    This call is made after init, to let the class preallocate or create data.
    Only called once per font.
    
    :param integer maxwidth: The maximum expected width of any character in the font
    :param integer maxheight: The maximum expected height of any character in the font
