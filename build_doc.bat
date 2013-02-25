
echo off

set PATH=%PATH%;%~dp0

pushd doc

cd doc

make.bat html

popd
