The structure
=============

The pseudo code for generating a font goes like this::
    
    read .fontinfo file
    
    read font from freetype2

    for each glyph:
        get glyph bitmap from freetype2
        
        for each layer:
            use color function with glyph bitmap as input
            apply each effect on the image
            
            alpha blend layer on top of previous
            
        for each post effect:
            apply effect on image

    render glyphs to texture
    save texture
    
    save glyph info
    
