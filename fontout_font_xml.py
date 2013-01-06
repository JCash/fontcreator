import os, struct, logging
from PIL import image

def ReadFormat(f, format):
    return struct.unpack(format, f.read( struct.calcsize(format) ) )

        
def _save_glyph_texture(texturename, info, glyphs):
    im = Image.new('RGBA', info.texturesize, (0,0,0,0) )
    
    offx = info.internalpadding[0]
    offy = info.internalpadding[1]
    #for code, char in glyphs.iteritems():
    for glyph in glyphs:
        if glyph.info.bitmap is None:
            # TODO: Add glyphs 
            continue
        
        x,y,w,h = glyph.bitmapbox
        x -= offx
        y -= offy
        w += offx*2
        h += offy*2
        im.paste( (255,255,255,255), map(int, (x, y, x + w, y + h)) )
    
    texturename = texturename.replace('_dif', '_org')
    im.save(texturename)
    logging.debug("Wrote %s" % texturename)


def _save_font_xml(options, output, info, glyphs):
    
    basename, ext = os.path.splitext(output)
    texturedif = basename + info.textureformat
    textureglyphs = basename.replace('_dif', '') + '_org' + info.textureformat
    
    lowerdatadir = options.datadir.lower()
    
    if texturedif.lower().startswith(lowerdatadir):
        texturedif = texturedif[len(lowerdatadir)+1:]
        
    if textureglyphs.lower().startswith(lowerdatadir):
        textureglyphs = textureglyphs[len(lowerdatadir)+1:]
    
    texturedif = texturedif.replace('\\', '/')
    textureglyphs = textureglyphs.replace('\\', '/')
    
    compiledtexturedif = texturedif.replace(info.textureformat, '.ddsc')
    

    header = """<?xml version="1.0" encoding="UTF-8"?>
<adf>
    <instances>
        <instance root="font">
            <struct type="Font" name="font">
                <member name="Dependencies">#1</member>
                <member name="MaskTexture">"%s" </member>
                <member name="Texture">"%s" </member>
                <member name="Leading">-1.0 </member>
                <member name="Tracking">1.0 </member>
                <member name="Ranges">#2</member>
            </struct>
            <array id="#1">"%s" "%s" </array>
            <array id="#2">
            
                <!-- Add your changes here. ID number should start at %d -->

                <!-- Here starts all the generated glyphs -->
    """
    
    footer = """
            </array>
        </instance>
    </instances>
</adf>
    """
    
    runningnumber = 3
    template = """
                <struct type="GlyphRange" id="#%d">
                    <member name="UnicodeStart" type="int">%d</member>
                    <member name="Left" type="int">%d</member>
                    <member name="Top" type="int">%d</member>
                    <member name="Right" type="int">%d</member>
                    <member name="Bottom" type="int">%d</member>
                    <member name="Baseline" type="int">%d</member>
                </struct>"""
    
    offx = info.internalpadding[0]
    offy = info.internalpadding[1]
    
    s = ''
    #for code, char in items:
    for glyph in glyphs:
        if glyph.info.bitmap is None:
            continue
        
        x,y,w,h = glyph.bitmapbox
        x -= offx
        y -= offy
        w += offx*2
        h += offy*2
        
        s += template % ( runningnumber, ord(glyph.info.unicode), x, y, x+w, y+h, glyph.baseline )
        runningnumber += 1
    
    s = header % (textureglyphs, compiledtexturedif, textureglyphs, texturedif, runningnumber) + s
    s += footer
    
    with open(output, 'wb') as f:
        f.write(s)
    logging.debug("Wrote %s" % output)


def write(options, info, glyphs, pairkernings):
    _save_glyph_texture(options.texturename, info, glyphs)
    
    fontxml = os.path.splitext(options.texturename)[0] + '.font_xml'
    _save_font_xml(options, fontxml, info, glyphs)
    return 0




