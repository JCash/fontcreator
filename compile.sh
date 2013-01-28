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
	
g++ -O2 \
	source/demo.cpp \
	-L/opt/local/lib \
	-I/opt/local/include \
	-I/usr/local/include/ \
	-lglfw \
	-lpng \
	-framework IOKit \
	-framework Carbon  \
	-framework OpenGL \
	-framework Foundation \
	-framework AppKit \
	-o build/demo
