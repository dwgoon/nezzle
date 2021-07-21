"""
Created on Wed Feb  1 19:29:49 2017

@author: dwlee
"""

import math
from sys import argv
import numpy as np

from qtpy.QtWidgets import QApplication
from qtpy.QtCore import QPoint, QPointF, Qt
from qtpy.QtCore import QRectF
from qtpy.QtCore import QLineF

from qtpy.QtGui import QTransform
from qtpy.QtGui import QColor, QPainterPath, QPainter
from qtpy.QtGui import QPolygonF
from qtpy.QtGui import QPen
from qtpy.QtWidgets import QGraphicsScene, QGraphicsView
from qtpy.QtWidgets import QGraphicsItem

from nezzle.utils import dist
from nezzle.utils import dot
from nezzle.utils import length
from nezzle.utils import internal_division
from nezzle.utils import rotate
from nezzle.graphics import quadbezier
from nezzle.graphics.mixins import Lockable
from nezzle.graphics.mappableitem import PainterOptionItem
from nezzle.graphics import HeaderClassFactory


# class BaseLink(PainterOptionItem):
#
#     ITEM_TYPE = 'LINK'
#
#     def __init__(self, iden, source, target, *args,
#                  header=None, width=2, **kwargs):
#
#         super().__init__(iden, *args, **kwargs)
#         self._source = source
#         self._target = target
#         self.source.add_link(self)
#         self.target.add_link(self)
#
#         self._angle_header = None
#         self._pos_header = QPointF()
#         self._path_paint = QPainterPath()
#
#         self.setFlags(QGraphicsItem.ItemIsSelectable
#                       | QGraphicsItem.ItemIsFocusable
#                       | QGraphicsItem.ItemSendsGeometryChanges)
#
#         self._attr.set_trigger('WIDTH', self._trigger_set_width, when='set')
#         self._attr.set('WIDTH', width, trigger=False)
#         self._width = width
#
#         self._attr.set_trigger('HEADER', self._trigger_set_header, when='set')
#         self._attr.set('HEADER', header, trigger=False)
#         self._header = header
#         if header:
#             self._header.parent = self
#
#         self._initialize()
#
#     def __str__(self):
#         return 'Link(%s, %s)'%(self.source.name, self.target.name)
#
#     @property
#     def width(self):
#         return self._attr['WIDTH']
#
#     @width.setter
#     def width(self, val):
#         self._attr['WIDTH'] = val
#
#     def set_width(self, val, header=True):
#         if header:
#             w = self.width
#             scale = val/w
#             self.header.width *= scale
#             self.header.height *= scale
#
#         self._width = val
#         self._attr.set('WIDTH', val, trigger=False)
#         self.update()
#
#     def _trigger_set_width(self, key, value):
#         self.set_width(value)
#         return value
#
#     def _trigger_set_header(self, key, value):
#         self._header = value
#         self._header.parent = self
#         self.update()
#         return value
#
#     @property
#     def header(self):
#         return self._attr['HEADER']
#
#     @header.setter
#     def header(self, obj):
#         self._attr['HEADER'] = obj
#
#     # Read-only properties
#     @property
#     def source(self):
#         return self._source
#
#     @property
#     def target(self):
#         return self._target
#
#     @property
#     def pos_src(self):
#         """
#         The position of source relative to its parent lins
#         """
#         return self._source.pos() - self.pos()
#
#     @property
#     def pos_tgt(self):
#         """
#         The position of target relative to its parent lins
#         """
#         return self._target.pos() - self.pos()
#
#     @property
#     def pos_header(self):
#         return self._pos_header
#
#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             """
#             The following check prevents this item being selected
#             simply according to boundingRect.
#             """
#             pos = event.pos() - self.pos()
#             if self._path_paint.contains(pos):
#                 self.setSelected(True)
#                 event.accept()
#         else:
#             event.reject()
#
#     def boundingRect(self):
#         rect = self._path_paint.boundingRect()
#         if self._pen:
#             wp = self._pen.width()
#             rect.adjust(-wp, -wp, +wp, +wp)
#
#         return rect
#
#     def shape(self):
#         return self._path_paint
#
#     def itemChange(self, change, value):
#         return super().itemChange(change, value)
#
#     def is_node_selected(self):
#         return self.source.isSelected() or self.target.isSelected()
#
#     # def are_nodes_overlapped(self):
#     #     v = self.pos_tgt - self.pos_src
#     #     angle_rad = np.arccos(v.x() / length(v))
#     #     radius_src = self.source.calculate_radius(angle_rad)
#     #
#     #     v *= -1
#     #     angle_rad = np.arccos(v.x() / length(v))
#     #     radius_tgt = self.target.calculate_radius(angle_rad)
#     #
#     #     return dist(self.pos_src, self.pos_tgt) <= radius_src + radius_tgt
#
#     def _identify_pos(self):
#         m = internal_division(self.source.pos(), self.target.pos(), 0.5, 0.5)
#         self.setPos(m)
#
#     def _create_header_path(self):
#         points = self.header.calculate_points(self.pos_header,
#                                               self.width,
#                                               self._angle_header)
#         path = QPainterPath()
#         path.moveTo(points[0])
#         for pt in points[1:]:
#             path.lineTo(pt)
#
#         self._path_header = path
#
#     def update(self, *args, **kwargs):
#         self._create_path()
#         self._invalidate()
#         return super().update(*args, **kwargs)
#
#     def paint(self, painter, option, widget):
#         super().paint(painter, option, widget)
#         #painter.drawPath(self._path_paint)
#
#     def to_dict(self):
#         attr = super().to_dict()
#         attr['ID_SOURCE'] = self.source.iden
#         attr['ID_TARGET'] = self.target.iden
#         if self.header:
#             attr['HEADER'] = self.header.to_dict()
#
#         return attr
#
#     @classmethod
#     def from_dict(cls, attr, source, target):
#         iden = attr.pop('ID')
#         width = attr.pop('WIDTH')
#
#         obj = cls(iden, source, target, width=width)
#
#         if 'HEADER' in attr:
#             attr_header = attr.pop('HEADER')
#             HeaderClass = HeaderClassFactory.create(attr_header['TYPE'])
#             header = HeaderClass.from_dict(attr_header)
#             obj.header = header
#
#         obj._attr.update(attr)
#         return obj
#
#     def copy(self, source=None, target=None):
#         if not source:
#             source = self.source
#
#         if not target:
#             target = self.target
#
#         return self.from_dict(self.to_dict(), source, target)
#
#     def _initialize(self):
#         pass
#
#     def _create_path(self):
#         raise NotImplementedError()
#
#     def _identify_header(self):
#         raise NotImplementedError()
#
#     def _identify_header_pos(self):
#         raise NotImplementedError()
#
#     def _calculate_header_angle(self):
#         raise NotImplementedError()


class BaseLink(PainterOptionItem):

    ITEM_TYPE = 'LINK'

    def __init__(self, iden, *args,
                 header=None, width=2, **kwargs):

        super().__init__(iden, *args, **kwargs)

        self._pos_header = QPointF()
        self._path_paint = QPainterPath()

        self.setFlags(QGraphicsItem.ItemIsSelectable
                      | QGraphicsItem.ItemIsFocusable
                      | QGraphicsItem.ItemSendsGeometryChanges)

        self._attr.set_trigger('WIDTH', self._trigger_set_width, when='set')
        self._attr.set('WIDTH', width, trigger=False)
        self._width = width

        self._attr.set_trigger('HEADER', self._trigger_set_header, when='set')
        self._attr.set('HEADER', header, trigger=False)

        self._header = header
        if header:
            self._header.parent = self
            self._angle_header = None  # degrees

        self._initialize()

    def __str__(self):
        return 'Link(%s)'%(self._iden)

    @property
    def width(self):
        return self._attr['WIDTH']

    @width.setter
    def width(self, val):
        self._attr['WIDTH'] = val

    def set_width(self, val, header=True):
        if header and self.header:
            self.header.set_size_from_link(link_width=val)
            # w = self.width
            # scale = val/w
            # self.header.width *= scale
            # self.header.height *= scale

        self._width = val
        self._attr.set('WIDTH', val, trigger=False)
        self.update()

    def _trigger_set_width(self, key, value):
        self.set_width(value)
        return value

    def _trigger_set_header(self, key, value):
        self._header = value
        if self._header:
            self._header.parent = self

        self._attr.set('HEADER', value, trigger=False)
        self.update()

        return value

    @property
    def header(self):
        return self._attr['HEADER']

    @header.setter
    def header(self, obj):
        self._attr['HEADER'] = obj

    @property
    def pos_header(self):
        return self._pos_header

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            """
            The following check prevents this item being selected
            simply according to boundingRect.
            """

            pos = event.pos() - self.pos()
            if self._path_paint.contains(pos):
                print("[MOUSE EVENT] Selected!")
                self.setSelected(True)
                event.accept()
        else:
            event.reject()

    def boundingRect(self):
        rect = self._path_paint.boundingRect()
        if self._pen:
            wp = self._pen.width()
            rect.adjust(-wp, -wp, +wp, +wp)

        return rect

    def shape(self):
        return self._path_paint

    def itemChange(self, change, value):
        return super().itemChange(change, value)

    def _create_header_path(self):
        points = self.header.calculate_points(self.pos_header,
                                              self.width,
                                              self._angle_header)
        path = QPainterPath()
        path.moveTo(points[0])
        for pt in points[1:]:
            path.lineTo(pt)

        self._path_header = path

    def update(self, *args, **kwargs):
        self._create_path()
        self._invalidate()
        return super().update(*args, **kwargs)

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        painter.drawPath(self._path_paint)

    def to_dict(self):
        attr = super().to_dict()
        if self.header:
            attr['HEADER'] = self.header.to_dict()

        return attr

    @classmethod
    def header_from_dict(cls, attr):
        if 'HEADER' in attr:
            attr_header = attr.pop('HEADER')
            if attr_header:
                HeaderClass = HeaderClassFactory.create(attr_header['TYPE'])
                header = HeaderClass.from_dict(attr_header)
                return header
        return None


    @classmethod
    def from_dict(cls, attr):
        raise NotImplementedError()

    def copy(self):
        return self.from_dict(self.to_dict())

    def _initialize(self):
        pass

    def _identify_pos(self):
        raise NotImplementedError()

    def _create_path(self):
        raise NotImplementedError()

    def _identify_header(self):
        raise NotImplementedError()

    def is_movable(self):
        return False

    # def _identify_header_pos(self):
    #     raise NotImplementedError()
    #
    # def _calculate_header_angle(self):
    #     raise NotImplementedError()


class TwoNodeLink(BaseLink):

    ITEM_TYPE = 'TWO_NODE_LINK'

    def __init__(self, iden, source, target, *args, **kwargs):

        self._source = source
        self._target = target
        self.source.add_link(self)
        self.target.add_link(self)
        super().__init__(iden, *args, **kwargs)

    def __str__(self):
        return 'Link(%s, %s)'%(self.source.name, self.target.name)

    # Read-only properties
    @property
    def source(self):
        return self._source

    @property
    def target(self):
        return self._target

    @property
    def pos_src(self):
        """
        The position of source relative to its parent lins
        """
        return self._source.pos() - self.pos()

    @property
    def pos_tgt(self):
        """
        The position of target relative to its parent lins
        """
        return self._target.pos() - self.pos()

    def is_node_selected(self):
        return self.source.isSelected() or self.target.isSelected()

    def are_nodes_close(self):
        """Decide whether the two nodes are overlapped
        to show the graphics of lins appropriately.
        """
        v = self.pos_tgt - self.pos_src
        angle_rad = np.arccos(v.x() / length(v))
        radius_src = self.source.calculate_radius(angle_rad)

        v *= -1
        angle_rad = np.arccos(v.x() / length(v))
        radius_tgt = self.target.calculate_radius(angle_rad)

        return dist(self.pos_src, self.pos_tgt) < radius_src + radius_tgt

    def _identify_pos(self):
        m = internal_division(self.source.pos(), self.target.pos(), 0.5, 0.5)
        self.setPos(m)

    # def _create_header_path(self):
    #     points = self.header.calculate_points(self.pos_header,
    #                                           self.width,
    #                                           self._angle_header)
    #     path = QPainterPath()
    #     path.moveTo(points[0])
    #     for pt in points[1:]:
    #         path.lineTo(pt)
    #
    #     self._path_header = path

    def to_dict(self):
        attr = super().to_dict()
        attr['ID_SOURCE'] = self.source.iden
        attr['ID_TARGET'] = self.target.iden
        return attr

    @classmethod
    def from_dict(cls, attr, source, target):
        iden = attr.pop('ID')
        width = attr.pop('WIDTH')

        obj = cls(iden, source, target, width=width)
        obj.header = cls.header_from_dict(attr)

        attr['ID_SOURCE'] = source.iden
        attr['ID_TARGET'] = target.iden
        obj._attr.update(attr)
        return obj

    def copy(self, source=None, target=None):
        if not source:
            source = self.source

        if not target:
            target = self.target

        return self.from_dict(self.to_dict(), source, target)
