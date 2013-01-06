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

Gradient color
--------------

.. autoclass:: fonteffects.Gradient


Texture fill
------------

.. autoclass:: fonteffects.Texture


Stripes
-------

.. autoclass:: fonteffects.Stripes