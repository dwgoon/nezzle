import traceback

import numpy as np

from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtCore import QLineF
from qtpy.QtCore import QRectF
from qtpy.QtGui import QVector2D
from qtpy.QtGui import QPen, QBrush, QColor
from qtpy.QtGui import QPainterPath
from qtpy.QtWidgets import QGraphicsItem

from nezzle.graphics.edges.straightedge import StraightEdge
from nezzle.graphics.edges.controlpoint import HorizontalConnectorControlPoint
from nezzle.graphics.edges.controlpoint import VerticalConnectorControlPoint

from nezzle.utils import angle
from nezzle.utils import dist
from nezzle.utils import dot
from nezzle.utils import internal_division
from nezzle.utils import normal_vector
from nezzle.utils import length
from nezzle.utils import rotate
from nezzle.graphics import quadbezier
from nezzle.graphics.mixins import Lockable

np.seterr('raise')


class ElbowEdge(StraightEdge):
    ITEM_TYPE = 'ELBOW_EDGE'

    def __init__(self, *args, **kwargs):
        self._ctrl_points = []
        self._t_head = 0

        # To avoid repetitive memory allocation, make this variable as a member.
        self._arr_t = np.arange(1, 0.5, -0.001, dtype=np.float64)
        super().__init__(*args, **kwargs)  # initialize() is called in the hierarchy of super().__init__

        for i in range(3):
            self._attr.set_trigger(f'CP{i}_POS_X',
                                   self._trigger_set_cp_pos_x,
                                   when='set')

            self._attr.set_trigger(f'CP{i}_POS_Y',
                                   self._trigger_set_cp_pos_y,
                                   when='set')


    @property
    def ctrl_points(self):
        return self._ctrl_points

    def _trigger_set_cp_pos_x(self, key, value):
        ix = int(key[2])
        cp = self._ctrl_points[ix]
        old_selected = cp.isSelected()
        cp.setSelected(True)
        cp.setX(value)
        cp.setSelected(old_selected)
        return value

    def _trigger_set_cp_pos_y(self, key, value):
        ix = int(key[2])
        cp = self._ctrl_points[ix]
        old_selected = cp.isSelected()
        cp.setSelected(True)
        cp.setY(value)
        cp.setSelected(old_selected)
        return value

    def initialize(self):
        self._identify_pos()
        self._create_connectors()
        self._create_control_items()
        self._create_subpoints()
        self._create_path()
        self._update_bounding_rect()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedHasChanged:
            self.update()

        return super().itemChange(change, value)

    def update(self):
        self.update_ctrl_points()
        super().update()

    def update_ctrl_points(self):
        for cp in self._ctrl_points:
            if not cp.isSelected():
                cp.update_pos_by_connectors()
                cp.update()

            if self.is_node_selected():
                cp.setVisible(False)
            else:
                cp.setVisible(True)

        # end of for

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        if self.isSelected():
            painter.setBrush(Qt.red)
            painter.drawEllipse(QPointF(-2.5, -2.5), 5, 5)
            painter.setPen(QColor(50, 50, 50, 100))

    def is_head_visible(self):
        if not self.head:
            return False

        v1 = self._cps[-2] - self._cps[-3]
        v2 = self.pos_head - self._cps[-3]
        ip = dot(v1, v2)  # Inner product
        return ip > 0  # Is v1.v2 = |v1||v2|cos(0) positive?

    def _create_connectors(self):
        self._pos_connectors = [QPointF(), QPointF(), QPointF(), QPointF()]

    def _create_subpoints(self):
        self._cps = []  # Central points
        self._fps = []  # Forward points
        self._bps = []  # Backward points

    def _create_control_items(self):
        raise NotImplementedError()

    def _identify_connectors_pos(self):
        raise NotImplementedError()

    def _identify_head_pos(self):
        offset = self._calculate_head_offset()

        pos_conn = self._cps[-3]
        pos_end = self._cps[-2]

        ph = internal_division(pos_conn, pos_end, dist(pos_conn, pos_end) - offset, offset)
        self.pos_head.setX(ph.x())
        self.pos_head.setY(ph.y())

    def _calculate_head_angle(self):
        # pos_vc1 = self._pos_connectors[1]
        pos_begin = self._cps[-3]
        self._angle_head = -QLineF(pos_begin, self.pos_head).angle()
        self._head_transform.angle = self._angle_head
        # print("Head Angle:", self._angle_head)

    def _identify_head(self):
        self._identify_head_pos()
        self._calculate_head_angle()
        self._create_head_path()

    def _calculate_head_offset(self):
        """
        self._cps[-1]: dummy point
        self._cps[-2]: real point (the end of node)
        self._cps[-3]: previous connector (the tail of head)
        """

        v = self._cps[-2] - self._cps[-3]

        try:
            angle_rad = np.arccos(v.x()/length(v))
        except ZeroDivisionError:
            return 0
        except Exception as err:
            print(err)
            return 0

        radius = self.target.calculate_radius(angle_rad)
        return radius + self.head.offset + self.head.height

    def _create_head_path(self):
        points = self.head.identify_points(self.pos_head,
                                             self.width,
                                             self._head_transform)
        path = QPainterPath()

        path.moveTo(points[-1])
        for pt in points[-2::-1]:
            path.lineTo(pt)

        self._path_head = path

    def _identify_elbow_points(self):
        # Update positions of source and target
        self._cps.clear()
        self._cps.append(self.pos_src)  # Dummy point

        for i, pos in enumerate(self._pos_connectors):
            self._cps.append(pos)

        self._cps.append(self.pos_trg)

        ix_begin = 0
        ix_end = len(self._cps) - 1

        # Position of each connector with respect to the position of target
        len_cps = len(self._cps)
        for i in range(1, len_cps-1):
            pos_conn = self._cps[i]
            pos_conn_on_src = pos_conn - self.pos_src
            if self.source.contains(pos_conn_on_src):
                ix_begin = i

            break

        for i in range(len_cps-2, 1, -1):
            pos_conn = self._cps[i]
            pos_conn_on_trg = pos_conn - self.pos_trg
            if self.target.contains(pos_conn_on_trg):
                ix_end = i

            break

        if ix_end - ix_begin <= 1:
            self._cps = [self._cps[0], self._cps[0], self._cps[1], self._cps[-2], self._cps[-1], self._cps[-1]]
        else:
            self._cps = [self._cps[ix_begin]] + self._cps[ix_begin:ix_end + 1] + [self._cps[ix_end]]

        # print(f"(ix_begin, ix_end)=({ix_begin}, {ix_end})")


        hw = self.width / 2  # The half of width
        len_cps = len(self._cps)

        self._fps.clear()
        for i in range(1, len_cps-1):
            p0 = self._cps[i - 1]
            p1 = self._cps[i]
            p2 = self._cps[i + 1]
            v1 = QVector2D(p1 - p0)
            v2 = QVector2D(p2 - p1)

            nv1 = hw * normal_vector(v1)  # Normal vector of v1
            nv2 = hw * normal_vector(v2)  # Normal vector of v2
            self._fps.append(p1 + (nv1 + nv2).toPointF())
        # end of for

        self._bps.clear()
        for i in range(len_cps - 2, 0, -1):
            p0 = self._cps[i + 1]
            p1 = self._cps[i]
            p2 = self._cps[i - 1]
            v1 = QVector2D(p1 - p0)
            v2 = QVector2D(p2 - p1)

            nv1 = hw * normal_vector(v1)  # Normal vector of v1
            nv2 = hw * normal_vector(v2)  # Normal vector of v2
            self._bps.append(p1 + (nv1 + nv2).toPointF())
        # end of for

    def _create_elbow_path(self):
        self._identify_elbow_points()
        self._path_paint = QPainterPath()
        self._path_paint.setFillRule(Qt.WindingFill)

        if not self._fps or not self._bps:
            return

        # Forward line
        self._path_paint.moveTo(self._fps[0])
        for i in range(1, len(self._fps) - 1):
            self._path_paint.lineTo(self._fps[i])
        # end of for

        if self.head:  # Add the head
            self._identify_head()

        if self.is_head_visible():
            self._path_paint.connectPath(self._path_head)
        else:  # if head is not visible, hide the head.
            self._path_paint.lineTo(self._fps[-1])
            self._path_paint.lineTo(self._bps[0])

        # Backward line
        for i in range(1, len(self._bps)):
            self._path_paint.lineTo(self._bps[i])
        # end of for

    def _create_path(self):
        self._identify_pos()  # Identify the position of this edge
        self._identify_connectors_pos()  # Identify the positions of connectors
        try:
            # if self.is_straight():
            #     return super()._create_path()
            if self.are_nodes_close():
                return

            self._create_elbow_path()
        except Exception as err:
            traceback.print_exc()
            print(err)


@Lockable
class VerticalElbowEdge(ElbowEdge):

    ITEM_TYPE = 'VERTICAL_ELBOW_EDGE'

    def _create_control_items(self):
        m_st = internal_division(self.pos_src, self.pos_trg, 0.5, 0.5)
        m_sm = internal_division(self.pos_src, m_st, 0.5, 0.5)
        m_mt = internal_division(m_st, self.pos_trg, 0.5, 0.5)

        cp0 = VerticalConnectorControlPoint(iden="CP0", parent=self, pos=m_sm)
        cp0.append_connector(self._pos_connectors[0])
        cp0.append_connector(self._pos_connectors[1])
        self._ctrl_points.append(cp0)

        cp1 = HorizontalConnectorControlPoint(iden="CP1", parent=self, pos=m_st)
        cp1.append_connector(self._pos_connectors[1])
        cp1.append_connector(self._pos_connectors[2])
        self._ctrl_points.append(cp1)

        cp2 = VerticalConnectorControlPoint(iden="CP2", parent=self, pos=m_mt)
        cp2.append_connector(self._pos_connectors[2])
        cp2.append_connector(self._pos_connectors[3])
        self._ctrl_points.append(cp2)

    def _identify_connectors_pos(self):
        pos_cp0 = self._ctrl_points[0].pos()
        pos_cp1 = self._ctrl_points[1].pos()
        pos_cp2 = self._ctrl_points[2].pos()

        con0 = self._pos_connectors[0]
        con1 = self._pos_connectors[1]
        con2 = self._pos_connectors[2]
        con3 = self._pos_connectors[3]

        con0.setX(self.pos_src.x())
        con0.setY(pos_cp0.y())

        con1.setX(pos_cp1.x())
        con1.setY(pos_cp0.y())

        con2.setX(pos_cp1.x())
        con2.setY(pos_cp2.y())

        con3.setX(self.pos_trg.x())
        con3.setY(pos_cp2.y())


@Lockable
class HorizontalElbowEdge(ElbowEdge):

    ITEM_TYPE = 'HORIZONTAL_ELBOW_EDGE'

    def _create_control_items(self):
        m_st = internal_division(self.pos_src, self.pos_trg, 0.5, 0.5)
        m_sm = internal_division(self.pos_src, m_st, 0.5, 0.5)
        m_mt = internal_division(m_st, self.pos_trg, 0.5, 0.5)

        cp0 = HorizontalConnectorControlPoint(iden="CP0", parent=self, pos=m_sm)
        cp0.append_connector(self._pos_connectors[0])
        cp0.append_connector(self._pos_connectors[1])
        self._ctrl_points.append(cp0)

        cp1 = VerticalConnectorControlPoint(iden="CP1", parent=self, pos=m_st)
        cp1.append_connector(self._pos_connectors[1])
        cp1.append_connector(self._pos_connectors[2])
        self._ctrl_points.append(cp1)

        cp2 = HorizontalConnectorControlPoint(iden="CP2", parent=self, pos=m_mt)
        cp2.append_connector(self._pos_connectors[2])
        cp2.append_connector(self._pos_connectors[3])
        self._ctrl_points.append(cp2)

    def _identify_connectors_pos(self):
        pos_cp0 = self._ctrl_points[0].pos()
        pos_cp1 = self._ctrl_points[1].pos()
        pos_cp2 = self._ctrl_points[2].pos()

        con0 = self._pos_connectors[0]
        con1 = self._pos_connectors[1]
        con2 = self._pos_connectors[2]
        con3 = self._pos_connectors[3]

        con0.setX(pos_cp0.x())
        con0.setY(self.pos_src.y())

        con1.setX(pos_cp0.x())
        con1.setY(pos_cp1.y())

        con2.setX(pos_cp2.x())
        con2.setY(pos_cp1.y())

        con3.setX(pos_cp2.x())
        con3.setY(self.pos_trg.y())
