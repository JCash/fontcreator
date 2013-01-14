// Distance map contour texturing, Stefan Gustavson 2009
// A re-implementation of Green's method, with an
// 8-bit distance map but explicit texel interpolation.
// This code is in the public domain.

uniform sampler2D disttexture, reftexture;
uniform float texw, texh;
varying float onestepu, onestepv;
varying vec2 st;

void main( void )
{
  // Scale texcoords to range ([0,texw], [0,texh])
  vec2 uv = st * vec2(texw, texh);

  // Compute texel-local (u,v) coordinates for the four closest texels
  vec2 uv00 = floor(uv - vec2(0.5)); // Lower left corner of lower left texel
  vec2 uvthis = floor(uv); // Lower left corner of texel containing (u,v)
  vec2 uvlerp = uv - uv00 - vec2(0.5); // Texel-local lerp blends [0,1]

  // Perform explicit texture interpolation of D coefficient.
  // This works around the currently very bad texture interpolation
  // precision in ATI hardware.

  // Center st00 on lower left texel and rescale to [0,1] for texture lookup
  vec2 st00 = (uv00  + vec2(0.5)) * vec2(onestepu, onestepv);

  // Compute g_u, g_v, D coefficients from four closest 8-bit RGBA texels
  vec4 rawtex00 = texture2D(disttexture, st00);
  vec4 rawtex10 = texture2D(disttexture, st00 + vec2(0.5*onestepu, 0.0));
  vec4 rawtex01 = texture2D(disttexture, st00 + vec2(0.0, 0.5*onestepv));
  vec4 rawtex11 = texture2D(disttexture, st00 + vec2(0.5*onestepu, 0.5*onestepv));

  // Restore the value for D from its 8-bit encoding
  vec2 D00_10 = 16.0*(vec2(rawtex00.r, rawtex10.r)-0.50196);
  vec2 D01_11 = 16.0*(vec2(rawtex01.r, rawtex11.r)-0.50196);

  // Interpolate D between four closest texels
  vec2 uvlocal = fract(uv)-0.5; // Texel-local uv coordinates [-0.5,0.5]
  // Interpolate along v
  vec2 D0_1 = mix(D00_10, D01_11, uvlerp.y);
  // Interpolate along u
  float D = mix(D0_1.x, D0_1.y, uvlerp.x);

  // Perform anisotropic analytic antialiasing (fwidth() is slightly wrong)
  float aastep = length(vec2(dFdx(D), dFdy(D)));
  
  // 'pattern' is 1 where D>0, 0 where D<0, with proper AA around D=0.
  float pattern = smoothstep(-aastep, aastep, D);

  // Final fragment color
  gl_FragColor = vec4(pattern, pattern, pattern, 1.0);
}
