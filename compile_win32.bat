
call "%VS110COMNTOOLS%vsvars32.bat"

mkdir shared
mkdir shared\win32

cl /D_USRDLL /D_WINDLL /O2 source/sedt.cpp source/utils.cpp /link /DLL /OUT:shared\win32\_utils.dll

cl /D_USRDLL /D_WINDLL /O2 source/binpack/Rect.cpp source/binpack/GuillotineBinPack.cpp source/binpack/SkylineBinPack.cpp source/binpack/MaxRectsBinPack.cpp source/binpack.cpp /link /DLL /OUT:shared\win32\_binpack.dll

del *.obj