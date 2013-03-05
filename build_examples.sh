rm -rf doc/source/examples
platform=$(python -c "import sys, platform; platforms = { 'win32':'windows', 'linux2':'linux', 'darwin':'darwin'}; arch = '64' if sys.maxsize > 2**32 else '32'; print platforms[sys.platform] + arch;")

# from stack overflow
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

LD_LIBRARY_PATH=/opt/local/lib:$DIR/shared/$platform python examples/build.py $*
