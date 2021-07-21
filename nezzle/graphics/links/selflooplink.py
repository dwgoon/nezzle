# -*- coding: utf-8 -*-

import math

from qtpy.QtCore import Qt
from qtpy.QtCore import QRectF
from qtpy.QtGui import QPainterPath
from qtpy.QtWidgets import QGraphicsItem

from qtpy.QtGui import QColor
from qtpy.QtGui import QBrush

from .baselink import BaseLink
from nezzle.graphics import HeaderClassFactory
from nezzle.graphics.mixins import Lockable


@Lockable
class SelfloopLink(BaseLink):

    ITEM_TYPE = 'SELFLOOP_LINK'

    def __init__(self, iden, node, *args, **kwargs):
        self._node = node
        self._radius_core = None
        self._angle_offset = None
        self._angle_sweep = None
        self._angle_begin = None
        super().__init__(iden, *args, **kwargs)
        # self._attr.set_trigger('RADIUS_CORE',
        #                        self._trigger_set_radius_core, when='set')

        self.node.add_link(self)

    @property
    def node(self):
        return self._node

    # @property
    # def radius_core(self):
    #     return self._attr['RADIUS_CORE']

    # def _trigger_set_radius_core(self, key, value):
    #     self._radius_core = value
    #     return value

    # @property
    # def angle_offset(self):
    #     return self._attr['ANGLE_OFFSET']

    # def _trigger_set_angle_offset(self, key, value):
    #     self._angle_offset = value
    #     return value

    def _initialize(self):
        self._create_path()

    def _identify_pos(self):
        node_hw = self._node.width/2  # Half of nodes width
        node_hh = self._node.height/2  # Half of nodes height
        len_minor = min(node_hw, node_hh)
        self._radius_core = (node_hw**2 + node_hh**2)/(2*len_minor)

        if node_hw > node_hh:  # X-axis is major.
            x = -node_hw
            y = -self._radius_core
        else:  # Y-axis is major.
            x = -self._radius_core
            y = -node_hh

        self.setPos(x+self._node.x(), y+self._node.y())

    def _calculate_angle_offset(self):
        if self.header:
            offset = self.header.offset + self.header.height
            self._angle_offset = math.degrees(offset/self._radius_core)
        else:
            self._angle_offset = 0

    def _calculate_angle_sweep(self):
        node_hw = self._node.width/2  # Half of nodes width
        node_hh = self._node.height/2  # Half of nodes height
        radius = self._radius_core
        self._angle_sweep = 360 - self._angle_offset

        # Law of cosine
        cosine = (2*radius**2-(node_hw**2+node_hh**2))/(2*radius**2)
        self._angle_sweep -= math.degrees(math.acos(cosine))

    def _calculate_header_angle(self):
        """Calculate the angle between the tangent line of
        the core circle at the axis between 3rd and 4th quadrants
        (where the header angle is not rotated yet) and the tangent
        line of header pos.
        """
        self._angle_header = self._angle_sweep - (self._angle_begin-90)

    def _calculate_angle_begin(self):
        node_hw = self._node.width / 2  # Half of nodes width
        #node_hh = self._node.height / 2  # Half of nodes height
        radius = self._radius_core

        self._angle_begin = 270

        """Law of cosine
           dist_sq is the square of distance between
           minus Y-axis of loop and ellipse.
        """
        dist_sq = (self.x()-self._node.x()+node_hw)**2 \
                   + (self.y()-self._node.y()+radius)**2

        cosine = (2*radius**2-dist_sq)/(2*radius**2)
        self._angle_begin += math.degrees(math.acos(cosine))

    def _identify_header(self):
        SelfloopLink._identify_header_pos(self)
        SelfloopLink._calculate_header_angle(self)
        super()._create_header_path()

    def _identify_header_pos(self):
        radius = self._radius_core
        rect_core = QRectF(-radius, -radius,
                           2*radius, 2*radius)

        pos = self._identify_arc_pos(rect_core,
                                     -self._angle_sweep)
        self.pos_header.setX(pos.x())
        self.pos_header.setY(pos.y())

    def _identify_arc_pos(self, rect, angle):
        path = QPainterPath()
        path.arcMoveTo(rect, self._angle_begin+angle)
        return path.currentPosition()

    def _create_path(self):

        self._identify_pos()

        # The calculating the angles, offset and sweep, should be done
        # in the sequence: (1) offset, (2) sweep.
        self._calculate_angle_offset()
        self._calculate_angle_sweep()
        self._calculate_angle_begin()

        """
        [REF] http://stackoverflow.com/a/17123051/4136588

        """
        self._path_paint = QPainterPath()
        path = self._path_paint

        radius = self._radius_core
        half_width = self.width/2
        diameter = 2*radius
        rect_outer = QRectF(-radius-half_width,
                            -radius-half_width,
                            diameter+self.width,
                            diameter+self.width)

        rect_inner = QRectF(-radius+half_width,
                            -radius+half_width,
                            diameter-self.width,
                            diameter-self.width)

        begin_angle = self._angle_begin  #270
        path.arcMoveTo(rect_outer, begin_angle)
        path.arcTo(rect_outer, begin_angle, -self._angle_sweep)

        if self.header:
            SelfloopLink._identify_header(self)
            self._path_paint.connectPath(self._path_header)
        else:
            path.lineTo(self._identify_arc_pos(rect_inner, -self._angle_sweep))

        path.arcTo(rect_inner, begin_angle-self._angle_sweep, self._angle_sweep)
        path.lineTo(self._identify_arc_pos(rect_outer, 0))
        path.closeSubpath()

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        #painter.drawPath(self._path_paint)

        #color = QColor(self._attr['FILL_COLOR'])
        # painter.drawPath(self._path_paint)
        #painter.setBrush(color)
        #painter.fillPath(self._path_paint, QBrush(color))
        #painter.drawPath(self._path_paint)

        # painter.setBrush(Qt.blue)
        #
        # painter.drawEllipse(-1,
        #                     -1, 2, 2)
        #
        # painter.setBrush(QColor(0, 0, 255, 100))
        # # for i in range(self._path_paint.elementCount()):
        # #     elem = self._path_paint.elementAt(i)
        # #     painter.drawEllipse(-1 + elem.x,
        # #                         -1 + elem.y, 2, 2)
        #
        # if self.header:
        #     painter.drawPath(self._path_header)
        #     # for i in range(self._path_header.elementCount()):
        #     #     elem = self._pat_header.elementAt(i)
        #     #     painter.drawEllipse(-1 + elem.x,h
        #     #                         -1 + elem.y, 2, 2)



    # def itemChange(self, change, value):
    #
    #     if change == QGraphicsItem.ItemSelectedHasChanged:
    #         if self.header:
    #             print("angle_header: ", self._angle_header)
    #
    #         print("Node width, height", self._node.width, self._node.height)
    #         print("angle_offset: ", self._angle_offset)
    #         print("sweep angle: ", self._angle_sweep)
    #         print("radius_core:", self._radius_core)
    #
    #     return super().itemChange(change, value)


    def to_dict(self):
        attr = super().to_dict()
        attr['ID_NODE'] = self.node.iden
        return attr

    @classmethod
    def from_dict(cls, attr, node):
        iden = attr.pop('ID')
        width = attr.pop('WIDTH')

        obj = cls(iden, node, width=width)
        obj.header = cls.header_from_dict(attr)

        attr['ID_NODE'] = node.iden
        obj._attr.update(attr)
        return obj
