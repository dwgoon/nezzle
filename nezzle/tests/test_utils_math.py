# -*- coding: utf-8 -*-
"""Headless tests for nezzle.utils.math.

The scalar implementations of rotate/length/dist/internal_division replaced
QTransform/numpy pipelines for performance; these tests pin them to their
original reference behavior.
"""
import math
import random

import pytest
from qtpy.QtCore import QPointF
from qtpy.QtGui import QTransform

from nezzle.utils.math import (
    rotate,
    dist,
    length,
    internal_division,
    solve_cubic,
    reflect_xaxis,
    reflect_yaxis,
)


def _rotate_reference(ap, rp, angle, tlen=None):
    """The original QTransform-based implementation, kept as the oracle."""
    transform = QTransform()
    v = rp - ap
    len_v = math.hypot(v.x(), v.y())
    if len_v == 0:
        return rp
    if not tlen:
        tlen = len_v
    transform.translate(ap.x(), ap.y())
    transform.rotate(angle)
    transform.scale(tlen / len_v, tlen / len_v)
    transform.translate(-ap.x(), -ap.y())
    return transform.map(rp)


class TestRotate:
    def test_matches_qtransform_reference(self):
        rng = random.Random(123)
        for _ in range(2000):
            ap = QPointF(rng.uniform(-500, 500), rng.uniform(-500, 500))
            rp = QPointF(rng.uniform(-500, 500), rng.uniform(-500, 500))
            angle = rng.uniform(-720, 720)
            tlen = rng.choice([None, rng.uniform(0.1, 100.0)])

            expected = _rotate_reference(ap, rp, angle, tlen)
            actual = rotate(ap, rp, angle, tlen)

            assert actual.x() == pytest.approx(expected.x(), abs=1e-9)
            assert actual.y() == pytest.approx(expected.y(), abs=1e-9)

    def test_quarter_turns_in_screen_coords(self):
        org = QPointF(0, 0)
        # Qt screen coords are y-down: +90 degrees appears clockwise.
        p = rotate(org, QPointF(1, 0), 90)
        assert (p.x(), p.y()) == pytest.approx((0.0, 1.0), abs=1e-12)

        p = rotate(org, QPointF(1, 0), -90)
        assert (p.x(), p.y()) == pytest.approx((0.0, -1.0), abs=1e-12)

    def test_target_length_rescales(self):
        org = QPointF(0, 0)
        p = rotate(org, QPointF(1, 0), 90, tlen=2.0)
        assert (p.x(), p.y()) == pytest.approx((0.0, 2.0), abs=1e-12)

    def test_degenerate_zero_vector_returns_point(self):
        p = QPointF(3.0, 4.0)
        assert rotate(p, QPointF(3.0, 4.0), 37.0) == QPointF(3.0, 4.0)


class TestLengthDist:
    def test_length(self):
        assert length(QPointF(3, 4)) == pytest.approx(5.0)
        assert length(QPointF(1, 1)) == pytest.approx(math.sqrt(2))
        assert length(QPointF(0, 0)) == 0.0

    def test_dist(self):
        assert dist(QPointF(0, 10), QPointF(10, 0)) == pytest.approx(
            math.sqrt(200))
        assert dist(QPointF(-3, -4), QPointF(0, 0)) == pytest.approx(5.0)
        p = QPointF(7.5, -2.25)
        assert dist(p, p) == 0.0


class TestInternalDivision:
    def test_midpoint(self):
        ip = internal_division(QPointF(0, 0), QPointF(2, 0), 1, 1)
        assert ip == QPointF(1, 0)

    def test_asymmetric_ratios(self):
        ip = internal_division(QPointF(0, 0), QPointF(1, 1), 0.3, 0.7)
        assert (ip.x(), ip.y()) == pytest.approx((0.3, 0.3))

        ip = internal_division(QPointF(0, 0), QPointF(2, 0), 2, 8)
        assert (ip.x(), ip.y()) == pytest.approx((0.4, 0.0))

    def test_endpoints(self):
        p1 = QPointF(-5, 3)
        p2 = QPointF(11, -7)
        ip = internal_division(p1, p2, 0, 1)  # all weight on p1
        assert (ip.x(), ip.y()) == pytest.approx((p1.x(), p1.y()))
        ip = internal_division(p1, p2, 1, 0)  # all weight on p2
        assert (ip.x(), ip.y()) == pytest.approx((p2.x(), p2.y()))


class TestSolveCubic:
    def test_three_well_separated_real_roots(self):
        rng = random.Random(7)
        n_checked = 0
        while n_checked < 300:
            roots = sorted(rng.uniform(-5, 5) for _ in range(3))
            if min(b - a for a, b in zip(roots, roots[1:])) < 0.3:
                continue
            r0, r1, r2 = roots
            a = rng.choice([1.0, 2.0, -1.5, 0.5])
            b = -a * (r0 + r1 + r2)
            c = a * (r0 * r1 + r0 * r2 + r1 * r2)
            d = -a * r0 * r1 * r2

            sols = sorted(solve_cubic(a, b, c, d))
            assert len(sols) == 3
            assert sols == pytest.approx(roots, abs=1e-6)
            n_checked += 1

    def test_single_real_root(self):
        # (x - r) * (x^2 + 1): one real root, complex pair discarded
        for r in (-2.5, 0.5, 3.0):
            sols = solve_cubic(1.0, -r, 1.0, -r)
            assert len(sols) == 1
            assert sols[0] == pytest.approx(r, abs=1e-9)

    def test_triple_root(self):
        # (x - 1)^3
        sols = solve_cubic(1.0, -3.0, 3.0, -1.0)
        assert sols == pytest.approx([1.0], abs=1e-6)

    def test_docstring_cases(self):
        assert solve_cubic(1, 0, 0, -1) == pytest.approx([1.0])
        assert solve_cubic(1, 0, 0, 1) == pytest.approx([-1.0])
        assert sorted(solve_cubic(1, -4, 3, 0)) == pytest.approx(
            [0.0, 1.0, 3.0], abs=1e-9)


class TestReflect:
    def test_reflect_yaxis(self):
        tp = reflect_yaxis(QPointF(1, 0), QPointF(3, 5))
        assert (tp.x(), tp.y()) == pytest.approx((-1.0, 5.0))

    def test_reflect_xaxis(self):
        tp = reflect_xaxis(QPointF(0, 1), QPointF(3, 5))
        assert (tp.x(), tp.y()) == pytest.approx((3.0, -3.0))
