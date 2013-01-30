#include "utils.h"
#include <stdio.h>
#include <float.h>


template<typename DTYPE, size_t MAX>
static void _convolve1d(const Image* image, const float* kernel, size_t kernelsize, size_t axis, void* _out)
{
	const size_t width = image->m_Width;
	const size_t height = image->m_Height;
	const size_t channels = image->m_Channels;
	const DTYPE* data = (DTYPE*)image->m_Data;
	DTYPE* out = (DTYPE*)_out;

	const size_t halfkernelsize = kernelsize / 2;
	const size_t rowsize = image->m_Width * channels;

	if( axis == 0 )
	{
		for( size_t y = 0; y < height; ++y )
		{
			for( size_t x = 0; x < width; ++x )
			{
				for( size_t c = 0; c < channels; ++c )
				{
					const int32_t xx = x - halfkernelsize;

					double sum = 0;
					for( size_t i = 0; i < kernelsize; ++i )
					{
						double value = 0;
						if( xx >= 0 && xx < width )
						{
							value = data[y * rowsize + (xx + i) * channels + c];
						}
						sum += value * kernel[i];
					}

					if( sum > MAX )
						sum = MAX;

					out[y * rowsize + x * channels + c] = DTYPE(sum);
				}
			}
		}
	}
	else
	{
		for( size_t x = 0; x < width; ++x )
		{
			for( size_t y = 0; y < height; ++y )
			{
				for( size_t c = 0; c < channels; ++c )
				{
					const int32_t yy = y - halfkernelsize;

					double sum = 0;
					for( size_t i = 0; i < kernelsize; ++i )
					{
						double value = 0;
						if( yy >= 0 && yy < height )
						{
							value = data[(yy + i) * rowsize + x * channels + c];
						}
						sum += value * kernel[i];
					}

					if( sum > MAX )
						sum = MAX;

					out[y * rowsize + x * channels + c] = DTYPE(sum);
				}
			}
		}
	}
}

template<typename DTYPE, size_t MAX>
static void _convolve1d_stacked(const Image* image, const float* kernel, size_t kernelsize, size_t axis, void* _out)
{
	const size_t width = image->m_Width;
	const size_t height = image->m_Height;
	const size_t channels = image->m_Channels;
	const size_t pagesize = width * height;
	const DTYPE* data = (DTYPE*)image->m_Data;
	DTYPE* out = (DTYPE*)_out;

	const size_t halfkernelsize = kernelsize / 2;

	if( axis == 0 )
	{
		for( size_t c = 0; c < channels; ++c )
		{
			for( size_t y = 0; y < height; ++y )
			{
				for( size_t x = 0; x < width; ++x )
				{
					double sum = 0;
					for( size_t k = 0; k < kernelsize; ++k )
					{
						int32_t xx = x - halfkernelsize + k;
						if( xx < 0 )
							xx = 0;
						else if( xx >= width )
							xx = width -1;

						const double value = data[c * pagesize + y * width + xx];

						sum += value * kernel[k];
					}

					if( sum > MAX )
						sum = MAX;

					out[c * pagesize + y * width + x] = DTYPE(sum);
				}
			}
		}
	}
	else
	{
		for( size_t c = 0; c < channels; ++c )
		{
			for( size_t x = 0; x < width; ++x )
			{
				for( size_t y = 0; y < height; ++y )
				{
					double sum = 0;
					for( size_t k = 0; k < kernelsize; ++k )
					{
						int32_t yy = y - halfkernelsize + k;
						if( yy < 0 )
							yy = 0;
						else if( yy >= height )
							yy = height - 1;

						const double value = data[c * pagesize + yy * width + x];
						sum += value * kernel[k];
					}

					if( sum > MAX )
						sum = MAX;

					out[c * pagesize + y * width + x] = DTYPE(sum);
				}
			}
		}
	}
}


void convolve1d(const Image* image, const float* kernel, size_t kernelsize, size_t axis, void* out)
{
	if( image->m_Type == E_UINT )
	{
		if( image->m_Layout == E_INTERLEAVED )
		{
			if( image->m_ChannelDepth == 8 )
				_convolve1d<uint8_t, 255>( image, kernel, kernelsize, axis, out);
			else if( image->m_ChannelDepth == 16 )
				_convolve1d<uint16_t, 65535>( image, kernel, kernelsize, axis, out);
			else if( image->m_ChannelDepth == 32 )
				_convolve1d<uint32_t, 0xFFFFFFFF>( image, kernel, kernelsize, axis, out);
			else if( image->m_ChannelDepth == 64 )
				_convolve1d<uint64_t, 0xFFFFFFFF>( image, kernel, kernelsize, axis, out);
		}
		else
		{
			if( image->m_ChannelDepth == 8 )
				_convolve1d_stacked<uint8_t, 255>( image, kernel, kernelsize, axis, out);
			else if( image->m_ChannelDepth == 16 )
				_convolve1d_stacked<uint16_t, 65535>( image, kernel, kernelsize, axis, out);
			else if( image->m_ChannelDepth == 32 )
				_convolve1d_stacked<uint32_t, 0xFFFFFFFF>( image, kernel, kernelsize, axis, out);
			else if( image->m_ChannelDepth == 64 )
				_convolve1d_stacked<uint64_t, 0xFFFFFFFF>( image, kernel, kernelsize, axis, out);
		}
	}
	else // float
	{
		if( image->m_Layout == E_INTERLEAVED )
		{
			if( image->m_ChannelDepth == 32 )
				_convolve1d<float, 1>( image, kernel, kernelsize, axis, out);
			else if( image->m_ChannelDepth == 64 )
				_convolve1d<double, 1>( image, kernel, kernelsize, axis, out);
		}
		else
		{
			if( image->m_ChannelDepth == 32 )
				_convolve1d_stacked<float, 1>( image, kernel, kernelsize, axis, out);
			else if( image->m_ChannelDepth == 64 )
				_convolve1d_stacked<double, 1>( image, kernel, kernelsize, axis, out);
		}
	}
}


template<typename DTYPE, size_t MAX>
static void _minmax(const Image* image, const float* kernel, size_t kernelwidth, size_t kernelheight, bool maximum, void* _out)
{
	const size_t width = image->m_Width;
	const size_t height = image->m_Height;
	const size_t channels = image->m_Channels;
	const DTYPE* data = (DTYPE*)image->m_Data;
	DTYPE* out = (DTYPE*)_out;

	for( size_t y = 0; y < height; ++y )
	{
		for( size_t x = 0; x < width; ++x )
		{
			for( size_t c = 0; c < channels; ++c )
			{
				const int32_t xx = x - kernelwidth / 2;
				const int32_t yy = y - kernelheight / 2;

				const bool test = x == 2 && y == 0;

				DTYPE extrema = maximum ? 0 : DTYPE(MAX);
				for( size_t ky = 0; ky < kernelheight; ++ky )
				{
					const int32_t yyy = yy + ky;
					if( yyy < 0 || yyy >= height )
						continue;

					for( size_t kx = 0; kx < kernelwidth; ++kx )
					{
						const int32_t xxx = xx + kx;
						if( xxx < 0 || xxx >= width )
							continue;

						if( kernel[ky * kernelwidth + kx] == 0 )
							continue;

						const int32_t index = yyy * width * channels + xxx * channels + c;
						const DTYPE value = data[yyy * width * channels + xxx * channels + c];

						if( test )
						{
							//printf("sample x, y, c %d, %d, %lu = %f    index = %d\n", xxx, yyy, c, value, index);
						}

						if( maximum )
						{
							if( value > extrema )
								extrema = value;
						}
						else
						{
							if( value < extrema )
								extrema = value;
						}
					}
				}

				static bool first = true;
				if( test )
				{
					first = false;
					//printf("x, y, c %lu, %lu, %lu = %d\n", x, y, c, extrema);
				}

				out[ y * width * channels + x * channels + c] = extrema;
			}
		}
	}
}

template<typename DTYPE, size_t MAX>
static void _minmax_stacked(const Image* image, const float* kernel, size_t kernelwidth, size_t kernelheight, bool maximum, void* _out)
{
	const size_t width = image->m_Width;
	const size_t height = image->m_Height;
	const size_t channels = image->m_Channels;
	const size_t pagesize = width * height;
	const DTYPE* data = (DTYPE*)image->m_Data;
	DTYPE* out = (DTYPE*)_out;

	for( size_t c = 0; c < channels; ++c )
	{
		for( size_t y = 0; y < height; ++y )
		{
			for( size_t x = 0; x < width; ++x )
			{
				const int32_t xx = x - kernelwidth / 2;
				const int32_t yy = y - kernelheight / 2;

				DTYPE extrema = maximum ? 0 : DTYPE(MAX);
				for( size_t ky = 0; ky < kernelheight; ++ky )
				{
					const int32_t yyy = yy + ky;
					if( yyy < 0 || yyy >= height )
						continue;

					for( size_t kx = 0; kx < kernelwidth; ++kx )
					{
						const int32_t xxx = xx + kx;
						if( xxx < 0 || xxx >= width )
							continue;

						if( kernel[ky * kernelwidth + kx] == 0 )
							continue;

						const int32_t index = c * pagesize + yyy * width + xxx;
						const DTYPE value = data[index];

						if( maximum )
						{
							if( value > extrema )
								extrema = value;
						}
						else
						{
							if( value < extrema )
								extrema = value;
						}
					}
				}

				out[ c * pagesize + y * width + x ] = extrema;
			}
		}
	}
}


void maximum(const Image* image, const float* kernel, size_t kernelwidth, size_t kernelheight, void* out)
{
	if( image->m_Type == E_UINT )
	{
		if( image->m_Layout == E_INTERLEAVED )
		{
			if( image->m_ChannelDepth == 8 )
				_minmax<uint8_t, 255>(image, kernel, kernelwidth, kernelheight, true, out);
			else if( image->m_ChannelDepth == 16 )
				_minmax<uint16_t, 65535>(image, kernel, kernelwidth, kernelheight, true, out);
			else if( image->m_ChannelDepth == 32 )
				_minmax<uint32_t, 0xFFFFFFFF>(image, kernel, kernelwidth, kernelheight, true, out);
		}
		else
		{
			if( image->m_ChannelDepth == 8 )
				_minmax_stacked<uint8_t, 255>(image, kernel, kernelwidth, kernelheight, true, out);
			else if( image->m_ChannelDepth == 16 )
				_minmax_stacked<uint16_t, 65535>(image, kernel, kernelwidth, kernelheight, true, out);
			else if( image->m_ChannelDepth == 32 )
				_minmax_stacked<uint32_t, 0xFFFFFFFF>(image, kernel, kernelwidth, kernelheight, true, out);
		}
	}
	else // float
	{
		if( image->m_Layout == E_INTERLEAVED )
		{
			if( image->m_ChannelDepth == 32 )
				_minmax<float, 255>(image, kernel, kernelwidth, kernelheight, true, out);
			else if( image->m_ChannelDepth == 64 )
				_minmax<double, 255>(image, kernel, kernelwidth, kernelheight, true, out);
		}
		else // stacked
		{
			if( image->m_ChannelDepth == 32 )
				_minmax_stacked<float, 255>(image, kernel, kernelwidth, kernelheight, true, out);
			else if( image->m_ChannelDepth == 64 )
				_minmax_stacked<double, 255>(image, kernel, kernelwidth, kernelheight, true, out);
		}
	}
}


void minimum(const Image* image, const float* kernel, size_t kernelwidth, size_t kernelheight, void* out)
{
	if( image->m_Type == E_UINT )
	{
		if( image->m_Layout == E_INTERLEAVED )
		{
			if( image->m_ChannelDepth == 8 )
				_minmax<uint8_t, 255>(image, kernel, kernelwidth, kernelheight, false, out);
			else if( image->m_ChannelDepth == 16 )
				_minmax<uint16_t, 65535>(image, kernel, kernelwidth, kernelheight, false, out);
			else if( image->m_ChannelDepth == 32 )
				_minmax<uint32_t, 0xFFFFFFFF>(image, kernel, kernelwidth, kernelheight, false, out);
		}
		else
		{
			if( image->m_ChannelDepth == 8 )
				_minmax_stacked<uint8_t, 255>(image, kernel, kernelwidth, kernelheight, false, out);
			else if( image->m_ChannelDepth == 16 )
				_minmax_stacked<uint16_t, 65535>(image, kernel, kernelwidth, kernelheight, false, out);
			else if( image->m_ChannelDepth == 32 )
				_minmax_stacked<uint32_t, 0xFFFFFFFF>(image, kernel, kernelwidth, kernelheight, false, out);
		}
	}
	else // float
	{
		if( image->m_Layout == E_INTERLEAVED )
		{
			if( image->m_ChannelDepth == 32 )
				_minmax<float, 255>(image, kernel, kernelwidth, kernelheight, false, out);
			else if( image->m_ChannelDepth == 64 )
				_minmax<double, 255>(image, kernel, kernelwidth, kernelheight, false, out);
		}
		else
		{
			if( image->m_ChannelDepth == 32 )
				_minmax_stacked<float, 255>(image, kernel, kernelwidth, kernelheight, false, out);
			else if( image->m_ChannelDepth == 64 )
				_minmax_stacked<double, 255>(image, kernel, kernelwidth, kernelheight, false, out);
		}
	}
}


template<typename DTYPE>
static void _half_size(const Image* image, void* _out)
{
	const size_t width = image->m_Width;
	const size_t height = image->m_Height;
	const size_t channels = image->m_Channels;
	const DTYPE* data = (DTYPE*)image->m_Data;
	DTYPE* out = (DTYPE*)_out;

	const size_t halfwidth = image->m_Width/2;
	const size_t halfheight = image->m_Height/2;

	if( image->m_Layout == E_INTERLEAVED )
	{
		for( uint32_t y = 0; y < halfheight; ++y)
		{
			for( uint32_t x = 0; x < halfwidth; ++x)
			{
				uint32_t xx = x*2;
				uint32_t yy = y*2;
				for( uint32_t c = 0; c < channels; ++c)
				{
					DTYPE s0 = data[ yy * channels + xx * channels + c ];
					DTYPE s1 = data[ yy * channels + (xx+1) * channels + c ];
					DTYPE s2 = data[ (yy+1) * channels + xx * channels + c ];
					DTYPE s3 = data[ (yy+1) * channels + (xx+1) * channels + c ];
					out[ y * halfwidth * channels + x * channels + c] = (s0 + s1 + s2 + s3) / DTYPE(4);
				}
			}
		}
	}
	else
	{
<<<<<<< HEAD
		const size_t pagesize = width * height;
		const size_t halfpagesize = halfwidth * halfheight;
=======
		const size_t pagesize = halfwidth * halfheight;
>>>>>>> de3b330fc3f9ff1b314828fed60532b8a54ff6ed

		for( uint32_t c = 0; c < channels; ++c)
		{
			for( uint32_t y = 0; y < halfheight; ++y)
			{
<<<<<<< HEAD
				for( uint32_t x = 0; x < halfwidth; ++x)
				{
					uint32_t xx = x*2;
					uint32_t yy = y*2;
					DTYPE s0 = data[ c * pagesize + yy * width + xx ];
					DTYPE s1 = data[ c * pagesize + yy * width + (xx+1) ];
					DTYPE s2 = data[ c * pagesize + (yy+1) * width + xx ];
					DTYPE s3 = data[ c * pagesize + (yy+1) * width + (xx+1) ];

					out[ c * halfpagesize + y * halfwidth + x ] = (s0 + s1 + s2 + s3) / DTYPE(4);
=======
				for( uint32_t x = 0; y < halfwidth; ++x)
				{
					uint32_t xx = x*2;
					uint32_t yy = y*2;
					DTYPE s0 = data[ yy * channels + xx * channels + c ];
					DTYPE s1 = data[ yy * channels + (xx+1) * channels + c ];
					DTYPE s2 = data[ (yy+1) * channels + xx * channels + c ];
					DTYPE s3 = data[ (yy+1) * channels + (xx+1) * channels + c ];
					out[ c * pagesize + y * halfwidth + x] = (s0 + s1 + s2 + s3) / DTYPE(4);
>>>>>>> de3b330fc3f9ff1b314828fed60532b8a54ff6ed
				}
			}
		}
	}
}

void half_size(const Image* image, void* out)
{
	if( image->m_Type == E_UINT )
	{
		if( image->m_ChannelDepth == 8 )
			_half_size<uint8_t>(image, out);
		else if( image->m_ChannelDepth == 16 )
			_half_size<uint16_t>(image, out);
		else if( image->m_ChannelDepth == 32 )
			_half_size<uint32_t>(image, out);
	}
	else // float
	{
		if( image->m_ChannelDepth == 32 )
			_half_size<float>(image, out);
		else if( image->m_ChannelDepth == 64 )
			_half_size<double>(image, out);
	}
}
