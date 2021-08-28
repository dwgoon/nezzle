import numpy as np

from qtpy.QtCore import QPointF
from qtpy.QtCore import QLineF
from qtpy.QtGui import QPainterPath

from nezzle.utils import dist
from nezzle.utils import length
from nezzle.utils import internal_division
from nezzle.utils import rotate
from nezzle.graphics.mixins import Lockable
from nezzle.graphics.links.baselink import TwoNodeLink
from nezzle.graphics.arrows.transform import Rotate


@Lockable
class StraightLink(TwoNodeLink):
    """
    Straight link class.
    """
    ITEM_TYPE = 'STRAIGHT_LINK'

    def __init__(self, *args, **kwargs):
        self._angle_head = None
        self._head_transform = Rotate()
        super().__init__(*args, **kwargs)

    def initialize(self):
        self._identify_pos()
        self._create_path()
        self._update_bounding_rect()

    def _identify_head(self):
        StraightLink._identify_head_pos(self)
        StraightLink._calculate_head_angle(self)
        #self._identify_head_pos()
        #self._calculate_head_angle()
        super()._create_head_path()

    def _identify_head_pos(self):
        offset = self._calculate_head_offset()

        p1 = self.pos_src
        p2 = self.pos_tgt

        ph = internal_division(p1, p2, dist(p1, p2) - offset, offset)
        self.pos_head.setX(ph.x())
        self.pos_head.setY(ph.y())

    def _calculate_head_offset(self):
        v = self.pos_tgt - self.pos_src
        try:
            angle_rad = np.arccos(v.x()/length(v))
        except ZeroDivisionError:
            return 0

        radius = self.target.calculate_radius(angle_rad)
        return radius + self.head.offset + self.head.height

    def _calculate_head_angle(self):
        self._angle_head = -QLineF(self.pos_src, self.pos_tgt).angle()
        self._head_transform.angle = self._angle_head

    def _identify_pos(self):
        m = internal_division(self.source.pos(), self.target.pos(), 0.5, 0.5)
        self.setPos(m)

    def _create_path(self):
        """
        Both identifying the points and creating the path for a straight line
        are handled by this method.
        """

        self._identify_pos()
        self._path_paint = QPainterPath()

        line = QLineF(self.pos_src, self.pos_tgt)

        butt1 = self.pos_src + QPointF(0, -self.width / 2)
        butt2 = self.pos_src + QPointF(0, +self.width / 2)

        angle = -line.angle()  # QLine's angle is counter-clock wise.

        butt2_rotated = rotate(self.pos_src, butt2, angle)
        butt1_rotated = rotate(self.pos_src, butt1, angle)
        self._path_paint.moveTo(butt2_rotated)
        self._path_paint.lineTo(butt1_rotated)

        if self.head and not self.are_nodes_close():
            StraightLink._identify_head(self)
            self._path_paint.connectPath(self._path_head)
            self._path_paint.lineTo(butt2_rotated)
        else:
            head1 = self.pos_src + QPointF(line.length(), -self.width / 2)
            head2 = self.pos_src + QPointF(line.length(), +self.width / 2)

            self._path_paint.lineTo(rotate(self.pos_src, head1, angle))
            self._path_paint.lineTo(rotate(self.pos_src, head2, angle))

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        painter.drawPath(self._path_paint)


