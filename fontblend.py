import logging
import numpy as np

BLENDFUNCTIONS = dict()


def blendfunction(fun):
    """ Registers a class as a blend function

    :param fun: A function that takes two numpy images, blends them and then returns the resulting image.
    
    Example::
    
        @blendfunction
        def my_blend_function(base, blend):
            return base + blend
    """
    assert( callable(fun) )
    BLENDFUNCTIONS[fun.__name__.lower()] = fun
    logging.info( "Registered blend function %s" % fun.__name__.lower() )
    return fun


# TODO: vectorize these functions


@blendfunction
def blendnormal(base, blend):
    """ R = blend

    :param base: The base image
    :param blend: The blend image
    """
    return blend


# Darken blends

@blendfunction
def blenddarken(base, blend):
    """ R = min( base, blend )

    :param base: The base image
    :param blend: The blend image
    """
    return np.minimum(base, blend)


@blendfunction
def blendmultiply(base, blend):
    """ R = base * blend

    :param base: The base image
    :param blend: The blend image
    """
    return base * blend


@blendfunction
def blendcolorburn(base, blend):
    """ R = 1 - (1 - base) / blend

    :param base: The base image
    :param blend: The blend image
    """
    # 1 - (1-Base) / Blend
    ones = np.ones_like(base)
    return ones - (ones - base) / blend


@blendfunction
def blendlinearburn(base, blend):
    """ R = base + blend - 1

    :param base: The base image
    :param blend: The blend image
    """
    # R = Base + Blend - 1
    return base + blend - np.ones_like(base)


# Lighten blends

@blendfunction
def blendlighten(base, blend):
    """ R = max( base, blend )

    :param base: The base image
    :param blend: The blend image
    """
    return np.maximum(base, blend)


@blendfunction
def blendscreen(base, blend):
    """ R = 1 - (1 - base) * (1 - blend)

    :param base: The base image
    :param blend: The blend image
    """
    # R = 1 - (1-Base) * (1-Blend)
    ones = np.ones_like(base)
    return ones - (ones - base) * (ones - blend)


@blendfunction
def blendcolordodge(base, blend):
    """ R = base / (1 - blend)

    :param base: The base image
    :param blend: The blend image
    """
    # R = Base / (1-Blend)
    ones = np.ones_like(base)
    return base / (ones - blend)


@blendfunction
def blendlineardodge(base, blend):
    """ R = base + blend

    :param base: The base image
    :param blend: The blend image
    """
    return base + blend
