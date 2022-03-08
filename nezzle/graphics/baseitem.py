"""
[REF]
- http://stackoverflow.com/a/11604577
- http://stackoverflow.com/a/12144823
"""

import sys

if sys.version_info.minor > 9:
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtWidgets import QGraphicsItem
from qtpy.QtWidgets import QStyle
from qtpy.QtGui import QColor
from qtpy.QtGui import QPen

from nezzle.graphics.attributemapper import AttributeMapper
from nezzle.utils import TriggerDict


class MappableGraphicsItemMeta(type(QGraphicsItem),
                               type(MutableMapping)):

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)


class MappableItem(MutableMapping):
    def __init__(self, iden, *args, name=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._attr = TriggerDict()
        self._attr.set_trigger('ID', self._trigger_set_iden)
        self._attr.set_trigger('NAME', self._trigger_set_name)
        self._attr['ID'] = iden
        self._attr['NAME'] = name if name else iden

    @property
    def iden(self):
        return self._attr['ID']

    @iden.setter
    def iden(self, val):
        self._attr['ID'] = val

    @property
    def name(self):
        return self._attr['NAME']

    @name.setter
    def name(self, val):
        self._attr['NAME'] = val

    def _trigger_set_iden(self, key, value):
        self._iden = value
        return value

    def _trigger_set_name(self, key, value):
        self._name = value
        return value

    def __getitem__(self, key):
        return self._attr[key]

    def __setitem__(self, key, value):
        self._attr[key] = value

    def __delitem__(self, key):
        del self._attr[key]

    def __iter__(self):
        return iter(self._attr)

    def __len__(self):
        return len(self._attr)

    def __str__(self):
        return str(self._attr)

    def keys(self):
        return self._attr.keys()

    def values(self):
        return self._attr.values()

    def to_dict(self):
        return dict(self._attr)

    @classmethod
    def from_dict(cls, attr):
        obj = cls()
        for key, value in attr.items():
            obj[key] = value

        return obj


class MappableGraphicsItem(MappableItem,
                           QGraphicsItem,
                           metaclass=MappableGraphicsItemMeta):
    """
    A simple mappable class, which handles multiple attributes with
    its own attribute dictionary.
    """
    ITEM_TYPE = 'MAPPABLE_GRAPHICS_ITEM'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._attr['ITEM_TYPE'] = self.ITEM_TYPE

    def to_dict(self):
        attr = super().to_dict()
        attr["ZVALUE"] = self.zValue()
        return attr


class Movable(object):
    def is_movable(self):
        return False


class GeometryChangeItem(MappableGraphicsItem,
                         Movable):

    ITEM_TYPE = 'GEOMETRY_CHANGE_ITEM'

    def __init__(self, *args, **kwargs):
        pos = None
        if "pos" in kwargs:
            pos = kwargs.pop("pos")

        super().__init__(*args, **kwargs)

        self._attr.set_trigger('POS_X', self._trigger_set_x)
        self._attr.set_trigger('POS_Y', self._trigger_set_y)

        if pos:
            self._attr['POS_X'] = pos.x()
            self._attr['POS_Y'] = pos.y()
            self._attr['_OLD_POS'] = QPointF(pos)
        else:
            self._attr['POS_X'] = 0
            self._attr['POS_Y'] = 0
            self._attr['_OLD_POS'] = QPointF(0, 0)

        self.setFlags(QGraphicsItem.ItemIsMovable
                      | QGraphicsItem.ItemSendsGeometryChanges)

    def _trigger_set_x(self, key, value):
        self.setX(value)
        return value

    def _trigger_set_y(self, key, value):
        self.setY(value)
        return value

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            pos = value
            self._attr.set('POS_X', pos.x(), trigger=False)
            self._attr.set('POS_Y', pos.y(), trigger=False)

        return super().itemChange(change, value)


    def gather_children(self):
        children = self.childItems()
        return children

    def update_children_old_positions(self):
        children = self.gather_children()
        if children:
            for child in children:
                if child.is_movable():
                    child["_OLD_POS"] = child.pos()


class PainterOptionItem(GeometryChangeItem):

    ITEM_TYPE = 'PAINTER_OPTION_ITEM'

    _attr_map = AttributeMapper()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._attr.set_trigger("BORDER_WIDTH", self._trigger_set_border_width)
        self._attr.set_trigger('BORDER_COLOR', self._trigger_set_border_color)
        self._attr.set_trigger('BORDER_JOIN', self._trigger_set_border_join)
        self._attr.set_trigger('BORDER_LINE', self._trigger_set_border_line)
        self._attr.set_trigger("FILL_COLOR", self._trigger_set_fill_color)

        self._pen = QPen()
        self._pen.setBrush(Qt.transparent)
        self._pen.setJoinStyle(Qt.MiterJoin)

        self._color = QColor()

    @property
    def attr_map(self):
        return __class__._attr_map

    def _invalidate(self):
        if self.scene():
            self.scene().invalidate()

    def _trigger_set_border_width(self, key, value):
        width = int(value)
        self._pen.setWidth(width)
        self._invalidate()
        return width

    def _trigger_set_border_color(self, key, value):
        color = QColor(value)
        self._pen.setColor(color)
        self._invalidate()
        return color.name(QColor.HexArgb)

    def _trigger_set_border_join(self, key, value):
        if isinstance(value, str):
            join_style = self.attr_map.to_qt('BORDER_JOIN', value)
            self._pen.setJoinStyle(join_style)
            return value
        elif isinstance(value, Qt.JoinStyle):
            self._pen.setJoinStyle(value)
            return self.attr_map.to_str('BORDER_JOIN', value)
        else:
            err_msg = "It is not an border join option: %s"%(value)
            raise AttributeError(err_msg)

        self._invalidate()

        return value

    def _trigger_set_border_line(self, key, value):
        if isinstance(value, str):
            line_type = self.attr_map.to_qt('BORDER_LINE', value)
            self._pen.setStyle(line_type)
            return value
        elif isinstance(value, Qt.PenStyle):
            self._pen.setStyle(value)
            return self.attr_map.to_str('BORDER_LINE', value)
        else:
            err_msg = "It is not an border line type: %s"%(value)
            raise AttributeError(err_msg)

        self._invalidate()

        return value

    def _trigger_set_fill_color(self, key, value):
        self._color = QColor(value)
        self._invalidate()
        return self._color.name(QColor.HexArgb)

    def _set_border_options(self, painter):
        painter.setPen(self._pen)

    def _set_fill_options(self, painter):
        painter.setBrush(self._color)

    def _set_painter_options(self, painter):
        painter.setPen(Qt.NoPen)
        self._set_border_options(painter)
        self._set_fill_options(painter)

    def paint(self, painter, option, widget):

        painter.setClipRect(option.exposedRect)

        if option.state & QStyle.State_Selected:
            pen = QPen(self._pen)
            pen.setBrush(Qt.green)
            painter.setPen(pen)
            painter.setBrush(Qt.green)
        else:
            self._set_painter_options(painter)



