#ifndef UTILS_H
#define UTILS_H

#include <stdint.h>
#include <string.h>

extern "C" {

enum EImageLayout
{
	E_INTERLEAVED,	// rgba, rgba, rgba ...
	E_STACKED,		// rrrr..., gggg..., bbbb..., aaaa...
};

enum EDataType
{
	E_UINT,
	E_FLOAT,
};

struct Image
{
	void*	m_Data;
	size_t  m_Width;
	size_t  m_Height;
	size_t  m_Channels;
	EImageLayout m_Layout:2;
	EDataType 	 m_Type:2;
	uint32_t	 m_ChannelDepth:26;
};

void convolve1d(const Image* image, const float* kernel, size_t kernelsize, size_t axis, void* out);

void maximum(const Image* image, const float* kernel, size_t kernelwidth, size_t kernelheight, void* out);

void minimum(const Image* image, const float* kernel, size_t kernelwidth, size_t kernelheight, void* out);

void calculate_sedt(const Image* image, float radius, void* out);

}

#endif // UTILS_H
