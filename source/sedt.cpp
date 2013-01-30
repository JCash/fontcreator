/* Implements signed euclidian distance fields.
 * Implementation taken from: http://www.gbuffer.net/vector-textures
 *
 * More info:
 * http://perso.telecom-paristech.fr/~bloch/ANIM/Danielsson.pdf
 * http://www.ensta-paristech.fr/~manzaner/Download/IAD/Shih_Wu_04.pdf
 * http://fab.cba.mit.edu/classes/S62.12/docs/Meijster_distance.pdf
 * http://liu.diva-portal.org/smash/get/diva2:23335/FULLTEXT01  (pdf)
 *
 *
 * http://parmanoir.com/distance/  (interactive demo)
*/

#include "utils.h"
#include <math.h>
#include <assert.h>
#if defined(_WIN32) || defined(_WIN64)
#include <algorithm>
#define fmin std::min<float>
#define fmax std::max<float>
#endif
#include <stdio.h>

struct Vector2int16
{
	int16_t x;
	int16_t y;
	Vector2int16() {}
	Vector2int16(int16_t _x, int16_t _y) : x(_x), y(_y) {}
};

template<typename DTYPE, size_t MAX>
class SEDT
{
private:
	Vector2int16 *distMap;
	int w, h;

public:
	SEDT();
	~SEDT();

	void release();

	void init(int w, int h, const DTYPE* binImg, bool invert = false);

	void updatePix(int idx, int idxOffset, int x, int y, int xOffset, int yOffset );

	void compute(float* outDist);
};

template<typename DTYPE, size_t MAX>
SEDT<DTYPE, MAX>::SEDT()
{
	distMap = NULL;
}

template<typename DTYPE, size_t MAX>
SEDT<DTYPE, MAX>::~SEDT()
{
	release();
}

template<typename DTYPE, size_t MAX>
void SEDT<DTYPE, MAX>::release()
{
	delete[] distMap;
	distMap = NULL;
}

template<typename DTYPE, size_t MAX>
void SEDT<DTYPE, MAX>::init( int w, int h, const DTYPE* binImg, bool invert )
{
	const Vector2int16 z = Vector2int16(0,0);
	const Vector2int16 max = Vector2int16(w+1,h+1);

	this->w = w;
	this->h = h;

	release();

	distMap = new Vector2int16[w*h];

	const DTYPE halfrange = DTYPE(MAX) / 2;

	if (invert)
	{
		for (int i=0; i<w*h; ++i)
		{
			distMap[i] = (binImg[i] < halfrange) ? max : z;
		}
	}
	else
	{
		for (int i=0; i<w*h; ++i)
		{
			distMap[i] = (binImg[i] < halfrange) ? z : max;
		}
	}
}


template<typename DTYPE, size_t MAX>
void SEDT<DTYPE, MAX>::updatePix( int idx, int idxOffset, int x, int y, int xOffset, int yOffset )
{
	if (x+xOffset < 0 || x+xOffset >= w || y+yOffset < 0 || y+yOffset >= h)
	{
		return;
	}

	Vector2int16 n = distMap[idx + idxOffset];
	Vector2int16 &p = distMap[idx];

	n.x += xOffset;
	n.y += yOffset;

	if (p.x*p.x + p.y*p.y > n.x*n.x + n.y*n.y)
		p = n;
}

template<typename DTYPE, size_t MAX>
void SEDT<DTYPE, MAX>::compute( float* outDist )
{
	int idx;

	// Pass 0
	for (int y=0;y<h;y++)
	{
		idx = y*w;

		for (int x=0;x<w;x++)
		{
			updatePix( idx, -1, x, y, -1,  0 );
			updatePix( idx, -w, x, y,  0, -1 );
			updatePix( idx, -w-1, x, y, -1, -1 );
			updatePix( idx, -w+1, x, y,  1, -1 );

			++idx;
		}

		--idx;

		for (int x=w-1; x>=0; x--)
		{
			updatePix( idx, 1, x, y, 1, 0 );

			--idx;

		}
	}

	// Pass 1
	idx = w*h-1;
	for (int y=h-1; y>=0; y--)
	{
		idx = (y+1)*w - 1;

		for (int x=w-1; x>=0; x--)
		{
			updatePix( idx, 1, x, y,  1,  0 );
			updatePix( idx, w, x, y,  0,  1 );
			updatePix( idx, w-1, x, y, -1,  1 );
			updatePix( idx, w+1, x, y,  1,  1 );

			--idx;
		}

		++idx;

		for (int x=0;x<w;x++)
		{
			updatePix( idx, -1, x, y, -1, 0 );

			++idx;
		}

		idx -= w;
	}

	for (int i=0; i<w*h; ++i)
	{
		outDist[i] = sqrt((double)distMap[i].x*distMap[i].x + distMap[i].y*distMap[i].y);
	}
}


template<typename DTYPE, size_t MAX>
static void _calculate_sedt(const Image* image, float radius, void* _out)
{
	const size_t w = image->m_Width;
	const size_t h = image->m_Height;
	const size_t pagesize = w * h;

	const DTYPE* src = (const DTYPE*)image->m_Data;
	DTYPE* out = (DTYPE*)_out;

	float* img1 = new float[pagesize * 2];
	float* img2 = img1 + pagesize;

	/*
	printf("sizeof( DTYPE ) == %u\n", sizeof(DTYPE));
	printf("image %d\n", image->m_Layout);
	printf("chdepth %d\n", image->m_ChannelDepth);
	printf("w, h, d %d, %d, %d\n", w, h, image->m_Channels);
	*/

	SEDT<DTYPE, MAX> sedt;
	sedt.init(w, h, src, 0);
	sedt.compute(img1);

	sedt.init(w, h, src, 1);
	sedt.compute(img2);

	for( int i = 0; i < pagesize; ++i )
	{
		float value = (img1[i] - img2[i]) / radius;
		value = (value * 0.5f) + 0.5f;
		value = fmin(1.0f, fmax(0.0f, value));

		// scale back to input range
		out[i] = DTYPE(value * MAX);
	}

	delete [] img1;
}

void calculate_sedt(const Image* image, float radius, void* out)
{
	if( image->m_Channels > 1)
	{
		printf("calculate_sedt supports 1 channel only\n");
		return;
	}

	if( image->m_Type == E_UINT )
	{
		assert(false && "UINT Not implemented!!");
		/*
		if( image->m_ChannelDepth == 8 )
			_calculate_sedt<uint8_t, 255>( image, radius, out );
		else if( image->m_ChannelDepth == 16 )
			_calculate_sedt<uint16_t, 65535>( image, radius, out );
		else if( image->m_ChannelDepth == 32 )
			_calculate_sedt<uint32_t, 0xFFFFFFFF>( image, radius, out );
		else if( image->m_ChannelDepth == 64 )
			_calculate_sedt<uint64_t, 0xFFFFFFFF>( image, radius, out );
			*/
	}
	else if( image->m_Type == E_FLOAT )
	{
		if( image->m_ChannelDepth == 32 )
			_calculate_sedt<float, 1>( image, radius, out );
		else if( image->m_ChannelDepth == 64 )
			_calculate_sedt<double, 1>( image, radius, out );
	}
}
