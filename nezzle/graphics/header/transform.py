
from nezzle.utils.math import rotate
from nezzle.utils.math import reflect_yaxis, reflect_xaxis


class BaseTransform(object):

    def __call__(self, pos_point, pos_header=None):
        raise NotImplemented()



class Rotate(BaseTransform):
    def __init__(self, angle=None):
        self._angle = angle

    def __call__(self, pos_point, pos_header=None):
        return rotate(pos_header, pos_point, self._angle)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, val):
        self._angle = val


class Reflect(BaseTransform):
    def __init__(self, axis):
        if axis in [0, "y"]:
            self._reflect = reflect_yaxis
        elif axis in [1, "x"]:
            self._reflect = reflect_xaxis

    def __call__(self, pos_point, pos_header=None):
        return self._reflect(pos_header, pos_point)