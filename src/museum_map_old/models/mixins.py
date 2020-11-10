class AttributesMixin(object):

    def __contains__(self, key):
        return self.attributes and key in self.attributes

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        if self.attributes:
            self.attributes[key] = value
        else:
            self.attributes = {key: value}
