Color Functions
===============

.. contents::
    :local:
    :backlinks: top
    
These functions can be used for filling the layer with color::

    layers = [Layer(color=mycolor)]
    
    [mycolor]
    type=solid
    color = (0,0,0)
    
    
Each color function has it's own parameters.

Solid color
-----------

.. autoclass:: fonteffects.Solid
	:noindex:

Gradient color
--------------

.. autoclass:: fonteffects.Gradient
	:noindex:


Texture fill
------------

.. autoclass:: fonteffects.Texture
	:noindex:


Stripes
-------

.. autoclass:: fonteffects.Stripes
	:noindex:

	
DistanceField
-------------

.. autoclass:: fonteffects.DistanceField
	:noindex:
