g++ -shared -O2 -Wall \
	source/sedt.cpp \
	source/utils.cpp \
	-o shared/darwin64/_utils.dylib
	
g++ -shared -O2 -Wall \
	source/binpack/Rect.cpp \
	source/binpack/GuillotineBinPack.cpp \
	source/binpack/SkylineBinPack.cpp \
	source/binpack/MaxRectsBinPack.cpp \
	source/binpack.cpp \
	-o shared/darwin64/_binpack.dylib
	
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
