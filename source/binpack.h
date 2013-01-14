#ifndef UTILS_H
#define UTILS_H

/** A wrapper for the RectangleBinPack implementation by Jukka Jylänki.
 * More info at: http://clb.demon.fi/files/RectangleBinPack.pdf
 * Source at: http://clb.demon.fi/files/RectangleBinPack/
 */

#include <stdint.h>
#include <string.h>

#if defined(_MSC_VER)
	#define DLL_EXPORT __declspec(dllexport)
#else
	#define DLL_EXPORT
#endif

extern "C" {

enum EPackerType
{
	E_SKYLINE_BL,	// Bottom left
	E_SKYLINE_MW,	// Min Waste

	E_MAXRECTS_BSSF, ///< Positions the rectangle against the short side of a free rectangle into which it fits the best.
	E_MAXRECTS_BLSF, ///< Positions the rectangle against the long side of a free rectangle into which it fits the best.
	E_MAXRECTS_BAF,  ///< Positions the rectangle into the smallest free rect into which it fits.
	E_MAXRECTS_BL,	 ///< Does the Tetris placement.
	E_MAXRECTS_CP,	 ///< Chooses the placement where the rectangle touches other rects as much as possible.
};

struct DLL_EXPORT SRect
{
	int32_t x;
	int32_t y;
	int32_t width;
	int32_t height;
};

struct SPacker;

typedef SPacker* HPacker;

DLL_EXPORT HPacker create_packer(EPackerType type, int32_t w, int32_t h, bool allow_rotate);

DLL_EXPORT SRect pack_rect(HPacker packer, int32_t w, int32_t h);

DLL_EXPORT void destroy_packer(HPacker packer);

DLL_EXPORT float get_occupancy(HPacker packer);

}

#endif
