"""
Identifying sub-control points (sps), Q and D points
for quadratic Bezier curve with a width is based on
the following article:

"Quadratic bezier offsetting with selective subdivision"
by Gabriel Suchowolski, Jul 10, 2012

http://microbians.com/?page=math&id=math-quadraticbezieroffseting
"""

import numpy as np
# from cachetools import cached

from qtpy.QtCore import QPointF

from nezzle.utils import dist
from nezzle.utils import dot
from nezzle.utils import length
from nezzle.utils import internal_division
from nezzle.utils import solve_cubic
from nezzle.utils import rotate


def _integrate_sqrt_quad(coeff: np.ndarray, bounds: np.ndarray) -> float:
    """
    An exact solution of integrating sqrt(a*x^2 + b*x + c) over bounds.

    Args:
        coeff: A sequence of the coefficients, (a, b, c).
        bounds: Upper nad lower bounds.
    """

    if np.abs(bounds[0] - bounds[1]) < 1e-5:
        return 0.0

    a, b, c = coeff

    """
    # The function of definite integral
    # (1) Calcuate Fq
    f = np.sqrt(a*q**2 + b*q + c)
    g = (2*a*q + b) / (a**0.5) + 2*f
    Fq = (b/(4.*a) + 0.5*q)*f+(4*a*c-b**2)/(8*a**(1.5))*np.log(g)

    # (2) Calculate Fp
    f = np.sqrt(a*p**2 + b*p + c)
    g = (2 * a * p + b) / (a ** 0.5) + 2 * f
    Fp = (b / (4. * a) + 0.5 * p) * f + (4 * a * c - b ** 2) / (8 * a ** (1.5)) * np.log(g)
    """

    f = np.sqrt(a * bounds ** 2 + b * bounds + c)
    g = (2 * a * bounds + b) / (a ** 0.5) + 2 * f
    F = (b / (4. * a) + 0.5 * bounds) * f + (4 * a * c - b ** 2) / (8 * a ** (1.5)) * np.log(g)
    return F[1] - F[0]


def arc_length(x: np.ndarray, y: np.ndarray, t1: float, t2: float) -> float:
    """
    The arc length of quadratic Bezier curve, given (t1, t2)

    Args:
        x: The x-axis coordinates of the three control points of quadratic Bezier curve.
        y: The x-axis coordinates of the three control points of quadratic Bezier curve.
        t1: The lower bound.
        t2: The upper bound.

    '''math
    x'(t)^2 = 4*((P-Q)^2*t^2 -2*P*(P-Q)*t + P^2)
    y'(t)^2 = 4*((R-S)^2*t^2 -2*R*(R-S)*t + R^2)
    '''

    Integrate 2*\sprt{x'(t)^2 + y'(t)^2} over (t1, t2)
    """

    #p0, p1, p2 = cps

    p = x[1] - x[0]  #p1.x() - p0.x()
    q = x[2] - x[1]  #p2.x() - p1.x()
    r = y[1] - y[0]  #p1.y() - p0.y()
    s = y[2] - y[1]  #p2.y() - p1.y()

    coeff = np.zeros(3, dtype=np.float64)
    coeff[0] = (p - q) ** 2 + (r - s) ** 2
    coeff[1] = -2 * ((p - q) * p + (r - s) * r)
    coeff[2] = p ** 2 + r ** 2

    return 2 * _integrate_sqrt_quad(coeff, np.array([t1, t2]))


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