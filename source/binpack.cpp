
#include "binpack.h"
#include "binpack/SkylineBinPack.h"
#include "binpack/MaxRectsBinPack.h"
#include "assert.h"

struct SPacker
{
	EPackerType	m_Type;
	void*		m_Packer;
};

HPacker create_packer(EPackerType type, int32_t w, int32_t h, bool allow_rotate)
{
	SPacker* packer = new SPacker;
	packer->m_Type = type;
	if( type == E_SKYLINE_BL || type == E_SKYLINE_MW )
		packer->m_Packer = new SkylineBinPack(w, h, true, allow_rotate);
	else if( type == E_MAXRECTS_BSSF ||
			 type == E_MAXRECTS_BLSF ||
			 type == E_MAXRECTS_BAF ||
			 type == E_MAXRECTS_BL ||
			 type == E_MAXRECTS_CP )
		packer->m_Packer = new MaxRectsBinPack(w, h);
	return packer;
}

SRect pack_rect(HPacker _packer, int32_t w, int32_t h)
{
	const SPacker* packer = (SPacker*)_packer;
	const EPackerType type = packer->m_Type;
	Rect rect;

	if( type == E_SKYLINE_BL )
		rect = ((SkylineBinPack*)packer->m_Packer)->Insert(w, h, SkylineBinPack::LevelBottomLeft);
	else if( type == E_SKYLINE_MW )
		rect = ((SkylineBinPack*)packer->m_Packer)->Insert(w, h, SkylineBinPack::LevelMinWasteFit);
	else if( type == E_MAXRECTS_BSSF )
		rect = ((MaxRectsBinPack*)packer->m_Packer)->Insert(w, h, MaxRectsBinPack::RectBestShortSideFit);
	else if( type == E_MAXRECTS_BLSF )
		rect = ((MaxRectsBinPack*)packer->m_Packer)->Insert(w, h, MaxRectsBinPack::RectBestLongSideFit);
	else if( type == E_MAXRECTS_BAF )
		rect = ((MaxRectsBinPack*)packer->m_Packer)->Insert(w, h, MaxRectsBinPack::RectBestAreaFit);
	else if( type == E_MAXRECTS_BL )
		rect = ((MaxRectsBinPack*)packer->m_Packer)->Insert(w, h, MaxRectsBinPack::RectBottomLeftRule);
	else if( type == E_MAXRECTS_CP )
		rect = ((MaxRectsBinPack*)packer->m_Packer)->Insert(w, h, MaxRectsBinPack::RectContactPointRule);
	else
	{
		assert(false && "Wrong type");
	}

	SRect out;
	out.x = rect.x;
	out.y = rect.y;
	out.width = rect.width;
	out.height = rect.height;
	return out;
}

void destroy_packer(HPacker _packer)
{
	SPacker* packer = (SPacker*)_packer;
	const EPackerType type = packer->m_Type;
	if( type == E_SKYLINE_BL || type == E_SKYLINE_MW )
		delete (SkylineBinPack*)(packer->m_Packer);
	else if( type == E_MAXRECTS_BSSF ||
			 type == E_MAXRECTS_BLSF ||
			 type == E_MAXRECTS_BAF ||
			 type == E_MAXRECTS_BL ||
			 type == E_MAXRECTS_CP )
		delete (MaxRectsBinPack*)(packer->m_Packer);
	delete packer;
}


float get_occupancy(HPacker _packer)
{
	const SPacker* packer = (SPacker*)_packer;
	const EPackerType type = packer->m_Type;
	if( type == E_SKYLINE_BL || type == E_SKYLINE_MW )
		return ((SkylineBinPack*)packer->m_Packer)->Occupancy();
	else if( type == E_MAXRECTS_BSSF ||
			 type == E_MAXRECTS_BLSF ||
			 type == E_MAXRECTS_BAF ||
			 type == E_MAXRECTS_BL ||
			 type == E_MAXRECTS_CP )
		return ((MaxRectsBinPack*)packer->m_Packer)->Occupancy();
	return 0.0f;
}

