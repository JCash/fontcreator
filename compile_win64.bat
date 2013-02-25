
call "%VS100COMNTOOLS%..\..\VC\vcvarsall.bat" amd64

mkdir shared
mkdir shared\win64

cl /D_USRDLL /D_WINDLL /O2 source/sedt.cpp source/utils.cpp /link /DLL /OUT:shared\win64\_utils.dll

cl /D_USRDLL /D_WINDLL /O2 source/binpack/Rect.cpp source/binpack/GuillotineBinPack.cpp source/binpack/SkylineBinPack.cpp source/binpack/MaxRectsBinPack.cpp source/binpack.cpp /link /DLL /OUT:shared\win64\_binpack.dll

del *.obj