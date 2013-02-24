Overview
=========

About
-----

The project started as a response to the lack of bitmap font generators that
worked on a mac & linux platform. The trusted old BMFont_ generator made by Angelcode was an inspiration
but since it was too heavily relying on windows code, it was not an option.

.. _BMFont: http://www.angelcode.com/products/bmfont/

Also, at the same time, the project was expected to be an experimental & learning experience in
image processing, numpy, fonts and glyphs. The goal was to make a robust and performant platform independent 
solution for making fonts, ease enough to be used by non artists as well as professional artists.

Although the need for bitmap fonts have lessened over the years, it was still a fun experiment.


Layers & Effects
----------------

One of the goals was to mimic the workflow of an artist making a bitmap font in photoshop, with layers, blends and effects.

The layers are stacked upon each other and they support both blending and opacity.
Each layer have a color function that produces pixels given the a gray scale glyph image as input.
Each layer can have zero or more effects applied to it.

The effects can also be applied as post effects that are applied after all layers are combined.

Each blend function is a good representation of how Photoshop blends it's layers.
Some good reads:

- http://dunnbypaul.net/blends/
- http://www.imagemagick.org/Usage/morphology/
- http://stackoverflow.com/questions/5919663/how-does-photoshop-blend-two-images-together

Performance
------------

Another goal was to make the tool as fast as possible with the target of generating a normal bitmap font with several layers in less than a second.
To reach this goal, the tool has been profiled using ``cProfile`` and ``gprof2dot`` to find the hot spots.

Some functionality was also hard to find a nice pythonic way to implement, so the tool uses C++ for a few
processing functions such as the bin packing algorithms and the distance field calculations. 

