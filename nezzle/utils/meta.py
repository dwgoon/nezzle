# -*- coding: utf-8 -*-

def Singleton(_class):
    class __Singleton(_class):
        __instance = None

        def __new__(cls, *args, **kwargs):
            if cls.__instance is None:
                cls.__instance = super().__new__(cls, *args, **kwargs)

                # Creation and initialization of '__initialized'
                cls.__instance.__initialized = False
            # end of if
            return cls.__instance

        def __init__(self, *args, **kwargs):
            if self.__initialized:
                return

            super().__init__(*args, **kwargs)
            self.__initialized = True

        def __repr__(self):
            return '<{0} Singleton object at {1}>'.format(
                _class.__name__, hex(id(self)))

        def __str__(self):
            return super().__str__()
    # end of def class

    __Singleton.__name__ = _class.__name__
    return __Singleton
