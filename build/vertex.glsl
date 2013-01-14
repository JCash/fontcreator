// Distance map contour texturing according to Green (2007),
// implementation by Stefan Gustavson 2009.
// This code is in the public domain.

uniform sampler2D disttexture, reftexture;
uniform float texw, texh;
varying float onestepu, onestepv;
varying vec2 st;

void main( void )
{
  // Get the texture coordinates
  st = gl_MultiTexCoord0.xy;
  onestepu = 1.0 / texw; // Saves a division in the fragment shader
  onestepv = 1.0 / texh;
  gl_Position = ftransform();
}
