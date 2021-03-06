from qtpy.QtCore import QObject
from nezzle.constants import Lock


class SystemState(QObject):

    def __init__(self):

        self._lock_state = 0

    @property
    def lock_state(self):
        return self._lock_state

    def is_locked(self, item_type):

        if isinstance(item_type, str):
            item_type = item_type.casefold()
            if item_type.endswith('_node'):
                lock = Lock.NODES
            elif item_type.endswith('_edge'):
                lock = Lock.EDGES
            elif item_type.endswith('_label'):
                lock = Lock.LABELS
        elif isinstance(item_type, int):
            lock = item_type
        else:
            raise TypeError("item_should be a str or int, not %s"%item_type)

        return (self.lock_state & lock) != 0

    def set_locked(self, lock, b):

        if b is True:
            self._lock_state |= lock
        else:
            self._lock_state &= (~lock)

# end of class SystemState


system_state = SystemState()

def get_system_state():
    global system_state
    return system_state