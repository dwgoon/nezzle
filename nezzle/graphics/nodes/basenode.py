from qtpy.QtCore import QRectF
from qtpy.QtWidgets import QGraphicsItem

from nezzle.graphics import PainterOptionItem


class BaseNode(PainterOptionItem):

    ITEM_TYPE = 'NODE'

    def __init__(self, iden, width, height, *args, pos=None, **kwargs):
        super().__init__(iden, *args, **kwargs)
        self._iden = iden
        self._rect = QRectF()
        self._links = []

        self._attr.set_trigger('WIDTH', self._trigger_set_width)
        self._attr.set_trigger('HEIGHT', self._trigger_set_height)

        self.width = width
        self.height = height

        if pos:
            self.setPos(pos)

        self.setFlags(QGraphicsItem.ItemIsSelectable
                      | QGraphicsItem.ItemIsMovable
                      | QGraphicsItem.ItemIsFocusable
                      | QGraphicsItem.ItemSendsGeometryChanges)

    # end of def __init__

    def __str__(self):
        return 'Node(%s)'%(self.name)

    @property
    def links(self):
        return self._links

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, val):
        self._attr['WIDTH'] = val

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, val):
        self._attr['HEIGHT'] = val

    def is_movable(self):
        return True

    def boundingRect(self):
        rect = QRectF(self._rect)
        if self._pen:
            wp = self._pen.width()
            rect.adjust(-wp, -wp, +wp, +wp)

        return rect

    def update(self, *args, **kwargs):
        for link in self._links:
            link.update()
        self._invalidate()
        return super().update(*args, **kwargs)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.update()

        return super().itemChange(change, value)

    def add_link(self, link):
        self._links.append(link)

    def remove_link(self, link):
        if link in self._links:
            self._links.remove(link)

    def copy(self):
        return self.from_dict(self.to_dict())

    def _trigger_set_width(self, key, value):
        self._width = value
        self._rect.setX(-value/2)
        self._rect.setWidth(value)
        self.update()
        return value

    def _trigger_set_height(self, key, value):
        self._height = value
        self._rect.setY(-value/2)
        self._rect.setHeight(value)
        self.update()
        return value

    @classmethod
    def from_dict(cls, attr):
        iden = attr.pop('ID')
        width = attr.pop('WIDTH')
        height = attr.pop('HEIGHT')

        obj = cls(iden=iden, width=width, height=height)
        obj._attr.update(attr)

        return obj