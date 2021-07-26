import numpy as np
from qtpy.QtCore import Qt
from qtpy.QtCore import QLineF
from qtpy.QtCore import QRectF
from qtpy.QtGui import QBrush, QColor, QPainterPath
from qtpy.QtWidgets import QGraphicsItem

from .straightlink import StraightLink
from .controlpoint import ControlPoint

from nezzle.utils import dist
from nezzle.utils import dot
from nezzle.utils import internal_division
from nezzle.utils import length
from nezzle.utils import rotate
from nezzle.graphics import quadbezier
from nezzle.graphics.mixins import Lockable


@Lockable
class CurvedLink(StraightLink):

    ITEM_TYPE = 'CURVED_LINK'

    def __init__(self, *args, **kwargs):
        self._t_header = 0
        super().__init__(*args, **kwargs)

        self._attr.set_trigger('CTRL_POS_X',
                               self._trigger_set_ctrl_pos_x,
                               when='set')

        self._attr.set_trigger('CTRL_POS_Y',
                               self._trigger_set_ctrl_pos_y,
                               when='set')


        # To avoid repetitive memory allocation, make this variable as a member.
        self._arr_t = np.arange(1, 0.5, -0.001, dtype=np.float64)

    @property
    def pos_ctrl(self):
        return self._ctrl_point.pos()

    @property
    def ctrl_point(self):
        return self._ctrl_point

    def _trigger_set_ctrl_pos_x(self, key, value):
        self._ctrl_point.setX(value)
        return value

    def _trigger_set_ctrl_pos_y(self, key, value):
        self._ctrl_point.setY(value)
        return value

    # def boundingRect(self):
    #
    #     # All self.pos_xxxx are relative positions to the this link.
    #     # Thus, the origin of self.pos_xxxx is actually the position of this link.
    #     if self.is_straight():
    #         return super().boundingRect()
    #
    #     for i in range(self._path_paint.elementCount()):
    #         print(i, self._path_paint.elementAt(i))
    #
    #     pad_x = self.width
    #     pad_y = 2 * self._ctrl_point.radius  # Padding with the radius of control point
    #     max_x = max([self.pos_ctrl.x(), self.pos_src.x(), self.pos_tgt.x()]) + pad_x
    #     max_y = max([self.pos_ctrl.y(), self.pos_src.y(), self.pos_tgt.y()]) + pad_y
    #
    #     min_x = min([self.pos_ctrl.x(), self.pos_src.x(), self.pos_tgt.x()]) - pad_x
    #     min_y = min([self.pos_ctrl.y(), self.pos_src.y(), self.pos_tgt.y()]) - pad_y
    #
    #     rect = QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
    #     return rect

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            self._ctrl_point.update()

        return super().itemChange(change, value)

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        ## [DEBUG] Draw the bounding rect
        #rect = self.boundingRect()
        #painter.setBrush(QBrush(QColor(0, 255, 0, 100)))
        #painter.drawRect(rect)
        #######################

        if self.isSelected():
            painter.setBrush(Qt.red)
            # painter.setBrush(QBrush(QColor(0, 255, 0, 100)))
            painter.drawEllipse(-2.5, -2.5, 5, 5)
            painter.setPen(QColor(50, 50, 50, 100))

            # Draw control lines
            painter.drawLine(self.pos_ctrl, self.pos_src)
            painter.drawLine(self.pos_ctrl, self.pos_tgt)

        ## [DEBUG]
        if self.header:
            painter.setPen(Qt.black)
            painter.setBrush(Qt.white)
            painter.drawEllipse(-0.5 + self.pos_header.x(), -0.5 + self.pos_header.y(), 1, 1)

            painter.setPen(Qt.green)
            painter.setBrush(Qt.green)
            for i in range(0, 3):
                elem = self._path_header.elementAt(i)
                painter.drawEllipse(-0.5+elem.x, -0.5+elem.y, 1, 1)

            painter.setPen(Qt.blue)
            painter.setBrush(Qt.blue)
            for i in range(3, self._path_header.elementCount()):
                elem = self._path_header.elementAt(i)
                painter.drawEllipse(-0.5+elem.x, -0.5+elem.y, 1, 1)
        ##########################################################

    def is_straight(self):
        v1 = self.pos_src - self.ctrl_point.pos()
        v2 = self.pos_tgt - self.ctrl_point.pos()
        len_v1 = length(v1)
        len_v2 = length(v2)
        
        try:
            inner_product = np.clip(dot(v1, v2)/(len_v1*len_v2), -1, 1)
            control_angle = np.arccos(inner_product)
        except ZeroDivisionError:
            return True
            
        return np.isclose(control_angle, 0, atol=0.1) \
               or np.isclose(control_angle, np.pi, atol=1e-1)

    def _initialize(self):
        self._identify_pos()
        self._create_control_items()
        self._create_subpoints()
        self._create_path()
        self._update_bounding_rect()

    def _update_bounding_rect(self):
        super()._update_bounding_rect()

        rect_cl_src = QRectF(self.pos_ctrl, self.pos_src)
        rect_cl_tgt = QRectF(self.pos_ctrl, self.pos_tgt)

        rect = self._bounding_rect
        rect = rect.united(rect_cl_src)
        rect = rect.united(rect_cl_tgt)
        self._bounding_rect = rect

    def _create_control_items(self):
        mid = internal_division(self.pos_src, self.pos_tgt, 0.5, 0.5)
        self._ctrl_point = ControlPoint(parent=self, pos=mid)

    def _create_subpoints(self):
        self.cps = 3 * [None]
        self.cps[0] = self.pos_src
        self.cps[2] = self.pos_tgt

        self._qps_top = []
        self._qps_bottom = []

        self._dps_top = []
        self._dps_bottom = []

    def _identify_header(self):
        CurvedLink._identify_header_pos(self)
        CurvedLink._calculate_header_angle(self)
        super()._create_header_path()

    def _identify_header_pos(self):
        offset = self._calculate_header_offset()

        p1 = self.pos_src
        p2 = self.pos_tgt
        pc = self.ctrl_point.pos()

        x = np.array([p1.x(), pc.x(), p2.x()], dtype=np.float64)
        y = np.array([p1.y(), pc.y(), p2.y()], dtype=np.float64)

        arclen = quadbezier.arc_length(x, y, self._arr_t, 1)
        rchange = np.abs(arclen - offset) / offset

        ix = np.argmax(rchange < 5e-2)
        t = self._arr_t[ix]
        self._t_header = t
        #print("t: %f"%(t))

        ph = (1-t)**2*p1 + 2*(1-t)*t*pc + t**2*p2
        self.pos_header.setX(ph.x())
        self.pos_header.setY(ph.y())

    def _calculate_header_offset(self):
        v = self.pos_ctrl - self.pos_tgt
        try:
            angle_rad = np.arccos(v.x() / length(v))
        except ZeroDivisionError:
            return self.header.offset + self.header.height

        radius = self.target.calculate_radius(angle_rad)
        return radius + self.header.offset + self.header.height

    def _calculate_header_angle(self):
        self._angle_header = -QLineF(self.pos_ctrl, self.pos_header).angle()
        self._header_transform.angle = self._angle_header

    def _identify_curve_points(self):
        # Control points for quadratic Bezier curve
        cps = [self.pos_src,
               self.ctrl_point.pos(),
               self.pos_tgt]

        if self.header:
            if self.is_straight():
                StraightLink._identify_header(self)
                return
            else:
                CurvedLink._identify_header(self)
                cps[2] = self.pos_header

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

        if self.header:
            self._path_paint.connectPath(self._path_header)
        else:
            self._path_paint.lineTo(self._qps_bottom[-1])

        for i in range(len(self._dps_bottom) - 1, -1, -1):
            self._path_paint.quadTo(self._dps_bottom[i],
                                    self._qps_bottom[i])

        self._path_paint.lineTo(self._qps_top[0])

    def _create_path(self):
        self._identify_pos()
        if self.is_straight():
            return StraightLink._create_path(self)

        try:
            self._create_curve_path()
        except FloatingPointError:
            super(StraightLink, self)._create_path()

