"""
Identifying sub-control points (sps), Q and D points
for quadratic Bezier curve with a width is based on
the following article:

"Quadratic bezier offsetting with selective subdivision"
by Gabriel Suchowolski, Jul 10, 2012

http://microbians.com/?page=math&id=math-quadraticbezieroffseting
"""

import math
from typing import Union
import numpy as np
# from cachetools import cached

from qtpy.QtCore import QPointF

from nezzle.utils import dist
from nezzle.utils import dot
from nezzle.utils import length
from nezzle.utils import internal_division
from nezzle.utils import solve_cubic
from nezzle.utils import rotate


def _rot90_scaled(ap_x, ap_y, rp_x, rp_y, sign, tlen):
    """Rotate (rp_x, rp_y) around (ap_x, ap_y) by sign*90 degrees in Qt screen
    coords (y-down, clockwise positive) and scale the resulting vector so its
    length equals ``tlen``. Returns the rotated point as raw floats.

    Equivalent to ``rotate(ap, rp, sign*90, tlen)`` but avoids the per-call
    QTransform allocation + 5 Qt FFI hops, which dominate cost in the offset
    pipeline.
    """
    vx = rp_x - ap_x
    vy = rp_y - ap_y
    len_v = math.sqrt(vx * vx + vy * vy)
    if len_v == 0.0:
        return rp_x, rp_y
    s = tlen / len_v
    if sign > 0:  # +90 deg in Qt (cw in screen coords): (x,y) -> (-y, x)
        nx = -vy * s
        ny = vx * s
    else:  # -90 deg: (x,y) -> (y, -x)
        nx = vy * s
        ny = -vx * s
    return ap_x + nx, ap_y + ny


# def _integrate_sqrt_quad(coeff: np.ndarray, bounds: np.ndarray) -> float:
#     """
#     An exact solution of integrating sqrt(a*x^2 + b*x + c) over bounds.
#
#     Args:
#         coeff: A sequence of the coefficients, (a, b, c).
#         bounds: Upper nad lower bounds.
#     """
#
#     if np.abs(bounds[0] - bounds[1]) < 1e-5:
#         return 0.0
#
#     a, b, c = coeff
#
#     """
#     # The function of definite integral
#     # (1) Calcuate Fq
#     f = np.sqrt(a*q**2 + b*q + c)
#     g = (2*a*q + b) / (a**0.5) + 2*f
#     Fq = (b/(4.*a) + 0.5*q)*f+(4*a*c-b**2)/(8*a**(1.5))*np.log(g)
#
#     # (2) Calculate Fp
#     f = np.sqrt(a*p**2 + b*p + c)
#     g = (2 * a * p + b) / (a ** 0.5) + 2 * f
#     Fp = (b / (4. * a) + 0.5 * p) * f + (4 * a * c - b ** 2) / (8 * a ** (1.5)) * np.log(g)
#     """
#
#     f = np.sqrt(a * bounds ** 2 + b * bounds + c)
#     g = (2 * a * bounds + b) / (a ** 0.5) + 2 * f
#     F = (b / (4. * a) + 0.5 * bounds) * f + (4 * a * c - b ** 2) / (8 * a ** (1.5)) * np.log(g)
#     return F[1] - F[0]
#
#
# def arc_length(x: np.ndarray, y: np.ndarray, t1: float, t2: float) -> float:
#     """
#     The arc length of quadratic Bezier curve, given (t1, t2)
#
#     Args:
#         x: The x-axis coordinates of the three control points of quadratic Bezier curve.
#         y: The x-axis coordinates of the three control points of quadratic Bezier curve.
#         t1: The lower bound.
#         t2: The upper bound.
#
#     '''math
#     x'(t)^2 = 4*((P-Q)^2*t^2 -2*P*(P-Q)*t + P^2)
#     y'(t)^2 = 4*((R-S)^2*t^2 -2*R*(R-S)*t + R^2)
#     '''
#
#     Integrate 2*\sprt{x'(t)^2 + y'(t)^2} over (t1, t2)
#     """
#
#     #p0, p1, p2 = cps
#
#     p = x[1] - x[0]  #p1.x() - p0.x()
#     q = x[2] - x[1]  #p2.x() - p1.x()
#     r = y[1] - y[0]  #p1.y() - p0.y()
#     s = y[2] - y[1]  #p2.y() - p1.y()
#
#     coeff = np.zeros(3, dtype=np.float64)
#     coeff[0] = (p - q) ** 2 + (r - s) ** 2
#     coeff[1] = -2 * ((p - q) * p + (r - s) * r)
#     coeff[2] = p ** 2 + r ** 2
#
#     return 2 * _integrate_sqrt_quad(coeff, np.array([t1, t2]))

def _integrate_sqrt_quad(coeff: np.ndarray,
                         lower: Union[np.ndarray, float],
                         upper: Union[np.ndarray, float]) -> Union[np.ndarray, float]:
    """
    An exact solution of integrating sqrt(a*x^2 + b*x + c) over bounds.

    Args:
        coeff: A sequence of the coefficients, (a, b, c).
        bounds: Upper nad lower bounds.
    """

    a, b, c = coeff


    # The function of definite integral
    # (1) Calcuate Fl (lower)
    f = np.sqrt(a*lower**2 + b*lower + c)
    g = (2*a*lower + b) / (a**0.5) + 2*f
    Fl = (b/(4.*a) + 0.5*lower)*f+(4*a*c-b**2)/(8*a**(1.5))*np.log(g)

    # (2) Calculate Fu (upper)
    f = np.sqrt(a*upper**2 + b*upper + c)
    g = (2 * a * upper + b) / (a ** 0.5) + 2 * f
    Fu = (b / (4. * a) + 0.5 * upper) * f + (4 * a * c - b ** 2) / (8 * a ** (1.5)) * np.log(g)

    return Fu - Fl


def arc_length(x: np.ndarray,
               y: np.ndarray,
               lower: Union[np.ndarray, float],
               upper: Union[np.ndarray, float]) -> Union[np.ndarray, float]:
    """
    The arc length of quadratic Bezier curve, given (t1, t2)

    Args:
        x: The x-axis coordinates of the three control points of quadratic Bezier curve.
        y: The x-axis coordinates of the three control points of quadratic Bezier curve.
        lower: The lower bound.
        upper: The upper bound.

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

    return 2 * _integrate_sqrt_quad(coeff, lower, upper)



def _arc_length_scalar(a, b, c, lower, upper):
    """Pure-Python scalar version of ``2 * integrate_sqrt_quad(coeff, lo, hi)``.

    Avoids numpy ufunc overhead on scalars. Returns ``2 * (F(upper) - F(lower))``
    where ``F(t) = int sqrt(a*t^2 + b*t + c) dt``.
    """
    sqrt_a = math.sqrt(a)
    inv_4a = 0.25 / a
    inv_8a32 = 1.0 / (8.0 * a * sqrt_a)
    coef_log = (4.0 * a * c - b * b) * inv_8a32

    fl = math.sqrt(a * lower * lower + b * lower + c)
    gl = (2.0 * a * lower + b) / sqrt_a + 2.0 * fl
    Fl = (b * inv_4a + 0.5 * lower) * fl + coef_log * math.log(gl)

    fu = math.sqrt(a * upper * upper + b * upper + c)
    gu = (2.0 * a * upper + b) / sqrt_a + 2.0 * fu
    Fu = (b * inv_4a + 0.5 * upper) * fu + coef_log * math.log(gu)

    return 2.0 * (Fu - Fl)


def find_t_for_arclen(p1, pc, p2, target_len, t_min=0.5, t_max=1.0):
    """Find ``t in [t_min, t_max]`` such that the arc length of the quadratic
    Bezier ``B(s) = (1-s)^2 p1 + 2s(1-s) pc + s^2 p2`` from ``t`` to 1 equals
    ``target_len``.

    Closed-form 2-term Taylor expansion of L(u) = arc_length(1-u, 1) around
    u=0 seeds a safeguarded (bracketed) Newton iteration on the exact
    closed-form arc length. L(t, 1) is strictly decreasing in t, so the
    bisection fallback guarantees convergence even on near-cusp curves where
    |B'(t)| has a sharp interior minimum and a raw Newton step would
    overshoot. Allocation-free, <= 8 scalar arc-length evaluations (typically
    1-2) — still ~2 orders of magnitude cheaper than the old 500-sample scan.

    Returns ``t_max`` for degenerate inputs (target_len <= 0, zero tangent at
    endpoint, or the whole [t_min, 1] arc shorter than target_len — the head
    is hidden at the target node, matching the old scan's fallback).
    """
    if target_len <= 0.0:
        return t_max

    px = pc.x() - p1.x();  qx = p2.x() - pc.x()
    py = pc.y() - p1.y();  qy = p2.y() - pc.y()

    # |B'(1)| = 2 * |p2 - pc|
    speed1_sq = qx * qx + qy * qy
    if speed1_sq < 1e-24:
        return t_max
    alpha = 2.0 * math.sqrt(speed1_sq)            # = |B'(1)|

    # Coefficients of |B'(s)|^2 / 4 = a*s^2 + b*s + c (match _integrate_sqrt_quad)
    a = (px - qx) * (px - qx) + (py - qy) * (py - qy)
    b = -2.0 * ((px - qx) * px + (py - qy) * py)
    c = px * px + py * py

    # L(u) ~ alpha*u - gamma*u^2 with gamma = (2a + b) / alpha
    # (from L'(0)=alpha, L''(0)=-2(2a+b)/alpha)
    gamma = (2.0 * a + b) / alpha

    if abs(gamma) < 1e-9 or abs(a) < 1e-12:
        u = target_len / alpha                     # first-order fallback
    else:
        disc = alpha * alpha - 4.0 * gamma * target_len
        if disc < 0.0:
            u = target_len / alpha                 # Taylor regime exceeded
        else:
            # Smaller root → physical (u → 0 as target_len → 0)
            u = (alpha - math.sqrt(disc)) / (2.0 * gamma)

    t = 1.0 - u

    # Safeguarded Newton refinement on the exact arc length. The Taylor
    # estimate is only trustworthy when |B'| varies mildly over [t, 1]; on
    # near-cusp curves it lands far from the root and an unguarded Newton
    # step divides by a tiny |B'(t)| and overshoots through the interior
    # speed minimum. Bracketing [lo, hi] + bisection fallback makes the
    # iteration unconditionally convergent (L(t, 1) is monotone in t).
    if abs(a) > 1e-12:
        try:
            if _arc_length_scalar(a, b, c, t_min, 1.0) < target_len:
                return t_max  # No solution in range: hide head at the node.

            lo, hi = t_min, t_max
            if not (lo < t < hi):
                t = 0.5 * (lo + hi)

            for _ in range(8):
                L_at_t = _arc_length_scalar(a, b, c, t, 1.0)
                err = L_at_t - target_len
                if abs(err) <= 5e-3 * target_len:
                    break
                if err > 0.0:  # Too much remaining length -> move t up.
                    lo = t
                else:
                    hi = t
                # F(t) = L(t,1) - target; F'(t) = -|B'(t)| = -2*sqrt(speed_sq)
                speed_t_sq = a * t * t + b * t + c
                if speed_t_sq > 1e-18:
                    t_new = t + err / (2.0 * math.sqrt(speed_t_sq))
                else:
                    t_new = 0.5 * (lo + hi)
                if not (lo < t_new < hi):
                    t_new = 0.5 * (lo + hi)  # Bisect when Newton escapes.
                t = t_new
        except (ValueError, ZeroDivisionError):
            pass  # keep the Taylor estimate

    if t < t_min:
        return t_min
    if t > t_max:
        return t_max
    return t


def nearest_point(cps, pa):
    """
    Find the nearest point of the quadratic bezier curve
    from the control point

    cps: sequence of control points (QPointF)
    pa: arbitrary point
    """
    p1, pc, p2 = cps[0], cps[1], cps[2]

    p1x, p1y = p1.x(), p1.y()
    pcx, pcy = pc.x(), pc.y()
    p2x, p2y = p2.x(), p2.y()
    pax, pay = pa.x(), pa.y()

    # Numerical conditioning: scale by 1e8 then standardize across the 4 points.
    # Preserves the numerical behavior of the original implementation but
    # avoids 4x numpy array allocations + np.average/np.std for size-4 inputs.
    SCALE = 1e8
    sx0 = p1x * SCALE; sy0 = p1y * SCALE
    sx1 = p2x * SCALE; sy1 = p2y * SCALE
    sx2 = pcx * SCALE; sy2 = pcy * SCALE
    sx3 = pax * SCALE; sy3 = pay * SCALE

    mean_x = (sx0 + sx1 + sx2 + sx3) * 0.25
    mean_y = (sy0 + sy1 + sy2 + sy3) * 0.25

    dx0 = sx0 - mean_x; dy0 = sy0 - mean_y
    dx1 = sx1 - mean_x; dy1 = sy1 - mean_y
    dx2 = sx2 - mean_x; dy2 = sy2 - mean_y
    dx3 = sx3 - mean_x; dy3 = sy3 - mean_y

    var_x = (dx0 * dx0 + dx1 * dx1 + dx2 * dx2 + dx3 * dx3) * 0.25
    var_y = (dy0 * dy0 + dy1 * dy1 + dy2 * dy2 + dy3 * dy3) * 0.25
    sv_x = math.sqrt(var_x) if var_x > 0 else 1.0
    sv_y = math.sqrt(var_y) if var_y > 0 else 1.0

    inv_sx = 1.0 / sv_x
    inv_sy = 1.0 / sv_y

    p1xs = dx0 * inv_sx; p1ys = dy0 * inv_sy
    p2xs = dx1 * inv_sx; p2ys = dy1 * inv_sy
    pcxs = dx2 * inv_sx; pcys = dy2 * inv_sy
    paxs = dx3 * inv_sx; pays = dy3 * inv_sy

    # v0 = pc - p1, v1 = p2 - pc, v3 = pa - p1
    v0x = pcxs - p1xs; v0y = pcys - p1ys
    v1x = p2xs - pcxs; v1y = p2ys - pcys
    v3x = paxs - p1xs; v3y = pays - p1ys

    diffx = v1x - v0x
    diffy = v1y - v0y

    sq_diff = diffx * diffx + diffy * diffy
    sq_v0 = v0x * v0x + v0y * v0y
    dot_v1v0 = v1x * v0x + v1y * v0y
    dot_v3_diff = v3x * diffx + v3y * diffy
    dot_v3_v0 = v3x * v0x + v3y * v0y

    a = sq_diff
    b = 3 * (dot_v1v0 - sq_v0)
    c = 2 * sq_v0 - dot_v3_diff
    d = -dot_v3_v0

    sols = solve_cubic(a, b, c, d)
    t = sols[0]

    if t < 0 or t > 1:
        raise FloatingPointError("Abnormal value for parameter, t: %f" % (t))

    # Evaluate the Bezier point in ORIGINAL (unscaled) coords.
    one_minus_t = 1.0 - t
    w0 = one_minus_t * one_minus_t
    w1 = 2.0 * t * one_minus_t
    w2 = t * t
    pt = QPointF(
        w0 * p1x + w1 * pcx + w2 * p2x,
        w0 * p1y + w1 * pcy + w2 * p2y,
    )
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
    hw = width * 0.5

    for i in range(0, len(sps)-1, 2):
        p, cp = sps[i], sps[i+1]
        px, py = p.x(), p.y()
        cpx, cpy = cp.x(), cp.y()
        tx, ty = _rot90_scaled(px, py, cpx, cpy, -1, hw)
        bx, by = _rot90_scaled(px, py, cpx, cpy, +1, hw)
        qps_top.append(QPointF(tx, ty))
        qps_bottom.append(QPointF(bx, by))

    p_last = sps[-1]
    p_prev = sps[-2]
    plx, ply = p_last.x(), p_last.y()
    ppx, ppy = p_prev.x(), p_prev.y()
    tx, ty = _rot90_scaled(plx, ply, ppx, ppy, +1, hw)
    bx, by = _rot90_scaled(plx, ply, ppx, ppy, -1, hw)
    qps_top.append(QPointF(tx, ty))
    qps_bottom.append(QPointF(bx, by))

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
    apx, apy = ap.x(), ap.y()

    # m1 = unit vector from ap to p1 rotated by angle_sign*90
    r1x, r1y = _rot90_scaled(apx, apy, p1.x(), p1.y(), angle_sign, 1.0)
    m1x = r1x - apx
    m1y = r1y - apy

    # m2 = unit vector from ap to p2 rotated by -angle_sign*90
    r2x, r2y = _rot90_scaled(apx, apy, p2.x(), p2.y(), -angle_sign, 1.0)
    m2x = r2x - apx
    m2y = r2y - apy

    mx = m1x + m2x
    my = m1y + m2y
    m_dot_m = mx * mx + my * my
    if m_dot_m == 0.0:
        return QPointF(apx, apy)
    k = width / m_dot_m
    return QPointF(apx + mx * k, apy + my * k)