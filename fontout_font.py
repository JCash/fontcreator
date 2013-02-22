"""
Generates a binary file given a set of glyphs

http://sv.wikipedia.org/wiki/UTF-8

"""

import os, struct
from cStringIO import StringIO

def _write_u16(f, endian, value):
    s = struct.pack(endian + "H", value)
    f.write(s)

def _write_i16(f, endian, value):
    s = struct.pack(endian + "h", value)
    f.write(s)
    
def _write_u64(f, endian, value):
    s = struct.pack(endian + "Q", value)
    f.write(s)
    
def _get_offset(f):
    return len(f.getvalue())

def _align_8(f):
    offset = _get_offset(f)
    align = offset % 8
    if align != 0:
        f.write('\0' * (align))
    
def write(options, info, pairkernings):
    output = os.path.splitext(options.output)[0] + '.font'
    endian = options.endian

    glyphs = sorted(info.glyphs, key=lambda x: x.utf8)
    
    f = StringIO()
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

    _align_8(f)
    
    table = [x.utf8 for x in glyphs]

    table_offset = _get_offset(f)
    s = struct.pack(endian + "%dI" % len(table), *table)
    f.write(s)
    
    _align_8(f)

    if pairkernings:
        unzipped = zip( *sorted(pairkernings.items()) )
        keys = unzipped[0]
        values = unzipped[1]
    else:
        keys = []
        values = []
    
    keys_offset = _get_offset(f)
    s = struct.pack(endian + "%dQ" % len(keys), *keys)
    f.write(s)
    
    _align_8(f)
    
    values_offset = _get_offset(f)
    s = struct.pack(endian + "%db" % len(values), *values)
    f.write(s)
    
    _align_8(f)
    
    name_offset = _get_offset(f)
    f.write( os.path.basename(options.input) + '\0')
    
    _align_8(f)
    
    texture_offset = _get_offset(f)
    texture = os.path.splitext(os.path.basename(options.output))[0] + info.textureformat
    f.write(texture + '\0')
    
    _align_8(f)
    
    data = f.getvalue()
    f.close()
    
    with open(output, 'wb') as f:
        f.write('FONT')
        
        _write_u16(f, endian, info.size)
        _write_u16(f, endian, info.texturesize[0])
        _write_u16(f, endian, info.texturesize[1])
        _write_i16(f, endian, info.ascender)
        _write_i16(f, endian, info.descender)
        _write_u16(f, endian, len(glyphs))
        _write_u16(f, endian, len(pairkernings))
        _write_u16(f, endian, 0)
        _write_u16(f, endian, 0)
        _write_u16(f, endian, 0)
        
        dataoffset = 12 * 2 + 6 * 8
        
        _write_u64(f, endian, dataoffset + name_offset)
        _write_u64(f, endian, dataoffset + texture_offset)
        _write_u64(f, endian, dataoffset + table_offset)
        _write_u64(f, endian, dataoffset + keys_offset)
        _write_u64(f, endian, dataoffset + values_offset)
        _write_u64(f, endian, dataoffset + 0)  # glyphs
        
        f.write( data )
    
    return 0

