# -*- coding: utf-8 -*-
"""
Identifying sub-control points (sps), Q and D points
for quadratic Bezier curve with a width is based on
the following article:

"Quadratic bezier offsetting with selective subdivision"
by Gabriel Suchowolski, Jul 10, 2012

http://microbians.com/?page=math&id=math-quadraticbezieroffseting
"""

import numpy as np

from cachetools import cached

from qtpy.QtCore import QPointF

from nezzle.utils import dist
from nezzle.utils import dot
from nezzle.utils import length
from nezzle.utils import internal_division
from nezzle.utils import solve_cubic
from nezzle.utils import rotate


def _calc_coeff(w0, w1, w2, wx):
    A = w0 - 2 * w1 + w2
    B = 2 * (w1 - w0)
    C = w0 - wx
    D = B ** 2 - 4 * A * C
    return A, B, C, D

def _solve_quad(coeff):
    A, B, C, D = coeff
    if A != 0:
        D = np.sqrt(D)
        s1 = (-B + D)/(2*A)
        s2 = (-B - D)/(2*A)
        sols = []

        # The parameter should be within [0, 1].
        if 0 <= s1 <= 1.0:
            sols.append(s1)
        if 0 <= s2 <= 1.0:
            sols.append(s2)

        return sols
    else:
        s = -C / B
        return [s]

def _is_on_the_curve(cps, pt, t):
    """
    Parameters
    ----------
    cps: The control points of quadratic Bezier curve.
    pt: Point to be checked.
    t: The quadratic Bezier curve parameter corresponding to pt.
    """
    p0, p1, p2 = cps
    px = (1-t)**2*p0 + 2*(1-t)*t*p1 + t** 2*p2
    return np.allclose((pt.x(), pt.y()), (px.x(), px.y()))


def identify_parameter(cps, pt):
    p0, p1, p2 = cps
    coeff_x = _calc_coeff(p0.x(), p1.x(), p2.x(), pt.x())
    sols_x = _solve_quad(coeff_x)
    for t in sols_x:
        if _is_on_the_curve(cps, pt, t):
            return t

    raise ValueError("There is no solution to find the correct t.")


def _integrate_sqrt_quad(coeff, p, q):
    """
    An exact solution of integrating sqrt(a*x^2 + b*x + c) within (p, q)

    Paramters
    ---------
    coeff: A sequence of the coefficients, (a, b, c)
    p, q: Integrating range, (p, q)
    """
    a, b, c = coeff

    def F(x):  # The function of definite integral
        f = np.sqrt(a*x**2 + b*x + c)
        g = (2*a*x + b) / (a**0.5) + 2*f
        return (b/(4.*a) + 0.5*x)*f+(4*a*c-b**2)/(8*a**(1.5))*np.log(g)

    return F(q) - F(p)


def arc_length(cps, t1, t2):
    """
    The arc length of quadratic Bezier curve, given (t1, t2)

    cps: The control points of quadratic Bezier curve.
    t1: The parameter value at the beginning.
    t2: The parameter value at the end.

    x'(t)^2 = 4*((P-Q)^2*t^2 -2*P*(P-Q)*t + P^2)
    y'(t)^2 = 4*((R-S)^2*t^2 -2*R*(R-S)*t + R^2)

    Integrate 2*sprt(x'(t)^2 + y'(t)^2) for (t1, t2)
    """

    p0, p1, p2 = cps

    P = p1.x() - p0.x()
    Q = p2.x() - p1.x()
    R = p1.y() - p0.y()
    S = p2.y() - p1.y()

    A = (P - Q) ** 2 + (R - S) ** 2
    B = -2 * ((P - Q) * P + (R - S) * R)
    C = P ** 2 + R ** 2

    return 2 * _integrate_sqrt_quad((A, B, C), t1, t2)


def nearest_point(cps, pa):
    """
    Find the nearest point of the quadratic bezier curve
    from the control point

    cps: sequence of control points (QPointF)
    pa: arbitrary point
    """
    p1 = cps[0]
    pc = cps[1]
    p2 = cps[2]

    coords_x = 1e8*np.array([p1.x(), p2.x(), pc.x(), pa.x()])
    coords_y = 1e8*np.array([p1.y(), p2.y(), pc.y(), pa.y()])

    mean_x = np.average(coords_x)
    mean_y = np.average(coords_y)

    sv_x = np.std(coords_x)
    sv_y = np.std(coords_y)

    sv_x = sv_x if sv_x != 0 else 1.0
    sv_y = sv_y if sv_y != 0 else 1.0

    p1_scaled = QPointF((p1.x()-mean_x)/sv_x, (p1.y()-mean_y)/sv_y)
    p2_scaled = QPointF((p2.x()-mean_x)/sv_x, (p2.y()-mean_y)/sv_y)
    pc_scaled = QPointF((pc.x()-mean_x)/sv_x, (pc.y()-mean_y)/sv_y)
    pa_scaled = QPointF((pa.x()-mean_x)/sv_x, (pa.y()-mean_y)/sv_y)

    v0 = pc_scaled - p1_scaled
    v1 = p2_scaled - pc_scaled
    v3 = pa_scaled - p1_scaled

    diff_v1v0 = v1 - v0
    sq_diff_v1v0 = diff_v1v0.x()**2 + diff_v1v0.y()**2
    sq_v0 = v0.x()**2 + v0.y()**2

    a = sq_diff_v1v0  # dot((v1 - v0), (v1 - v0))
    b = 3*(dot(v1, v0) - sq_v0)  # 3*(dot(v1, v0) - dot(v0, v0))
    c = 2*sq_v0 - dot(v3, diff_v1v0)  # 3*dot(v0, v0) - dot(v1, v0)
    d = -dot(v3, v0)

    #print("Nearest point cps: ", [p1, pc, p2])
    #print("Scaled cps:", [p1_scaled, pc_scaled, p2_scaled])
    #print("a, b, c, d", a, b, c, d)

    sols = solve_cubic(a, b, c, d)
    t = sols[0]
    f = a*t**3 + b*t**2 + c*t + d

    #print("t: ", t)
    #print("Assign: ", f)
    #assert np.abs(f)<1e-1
    assert np.allclose(np.imag(t), 0)
    t = np.real(t)

    if t<0 or t>1:
        raise FloatingPointError("Abnormal value for parameter, t: %f"%(t))

    pt = (1-t)**2*p1 + 2*t*(1-t)*pc + t**2*p2
    return pt, t


def identify_sps(cps):
    pt0 = cps[0]
    pc = cps[1]
    pt4 = cps[2]

    pt2, t2 = nearest_point(cps, pc)

    # Control points of subdivision
    p11 = internal_division(pt0, pc, t2, 1 - t2)
    p12 = internal_division(pc, pt4, t2, 1 - t2)

    pt1, t1 = nearest_point((pt0, p11, pt2), p11)
    pt3, t3 = nearest_point((pt2, p12, pt4), p12)

    c01 = internal_division(pt0, p11, t1, 1 - t1)
    c12 = internal_division(p11, pt2, t1, 1 - t1)
    c23 = internal_division(pt2, p12, t3, 1 - t3)
    c34 = internal_division(p12, pt4, t3, 1 - t3)

    return [pt0, c01, pt1, c12, pt2, c23, pt3, c34, pt4]


def identify_qps(sps, width):

    qps_top = []
    qps_bottom = []

    for i in range(0, len(sps)-1, 2):
        p, cp = sps[i], sps[i+1]
        q_top = rotate(p, cp, -90, width/2)
        q_bottom = rotate(p, cp, 90, width/2)
        qps_top.append(q_top)
        qps_bottom.append(q_bottom)

    q_top = rotate(sps[-1], sps[-2], 90, width/2)
    q_bottom = rotate(sps[-1], sps[-2], -90, width/2)
    qps_top.append(q_top)
    qps_bottom.append(q_bottom)

    return qps_top, qps_bottom


def identify_dps(sps, width):
    dps_top = []
    dps_bottom =[]

    for i in range(1, len(sps), 2):
        p1, cp, p2 = sps[i-1], sps[i], sps[i+1]
        d_top = identify_dp(cp, p1, p2, width, 1)
        d_bottom = identify_dp(cp, p1, p2, width, -1)
        dps_top.append(d_top)
        dps_bottom.append(d_bottom)

    return dps_top, dps_bottom


def identify_dp(ap, p1, p2, width, angle_sign):
    m1 = rotate(ap, p1, angle_sign*90, 1.0) - ap
    m2 = rotate(ap, p2, -angle_sign*90, 1.0) - ap
    m = m1 + m2
    k = m*width/dot(m, m)
    return ap + k