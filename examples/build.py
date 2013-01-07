
import sys, os, inspect
scriptdir = os.path.dirname( inspect.getsourcefile(inspect.currentframe()) )

EXAMPLEDIR = os.path.abspath(os.path.dirname(__file__))
OUTPUTDIR = os.path.normpath( os.path.join(EXAMPLEDIR, '..', 'doc', 'build') )
FONTCREATOR = os.path.normpath( os.path.join(EXAMPLEDIR, '..', 'fontcreator.py') )

TEXT="Hello World!"
EXT='.png'

DEBUG = False
if DEBUG:
    TEXT = 'H'

header = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

<head>
    <title>FontCreator</title>

    <!--[if lt IE 9]>
        <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

    <link rel="stylesheet" href="../../css/style.css" type="text/css" media="screen" charset="utf-8" />
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.6/jquery.js"></script>
</head>

<body onload="" style="background-color:#BBB">

    <div class="introbox">

       <p class="intro">The FontCreator is a tiny project to make bitmap fonts easily available to all developers.
       The main purpose was to give non artists the ability to create fonts that look really good.
       Also, the iteration times was essential to be able to tweak the font effectively.</p>

       <p class="intro">It's available on all platforms where Python and the <a href="http://www.freetype.org/">freetype2</a> library are available. E.g OSX, Linux, Windows to name a few.</p>

    </div>
"""
footer = """
    <!-- header starts here -->
    <div id="header-wrap">
        <header>
            <hgroup>
                <h1><a href="../../index.html"><img src="./logotext.png"/></a></h1>
                <h3>A bitmap font creator written in Python</h3>
            </hgroup>

            <nav>
                <!-- Menu Tabs -->
                <ul>
                    <li><a href="../../index.html" id="current">Home</a></li>
                    <li><a href="examples.html">Examples</a></li>
                    <li><a href="../../index.html">Downloads</a></li>
                    <li><a href="../../index.html">Support</a></li>
                    <li><a href="../../index.html">About</a></li>
                </ul>
            </nav>
        </header>
    </div>

    <script>
        function changecolor(id, color) {
            $('img[id="foo"]').each(function(index) {
                $(this).css("backgroundColor", color)
            })
        }

        function zoom(factor) {
            $('img[id="foo"]').each(function(index) {
                $(this).css("zoom", factor)
            })
        }
    </script>

    <div id="zoom" class="zoom" align="center">
        Zoom Image:&nbsp;
        <table>
        <tr>
            <td onmouseover="zoom(1.0)">100%</td>
            <td onmouseover="zoom(1.5)">150%</td>
            <td onmouseover="zoom(2.0)">200%</td>
            <td onmouseover="zoom(2.5)">250%</td>
            <td onmouseover="zoom(3.0)">300%</td>
        </tr>
        </table>

    </div>

    <div id="palette" class="palette" align="center">
        Change Background:&nbsp;
        <table style="background-color:#BBB; line-height: 12px;">
        <tr>
            <td width="12px" height="12px" bgcolor="none" onmouseover="changecolor('foo', 'inherit')">X</td>
            <td width="12px" height="12px" bgcolor="red" onmouseover="changecolor('foo', 'red')"></td>
            <td width="12px" height="12px" bgcolor="green" onmouseover="changecolor('foo', 'green')"></td>
            <td width="12px" height="12px" bgcolor="blue" onmouseover="changecolor('foo', 'blue')"></td>
            <td width="12px" height="12px" bgcolor="#000" onmouseover="changecolor('foo', '#000')"></td>
            <td width="12px" height="12px" bgcolor="#222" onmouseover="changecolor('foo', '#222')"></td>
            <td width="12px" height="12px" bgcolor="#444" onmouseover="changecolor('foo', '#444')"></td>
            <td width="12px" height="12px" bgcolor="#666" onmouseover="changecolor('foo', '#666')"></td>
            <td width="12px" height="12px" bgcolor="#7f7f7f" onmouseover="changecolor('foo', '#7f7f7f')"></td>
            <td width="12px" height="12px" bgcolor="#AAA" onmouseover="changecolor('foo', '#AAA')"></td>
            <td width="12px" height="12px" bgcolor="#CCC" onmouseover="changecolor('foo', '#CCC')"></td>
            <td width="12px" height="12px" bgcolor="#FFF" onmouseover="changecolor('foo', '#FFF')"></td>
        </tr>
        </table>
    </div>

    <script src="prettyphoto/js/jquery.js" type="text/javascript" charset="utf-8"></script>
    <link rel="stylesheet" href="prettyphoto/css/prettyPhoto.css" type="text/css" media="screen" charset="utf-8" />
    <script src="prettyphoto/js/jquery.prettyPhoto.js" type="text/javascript" charset="utf-8"></script>

    <script type="text/javascript" charset="utf-8">
        $(document).ready(function(){
            $("a[rel^='prettyPhoto']").prettyPhoto({theme: 'facebook'});
        });
    </script>

</body>
</html>
"""

def GenerateDoc(path, outputdir):
    print "Generating documentation for %s" % path

    filename = os.path.basename(path)
    texturename_text = filename.replace('.fontinfo', '_text' + EXT)
    outputpath_text = os.path.join(outputdir, texturename_text)
    texturename = filename.replace('.fontinfo', EXT)
    outputpath = os.path.join(outputdir, texturename)
    htmlname = filename.replace('.fontinfo', '.html')
    htmloutputpath = os.path.join(outputdir, htmlname)
    pstatspath = os.path.join(outputdir, filename) + '.pstats'

    verbose = '-v' if '-v' in sys.argv else ''

    #cmd = 'time %s -m cProfile -o %s.pstats %s -i %s -o %s -w "%s"' % (sys.executable, filename, FONTCREATOR, path, outputpath_text, TEXT)
    cmd = '%s -m cProfile -o %s %s -i %s -o %s -w "%s" %s' % (sys.executable, pstatspath, FONTCREATOR, path, outputpath_text, TEXT, verbose)
    print cmd
    if os.system(cmd) != 0:
        return 1

    gprof = '../../../../external/gprof2dot.py'
    if os.path.exists(gprof):
        if os.system('%s %s -f pstats %s | dot -Tpdf -o %s/%s.pdf' % (sys.executable, gprof, pstatspath, OUTPUTDIR, filename)) != 0:
            return 1
        print "Wrote %s/%s.pdf" % (OUTPUTDIR, filename)

    if not DEBUG:
        if os.system('%s %s -i %s -o %s' % (sys.executable, FONTCREATOR, path, outputpath)) != 0:
            return 1

    with open(path,'rb') as f:
        lines = f.readlines()

    desc = []
    for line in lines:
        line = line.strip()
        if not line or line[0] != '#':
            break
        desc.append(line[1:].strip())

    s = """
    <div class="roundedbox">
        <a href="%s" title="%s"><img id="foo" src="%s"/></a>
        <br/>
        <em>%s</em><br>
        %s<br>
        Files: <a href="%s">.fontinfo</a> <a href="%s">.png</a>
    </div>""" % (texturename, texturename_text, texturename_text, '<br/>'.join(desc[:-1]), desc[-1], path, htmlname)

    imghtml = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

    <head>
        <title>FontCreator</title>

        <!--[if lt IE 9]>
            <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
        <![endif]-->

        <link rel="stylesheet" href="../../css/style.css" type="text/css" media="screen" charset="utf-8" />
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.6/jquery.js"></script>
    </head>

<body onload="">

    <div class="bigimg">
        <em>%s</em><br>
        %s<br>
        <img id="foo" src="%s"/>
    </div>
    """ % ('<br/>'.join(desc[:-1]), desc[-1], texturename)

    with open(htmloutputpath, 'wb') as f:
        f.write(imghtml)
        f.write(footer)

    return s

HEADERTEXT="FontCreator"
HEADERNAME="logotext" + EXT

def GenerateHeaderImage(path, outputdir):
    print "Generating header logo with %s" % path

    filename = os.path.basename(path)
    outputpath_text = os.path.join(outputdir, HEADERNAME)

    if os.system('%s %s -i %s -o %s -w "%s"' % (sys.executable, FONTCREATOR, path, outputpath_text, HEADERTEXT)) != 0:
        return 1

    return 0

if __name__ == '__main__':
    olddir = os.getcwd()
    try:
        if scriptdir:
            os.chdir(scriptdir)

        docs = []
        fontinfos = sorted(os.listdir(EXAMPLEDIR))
        #fontinfos = ['00_pixel.fontinfo']
        #fontinfos = ['01_outline.fontinfo']
        #fontinfos = ['03_layers_effects.fontinfo']
        #fontinfos = ['05_distance_fields.fontinfo']
        fontinfos = [ os.path.join(EXAMPLEDIR, x) for x in fontinfos if x.endswith('.fontinfo') ]

        for file in fontinfos:
            doc = GenerateDoc( file, OUTPUTDIR )
            if not isinstance(doc, str):
                print "Aborting, an error occurred"
                sys.exit(1)

            docs.append(doc)
            print ""

        if not DEBUG:
            GenerateHeaderImage(fontinfos[-1], OUTPUTDIR)

        with open(os.path.join(OUTPUTDIR, 'examples.html'), 'wb') as f:
            f.write(header)
            f.write('\n'.join(docs))
            f.write(footer)
            print "Wrote examples.html"

    finally:
        os.chdir(olddir)


"""
#NAME=data/fonts/test_outline_outer
NAME=data/fonts/arial18
TEXT="Hello World!"

time python -m cProfile -o dbg.pstats compilers/fontcreator.py -i $NAME.fontinfo -o build/iphonesim/$NAME.fntb -v
python ../external/gprof2dot.py -f pstats dbg.pstats | dot -Tpdf -o dbg.pdf
echo "wrote dbg.pdf"

#python compilers/fontcreator.py -i data/fonts/couriernew18.fontinfo -o build/iphonesim/data/fonts/couriernew18.f$

echo "Testing debug write" $TEXT
python compilers/fontcreator.py -i $NAME.fontinfo -o build/iphonesim/$NAME.text.tga -w "$TEXT"

#python compilers/fontcreator.py -i build/iphonesim/data/fonts/aardvark.fntb -o write_test.tga --write "Hello hor$
#python compilers/fontcreator.py -i build/iphonesim/data/fonts/couriernew18.fntb -o write_test2.tga --write "Hell$

"""
