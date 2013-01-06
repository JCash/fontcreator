
from propertytypes import Property, PropertyValidateError


def _CapitalizeName(name):
    capitalizedname = name.split('_')
    capitalizedname = ''.join( [ x.capitalize() for x in capitalizedname ] )
    return capitalizedname


def _ConvertProperty(cls, name):

    capitalizedname = _CapitalizeName(name)

    fnget = lambda instance: getattr(instance, '_' + name)
    fnget = getattr(cls, 'get'+capitalizedname, fnget )

    def fnset(instance, value):
        instance.validate(name, value)
        setattr(instance, '_' + name, value)

    fnset = getattr(cls, 'set'+capitalizedname, fnset )

    setattr( cls, name, property(fnget, fnset) )


def _ConvertProperties(cls):

    props = dict()
    setattr(cls, '__properties', props)

    def getproperties(cls, props):
        for base in cls.__bases__:
            if hasattr(base, '__properties'):
                for name, prop in base.__properties.iteritems():
                    #if name in props:
                    #    print >>sys.stderr, "Property %s::%s overloads property %s::%s" % (cls.__name__, name, base.)
                    if not name in props:
                        props[name] = prop
            getproperties(base, props)

        for name, prop in cls.__dict__.iteritems():
            if isinstance(prop, Property):
                props[name] = prop

    getproperties(cls, props)

    for name, value in props.iteritems():
        if value.getName() is None:
            value.setName(name)

        _ConvertProperty(cls, name)

    def getPropertyInfo(instance, key):
        return getattr(instance, '__properties')[key]

    setattr(cls, 'getPropertyInfo', getPropertyInfo)


def _WrapNew(cls):

    infos = getattr(cls, '__properties')
    oldfn = getattr(cls, '__new__')

    def __new__(cls, *k, **kw):
        o = oldfn(cls, *k, **kw)

        for name, value in infos.iteritems():
            setattr(o, '_' + name, value.getDefault() )

        return o

    setattr(cls, '__new__', staticmethod(__new__))


def _WrapValidate(cls):

    def validate(instance, name, value):
        capitalizedname = _CapitalizeName(name)
        fn = getattr(instance, 'validate'+capitalizedname, None)
        if fn is not None:
            fn(value)

        infos = getattr(cls, '__properties')
        property = infos.get(name, None)

        if property is None:
            raise PropertyValidateError("No such property %s" % name)

        property.validate(value)

    setattr(cls, 'validate', validate)


def _WrapIterators(cls):

    """
    class PropertiesProxy(object):
        def __init__(self, owner):
            self.owner = owner

        def iteritems(instance):
            for name in getattr(cls, '__properties').iterkeys():
                prop = getattr(cls, name)
                yield (name, prop.fget(instance))

    setattr(cls, 'Properties', PropertiesProxy())
    """

    def iteritems(instance):
        for name in getattr(cls, '__properties').iterkeys():
            prop = getattr(cls, name)
            yield (name, prop.fget(instance))

    def iterkeys(instance):
        return getattr(cls, '__properties').iterkeys()

    def length(instance):
        return len(getattr(cls, '__properties'))

    def contains(instance, key):
        return key in getattr(cls, '__properties')

    setattr(cls, '__len__', length)
    setattr(cls, '__iter__', iteritems)
    setattr(cls, 'iteritems', iteritems)
    setattr(cls, 'iterkeys', iterkeys)
    setattr(cls, '__contains__', contains)

# **************************************************************************************************


def WrapPropertyClass(cls):
    """ A decorator that takes instances of Property and creates python properties from them
    The meta info for each property is retrieved by GetProperty.
    """

    _ConvertProperties(cls)
    _WrapNew(cls)
    _WrapIterators(cls)
    _WrapValidate(cls)

    cls.__is_property_class = True
    return cls


class property_class(object):
    """ A decorator that takes instances of Property and creates python properties from them
    The meta info for each property is retrieved by GetProperty.
    """

    def __call__(self, *k, **kw):
        return WrapPropertyClass(k[0])



