=======================
Extending the framework
=======================

.. toctree::
    :hidden:
    
    ./ext_colorfunction.rst


It's simple enough to extend the framework.
You can extend the font creator with new:

- :doc:`ext_colorfunction`
- Effect functions
- Blend functions
- Texture Render function
- Texture save function
- Font info save function


    

Good to know
============

Font Info File
--------------

- The colors are usually specified as 3-tuples of integers
- The colors are in the range [0, 255]
- Internally, the colors are converted to floats in the range [0.0, 1.0]  


Image
-----

For simplicity's sake, each function that handle images, expect a numpy array with certain criteria:

- Colors values are in the range [0.0, 1.0]
- image[x, y] will give you the pixel value of (x,y)
- Origin is at the top left corner of the image
- Most images are 4-channel, except for the glyphimage


