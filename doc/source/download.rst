Download & Installation
=======================

.. contents::
    :local:
    :backlinks: top

Prerequisites
-------------

The FontCreator should work on any platform that supports these prerequisites:

- `Python <http://www.python.org/download>`_
- `PIL <http://www.pythonware.com/products/pil>`_
- `numpy <http://www.scipy.org/Download>`_
- `freetype <http://www.freetype.org/download.html>`_
- `PySide <http://qt-project.org/wiki/PySideDownloads>`_
- `sphinx <http://sphinx.pocoo.org>`_

Note that the PIL package is only necessary if you want to use it for saving
to a standard image format (e.g. PNG, TGA etc)

For Linux and Mac, you can get these as regular packages. (On Mac using macports)

Downloads
---------

Here is the latest distribution of the FontCreator:

- FontCreator 0.1


Install
-------

Once you have the unarchived the package, make sure that the paths are set correctly
and that the **freetype** shared library is found

Windows::

    set PATH=%PATH%;C:\freetypelibpath
    
Linux::

    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/name/freetypelibpath
    
Mac::

    export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/name/freetypelibpath
    
.. caution::
    
    Linux/Mac: You should always avoid setting the library path on a global scope.
    As a rule of thumb, set it in a wrapper script instead!
    
Next, you can test that the tool by compiling an example file::

    > python fontcreator.py -i examples/00_pixel.fontinfo -o build/00_pixel.fontinfo

If all goes well, you should now be able to find two files **build/00_pixel.png** and **build/00_pixel.json**


Building Examples
-----------------

You can also build the examples to test the font creator::

    > python examples/build.py
    

