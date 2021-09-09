from qtpy.QtCore import QEvent
from qtpy.QtCore import QObject
from qtpy.QtWidgets import QGraphicsItem

from nezzle.systemstate import get_system_state


def Lockable(__class):

    class __Lockable(__class):

        def mousePressEvent(self, event):
            ss = get_system_state()
            if ss.is_locked(self.ITEM_TYPE):
                # event.ignore()
                event.ignore()
            else:
                return super().mousePressEvent(event)

        def itemChange(self, change, value):
            if change == QGraphicsItem.ItemSelectedChange:
                ss = get_system_state()
                if ss.is_locked(self.ITEM_TYPE):
                    return super().itemChange(change, False)

            return super().itemChange(change, value)

        def __repr__(self):
            return '<Lockable %s object at %s>'\
                   %(self.__class__.__name__, hex(id(self)))

        # def __str__(self):
        #     return super().__str__()

    __Lockable.__name__ = __class.__name__
    return __Lockable