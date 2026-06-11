import math

from qtpy.QtCore import QRectF
from qtpy.QtGui import QPainterPath

from nezzle.graphics.edges.baseedge import BaseEdge
from nezzle.graphics.mixins import Lockable
from nezzle.graphics.arrows.transform import Rotate


@Lockable
class SelfloopEdge(BaseEdge):

    ITEM_TYPE = 'SELFLOOP_EDGE'

    def __init__(self, iden, node, *args, angle_begin=270, **kwargs):
        self._node = node
        self._radius_core = None
        self._angle_offset = None
        self._angle_sweep = None
        self._angle_begin = angle_begin
        self._head_transform = Rotate()

        super().__init__(iden, *args, **kwargs)

        self.node.add_edge(self)

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, obj):
        self._node = obj

    def initialize(self):
        # Path construction is deferred: _identify_pos() computes
        # _radius_core, which is all the conservative bbox needs; the first
        # paint()/shape() builds the real path.
        self._identify_pos()

    def _update_conservative_bbox(self):
        """Fast O(1) superset bbox: the loop is centered at the edge's local
        origin with radius ``_radius_core``, so its local bbox is invariant
        under node position changes (only depends on node size + loop width).
        """
        if self._radius_core is None:
            # Pre-init: fall back to whatever path bbox + pen padding gives.
            return BaseEdge._update_conservative_bbox(self)
        r = self._radius_core
        margin = self._width * 0.5 + 2.0
        head = self._head
        if head:
            # Additive bound: covers the head's along-edge reach AND its
            # lateral half-width (e.g. Hammer heads are 7x edge width wide)
            # for any head rotation, since sqrt(h^2 + (w/2)^2) <= h + w/2.
            head_reach = (head.height + head.offset
                          + 0.5 * head.width + 2.0)
            if head_reach > margin:
                margin = head_reach
        if self._pen:
            margin += 2.0 * self._pen.width()
        side = 2.0 * (r + margin)
        self._bounding_rect = QRectF(-r - margin, -r - margin, side, side)

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
        if self.head:
            offset = self.head.offset + self.head.height
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

    def _calculate_head_angle(self):
        """Calculate the angle between the tangent line of
        the core circle at the axis between 3rd and 4th quadrants
        (where the head angle is not rotated yet) and the tangent
        line of head pos.
        """
        self._angle_head = self._angle_sweep - (self._angle_begin-90)
        self._head_transform.angle = self._angle_head

    def _calculate_angle_begin(self):
        node_hw = self._node.width / 2  # Half of nodes width
        #node_hh = self._node.height / 2  # Half of nodes height
        radius = self._radius_core

        # self._angle_begin = 270  # To set this angle at __init__

        """Law of cosine
           dist_sq is the square of distance between
           minus Y-axis of loop and ellipse.
        """
        dist_sq = (self.x()-self._node.x()+node_hw)**2 \
                   + (self.y()-self._node.y()+radius)**2

        cosine = (2*radius**2-dist_sq)/(2*radius**2)
        self._angle_begin += math.degrees(math.acos(cosine))

    def _identify_head(self):
        SelfloopEdge._identify_head_pos(self)
        SelfloopEdge._calculate_head_angle(self)
        super()._create_head_path()

    def _identify_head_pos(self):
        radius = self._radius_core
        rect_core = QRectF(-radius, -radius,
                           2*radius, 2*radius)

        pos = self._identify_arc_pos(rect_core,
                                     -self._angle_sweep)
        self.pos_head.setX(pos.x())
        self.pos_head.setY(pos.y())

    def _identify_arc_pos(self, rect, angle):
        path = QPainterPath()
        path.arcMoveTo(rect, self._angle_begin+angle)
        return path.currentPosition()

    def _create_path(self):
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

        if self.head:
            SelfloopEdge._identify_head(self)
            self._path_paint.connectPath(self._path_head)
        else:
            path.lineTo(self._identify_arc_pos(rect_inner, -self._angle_sweep))

        path.arcTo(rect_inner, begin_angle-self._angle_sweep, self._angle_sweep)
        path.lineTo(self._identify_arc_pos(rect_outer, 0))
        path.closeSubpath()

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

    def to_dict(self):
        attr = super().to_dict()
        attr['ID_NODE'] = self.node.iden
        return attr

    @classmethod
    def from_dict(cls, attr, node):
        iden = attr.pop('ID')
        width = attr.pop('WIDTH')

        obj = cls(iden, node, width=width)
        obj.head = cls.head_from_dict(attr)

        attr['ID_NODE'] = node.iden
        obj._attr.update(attr)
        return obj
