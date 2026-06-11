import math

from qtpy.QtCore import QPointF
from qtpy.QtCore import QLineF
from qtpy.QtCore import QRectF
from qtpy.QtGui import QPainterPath

from nezzle.utils import dist
from nezzle.utils import internal_division
from nezzle.graphics.mixins import Lockable
from nezzle.graphics.edges.baseedge import TwoNodeEdge
from nezzle.graphics.arrows.transform import Rotate


@Lockable
class StraightEdge(TwoNodeEdge):
    """Straight edge class.
    """
    ITEM_TYPE = 'STRAIGHT_EDGE'

    def __init__(self, *args, **kwargs):
        self._angle_head = None
        self._head_transform = Rotate()
        super().__init__(*args, **kwargs)

    def initialize(self):
        # Path construction is deferred: _brect_dirty/_geom_dirty start True,
        # boundingRect() answers from the closed-form conservative bbox and
        # the first paint()/shape() builds the real path. Building it eagerly
        # here only slowed bulk construction (network loading).
        self._identify_pos()

    def _identify_head(self):
        StraightEdge._identify_head_pos(self)
        StraightEdge._calculate_head_angle(self)
        super()._create_head_path()

    def _identify_head_pos(self):
        offset = self._calculate_head_offset()

        p1 = self.pos_src
        p2 = self.pos_trg

        ph = internal_division(p1, p2, dist(p1, p2) - offset, offset)
        self.pos_head.setX(ph.x())
        self.pos_head.setY(ph.y())

    def _calculate_head_offset(self):
        # Scalarized + clamped: avoids np.arccos NaN raise from the global
        # np.seterr('raise') in elbowedge.py when src and trg coincide.
        vx = self.pos_trg.x() - self.pos_src.x()
        vy = self.pos_trg.y() - self.pos_src.y()
        len_v_sq = vx * vx + vy * vy
        if len_v_sq < 1e-18:
            return 0
        cos_v = vx / math.sqrt(len_v_sq)
        if cos_v > 1.0:
            cos_v = 1.0
        elif cos_v < -1.0:
            cos_v = -1.0
        radius = self.target.calculate_radius(math.acos(cos_v))
        return radius + self.head.offset + self.head.height

    def _calculate_head_angle(self):
        self._angle_head = -QLineF(self.pos_src, self.pos_trg).angle()
        self._head_transform.angle = self._angle_head

    def _update_conservative_bbox(self):
        """Fast O(1) superset bbox from src/trg + width + head margin.

        Used by boundingRect() so off-screen straight edges in large graphs
        don't pay for a full _create_path() just to be culled.
        """
        ps = self.pos_src
        pt = self.pos_trg
        psx = ps.x(); psy = ps.y()
        ptx = pt.x(); pty = pt.y()
        minx = psx if psx < ptx else ptx
        maxx = psx if psx > ptx else ptx
        miny = psy if psy < pty else pty
        maxy = psy if psy > pty else pty

        # Direct _width/_head reads: this runs per edge per move, and the
        # property/TriggerDict hops are a third of its cost.
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

        self._bounding_rect = QRectF(minx - margin, miny - margin,
                                     (maxx - minx) + 2.0 * margin,
                                     (maxy - miny) + 2.0 * margin)

    def _create_path(self):
        """
        Both identifying the points and creating the path for a straight line
        are handled by this method.

        The rectangle corners are computed directly from the unit vector
        along src->trg: rotating (0, +-hw) onto the line frame gives the
        perpendicular offset (+-uy*hw, -+ux*hw). Equivalent to the previous
        QLineF.angle() + rotate() composition without 4 QTransform round
        trips per call.
        """

        self._path_paint = QPainterPath()

        ps = self.pos_src
        pt = self.pos_trg
        psx = ps.x(); psy = ps.y()
        ptx = pt.x(); pty = pt.y()

        dx = ptx - psx
        dy = pty - psy
        len_v = math.sqrt(dx * dx + dy * dy)
        if len_v == 0.0:
            ux, uy = 1.0, 0.0  # matches QLineF.angle() == 0 for a null line
        else:
            ux = dx / len_v
            uy = dy / len_v

        hw = self.width / 2
        ox = uy * hw
        oy = -ux * hw

        butt1 = QPointF(psx + ox, psy + oy)
        butt2 = QPointF(psx - ox, psy - oy)
        self._path_paint.moveTo(butt2)
        self._path_paint.lineTo(butt1)

        if self.head and not self.are_nodes_close():
            StraightEdge._identify_head(self)
            self._path_paint.connectPath(self._path_head)
            self._path_paint.lineTo(butt2)
        else:
            self._path_paint.lineTo(QPointF(ptx + ox, pty + oy))
            self._path_paint.lineTo(QPointF(ptx - ox, pty - oy))


