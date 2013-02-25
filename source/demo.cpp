/*
 * http://www.opengl.org/sdk/docs/man/
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <GL/glfw.h> // GLFW is a cross-platform OpenGL framework
#include <png.h>

/*
 * printError - Signal an error.
 */
void printError(const char *errtype, const char *errmsg) {
  fprintf(stderr, "%s: %s\n", errtype, errmsg);
}


/*
 * filelength - Determine the number of bytes in a file.
 * This is a lazy hack to avoid calling stat(), but it works.
 */
int filelength(const char *filename) {
  FILE *ifp;
  int length = 0;

  ifp = fopen(filename, "r");
  fseek(ifp, 0, SEEK_END);
  length = (int)ftell(ifp);
  fclose(ifp);
  return length;
}


/*
 * loadExtensions - Load (here: check for) the required OpenGL extensions.
 */
void loadExtensions() {
  // These extension strings indicate that the OpenGL Shading Language,
  // GLSL shader objects and floating-point textures are supported.
  if(!glfwExtensionSupported("GL_ARB_shading_language_100"))
    {
      printError("GL init error", "GL_ARB_shading_language_100 extension was not found");
      return;
    }
  if(!glfwExtensionSupported("GL_ARB_shader_objects"))
    {
      printError("GL init error", "GL_ARB_shader_objects extension was not found");
      return;
    }
}


/*
 * readShaderFile - read shader source from a file to a string.
 */
char* readShaderFile(const char *filename) {
  FILE *file = fopen(filename, "r");
  if(file == NULL)
    {
      printError("I/O error", "Cannot open shader file!");
      return 0;
    }
  int bytesinfile = filelength(filename);
  char *buffer = (char*)malloc(bytesinfile+1);
  int bytesread = fread( buffer, 1, bytesinfile, file);
  buffer[bytesread] = 0; // Terminate the string with 0
  fclose(file);

  return buffer;
}


/*
 * createShader - create, load, compile and link the shader object.
 */
GLuint createShader(const char *vertfilename, const char *fragfilename) {

  GLuint programObj;
  GLuint fragmentShader;
  const char *vertexShaderStrings[1];
  GLint vertexCompiled;
	const char *fragmentShaderStrings[1];
	GLint fragmentCompiled;
	GLint shadersLinked;
	char str[4096]; // For error messages from the GLSL compiler and linker

	// Create the vertex and fragment shaders
	GLuint vertexShader = glCreateShader( GL_VERTEX_SHADER );

	char *vertexShaderAssembly = readShaderFile( vertfilename );
	vertexShaderStrings[0] = vertexShaderAssembly;
	glShaderSource( vertexShader, 1, vertexShaderStrings, NULL );
	glCompileShader( vertexShader );
	free((void *)vertexShaderAssembly);

	glGetShaderiv( vertexShader, GL_COMPILE_STATUS, &vertexCompiled );
	if(vertexCompiled == GL_FALSE)
    {
	  glGetShaderInfoLog( vertexShader, sizeof(str), NULL, str );
	  printError("Vertex shader compile error", str);
    }

	fragmentShader = glCreateShader( GL_FRAGMENT_SHADER );

	char *fragmentShaderAssembly = readShaderFile( fragfilename );
	fragmentShaderStrings[0] = fragmentShaderAssembly;
	glShaderSource( fragmentShader, 1, fragmentShaderStrings, NULL );
	glCompileShader( fragmentShader );
	free((void *)fragmentShaderAssembly);

	glGetShaderiv( fragmentShader, GL_COMPILE_STATUS, &fragmentCompiled );
	if(fragmentCompiled == GL_FALSE)
	{
		glGetShaderInfoLog( fragmentShader, sizeof(str), NULL, str );
		printError("Fragment shader compile error", str);
	}

	// Create a program object and attach the compiled shaders
	programObj = glCreateProgram();
	glAttachShader( programObj, vertexShader );
	glAttachShader( programObj, fragmentShader );

	// Link the program object and print out the info log
	glLinkProgram( programObj );
	glGetShaderiv( programObj, GL_LINK_STATUS, &shadersLinked );

	if( shadersLinked == GL_FALSE )
	{
		glGetProgramInfoLog( programObj, sizeof(str), NULL, str );
		printError("Program object linking error", str);
	}

  return programObj;
}


/*
 * setUniformVariables - set the uniform shader variables we need.
 */
 void setUniformVariables(GLuint programObj,
                          int disttexture, int reftexture,
                          float texw, float texh) {

  GLint location_disttexture = -1;
  GLint location_reftexture = -1;
  GLint location_texw = -1;
  GLint location_texh = -1;

  // Activate the shader to set its state
  glUseProgram( programObj );
  // Locate the uniform shader variables by name and set them:
  // two textures and two integers to tell the size of the first texture
  location_disttexture = glGetUniformLocation( programObj, "disttexture" );
  if(location_disttexture != -1)
    glUniform1i( location_disttexture, disttexture );

  location_reftexture = glGetUniformLocation( programObj, "reftexture" );
  if(location_reftexture != -1)
    glUniform1i( location_reftexture, reftexture );

  location_texw = glGetUniformLocation( programObj, "texw" );
  if(location_texw != -1)
    glUniform1f( location_texw, texw );

  location_texh = glGetUniformLocation( programObj, "texh" );
  if(location_texh != -1)
    glUniform1f( location_texh, texh );

  // Deactivate the shader again
  glUseProgram( 0 );
}

 /*
  * Taken from http://stackoverflow.com/questions/11296644/loading-png-textures-to-opengl-with-libpng-only
  */

 GLuint png_texture_load(const char * file_name, GLuint texID, int * width, int * height)
 {
     png_byte header[8];

     FILE *fp = fopen(file_name, "rb");
     if (fp == 0)
     {
         perror(file_name);
         return 0;
     }

     // read the header
     fread(header, 1, 8, fp);

     if (png_sig_cmp(header, 0, 8))
     {
         fprintf(stderr, "error: %s is not a PNG.\n", file_name);
         fclose(fp);
         return 0;
     }

     png_structp png_ptr = png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
     if (!png_ptr)
     {
         fprintf(stderr, "error: png_create_read_struct returned 0.\n");
         fclose(fp);
         return 0;
     }

     // create png info struct
     png_infop info_ptr = png_create_info_struct(png_ptr);
     if (!info_ptr)
     {
         fprintf(stderr, "error: png_create_info_struct returned 0.\n");
         png_destroy_read_struct(&png_ptr, (png_infopp)NULL, (png_infopp)NULL);
         fclose(fp);
         return 0;
     }

     // create png info struct
     png_infop end_info = png_create_info_struct(png_ptr);
     if (!end_info)
     {
         fprintf(stderr, "error: png_create_info_struct returned 0.\n");
         png_destroy_read_struct(&png_ptr, &info_ptr, (png_infopp) NULL);
         fclose(fp);
         return 0;
     }

     // the code in this if statement gets called if libpng encounters an error
     if (setjmp(png_jmpbuf(png_ptr))) {
         fprintf(stderr, "error from libpng\n");
         png_destroy_read_struct(&png_ptr, &info_ptr, &end_info);
         fclose(fp);
         return 0;
     }

     // init png reading
     png_init_io(png_ptr, fp);

     // let libpng know you already read the first 8 bytes
     png_set_sig_bytes(png_ptr, 8);

     // read all the info up to the image data
     png_read_info(png_ptr, info_ptr);

     // variables to pass to get info
     int bit_depth, color_type;
     png_uint_32 temp_width, temp_height;

     // get info about png
     png_get_IHDR(png_ptr, info_ptr, &temp_width, &temp_height, &bit_depth, &color_type, NULL, NULL, NULL);

     if (width){ *width = temp_width; }
     if (height){ *height = temp_height; }

     // Update the png info struct.
     png_read_update_info(png_ptr, info_ptr);

     // Row size in bytes.
     int rowbytes = png_get_rowbytes(png_ptr, info_ptr);

     // glTexImage2d requires rows to be 4-byte aligned
     rowbytes += 3 - ((rowbytes-1) % 4);

     // Allocate the image_data as a big block, to be given to opengl
     png_byte* image_data;
     image_data = (png_byte *)malloc(rowbytes * temp_height * sizeof(png_byte)+15);
     if (image_data == NULL)
     {
         fprintf(stderr, "error: could not allocate memory for PNG image data\n");
         png_destroy_read_struct(&png_ptr, &info_ptr, &end_info);
         fclose(fp);
         return 0;
     }

     // row_pointers is for pointing to image_data for reading the png with libpng
     png_bytep* row_pointers = (png_bytep*)malloc(temp_height * sizeof(png_bytep));
     if (row_pointers == NULL)
     {
         fprintf(stderr, "error: could not allocate memory for PNG row pointers\n");
         png_destroy_read_struct(&png_ptr, &info_ptr, &end_info);
         free(image_data);
         fclose(fp);
         return 0;
     }

     // set the individual row_pointers to point at the correct offsets of image_data
     int i;
     for (i = 0; i < temp_height; i++)
     {
         row_pointers[temp_height - 1 - i] = image_data + i * rowbytes;
     }

     // read the png into image_data through row_pointers
     png_read_image(png_ptr, row_pointers);

     // Generate the OpenGL texture object
     glBindTexture(GL_TEXTURE_2D, texID);
     if( bit_depth == 8 )
         glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, temp_width, temp_height, 0, GL_RED, GL_UNSIGNED_BYTE, image_data);
     else if( bit_depth == 24 )
    	 glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, temp_width, temp_height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data);
     else if( bit_depth == 32 )
    	 glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, temp_width, temp_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data);

     glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST );
     glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST );
     glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
     glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);

     // clean up
     png_destroy_read_struct(&png_ptr, &info_ptr, &end_info);
     free(image_data);
     free(row_pointers);
     fclose(fp);
     return texID;
 }

/*
 * loadDistTexture - load 8-bit distance texture data
 * from a TGA file and set up the corresponding texture object.
 */
void loadDistTexture(const char *filename, GLuint texID, int *texw, int *texh) {

  GLFWimage teximg; // Use intermediate GLFWimage to get width and height

  if(!glfwReadImage(filename, &teximg, GLFW_NO_RESCALE_BIT))
    printError("I/O error", "Failed to load distance texture from TGA file.");

  *texw = teximg.Width;
  *texh = teximg.Height;

  glActiveTexture(GL_TEXTURE0);
  glBindTexture( GL_TEXTURE_2D, texID );

  glfwLoadTextureImage2D( &teximg, 0 );
  // The special shader used to render this texture performs its own minification
  // and magnification. Specify nearest neighbor sampling for speed.
  // Using only 8 bits for the distance encoding, extreme minification is
  // problematic, so a mipmap for minification would actually be useful here.
  glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST );
  glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST );
  glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
  glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
  glfwFreeImage(&teximg); // Clean up the malloc()'ed data pointer
}


/*
 * loadRefTexture - Load reference texture data from a TGA file.
 * The reference texture is assumed to be of the same size as the
 * corresponding distance texture. If it isn't, rendering will be wrong.
 */
void loadRefTexture(const char *filename, GLuint texID) {

  glActiveTexture(GL_TEXTURE1);
  glBindTexture( GL_TEXTURE_2D, texID );

  if(!glfwLoadTexture2D(filename, 0)) // Use GLFW's built-in TGA support
    printError("I/O error", "Failed to load reference texture from TGA file");

  glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST );
  glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST );
  glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
  glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
}


/*
 * showFPS - Calculate and report frames per second (updated once per second)
 * and current magnification level in the window title bar.
 */
void showFPS(int texw, int texh, float zoom) {

  static double t0 = 0.0;
  static int frames = 0;
  static char titlestr[200];
  double t, fps;

  // Get current time
  t = glfwGetTime();  // Number of seconds since glfwInit()
  // If one second has passed, or if this is the very first frame
  if( (t - t0) > 1.0 || frames == 0 )
    {
      fps = (double)frames / (t - t0);
      sprintf(titlestr, "%dx%d texture, %.1fx zoom, %.1f FPS", texw, texh, zoom, fps);
      glfwSetWindowTitle(titlestr);
      t0 = t;
      frames = 0;
    }
  frames ++;
}


/*
 * renderScene - the OpenGL commands to render our scene.
 */
void renderScene(GLuint programObj,
                 float posx, float posy, float zoom, float rotx, float rotz)
{
  int width, height;

  // Get window size (may be resized at any time)
  glfwGetWindowSize( &width, &height );
  if( height<1 ) height = 1;
  if( width<1 ) width = 1;

  // Clear color buffer
  glClearColor( 0.0f, 0.0f, 0.5f, 0.0f );
  glColorMask( GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE );
  glClear( GL_COLOR_BUFFER_BIT );

  // Select and set up the projection matrix
  glMatrixMode( GL_PROJECTION );
  glLoadIdentity();
  // Handle interactive zoom by changing FOV (scaling would cause clipping)
  gluPerspective( 45.0f/zoom, (GLfloat)width/(GLfloat)height, 1.0f, 100.0f );
  glViewport( 0, 0, width, height );

  // Select and set up the modelview matrix
  glMatrixMode( GL_MODELVIEW );
  glLoadIdentity();

  // Use the shader object for the rendering
  glUseProgram( programObj );

  // Handle interactive pan, tilt and rotation
  gluLookAt(10.0f/width*posx, -10.0f/height*posy, 12.0f,
            10.0f/width*posx, -10.0f/height*posy, 0.0f,
            0.0f, 1.0f, 0.0f);
  glRotatef(-rotx, 1.0f, 0.0f, 0.0f);
  glRotatef(rotz, 0.0f, 0.0f, 1.0f);

  // Draw one texture mapped quad in the (x,y) plane
  glBegin( GL_QUADS );
  glTexCoord2f( 0.0f, 0.0f );
  glVertex2f( -5.0f, -5.0f );
  glTexCoord2f( 1.0f, 0.0f );
  glVertex2f( 5.0f, -5.0f );
  glTexCoord2f( 1.0f, 1.0f );
  glVertex2f( 5.0f, 5.0f );
  glTexCoord2f( 0.0f, 1.0f );
  glVertex2f( -5.0f, 5.0f );
  glEnd();

  // Deactivate the shader object.
  glUseProgram(0);
}


//========================================================================
// main()
//========================================================================

int main(int argc, char *argv[])
{
  // UI-related variables
  int running = 0;
  int mousebtn1, lastmousebtn1;
  int mousex, mousey, lastmousex, lastmousey;
  float posx, posy, zoom, rotx, rotz;

  // Shader-related variables
  GLuint textureID[2];
  int texw = 0;
  int texh = 0;
  GLuint currentProgramObj;
  GLuint programObj[2];

  // Initialise GLFW
  glfwInit();

  // Open OpenGL window
  if( !glfwOpenWindow( 512, 512, 0,0,0,0, 0,0, GLFW_WINDOW ) )
    {
      glfwTerminate();
      return 0;
    }

  // Init user interface (mouse drag for pan/zoom/tilt/rotation)
  posx = 0.0f;
  posy = 0.0f;
  zoom = 0.7f;
  rotx = 0.0f;
  rotz = 0.0f;
  glfwGetMousePos(&mousex, &mousey); // Requires an open window
  lastmousex = mousex;
  lastmousey = mousey;
  mousebtn1 = lastmousebtn1 = GLFW_RELEASE;

  // Load OpenGL extensions (requires an open window)
  loadExtensions();

  // Load textures
  glEnable(GL_TEXTURE_2D);
  glGenTextures( 2, textureID );
  //loadDistTexture("build/05_distance_fields.tga", textureID[0], &texw, &texh);
  //png_texture_load("doc/build/05_distance_fields.png", textureID[0], &texw, &texh);
  png_texture_load("../minosaur/content/fonts/verdana.png", textureID[0], &texw, &texh);
  loadRefTexture("doc/build/05_distance_fields.png", textureID[1]);

  // Create, load and compile the shader programs
  programObj[0] = createShader("build/vertex.glsl", "build/fragment1.glsl");
  programObj[1] = createShader("build/vertex.glsl", "build/fragment2.glsl");
  currentProgramObj = programObj[0];

  // Disable vertical sync (on cards that support
  // it, and if current driver settings so permit)
  glfwSwapInterval( 0 );

  // Main loop
  running = GL_TRUE;
  while( running )
    {
      showFPS(texw, texh, zoom);

      // Set the uniform shader variables
      setUniformVariables(currentProgramObj, 0, 1, (float)texw, (float)texh);

      renderScene(currentProgramObj, posx, posy, zoom, rotx, rotz);

      glfwSwapBuffers();

      // Handle mouse pan (button 1 drag), zoom (shift-btn 1 drag up/down),
      // tilt (ctrl-btn 1 drag up/down) and rotation (ctrl-btn 1 drag left/right)
      lastmousebtn1 = mousebtn1;
      mousebtn1 = glfwGetMouseButton(GLFW_MOUSE_BUTTON_1);
      lastmousex = mousex;
      lastmousey = mousey;
      glfwGetMousePos(&mousex, &mousey);

      if((mousebtn1 == GLFW_PRESS) && (lastmousebtn1 == GLFW_PRESS)) {
        if(glfwGetKey(GLFW_KEY_LSHIFT)) {
          zoom *= pow(1.01, (lastmousey - mousey));
	      if(zoom < 0.26f) zoom = 0.26f; // Do not go beyond 180 degrees FOV
        }
        else if (glfwGetKey(GLFW_KEY_LCTRL)) {
          rotz -= (lastmousex - mousex) * 0.5;
          rotx += (lastmousey - mousey) * 0.5;
      	  if(rotx > 89.5f) rotx = 89.5f;
          if(rotx < 0.0f) rotx = 0.0f;
        }
        else {
      	  posx += (lastmousex - mousex) / zoom;
	      posy += (lastmousey - mousey) / zoom;
        }
      }

      if(glfwGetKey('1')) {
        loadDistTexture("build/dist1.tga", textureID[0], &texw, &texh);
        loadRefTexture("build/ref1.tga", textureID[1]);
      }
      if(glfwGetKey('2')) {
        loadDistTexture("build/dist2.tga", textureID[0], &texw, &texh);
        loadRefTexture("build/ref2.tga", textureID[1]);
      }
      if(glfwGetKey('3')) {
        loadDistTexture("build/dist3.tga", textureID[0], &texw, &texh);
        loadRefTexture("build/ref3.tga", textureID[1]);
      }
      if(glfwGetKey('4')) {
        loadDistTexture("build/dist4.tga", textureID[0], &texw, &texh);
        loadRefTexture("build/ref4.tga", textureID[1]);
      }
      if(glfwGetKey('4')) {
        loadDistTexture("build/dist4.tga", textureID[0], &texw, &texh);
        loadRefTexture("build/ref4.tga", textureID[1]);
      }
      if(glfwGetKey('5')) {
        loadDistTexture("build/05_distance_fields.tga", textureID[0], &texw, &texh);
        loadRefTexture("build/05_distance_fields.tga", textureID[1]);
      }

      if(glfwGetKey('8')) {
        currentProgramObj = programObj[0];
      }
      if(glfwGetKey('9')) {
        currentProgramObj = programObj[1];
      }

      // Check if the ESC key is pressed or the window has been closed
      running = !glfwGetKey( GLFW_KEY_ESC ) &&
	glfwGetWindowParam( GLFW_OPENED );
    }

  // Close the window (if still open) and terminate GLFW
  glfwTerminate();

  return 0;
}
