import numpy as np
from qtpy.QtCore import Qt
from qtpy.QtCore import QLineF
from qtpy.QtCore import QRectF
from qtpy.QtGui import QColor, QPainterPath
from qtpy.QtWidgets import QGraphicsItem

from nezzle.graphics.edges.straightedge import StraightEdge
from nezzle.graphics.edges.controlpoint import ControlPoint

from nezzle.utils import dot
from nezzle.utils import internal_division
from nezzle.utils import length
from nezzle.graphics import quadbezier
from nezzle.graphics.mixins import Lockable


@Lockable
class CurvedEdge(StraightEdge):

    ITEM_TYPE = 'CURVED_EDGE'

    def __init__(self, *args, **kwargs):
        self._t_head = 0
        super().__init__(*args, **kwargs)

        self._attr.set_trigger('CP_POS_X',
                               self._trigger_set_cp_pos_x,
                               when='set')

        self._attr.set_trigger('CP_POS_Y',
                               self._trigger_set_cp_pos_y,
                               when='set')


        # To avoid repetitive memory allocation, make this variable as a member.
        self._arr_t = np.arange(1, 0.5, -0.001, dtype=np.float64)

    @property
    def pos_ctrl(self):
        return self._ctrl_point.pos()

    @property
    def ctrl_point(self):
        return self._ctrl_point

    def _trigger_set_cp_pos_x(self, key, value):
        self._ctrl_point.setX(value)
        return value

    def _trigger_set_cp_pos_y(self, key, value):
        self._ctrl_point.setY(value)
        return value

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            self._ctrl_point.update()

        return super().itemChange(change, value)

    def update(self):
        self.update_ctrl_points()
        super().update()

    def update_ctrl_points(self):
        cp = self._ctrl_point
        if self.is_node_selected():
            cp.setVisible(False)
        else:
            cp.setVisible(True)

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        if self.isSelected():
            painter.setBrush(Qt.red)
            painter.drawEllipse(-2.5, -2.5, 5, 5)
            painter.setPen(QColor(50, 50, 50, 100))

            if not self.is_node_selected():
                # Draw control lines
                painter.drawLine(self.pos_ctrl, self.pos_src)
                painter.drawLine(self.pos_ctrl, self.pos_trg)

    def is_straight(self):
        v1 = self.pos_src - self.ctrl_point.pos()
        v2 = self.pos_trg - self.ctrl_point.pos()
        len_v1 = length(v1)
        len_v2 = length(v2)
        dot_v1v2 = dot(v1, v2)

        if len_v1 <= 1e-8 or len_v2 <= 1e-8:
            return True

        try:
            inner_product = np.clip(dot_v1v2/(len_v1*len_v2), -1, 1)
            control_angle = np.arccos(inner_product)
        except ZeroDivisionError:
            return True
            
        return np.isclose(control_angle, 0, atol=0.1) \
               or np.isclose(control_angle, np.pi, atol=1e-1)

    def initialize(self):
        self._identify_pos()
        self._create_control_items()
        self._create_subpoints()
        self._create_path()
        self._update_bounding_rect()

    def _update_bounding_rect(self):
        super()._update_bounding_rect()

        rect_ctrl_src = QRectF(self.pos_ctrl, self.pos_src)
        rect_ctrl_trg = QRectF(self.pos_ctrl, self.pos_trg)

        rect = self._bounding_rect
        rect = rect.united(rect_ctrl_src)
        rect = rect.united(rect_ctrl_trg)
        self._bounding_rect = rect

    def _create_control_items(self):
        mid = internal_division(self.pos_src, self.pos_trg, 0.5, 0.5)
        self._ctrl_point = ControlPoint(parent=self, pos=mid)

    def _create_subpoints(self):
        self.cps = 3 * [None]
        self.cps[0] = self.pos_src
        self.cps[2] = self.pos_trg

        self._qps_top = []
        self._qps_bottom = []

        self._dps_top = []
        self._dps_bottom = []

    def _identify_head(self):
        CurvedEdge._identify_head_pos(self)
        CurvedEdge._calculate_head_angle(self)
        super()._create_head_path()

    def _identify_head_pos(self):
        offset = self._calculate_head_offset()

        p1 = self.pos_src
        p2 = self.pos_trg
        pc = self.ctrl_point.pos()

        x = np.array([p1.x(), pc.x(), p2.x()], dtype=np.float64)
        y = np.array([p1.y(), pc.y(), p2.y()], dtype=np.float64)

        arclen = quadbezier.arc_length(x, y, self._arr_t, 1)
        rchange = np.abs(arclen - offset) / offset

        ix = np.argmax(rchange < 5e-2)
        t = self._arr_t[ix]
        self._t_head = t

        ph = (1-t)**2*p1 + 2*(1-t)*t*pc + t**2*p2
        self.pos_head.setX(ph.x())
        self.pos_head.setY(ph.y())

    def _calculate_head_offset(self):
        v = self.pos_ctrl - self.pos_trg
        try:
            angle_rad = np.arccos(v.x() / length(v))
        except ZeroDivisionError:
            return self.head.offset + self.head.height

        radius = self.target.calculate_radius(angle_rad)
        return radius + self.head.offset + self.head.height

    def _calculate_head_angle(self):
        self._angle_head = -QLineF(self.pos_ctrl, self.pos_head).angle()
        self._head_transform.angle = self._angle_head

    def _identify_curve_points(self):
        # Control points for quadratic Bezier curve
        cps = [self.pos_src,
               self.ctrl_point.pos(),
               self.pos_trg]

        if self.head:
            if self.is_straight():
                StraightEdge._identify_head(self)
                return
            else:
                CurvedEdge._identify_head(self)
                cps[2] = self.pos_head

        sps = quadbezier.identify_sps(cps)
        qps_top, qps_bottom = quadbezier.identify_qps(sps, self.width)
        dps_top, dps_bottom = quadbezier.identify_dps(sps, self.width)

        self._qps_top = qps_top
        self._qps_bottom = qps_bottom
        self._dps_top = dps_top
        self._dps_bottom = dps_bottom

    def _create_curve_path(self):

        self._identify_curve_points()
        self._path_paint = QPainterPath()
        # self._path_paint.clear()  # supported from Qt 5.13
        self._path_paint.setFillRule(Qt.WindingFill)

        self._path_paint.moveTo(self._qps_top[0])
        for i in range(len(self._dps_top)):
            self._path_paint.quadTo(self._dps_top[i], self._qps_top[i + 1])

        if self.head:
            self._path_paint.connectPath(self._path_head)
        else:
            self._path_paint.lineTo(self._qps_bottom[-1])

        for i in range(len(self._dps_bottom) - 1, -1, -1):
            self._path_paint.quadTo(self._dps_bottom[i],
                                    self._qps_bottom[i])

        self._path_paint.lineTo(self._qps_top[0])

    def _create_path(self):
        self._identify_pos()
        if self.is_straight():
            return StraightEdge._create_path(self)

        try:
            self._create_curve_path()
        except FloatingPointError:
            super(StraightEdge, self)._create_path()