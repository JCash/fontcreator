Numpy
=====

The numpy and scipy packages are a great way to provide your tool
with well tested and performant code for image processing.

Image
-----

For simplicity's sake, each function that handle images, expect a numpy array with certain criteria:

- Colors values are in the range [0.0, 1.0]
- image[x, y] will give you the pixel value of (x,y)
- Origin is at the top left corner of the image

