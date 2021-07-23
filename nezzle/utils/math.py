# -*- coding: utf-8 -*-
"""
Utility functions for mathematical calculation.
"""

import numpy as np

from qtpy.QtCore import QPointF
from qtpy.QtGui import QTransform


def dot(v1, v2):
    """Calculate the dot product of two vectors.

    It is equal to v1.x()*v2.x() + v1.y()*v2.y().

    This function is a simple wrapper of
    QPointF.dotProduct(v1, v2).

    Parameters
    ----------
    v1 : QPointF
        First vector from the origin.
    v2 : QPointF
        Second vector from the origin.

    Returns
    -------
    dp : float
        Dot product of the two vectors.

    Examples
    --------
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

    Parameters
    ----------
    v : QPointF
        A vector from the origin.

    Returns
    -------
    len : float
        Length of the vector, v.

    Examples
    --------
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
    return np.sqrt(v.x()**2 + v.y()**2)


def dist(p1, p2):
    """Calculate the distance between two points.

    Parameters
    ----------
    p1 : QPointF
        First point
    p2 : QPointF
        Second point

    Returns
    -------
    distance : float
        Distance between the two points.

    Examples
    --------
    >>> a = QPointF(0, 10)
    >>> b = QPointF(10, 0)
    >>> dist(a, b)  # square root of 2
    14.142135623730951

    """
    diff = p1 - p2
    return np.sqrt(diff.x()**2 + diff.y()**2)


def angle(v1, v2):
    """Calculate the angle in degrees between two vectors.

    Parameters
    ----------
    v1 : QPointF
        First vector from the origin.
    v2 : QPointF
        Second vector from the origin.

    Returns
    -------
    angle : float
        Angle between the two vectors, v1 and v2.

    Examples
    --------
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
    return np.degrees(np.arccos(dot(v1, v2)/(len_v1*len_v2)))


def internal_division(p1, p2, r1, r2):
    """Find the point internally dividing two points.

    ip = r2/(r1+r2)*p1 + r1/(r1+r2)*b

    (p1)---<r1>---(ip)---<r2>---(p2)


    Parameters
    ----------
    p1 : QPointF
        First point.
    p2 : QPointF
        Second point.
    r1 : float
        Ratio from the p1.
    r2 : float
        Ratio from the p2.

    Returns
    -------
    ip : QPointF
        Internal point of the two points.

    Examples
    --------
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
    sum_r = r1+r2
    return (r2/sum_r*p1) + (r1/sum_r*p2)


def solve_cubic(a, b, c, d):
    """Solve a cubic equation: a*x^3 + b*x^2+ c*x + d

    This is a Python version of the cubic equation solver [#F1]_.

    Parameters
    ----------
    a : float
        Coefficient of x^3.
    b : float
        Coefficient of x^2.
    c : float
        Coefficient of x.
    d : float
        Constant term.

    Returns
    -------
    x : list
        Solutions of the cubic equation.
        The number of solutions is three at most.

    Examples
    --------
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

    References
    ----------
    .. [#F1] Glassner, "Graphics Gems", 1993, Chapter 8.1,
       pp. 404-407.
    """

    sols = []
    A = b / a
    B = c / a
    C = d / a

    # Substitute x = y - A/3 to eliminate quadratic term:
    # x^3 +px + q = 0

    sq_A = A * A
    p = 1.0/3 * (-1.0/3*sq_A + B)
    q = 1.0/2 * (2.0/27*A*sq_A - 1.0/3*A*B + C)

    # Use Cardano's formula
    cb_p = p * p * p
    D = q * q + cb_p

    if np.isclose(D, 1e-12):
        if np.isclose(q, 1e-12):  # One triple solution
            sols.append(0)
        else:  # One single and one double solution
            u = np.cbrt(-q)
            sols.append(2 * u)
            sols.append(-u)

    elif D < 0:  # Casus irreducibilis: three real solutions
        phi = 1.0/3 * np.arccos(-q/np.sqrt(-cb_p))
        t = 2*np.sqrt(-p)
        s0 = t*np.cos(phi)
        s1 = -t*np.cos(phi + np.pi/3)
        s2 = -t*np.cos(phi - np.pi/3)
        sols = [s0, s1, s2]
    else:  # one real solution
        sqrt_D = np.sqrt(D)
        u = np.cbrt(sqrt_D - q)
        v = - np.cbrt(sqrt_D + q)
        sols = [u + v]
    # end of if-else

    sub = 1.0/3*A
    for i, v in enumerate(sols):
        sols[i] -= sub

    return sols


def rotate(ap, rp, angle, tlen=None):
    """Rotate a point clockwise with respect to the given axis.

    Args:
        ap : QPointF
            Axis point.
        rp : QPointF
            Point to be rotated.
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
    transform = QTransform()
    v = rp - ap
    len_v = length(v)

    if len_v == 0:
        return rp

    if not tlen:
        tlen = len_v

    transform.translate(ap.x(), ap.y())
    transform.rotate(angle)
    transform.scale(tlen/len_v, tlen/len_v)
    transform.translate(-ap.x(), -ap.y())
    tp = transform.map(rp)  # Point which has been transformed
    return tp




