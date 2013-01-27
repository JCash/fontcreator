"""
Generates a binary file given a set of glyphs

http://sv.wikipedia.org/wiki/UTF-8

"""

import sys, os, struct

def _write_str(f, endian, value):
    s = struct.pack(endian + "H", len(value))
    f.write(s)
    f.write(value)

def _write_u16(f, endian, value):
    s = struct.pack(endian + "H", value)
    f.write(s)

def _write_i16(f, endian, value):
    s = struct.pack(endian + "h", value)
    f.write(s)
    
def _write_u32(f, endian, value):
    s = struct.pack(endian + "I", value)
    f.write(s)
    
def write(options, info, pairkernings):
    output = os.path.splitext(options.output)[0] + '.font'
    endian = options.endian
    
    with open(output, 'wb') as f:
        _write_str(f, endian, os.path.basename(options.input) )
        _write_str(f, endian, os.path.relpath(options.output, options.datadir) )
        
        _write_u16(f, endian, info.size)
        _write_u16(f, endian, info.texturesize[0])
        _write_u16(f, endian, info.texturesize[1])
        _write_i16(f, endian, info.ascender)
        _write_i16(f, endian, info.descender)
        
        glyphs = sorted(info.glyphs, key=lambda x: x.utf8)
        table = [x.utf8 for x in glyphs]
        
        s = struct.pack(endian + "%dI" % len(table), *table)
        f.write(s)
        
        for glyph in glyphs:
            bbox = glyph.bitmapbox if glyph.bitmapbox is not None else (0, 0, 0, 0)
            s = struct.pack(endian + "IHHHHBbbx",
                            glyph.utf8,
                            bbox[0],
                            bbox[1],
                            bbox[2],
                            bbox[3],
                            glyph.advance,
                            glyph.bearingX,
                            glyph.bearingY)
            f.write(s)
    
        unzipped = zip( *sorted(pairkernings.items()) )
        keys = unzipped[0]
        values = unzipped[1]
        
        s = struct.pack(endian + "I%dQ" % len(keys), len(keys), *keys)
        f.write(s)
        
        s = struct.pack(endian + "%db" % len(values), *values)
        f.write(s)
    
    return 0

