
platform=$(python -c "import sys, platform; platforms = { 'win32':'windows', 'linux2':'linux', 'darwin':'darwin'}; arch = '64' if sys.maxsize > 2**32 else '32'; print platforms[sys.platform] + arch;")

# from stack overflow
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


pushd doc/
rm -rf build/

LD_LIBRARY_PATH=/opt/local/lib::$DIR/shared/$platform python ../fontcreator.py -h > source/modules/options.txt
LD_LIBRARY_PATH=/opt/local/lib::$DIR/shared/$platform make html

cd build/html

rm ../../../doc.zip
zip -rq ../../../doc.zip .

popd

