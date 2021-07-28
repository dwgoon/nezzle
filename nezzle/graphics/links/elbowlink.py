import numpy as np

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtCore import QLineF
from qtpy.QtCore import QRectF
from qtpy.QtGui import QVector2D
from qtpy.QtGui import QPen, QBrush, QColor
from qtpy.QtGui import QPainterPath
from qtpy.QtWidgets import QGraphicsItem

from nezzle.graphics.links.straightlink import StraightLink
from .controlpoint import ControlPoint, XaxisControlPoint

from nezzle.utils import angle
from nezzle.utils import dist
from nezzle.utils import dot
from nezzle.utils import internal_division
from nezzle.utils import normal_vector
from nezzle.utils import length
from nezzle.utils import rotate
from nezzle.graphics import quadbezier
from nezzle.graphics.mixins import Lockable


@Lockable
class ElbowLink(StraightLink):
    ITEM_TYPE = 'ELBOW_LINK'

    def __init__(self, *args, **kwargs):
        self._t_header = 0

        # To avoid repetitive memory allocation, make this variable as a member.
        self._arr_t = np.arange(1, 0.5, -0.001, dtype=np.float64)

        super().__init__(*args, **kwargs)

        self._attr.set_trigger('CTRL_POS_X',
                               self._trigger_set_ctrl_pos_x,
                               when='set')

        self._attr.set_trigger('CTRL_POS_Y',
                               self._trigger_set_ctrl_pos_y,
                               when='set')

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

    def _initialize(self):
        self._identify_pos()
        self._create_control_items()
        self._create_subpoints()
        self._create_path()
        self._update_bounding_rect()


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

    # def update(self, *args, **kwargs):
    #
    #     # TODO: Process multiple control points.
    #     """
    #     for cp in ctrl_points:
    #         cp.update()
    #     """
    #     print("Adjust ctrl point")
    #     m = internal_division(self.pos_src, self.pos_tgt, 0.5, 0.5)
    #     self._ctrl_point.setX(self._ctrl_point.x())
    #     self._ctrl_point.setY(m.y())
    #     self._ctrl_point.update()
    #
    #     return super().update(*args, **kwargs)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            self._ctrl_point.update()

        return super().itemChange(change, value)

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        ## [DEBUG] Draw the bounding rect
        rect = self.boundingRect()
        painter.setPen(QPen(QColor(0, 255, 0, 100)))
        painter.setBrush(QBrush(QColor(0, 255, 0, 100)))
        painter.drawRect(rect)
        #######################

        if self.isSelected():
            painter.setBrush(Qt.red)
            # painter.setBrush(QBrush(QColor(0, 255, 0, 100)))
            painter.drawEllipse(-2.5, -2.5, 5, 5)
            painter.setPen(QColor(50, 50, 50, 100))

            # Draw control lines
            painter.drawLine(self.pos_ctrl, self.pos_src)
            painter.drawLine(self.pos_ctrl, self.pos_tgt)

            # Draw connectors
            painter.setPen(Qt.red)
            for con in self._pos_connectors:
                painter.drawEllipse(con, 2, 2)

            # painter.setPen(Qt.blue)
            # for con in self._pos_horizontal_connectors:
            #     painter.drawEllipse(con, 2, 2)

        ## [DEBUG]
        # painter.setPen(Qt.black)
        # painter.setBrush(Qt.blue)
        # for i in range(self._path_paint.elementCount()):
        #     elem = self._path_paint.elementAt(i)
        #     painter.drawEllipse(-0.5+elem.x, -0.5+elem.y, 1, 1)

        # Draw central points
        painter.setPen(Qt.black)
        painter.setBrush(Qt.blue)
        for elem in self.cps:
            painter.drawEllipse(-0.5+elem.x(), -0.5+elem.y(), 1.5, 1.5)

        # Draw Forward line points
        painter.setPen(Qt.yellow)
        painter.setBrush(Qt.yellow)
        for elem in self.fps:
            painter.drawEllipse(-0.5 + elem.x(), -0.5 + elem.y(), 1.5, 1.5)

        # Draw Backward line points
        painter.setPen(Qt.cyan)
        painter.setBrush(Qt.cyan)
        for elem in self.bps:
            painter.drawEllipse(-0.5 + elem.x(), -0.5 + elem.y(), 1.5, 1.5)

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

        #########################################################

    def is_straight(self):
        td = 0.75 * self.width

        sx, sy = self.pos_src.x(), self.pos_src.y()
        tx, ty = self.pos_tgt.x(), self.pos_tgt.y()

        if (abs(sx - tx) < td) or (abs(sy - ty) < td):
            return True
        else:
            return False

    # def _update_bounding_rect(self):
    #     super()._update_bounding_rect()
    #
    #     rect_ctrl_src = QRectF(self.pos_ctrl, self.pos_src)
    #     rect_ctrl_tgt = QRectF(self.pos_ctrl, self.pos_tgt)
    #
    #     rect = self._bounding_rect
    #     rect = rect.united(rect_ctrl_src)
    #     rect = rect.united(rect_ctrl_tgt)
    #     self._bounding_rect = rect

    def _create_control_items(self):
        mid = internal_division(self.pos_src, self.pos_tgt, 0.5, 0.5)
        #self._ctrl_point = XaxisControlPoint(parent=self, pos=mid)
        self._ctrl_point = ControlPoint(parent=self, pos=mid)

    def _create_subpoints(self):
        self.cps = []  # Central points
        self.fps = []  # Forward points
        self.bps = []  # Backward points
        self._pos_connectors = [QPointF(), QPointF()]

        self.cps.append(self.pos_src)  # Dummy point
        self.cps.append(self.pos_src)
        self.fps.append(QPointF())
        self.bps.append(QPointF())
        for pos in self._pos_connectors:
            self.cps.append(pos)
            self.fps.append(QPointF())
            self.bps.append(QPointF())

        self.cps.append(self.pos_tgt)
        self.cps.append(self.pos_tgt)  # Dummy point
        self.fps.append(QPointF())
        self.bps.append(QPointF())

    def _identify_connectors_pos(self):
        pos_ctrl = self.ctrl_point.pos()

        vcon0 = self._pos_connectors[0]
        vcon1 = self._pos_connectors[1]

        # Vertical Connector (0)
        vcon0.setX(pos_ctrl.x())
        vcon0.setY(self.pos_src.y())

        # Vertical Connector (1)
        vcon1.setX(pos_ctrl.x())
        vcon1.setY(self.pos_tgt.y())

    def _identify_header_pos(self):
        # The version of StraightLink
        offset = self._calculate_header_offset()

        p1 = self._pos_connectors[1]
        p2 = self.pos_tgt

        print("dist(p1, p2) - offset: %f, offset: %f"%(dist(p1, p2) - offset, offset))
        ph = internal_division(p1, p2, dist(p1, p2) - offset, offset)
        self.pos_header.setX(ph.x())
        self.pos_header.setY(ph.y())

    def _calculate_header_angle(self):
        pos_vc1 = self._pos_connectors[1]
        self._angle_header = -QLineF(pos_vc1, self.pos_header).angle()
        self._header_transform.angle = self._angle_header
        # print("Header Angle:", self._angle_header)

    def _identify_header(self):
        self._identify_header_pos()
        self._calculate_header_angle()
        self._create_header_path()

    def _calculate_header_offset(self):
        # if self.is_straight():
        #     v = self.pos_tgt - self.pos_src
        # else:
        #     v = self.pos_tgt - self._pos_connectors[1]

        v = self.pos_tgt - self._pos_connectors[1]

        try:
            angle_rad = np.arccos(v.x()/length(v))
        except ZeroDivisionError:
            return 0

        radius = self.target.calculate_radius(angle_rad)
        return radius + self.header.offset + self.header.height

    def _create_header_path(self):
        points = self.header.identify_points(self.pos_header,
                                             self.width,
                                             self._header_transform)
        path = QPainterPath()

        path.moveTo(points[-1])
        for pt in points[-2::-1]:
            path.lineTo(pt)

        self._path_header = path

    def _identify_elbow_points(self):
        # Update positions of source and target
        self.cps[0] = self.pos_src  # Dummy point
        self.cps[1] = self.pos_src
        # for i, pos in enumerate(self._pos_connectors):
        #     self.cps[i+1] = pos
        self.cps[-1] = self.pos_tgt
        self.cps[-2] = self.pos_tgt # Dummy point

        hw = self.width / 2  # The half of width

        for i in range(1, len(self.cps) - 1):
            p0 = self.cps[i - 1]
            p1 = self.cps[i]
            p2 = self.cps[i + 1]
            v1 = QVector2D(p1 - p0)
            v2 = QVector2D(p2 - p1)

            nv1 = hw * normal_vector(v1)  # Normal vector of v1
            nv2 = hw * normal_vector(v2)  # Normal vector of v2
            self.fps[i-1] = p1 + (nv1 + nv2).toPointF()
        # end of for

        len_cps = len(self.cps)
        for i in range(len(self.cps) - 2, 0, -1):
            p0 = self.cps[i + 1]
            p1 = self.cps[i]
            p2 = self.cps[i - 1]
            v1 = QVector2D(p1 - p0)
            v2 = QVector2D(p2 - p1)

            nv1 = hw * normal_vector(v1)  # Normal vector of v1
            nv2 = hw * normal_vector(v2)  # Normal vector of v2
            self.bps[(len_cps-2)-i] = p1 + (nv1 + nv2).toPointF()
        # end of for

    def _create_elbow_path(self):
        self._identify_elbow_points()

        self._path_paint = QPainterPath()
        self._path_paint.setFillRule(Qt.WindingFill)

        # Forward line
        self._path_paint.moveTo(self.fps[0])
        for i in range(1, len(self.fps)-1):
            self._path_paint.lineTo(self.fps[i])
        # end of for

        # Transition to the backward line
        if self.header:  # Add the header
            # if self.is_straight():
            #     StraightLink._identify_header(self)
            # else:
            #     self._identify_header()

            self._identify_header()

            self._path_paint.connectPath(self._path_header)
        else:
            self._path_paint.lineTo(self.fps[-1])
            self._path_paint.lineTo(self.bps[0])

        # Backward line
        for i in range(1, len(self.bps)):
            self._path_paint.lineTo(self.bps[i])
        # end of for

    def _create_path(self):
        self._identify_pos()  # Identify the position of this link
        self._identify_connectors_pos()  # Identify the positions of connectors

        # if self.is_straight():
        #     StraightLink._create_path(self)
        # else:
        #     self._create_elbow_path()

        self._create_elbow_path()

        # try:
        #     self._create_elbow_path()
        # except FloatingPointError:
        #     super(StraightLink, self)._create_path()

