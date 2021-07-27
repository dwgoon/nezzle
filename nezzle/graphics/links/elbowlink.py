import numpy as np

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtCore import QLineF
from qtpy.QtCore import QRectF
from qtpy.QtGui import QBrush, QColor, QPainterPath
from qtpy.QtWidgets import QGraphicsItem

from nezzle.graphics.links.baselink import TwoNodeLink
from nezzle.graphics.links.straightlink import StraightLink
from .controlpoint import ControlPoint, XaxisControlPoint

from nezzle.utils import dist
from nezzle.utils import dot
from nezzle.utils import internal_division
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
        # rect = self.boundingRect()
        # painter.setBrush(QBrush(QColor(0, 255, 0, 100)))
        # painter.drawRect(rect)
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

        # Draw outer line points
        painter.setPen(Qt.yellow)
        painter.setBrush(Qt.yellow)
        for elem in self.ops:
            painter.drawEllipse(-0.5 + elem.x(), -0.5 + elem.y(), 1.5, 1.5)

        # Draw inner line points
        painter.setPen(Qt.cyan)
        painter.setBrush(Qt.cyan)
        for elem in self.ips:
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
        #self._ctrl_point = XaxisControlPoint(parent=self, pos=mid)
        #self._ctrl_point = XaxisControlPoint(parent=self, pos=mid)
        self._ctrl_point = ControlPoint(parent=self, pos=mid)

    def _create_subpoints(self):
        self.cps = []
        self.ops = []
        self.ips = []
        self._pos_connectors = [QPointF(), QPointF()]

        self.cps.append(self.pos_src)
        self.ops.append(QPointF())
        self.ips.append(QPointF())
        for pos in self._pos_connectors:
            self.cps.append(pos)
            self.ops.append(QPointF())
            self.ips.append(QPointF())

        self.cps.append(self.pos_tgt)
        self.ops.append(QPointF())
        self.ips.append(QPointF())

    def _identify_connectors_pos(self):
        pos_ctrl = self.ctrl_point.pos()

        # Vertical Connectors
        #  ____*
        #      |
        #      *----

        vcon0 = self._pos_connectors[0]
        vcon1 = self._pos_connectors[1]

        # Vertical Connector (0)
        vcon0.setX(pos_ctrl.x())
        vcon0.setY(self.pos_src.y())

        # Vertical Connector (1)
        vcon1.setX(pos_ctrl.x())
        vcon1.setY(self.pos_tgt.y())


        for i, pos in enumerate(self.cps):
            print("CPS[%d]: %s"%(i, pos))

        """
        # Vertical Connectors
        #  ____*
        #      |
        #      *----

        vcon0 = self._pos_connectors[0]
        vcon1 = self._pos_connectors[1]

        # Vertical Connector (0)
        vcon0.setX(pos_ctrl.x())
        vcon0.setY(self.pos_src.y())

        # Vertical Connector (1)
        vcon1.setX(pos_ctrl.x())
        vcon1.setY(self.pos_tgt.y())

        # Horizontal Connectors
        #  |
        #  *____*
        #       |

        hcon0 = self._pos_horizontal_connectors[0]
        hcon1 = self._pos_horizontal_connectors[1]

        # Horizontal Connector (0)
        hcon0.setX(self.pos_src.x())
        hcon0.setY(pos_ctrl.y())

        # Horizontal Connector (1)
        hcon1.setX(self.pos_tgt.x())
        hcon1.setY(pos_ctrl.y())
        """


    def _identify_header_pos(self):
        # offset = self._calculate_header_offset()
        #
        # p1 = self.pos_src
        # p2 = self.pos_tgt
        # pc = self.ctrl_point.pos()
        #
        # x = np.array([p1.x(), pc.x(), p2.x()], dtype=np.float64)
        # y = np.array([p1.y(), pc.y(), p2.y()], dtype=np.float64)
        #
        # arclen = quadbezier.arc_length(x, y, self._arr_t, 1)
        # rchange = np.abs(arclen - offset) / offset
        #
        # ix = np.argmax(rchange < 5e-2)
        # t = self._arr_t[ix]
        # self._t_header = t
        # # print("t: %f"%(t))
        #
        # ph = (1 - t) ** 2 * p1 + 2 * (1 - t) * t * pc + t ** 2 * p2
        # self.pos_header.setX(ph.x())
        # self.pos_header.setY(ph.y())

        # The version of StraightLink
        offset = self._calculate_header_offset()

        p1 = self._pos_connectors[1]
        p2 = self.pos_tgt

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
        if self.is_straight():
            v = self.pos_tgt - self.pos_src
        else:
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

        sx, sy = self.pos_src.x(), self.pos_src.y()
        tx, ty = self.pos_tgt.x(), self.pos_tgt.y()

        dx = tx - sx  # Direction from source to target in X-axis.
        dy = ty - sy  # Direction from source to target in Y-axis.

        if dx < 0:
            points.reverse()

        path.moveTo(points[0])
        for pt in points[1:]:
            path.lineTo(pt)

        self._path_header = path

    def _identify_elbow_points(self):
        # Update positions of source and target
        self.cps[0] = self.pos_src
        # for i, pos in enumerate(self._pos_connectors):
        #     self.cps[i+1] = pos
        self.cps[-1] = self.pos_tgt


        hw = self.width / 2  # The half of width

        # Outer line
        p0 = self.cps[0]
        p1 = self.cps[1]
        p2 = self.cps[2]
        v2 = p2 - p1

        ix_ops = 0
        dxdy = hw * -1 * QPointF(np.sign(v2.x()), np.sign(v2.y()))  # dxdy = hw * (-v2)
        self.ops[ix_ops] = self.pos_src + dxdy
        ix_ops += 1

        for i in range(1, len(self.cps) - 1):
            p0 = self.cps[i - 1]
            p1 = self.cps[i]
            p2 = self.cps[i + 1]
            v_out = -p0 + 2 * p1 - p2
            dxdy = hw * QPointF(np.sign(v_out.x()), np.sign(v_out.y()))
            self.ops[ix_ops] = p1 + dxdy
            ix_ops += 1
        # end of for

        p0 = self.cps[-3]
        p1 = self.cps[-2]
        p2 = self.cps[-1]
        v1 = p1 - p0
        dxdy = hw * QPointF(np.sign(v1.x()), np.sign(v1.y()))  # dxdy = hw * (-v1)
        self.ops[ix_ops] = p2 + dxdy
        ix_ops += 1

        # Inner line
        ix_ips = 0
        self.ips[ix_ips] = p2 - dxdy
        ix_ips += 1

        for i in range(len(self.cps) - 2, 0, -1):
            p0 = self.cps[i + 1]
            p1 = self.cps[i]
            p2 = self.cps[i - 1]

            v_in = p0 - 2 * p1 + p2
            dxdy = hw * QPointF(np.sign(v_in.x()), np.sign(v_in.y()))
            self.ips[ix_ips] = p1 + dxdy
            ix_ips += 1
        # end of for

        p0 = self.cps[2]
        p1 = self.cps[1]
        p2 = self.cps[0]
        v1 = p1 - p0
        dxdy = -hw * QPointF(np.sign(v1.x()), np.sign(v1.y()))  # dxdy = hw * (-v1)
        self.ips[ix_ips] = p2 + dxdy

    def _create_elbow_path(self):
        self._identify_elbow_points()

        self._path_paint = QPainterPath()
        self._path_paint.setFillRule(Qt.WindingFill)

        # Outer line
        ix_ops = 0
        self._path_paint.moveTo(self.ops[0])

        for i in range(1, len(self.ops)-1):
            self._path_paint.lineTo(self.ops[i])
        # end of for
        self._path_paint.lineTo(self.ops[-1])

        # Transition to the inner line
        if self.header:  # Add the header
            if self.is_straight():
                StraightLink._identify_header(self)
            else:
                self._identify_header()

            self._path_paint.connectPath(self._path_header)
        else:
            self._path_paint.lineTo(self.ips[0])

        # Inner line
        for i in range(1, len(self.ips) - 1):
            self._path_paint.lineTo(self.ips[i])
        # end of for
        self._path_paint.lineTo(self.ips[-1])


        """
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
        """


    # def _identify_pos(self):
    #     super()._identify_pos()


    def _create_path(self):
        self._identify_pos()  # Identify the position of this link
        self._identify_connectors_pos()  # Identify the positions of connectors

        if self.is_straight():
            #print("This is Straight!")
            StraightLink._create_path(self)
        else:
            #print("This is Elbow!")
            self._create_elbow_path()

        # try:
        #     self._create_elbow_path()
        # except FloatingPointError:
        #     super(StraightLink, self)._create_path()

