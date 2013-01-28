"""
Generates a binary file given a set of glyphs

http://sv.wikipedia.org/wiki/UTF-8

"""

import sys, os, struct
from cStringIO import StringIO

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
    
    f = StringIO()

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
    
    data = f.getvalue()
    f.close()
    
    with open(output, 'wb') as f:
        f.write('FONT')
        
        str1 = os.path.basename(options.input)
        offset1 = 4 + 2 * 8 + len(data)
        offset2 = offset1 + len(str1) + 1
        s = struct.pack(endian + "II", offset1, offset2)
        _write_str(f, endian, s)
        _write_str(f, endian, data)
        _write_str(f, endian, str1+'\0')
        _write_str(f, endian, os.path.relpath(options.output, options.datadir)+'\0')

    
    return 0

