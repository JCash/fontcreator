
# Very much influenced by the Django properties

class PropertyValidateError(Exception):
    pass

class Property(object):
    
    @staticmethod
    def _validate_empty(value):
        if hasattr(value, '__len__') and len(value) == 0:
            raise PropertyValidateError('The value must not be empty')
    
    def __init__(self, default=None, name=None, verbose_name=None, help='', read_only=False, show=False, allow_empty=False, validators=None):
        assert default is not None, 'You must specify a default value'
        
        self.default = default
        
        self.name = name if name is not None else verbose_name
        self.verbose_name = verbose_name if verbose_name is not None else name
        #assert self.name is not None, 'You must specify a name'
        
        self.help = help
        self.show = show
        self.read_only = read_only
        self.validators = validators if validators else []
        
        if not allow_empty:
            self.validators.append(Property._validate_empty)

    def __repr__(self):
        return "%s( default=%s, name='%s', verbose_name='%s', help='%s', read_only=%s, show=%s )" % ( self.__class__.__name__,
                                                                                                    str(self.getDefault()),
                                                                                                    self.getName(),
                                                                                                    self.getVerboseName(),
                                                                                                    self.getHelp(),
                                                                                                    str(self.getReadOnly()),
                                                                                                    str(self.getShow()) )
            
    def validate(self, value):
        for fn in self.validators:
            fn(value)
    
    def setName(self, name):
        self.name = name
        if self.verbose_name is None:
            self.verbose_name = name
        
    def getName(self):
        return self.name
    
    def getVerboseName(self):
        return self.verbose_name
    
    def getDefault(self):
        return self.default
    
    def getHelp(self):
        return self.help

    def getReadOnly(self):
        return self.read_only

    def getShow(self):
        return self.show
    
    
            
class NumericProperty(Property):
    
    def __init__(self, default=0, min=0, max=100, step=None, wrap=False, **kw):
        super(NumericProperty, self).__init__(default, **kw)
        
        self.min = min
        self.max = max
        self.step = step
        self.wrap = wrap
        
        def _validate_range(value):
            if value < self.min or value > self.max:
                raise PropertyValidateError('Value not in range [%s, %s]: %s' % (str(self.min), str(self.max), str(value)))
            # TODO: Check the steps
            
        self.validators.append( _validate_range )

    def getStep(self):
        return self.step

    def getMin(self):
        return self.min

    def getMax(self):
        return self.max

    def getRange(self):
        return (self.min, self.max)

    def getWrap(self):
        return self.wrap
    

class IntProperty(NumericProperty):
    def __init__(self, default=0, **kw):
        super(IntProperty, self).__init__(default, **kw)
        assert isinstance(self.min, int)
        assert isinstance(self.max, int)
        assert self.step is None or isinstance(self.step, int)


class FloatProperty(NumericProperty):
    def __init__(self, default=0, **kw):
        super(FloatProperty, self).__init__(default, **kw)
        assert isinstance(self.min, (int, float))
        assert isinstance(self.max, (int, float))
        assert self.step is None or isinstance(self.step, (int,float))
        
        self.default = float(self.default)
        self.min = float(self.min)
        self.max = float(self.max)
        self.step = None if self.step is None else float(self.step)

                    
class ColorProperty(Property):
    def __init__(self, default=(255,255,255), **kw):
        super(ColorProperty, self).__init__(default, **kw)
        
        def _validate_range(value):
            if min(value) < 0 or max(value) > 255:
                raise PropertyValidateError('Value not in range [0, 255]: %s' % (str(value)))
            
        self.validators.append( _validate_range )


class AngleProperty(NumericProperty):
    def __init__(self, default=0, **kw):
        kw['min'] = 0
        kw['max'] = 360
        kw['wrap'] = True
        super(AngleProperty, self).__init__(default, **kw)


class OpacityProperty(NumericProperty):
    def __init__(self, default=100, **kw):
        kw['min'] = 0
        kw['max'] = 100
        super(OpacityProperty, self).__init__(default, **kw)


class Size1DProperty(NumericProperty):
    def __init__(self, default=1, **kw):
        kw['min'] = 0
        kw['max'] = 100
        super(Size1DProperty, self).__init__(default, **kw)


class StringProperty(Property):
    def __init__(self, default='', **kw):
        super(StringProperty, self).__init__(default, **kw)
        

class FileProperty(Property):
    def __init__(self, default='', **kw):
        super(FileProperty, self).__init__(default, **kw)



        