import sys, os, inspect
SCRIPTDIR = os.path.dirname( inspect.getsourcefile(inspect.currentframe()) )

EXAMPLEDIR = os.path.abspath(os.path.dirname(__file__))
SOURCEDIR = os.path.normpath( os.path.join(EXAMPLEDIR, '..', 'doc', 'source') )
OUTPUTDIR = os.path.normpath( os.path.join(EXAMPLEDIR, '..', 'doc', 'source', 'examples') )
FONTCREATOR = os.path.normpath( os.path.join(EXAMPLEDIR, '..', 'fontcreator.py') )

TEXT="Hello World!"
EXT='.png'

HEADERTEXT="FontCreator"
HEADERNAME="headertext" + EXT
HEADER_FONTINFO = 'header.fontinfo'

DEBUG = False
if DEBUG:
    TEXT = 'World'

HEADER = """
Examples
========

Here are some examples that are generated with the font creator

.. toctree::
    :maxdepth: 1
    
%s

"""

FOOTER = """
"""

def generate_doc(path, outputdir, profile=False):
    print "Generating documentation for %s" % path

    filename = os.path.basename(path)
    texturename_text = filename.replace('.fontinfo', '_text' + EXT)
    outputpath_text = os.path.join(outputdir, texturename_text)
    texturename = filename.replace('.fontinfo', EXT)
    outputpath = os.path.join(outputdir, texturename)
    rstname = filename.replace('.fontinfo', '.rst')
    rstoutputpath = os.path.join(outputdir, rstname)
    jsonname = filename.replace('.fontinfo', '.json')
    pstatspath = os.path.join(outputdir, filename) + '.pstats'

    verbose = '-v' if '-v' in sys.argv else ''

    cmd = '%s %s -i %s -o %s -w "%s" --bgcolor=0,0,0 %s' % (sys.executable, FONTCREATOR, path, outputpath_text, TEXT, verbose)

    if os.system(cmd) != 0:
        return 1

    timeit = 'time' if profile else ''
    cprofile = '-m cProfile -o %s' % pstatspath if profile else ''

    if not DEBUG:
        if os.system('%s %s %s %s -i %s -o %s' % (timeit, sys.executable, cprofile, FONTCREATOR, path, outputpath)) != 0:
            return 1

    if profile:
        gprof = 'gprof2dot'
        if os.system('%s -f pstats %s -e 0.1 -n 0.1 | dot -Tpdf -o %s/%s.pdf' % (gprof, pstatspath, OUTPUTDIR, filename)) != 0:
            return 1
        print "Wrote %s/%s.pdf" % (OUTPUTDIR, filename)

    with open(path,'rb') as f:
        lines = f.readlines()

    descsearch = True
    desc = []
    content = []
    for line in lines:
        line = line.strip()
        if descsearch:
            if line and line[0] != '#':
                descsearch = False
        
        if descsearch:
            desc.append(line[1:].strip())
        else:
            content.append(line)

    name = os.path.basename(path)
    s = """
%s
%s
%s

.. image:: %s

.. contents::
    :local:
    :backlinks: top
    
Brief
=====

""" % ( len(name) * '=', name, len(name) * '=', texturename_text)

    s += '.\n'.join(desc)
    
    s += """

.fontinfo
=========

.. code-block:: python

%s
""" % '\n'.join([' '*4 + line for line in content])

    s += """

Results
=======

The JSON file :download:`.json <./%s>`

.. image:: %s

""" % (jsonname, texturename) 

    with open(rstoutputpath, 'wb') as f:
        f.write(s)

    return s


def generate_header(path, outputdir):
    print "Generating header logo with %s" % path

    outputpath_text = os.path.join(outputdir, HEADERNAME)

    if os.system('%s %s -i %s -o %s -w "%s"' % (sys.executable, FONTCREATOR, path, outputpath_text, HEADERTEXT)) != 0:
        return 1

    return 0

if __name__ == '__main__':
    olddir = os.getcwd()
    
    profile = 'profile' in sys.argv
    try:
        if SCRIPTDIR:
            os.chdir(SCRIPTDIR)

        docs = []
        fontinfos = sorted(os.listdir(EXAMPLEDIR)) 
        if DEBUG:
            #fontinfos = ['00_pixel.fontinfo']
            #fontinfos = ['01_outline.fontinfo']
            #fontinfos = ['03_layers_effects.fontinfo']
            #fontinfos = ['05_distance_fields.fontinfo']
            fontinfos = ['adventure.fontinfo', '05_distance_fields.fontinfo']
            
        fontinfos = [ os.path.join(EXAMPLEDIR, x) for x in fontinfos if x.endswith('.fontinfo') ]

        for file in fontinfos:
            if file.endswith(HEADER_FONTINFO):
                continue
            doc = generate_doc( file, OUTPUTDIR, profile=profile )
            if not isinstance(doc, str):
                print "Aborting, an error occurred"
                sys.exit(1)

            docs.append(doc)
            print ""

        if not DEBUG:
            generate_header(HEADER_FONTINFO, OUTPUTDIR)

        path = os.path.join(OUTPUTDIR, 'examples.rst')
        rstfiles = [os.path.basename(fi).replace('.fontinfo', '.rst') for fi in fontinfos if not fi.endswith(HEADER_FONTINFO)]
        with open(path, 'wb') as f:
            header = HEADER % '\n'.join(['    ./%s' % rst for rst in rstfiles])
            f.write(header)
            f.write(FOOTER)
            print "Wrote", path

    finally:
        os.chdir(olddir)


