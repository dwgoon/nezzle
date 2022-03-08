from qtpy.QtCore import QRectF
from qtpy.QtWidgets import QGraphicsItem

from nezzle.graphics import PainterOptionItem


class BaseNode(PainterOptionItem):

    ITEM_TYPE = 'NODE'

    def __init__(self, iden, width, height, *args, **kwargs):
        super().__init__(iden, *args, **kwargs)
        self._iden = iden
        self._brect = QRectF()
        self._edges = []

        self._attr.set_trigger('WIDTH', self._trigger_set_width)
        self._attr.set_trigger('HEIGHT', self._trigger_set_height)

        self.width = width
        self.height = height

        # if pos:
        # #    self.setPos(pos)
        #     self._attr["POS_X"] = pos.x()
        #     self._attr["POS_Y"] = pos.y()

        self.setFlags(QGraphicsItem.ItemIsSelectable
                      | QGraphicsItem.ItemIsMovable
                      | QGraphicsItem.ItemIsFocusable
                      | QGraphicsItem.ItemSendsGeometryChanges)

    # end of def __init__

    def __str__(self):
        return 'Node(%s)'%(self.name)

    @property
    def edges(self):
        return self._edges

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

    def gather_children(self):
        children = super().gather_children()
        for edge in self.edges:
            for child in edge.childItems():
                if child not in children:
                    children.append(child)

        return children

    def boundingRect(self):
        rect = QRectF(self._brect)
        if self._pen:
            wp = self._pen.width()
            rect.adjust(-wp, -wp, +wp, +wp)

        return rect

    def update(self, *args, **kwargs):
        for edge in self._edges:
            edge.update()
        self._invalidate()
        return super().update(*args, **kwargs)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.update()
        elif change == QGraphicsItem.ItemSelectedHasChanged:
            self.update()

        return super().itemChange(change, value)

    def has_edge(self, edge):
        return edge in self._edges

    def add_edge(self, edge):
        if self.has_edge(edge):
            return
        self._edges.append(edge)

    def remove_edge(self, edge):
        if edge in self._edges:
            self._edges.remove(edge)

    def copy(self):
        return self.from_dict(self.to_dict())

    def _trigger_set_width(self, key, value):
        self._width = value
        self._brect.setX(-value / 2)
        self._brect.setWidth(value)
        self.update()
        return value

    def _trigger_set_height(self, key, value):
        self._height = value
        self._brect.setY(-value / 2)
        self._brect.setHeight(value)
        self.update()
        return value

    @classmethod
    def from_dict(cls, attr):
        iden = attr.pop('ID')
        width = attr.pop('WIDTH')
        height = attr.pop('HEIGHT')
        zvalue = attr.pop('ZVALUE')

        obj = cls(iden=iden, width=width, height=height)
        obj.setZValue(zvalue)
        obj._attr.update(attr)

        return obj
