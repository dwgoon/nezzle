import math

from qtpy.QtCore import QPointF

from nezzle.utils.math import reflect_yaxis, reflect_xaxis


class BaseTransform(object):

    def __call__(self, pos_point, pos_head=None):
        raise NotImplemented()


class Rotate(BaseTransform):
    def __init__(self, angle=None):
        self._angle = None
        self._cos = 1.0
        self._sin = 0.0
        if angle is not None:
            self.angle = angle

    def __call__(self, pos_point, pos_head=None):
        # Pure rotation of pos_point around pos_head by self._angle degrees
        # (same matrix as QTransform.rotate: x' = x*cos - y*sin,
        # y' = x*sin + y*cos). cos/sin are precomputed in the angle setter,
        # since a single head rotates 5-6 points with the same angle.
        hx = pos_head.x()
        hy = pos_head.y()
        vx = pos_point.x() - hx
        vy = pos_point.y() - hy
        c = self._cos
        s = self._sin
        return QPointF(hx + vx * c - vy * s, hy + vx * s + vy * c)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, val):
        self._angle = val
        rad = math.radians(val)
        self._cos = math.cos(rad)
        self._sin = math.sin(rad)


class Reflect(BaseTransform):
    def __init__(self, axis):
        if axis in [0, "y"]:
            self._reflect = reflect_yaxis
        elif axis in [1, "x"]:
            self._reflect = reflect_xaxis

    def __call__(self, pos_point, pos_head=None):
        return self._reflect(pos_head, pos_point)