g++ -shared -O2 \
	source/sedt.cpp \
	source/utils.cpp \
	-o _utils.dylib
	
g++ -shared -O2 \
	source/binpack/Rect.cpp \
	source/binpack/GuillotineBinPack.cpp \
	source/binpack/SkylineBinPack.cpp \
	source/binpack/MaxRectsBinPack.cpp \
	source/binpack.cpp \
	-o _binpack.dylib