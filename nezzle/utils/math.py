"""
Utility functions for mathematical calculation.
"""

import math as _math
import numpy as np

from qtpy.QtCore import QLineF
from qtpy.QtCore import QPointF
from qtpy.QtGui import QVector2D


def _cbrt_signed(x):
    """Real cube root that handles negative inputs (like np.cbrt).

    ``x ** (1/3)`` returns a complex number for negative x in Python, so
    this helper mimics np.cbrt without the numpy overhead.
    """
    if x < 0.0:
        return -((-x) ** (1.0 / 3.0))
    return x ** (1.0 / 3.0)


def dot(v1, v2):
    """Calculate the dot product of two vectors.

    It is equal to v1.x()*v2.x() + v1.y()*v2.y().

    This function is a simple wrapper of
    QPointF.dotProduct(v1, v2).

    Args:
        v1 : QPointF
            First vector from the origin.
        v2 : QPointF
            Second vector from the origin.

    Returns:
        dp : float
            Dot product of the two vectors.

    Examples:
        >>> v1 = QPointF(1, 2)
        >>> v2 = QPointF(2, 4)
        >>> dot(v1, v2)
        10.0

        >>> v1 = QPointF(1, 1)
        >>> v2 = QPointF(10, 10)
        >>> dot(v1, v2)
        20.0
    """
    return QPointF.dotProduct(v1, v2)


def length(v):
    """Calculate the length of a vector.

    Args:
        v : QPointF
            A vector from the origin.

    Returns:
        len : float
            Length of the vector, v.

    Examples:
        >>> v1 = QPointF(1, 0)
        >>> length(v1)
        1.0

        >>> v1 = QPointF(1, 1)
        >>> length(v1)
        1.4142135623730951

        >>> import math
        >>> length(v1) == np.sqrt(2)
        True
    """
    x = v.x()
    y = v.y()
    return _math.sqrt(x * x + y * y)


def dist(p1, p2):
    """Calculate the distance between two points.

    Args:
        p1 : QPointF
            First point
        p2 : QPointF
            Second point

    Returns:
        distance : float
            Distance between the two points.

    Examples:
        >>> a = QPointF(0, 10)
        >>> b = QPointF(10, 0)
        >>> dist(a, b)  # square root of 2
        14.142135623730951

    """
    dx = p1.x() - p2.x()
    dy = p1.y() - p2.y()
    return _math.sqrt(dx * dx + dy * dy)


def angle(v1, v2, radian=False):
    """Calculate the angle in degrees between two vectors.

    Args:
        v1 : QPointF
            First vector from the origin.
        v2 : QPointF
            Second vector from the origin.

    Returns:
        angle : float
            Angle between the two vectors, v1 and v2.

    Examples:
        >>> v1 = QPointF(10, 0)
        >>> v2 = QPointF(10, 10)
        >>> angle(v1, v2)
        45.00000000000001

        >>> v3 = QPointF(-10, 0)
        >>> angle(v1, v3)
        180.0

        >>> angle(v2, v3)
        135.0

        >>> v1 = QPointF()
    """

    len_v1 = length(v1)
    len_v2 = length(v2)

    theta = np.arccos(dot(v1, v2) / (len_v1 * len_v2))
    if radian:
        return theta  # in radian

    return np.degrees(theta)  # in degree

# def angle(v1, v2, radian=False):
#     """Get the angle between two vectors or points.
#     """
#     radian = np.pi / 180 if radian else 1
#
#     return QLineF(v1.x(), v1.y(), v2.x(), v2.y()).angle() * radian

def normal_vector(v):
    """Get the counter clock-wise normal vector for a given vector.
    """
    v = QVector2D(v.x(), v.y()).normalized()
    return QVector2D(-v.y(), v.x())


def internal_division(p1, p2, r1, r2):
    """Find the point internally dividing two points.

    ip = r2/(r1+r2)*p1 + r1/(r1+r2)*b

    (p1)---<r1>---(ip)---<r2>---(p2)


    Args:
        p1 : QPointF
            First point.
        p2 : QPointF
            Second point.
        r1 : float
            Ratio from the p1.
        r2 : float
            Ratio from the p2.

    Returns:
        ip : QPointF
            Internal point of the two points.

    Examples:
        >>> a = QPointF(0, 0)
        >>> b = QPointF(2, 0)
        >>> internal_division(a, b, 1, 1)
        PyQt5.QtCore.QPointF(1.0, 0.0)

        >>> c = QPointF(1, 1)
        >>> internal_division(a, c, 0.3, 0.7)
        PyQt5.QtCore.QPointF(0.3, 0.3)

        >>> internal_division(a, b, 2, 8)
        PyQt5.QtCore.QPointF(0.4, 0.0)
    """
    sum_r = r1 + r2
    f1 = r2 / sum_r
    f2 = r1 / sum_r
    return QPointF(f1 * p1.x() + f2 * p2.x(),
                   f1 * p1.y() + f2 * p2.y())


def solve_cubic(a, b, c, d):
    """Solve a cubic equation: a*x^3 + b*x^2+ c*x + d

    This is a Python version of the cubic equation solver [#F1]_.

    Args:
        a : float
            Coefficient of x^3.
        b : float
            Coefficient of x^2.
        c : float
            Coefficient of x.
        d : float
            Constant term.

    Returns:
        x : list
            Solutions of the cubic equation.
            The number of solutions is three at most.

    Examples:
        >>> solve_cubic(1, 0, 0, -1)
        [1.0]

        >>> solve_cubic(1, 0, 0, 1)
        [-1.0]

        >>> solve_cubic(1, -1, -4, 4)
        [1.9999999999999993, 1.0, -1.9999999999999998]

        >>> solve_cubic(3, -1, 1, 2)
        [-0.6666666666666663]

        >>> solve_cubic(1, -4, 3, 0)
        [3.0, 0.9999999999999997, 0.0]

    References:
         .. [#F1] Glassner, "Graphics Gems", 1993, Chapter 8.1,
           pp. 404-407.
    """

    # All inputs are scalars; using ``math.*`` avoids the ~30x overhead of
    # invoking numpy ufuncs on scalar arguments.
    A = b / a
    B = c / a
    C = d / a

    # Substitute x = y - A/3 to eliminate the quadratic term:
    # x^3 + px + q = 0
    sq_A = A * A
    p = (1.0 / 3.0) * (-(1.0 / 3.0) * sq_A + B)
    q = 0.5 * ((2.0 / 27.0) * A * sq_A - (1.0 / 3.0) * A * B + C)

    cb_p = p * p * p
    D = q * q + cb_p

    # Threshold matches the historical behavior of np.isclose(D, 1e-12)
    # (default atol=1e-8 dominates when comparing tiny values).
    _ZERO_TOL = 1e-8

    if abs(D) < _ZERO_TOL:
        if abs(q) < _ZERO_TOL:  # One triple solution
            sols = [0.0]
        else:  # One single and one double solution
            u = _cbrt_signed(-q)
            sols = [2.0 * u, -u]
    elif D < 0:  # Casus irreducibilis: three real solutions
        phi = (1.0 / 3.0) * _math.acos(-q / _math.sqrt(-cb_p))
        t = 2.0 * _math.sqrt(-p)
        s0 = t * _math.cos(phi)
        s1 = -t * _math.cos(phi + _math.pi / 3.0)
        s2 = -t * _math.cos(phi - _math.pi / 3.0)
        sols = [s0, s1, s2]
    else:  # One real solution
        sqrt_D = _math.sqrt(D)
        u = _cbrt_signed(sqrt_D - q)
        v = -_cbrt_signed(sqrt_D + q)
        sols = [u + v]

    sub = (1.0 / 3.0) * A
    return [s - sub for s in sols]


def rotate(ap, rp, angle, tlen=None):
    """Rotate a point clockwise with respect to the given axis.

    Args:
        ap : QPointF
            Axis point.
        rp : QPointF
            Point to be rotated.
        angle: float
            Angle in degree
        tlen : float (optional)
            Target length of the rotated point
            from the axis point.

    Returns:
        tp : QPointF
             Transformed point (i.e., rotated and scaled).

    Examples:
        >>> v1 = QPointF(1, 0)
        >>> org = QPointF(0, 0)
        >>> rotate(org, v1, 90)
        PyQt5.QtCore.QPointF(0.0, 1.0)

        >>> rotate(org, v1, 90, tlen=2.0)
        PyQt5.QtCore.QPointF(0.0, 2.0)

        >>> v1 = QPointF(1, 1)
        >>> rotate(org, v1, 45)
        PyQt5.QtCore.QPointF(0.0, 1.4142135623730951)
    """
    # Scalar math equivalent of the original QTransform pipeline
    # (translate/rotate/scale/translate + map). QTransform.rotate uses
    # x' = x*cos - y*sin, y' = x*sin + y*cos (clockwise on screen, y-down),
    # so the same matrix is applied here directly without the per-call
    # QTransform allocation and FFI hops.
    apx = ap.x(); apy = ap.y()
    vx = rp.x() - apx
    vy = rp.y() - apy
    len_v = _math.sqrt(vx * vx + vy * vy)

    if len_v == 0:
        return rp

    if not tlen:
        tlen = len_v

    k = tlen / len_v
    rad = _math.radians(angle)
    c = _math.cos(rad)
    s = _math.sin(rad)
    return QPointF(apx + (vx * c - vy * s) * k,
                   apy + (vx * s + vy * c) * k)


def reflect_yaxis(ap, rp):
    """Reflect a point with respect to the y-axis.

    Args:
        ap : QPointF
            Axis point.
        rp : QPointF
            Point to be reflected.

    Returns:
        tp : QPointF
             Transformed point.
    """

    # Temporary x-coord. (tx)
    tx = rp.x() - ap.x()  # Move the x-coord of origin to that of the axis point (ap).

    # New x-coord. (nx)
    nx = -tx + ap.x()  # Reflect and find the coordinates to the original origin.
    return QPointF(nx, rp.y())


def reflect_xaxis(ap, rp):
    """Reflect a point with respect to the x-axis.

    Args:
        ap : QPointF
            Axis point.
        rp : QPointF
            Point to be reflected.

    Returns:
        tp : QPointF
             Transformed point.
    """

    # Temporary y-coord. (ty)
    ty = rp.y() - ap.y()  # Move the x-coord of origin to that of the axis point (ap).

    # New x-coord. (ny)
    ny = -ty + ap.y()  # Reflect and find the coordinates to the original origin.
    return QPointF(rp.x(), ny)