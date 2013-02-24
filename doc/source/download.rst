Download & Installation
=======================

.. contents::
    :local:
    :backlinks: top


Downloads
---------

Download the zip:

- `fontcreator.zip <https://github.com/JCash/fontcreator/archive/master.zip>`_

Or get the code from GitHub::

	> git clone https://github.com/JCash/fontcreator.git


Prerequisites
-------------

The FontCreator should work on any platform that supports these prerequisites:

- `Python <http://www.python.org/download>`_
- `numpy <http://www.scipy.org/Download>`_
- `freetype <http://www.freetype.org/download.html>`_
- `PIL <http://www.pythonware.com/products/pil>`_ - For writing textures with PIL

Optional installations:

- `sphinx <http://sphinx.pocoo.org>`_ (for the documentation)
- `PySide <http://qt-project.org/wiki/PySideDownloads>`_ (for the Editor)

.. note:: Note that the PIL package is only necessary if you want to use it for saving
	to a standard image format (e.g. PNG, TGA etc). The examples use PIL.

For Linux and Mac, you can get these as regular packages. (On Mac using macports)




Install
-------

Once you have the unarchived the package, make sure that the paths are set correctly
and that the **freetype** shared library is found

Windows::

    set PATH=%PATH%;C:\freetypelibpath
    
Linux::

    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/local/lib
    
Mac::

    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/local/lib


Building Code
-------------

The font creator comes with a code for some image processing. These are easily built by
calling the appropriate compile script::

	> ./compile.sh

Once the code is built and the library path is set, you can test that the tool by compiling an example file::

    > python fontcreator.py -i examples/00_pixel.fontinfo -o build/00_pixel.fontinfo

If all goes well, you should now be able to find two files *build/00_pixel.png* and *build/00_pixel.json*


Building Examples
-----------------

You can also build the examples to test the font creator::

    > python examples/build.py
    
The fontcreator comes with a script that also sets the path for you::

	> ./build_examples.sh
    

Building Documentation
----------------------

To build the documentation::

	> ./build_doc.sh
	> open doc/build/html/index.html
    

