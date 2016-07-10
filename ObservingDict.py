class ObservingDict(dict):
    """
    Send all changes to an observer.
    """

    def __init__(self, value):
        dict.__init__(value)
        self.observers = []

    def add_observer(self, observer):
        """
        All changes to this dictionary will trigger calls to observer methods
        """
        self.observers.append(observer)

    def call_observers(self, key):
        for observer in self.observers:
            observer.dict_changed(self, key)

    def __setitem__(self, key, value):
        """
        Intercept the l[key]=value operations.
        Also covers slice assignment.
        """
        dict.__setitem__(self, key, value)
        self.call_observers(key)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.call_observers(key)

    def clear(self):
        dict.clear(self)
        self.call_observers(None)

    # def update(self, E, **F):
    #     dict.update(self, E, F)
    #     self.call_observers(None)

    def setdefault(self, key, value=None):
        dict.setdefault(self, key, value)
        self.call_observers(key)
        return value

    def pop(self, k, x=None):
        if k in self:
            dict.pop(self, k, x)
            self.call_observers(k)
            return value
        else:
            return x

    def popitem(self):
        key, value = dict.popitem(self)
        self.call_observers(key)
        return key, value
