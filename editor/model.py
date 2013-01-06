from fontinfo import SFontInfo


class Model(object):
    def __init__(self, options):
        self.options = options
        self.fontinfo = SFontInfo(options)
