import logging
import numpy as np

blendfunctions = dict()


def BlendFunction(fun):
    """ Registers a class as a blend function

    :param fun: A function that takes two numpy images, blends them and then returns the resulting image.
    """
    assert( callable(fun) )
    blendfunctions[fun.__name__.lower()] = fun
    logging.info( "Registered blend function %s" % fun.__name__.lower() )
    return fun


def GetBlendFunction(name):
    return blendfunctions[name]

# TODO: vectorize these functions


@BlendFunction
def blendnormal(*k, **kw):
    """ R = blend

    :param base: The base image
    :param blend: The blend image
    """
    return kw['blend']


# Darken blends

@BlendFunction
def blenddarken(*k, **kw):
    """ R = min( base, blend )

    :param base: The base image
    :param blend: The blend image
    """
    base = kw['base']
    blend = kw['blend']
    return np.minimum(base, blend)


@BlendFunction
def blendmultiply(*k, **kw):
    """ R = base * blend

    :param base: The base image
    :param blend: The blend image
    """
    base = kw['base']
    blend = kw['blend']
    return base * blend


@BlendFunction
def blendcolorburn(*k, **kw):
    """ R = 1 - (1 - base) / blend

    :param base: The base image
    :param blend: The blend image
    """
    base = kw['base']
    blend = kw['blend']
    # 1 - (1-Base) / Blend
    ones = np.ones_like(base)
    return ones - (ones - base) / blend


@BlendFunction
def blendlinearburn(*k, **kw):
    """ R = base + blend - 1

    :param base: The base image
    :param blend: The blend image
    """
    base = kw['base']
    blend = kw['blend']
    # R = Base + Blend - 1
    return base + blend - np.ones_like(base)


# Lighten blends

@BlendFunction
def blendlighten(*k, **kw):
    """ R = max( base, blend )

    :param base: The base image
    :param blend: The blend image
    """
    base = kw['base']
    blend = kw['blend']
    return np.maximum(base, blend)


@BlendFunction
def blendscreen(*k, **kw):
    """ R = 1 - (1 - base) * (1 - blend)

    :param base: The base image
    :param blend: The blend image
    """
    base = kw['base']
    blend = kw['blend']
    # R = 1 - (1-Base) * (1-Blend)
    ones = np.ones_like(base)
    return ones - (ones - base) * (ones - blend)


@BlendFunction
def blendcolordodge(*k, **kw):
    """ R = base / (1 - blend)

    :param base: The base image
    :param blend: The blend image
    """
    base = kw['base']
    blend = kw['blend']
    # R = Base / (1-Blend)
    ones = np.ones_like(base)
    return base / (ones - blend)


@BlendFunction
def blendlineardodge(*k, **kw):
    """ R = base + blend

    :param base: The base image
    :param blend: The blend image
    """
    base = kw['base']
    blend = kw['blend']
    return base + blend
