"""
Copyright @ 2013 Mathias Westerdahl

Generates a .json file given a set of glyphs
"""

import os, json

def _create_dict(options, info, pairkernings):
    d = dict()
    d['name'] = os.path.basename(options.input)
    d['size'] = info.size
    d['texturesize'] = info.texturesize
    d['texturename'] = os.path.basename(options.output)
    d['ascender'] = int(info.ascender)
    d['descender'] = int(info.descender)
    
    glyphdicts = []
    for glyph in info.glyphs:
        gd = dict()
        gd['character'] = glyph.unicode
        gd['advance'] = glyph.advance
        if glyph.bitmapbox:
            gd['bitmapbox'] = glyph.bitmapbox
            gd['bearing'] = (glyph.bearingX, glyph.bearingY)
        else:
            gd['bitmapbox'] = (0,0,0,0)
            gd['bearing'] = (0,0)
            
        glyphdicts.append(gd)
        
    d['glyphs'] = glyphdicts
    
    # to make the json format more readable, let's decode the pairs
    pd = []
    for key, value in pairkernings.iteritems():
        prevchar, char = ((key >> 32) & 0xFFFFFFFF, key & 0xFFFFFFFF)
        pd.append( (unichr(prevchar), unichr(char), value) )
    
    d['pairkernings'] = pd
    
    return d


def write(options, info, pairkernings):
    d = _create_dict(options, info, pairkernings)
    s = json.dumps(d, sort_keys=True, indent=4)
    with open( os.path.splitext(options.output)[0] + '.json', 'wb') as f:
        f.write(s)
    return 0
