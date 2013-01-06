"""
Generates a .json file given a set of glyphs
"""

import sys, os, json

def _create_dict(options, info, glyphs, pairkernings):
    d = dict()
    d['name'] = os.path.basename(options.input)
    d['size'] = info.size
    d['texturesize'] = info.texturesize
    d['texturename'] = options.output
    d['ascender'] = int(info.ascender)
    d['descender'] = int(info.descender)
    
    glyphdicts = []
    for glyph in glyphs:
        gd = dict()
        gd['character'] = glyph.info.unicode
        gd['advance'] = glyph.info.advance
        if glyph.bitmapbox:
            gd['bitmapbox'] = glyph.bitmapbox
            gd['bearing'] = (glyph.info.bearingX, glyph.info.bearingY)
        else:
            gd['bitmapbox'] = (0,0,0,0)
            gd['bearing'] = (0,0)
            
        glyphdicts.append(gd)
        
    d['glyphs'] = glyphdicts
    
    # to make the json format more readable, let's decode the pairs
    pd = []
    for key, value in pairkernings.iteritems():
        prevchar, char = ((key >> 16) & 0xFFFF, key & 0xFFFF)
        #pd[ (prevchar, char) ] = value
        pd.append( (unichr(prevchar), unichr(char), value) )
    
    d['pairkernings'] = pd
    
    return d


def write(options, info, glyphs, pairkernings):
    d = _create_dict(options, info, glyphs, pairkernings)
    s = json.dumps(d, sort_keys=True, indent=4)
    with open( os.path.splitext(options.output)[0] + '.json', 'wb') as f:
        f.write(s)
    return 0
