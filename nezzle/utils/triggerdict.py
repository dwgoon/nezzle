
from collections import UserDict


class TriggerDict(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._triggers_set = dict()
        self._triggers_get = dict()

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def set_trigger(self, key, func, when='set'):
        if when == 'set':
            self._triggers_set[key] = func
        elif when == 'get':
            self._triggers_get[key] = func
        else:
            ValueError("You should choose 'set' or 'get' "
                       "for the timing of trigger, not '%s.'"%(when))

    def set(self, key, value, trigger=True):
        if key not in self._triggers_set or not trigger:
            self.data[key] = value
            return

        if trigger:
            func = self._triggers_set[key]
            self.data[key] = func(key, value)

    def get(self, key, default=None, trigger=True):
        if key not in self._triggers_get or not trigger:
            return self.data.get(key, default)

        if trigger:
            func = self._triggers_get[key]
            value = self.data.get(key, default)
            return func(key, value)

