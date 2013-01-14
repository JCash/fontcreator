
rem call "%VS100COMNTOOLS%..\..\VC\vcvarsall.bat" amd64
call "%VS110COMNTOOLS%vsvars32.bat"

cl /D_USRDLL /D_WINDLL /O2 source/sedt.cpp source/utils.cpp /link /DLL /OUT:_utils.dll

cl /D_USRDLL /D_WINDLL /O2 source/binpack/Rect.cpp source/binpack/GuillotineBinPack.cpp source/binpack/SkylineBinPack.cpp source/binpack/MaxRectsBinPack.cpp source/binpack.cpp /link /DLL /OUT:_binpack.dll

del *.obj