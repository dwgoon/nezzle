# -*- coding: utf-8 -*-

from qtpy.QtCore import QObject
from nezzle.constants import Lock

class SystemState(QObject):

    def __init__(self):

        self._lockState = 0

    @property
    def lock_state(self):
        return self._lockState

    def is_locked(self, item_type):

        if isinstance(item_type, str):
            item_type = item_type.casefold()
            if item_type.endswith('_node'):
                lock = Lock.NODES
            elif item_type.endswith('_link'):
                lock = Lock.LINKS
            elif item_type.endswith('_label'):
                lock = Lock.LABELS
        elif isinstance(item_type, int):
            lock = item_type
        else:
            raise TypeError("item_should be a str or int, not %s"%item_type)

        return (self.lock_state & lock) != 0

    def set_locked(self, lock, b):

        if b is True:
            self._lockState |= lock
        else:
            self._lockState &= (~lock)

# end of class SystemState


system_state = SystemState()

def get_system_state():
    global system_state
    return system_state