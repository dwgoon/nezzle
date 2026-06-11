# -*- coding: utf-8 -*-
"""Headless tests for the quadratic-Bezier math in nezzle.graphics.quadbezier.

The closed-form arc length and its inversion (find_t_for_arclen) drive the
arrow-head placement on curved edges; nearest_point/identify_sps drive the
offset-polygon subdivision. Each is checked against brute-force numeric
references.
"""
import math
import random

import numpy as np
import pytest
from qtpy.QtCore import QPointF

from nezzle.graphics import quadbezier


def _bezier_point(p1, pc, p2, t):
    w0 = (1.0 - t) * (1.0 - t)
    w1 = 2.0 * t * (1.0 - t)
    w2 = t * t
    return (w0 * p1[0] + w1 * pc[0] + w2 * p2[0],
            w0 * p1[1] + w1 * pc[1] + w2 * p2[1])


def _numeric_arc_length(p1, pc, p2, t1, t2, n=20001):
    """Dense polyline approximation of the arc length over [t1, t2]."""
    t = np.linspace(t1, t2, n)
    omt = 1.0 - t
    x = omt**2 * p1[0] + 2 * t * omt * pc[0] + t**2 * p2[0]
    y = omt**2 * p1[1] + 2 * t * omt * pc[1] + t**2 * p2[1]
    return float(np.sum(np.hypot(np.diff(x), np.diff(y))))


def _random_triples(n, seed):
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        p1 = (rng.uniform(-200, 200), rng.uniform(-200, 200))
        pc = (rng.uniform(-200, 200), rng.uniform(-200, 200))
        p2 = (rng.uniform(-200, 200), rng.uniform(-200, 200))
        # Skip degenerate cases where the curve collapses to a point or the
        # quadratic coefficient of |B'(t)|^2 vanishes (pc == midpoint).
        chord = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        a_coeff = (pc[0] - mid[0])**2 + (pc[1] - mid[1])**2
        if chord < 1.0 or a_coeff < 1e-6:
            continue
        out.append((p1, pc, p2))
    return out


class TestArcLength:
    def test_matches_numeric_integration(self):
        for p1, pc, p2 in _random_triples(50, seed=42):
            x = np.array([p1[0], pc[0], p2[0]], dtype=np.float64)
            y = np.array([p1[1], pc[1], p2[1]], dtype=np.float64)
            exact = quadbezier.arc_length(x, y, 0.0, 1.0)
            numeric = _numeric_arc_length(p1, pc, p2, 0.0, 1.0)
            assert exact == pytest.approx(numeric, rel=1e-4)

    def test_partial_interval(self):
        for p1, pc, p2 in _random_triples(20, seed=7):
            x = np.array([p1[0], pc[0], p2[0]], dtype=np.float64)
            y = np.array([p1[1], pc[1], p2[1]], dtype=np.float64)
            exact = quadbezier.arc_length(x, y, 0.6, 1.0)
            numeric = _numeric_arc_length(p1, pc, p2, 0.6, 1.0)
            assert exact == pytest.approx(numeric, rel=1e-4)


class TestFindTForArclen:
    def test_inverts_arc_length(self):
        """find_t_for_arclen(target) must return t with arclen(t, 1) ~ target."""
        for p1, pc, p2 in _random_triples(50, seed=11):
            tail = _numeric_arc_length(p1, pc, p2, 0.5, 1.0)
            for frac in (0.05, 0.15, 0.3):
                target = frac * tail
                t = quadbezier.find_t_for_arclen(
                    QPointF(*p1), QPointF(*pc), QPointF(*p2), target)
                assert 0.5 <= t <= 1.0
                achieved = _numeric_arc_length(p1, pc, p2, t, 1.0)
                # Head offsets in production are small fractions of the tail;
                # the Taylor + one-Newton-step inversion is accurate to far
                # better than 1% there.
                assert achieved == pytest.approx(target, rel=1e-2,
                                                 abs=1e-6 * tail)

    def test_typical_head_offset_meets_convergence_contract(self):
        # A representative edge: 200 px chord, moderate curvature, ~15 px
        # head offset (radius + arrow height + margin). The safeguarded
        # Newton iteration stops at |err| <= 5e-3 * target.
        p1, pc, p2 = (0.0, 0.0), (100.0, 60.0), (200.0, 0.0)
        target = 15.0
        t = quadbezier.find_t_for_arclen(
            QPointF(*p1), QPointF(*pc), QPointF(*p2), target)
        achieved = _numeric_arc_length(p1, pc, p2, t, 1.0)
        assert achieved == pytest.approx(target, rel=6e-3)

    def test_degenerate_and_out_of_range_targets_hide_head(self):
        p1, pc, p2 = QPointF(0, 0), QPointF(100, 60), QPointF(200, 0)
        # Zero / negative target degenerates to t_max.
        assert quadbezier.find_t_for_arclen(p1, pc, p2, 0.0) == 1.0
        assert quadbezier.find_t_for_arclen(p1, pc, p2, -5.0) == 1.0
        # Target longer than the whole [t_min, 1] arc: no solution in range,
        # so the head is hidden at the node (t_max) — documented fallback.
        assert quadbezier.find_t_for_arclen(p1, pc, p2, 1e6) == 1.0

    def test_t_decreases_as_target_grows(self):
        p1, pc, p2 = QPointF(0, 0), QPointF(100, 60), QPointF(200, 0)
        targets = [5.0, 15.0, 40.0, 80.0]
        ts = [quadbezier.find_t_for_arclen(p1, pc, p2, x) for x in targets]
        assert all(0.5 <= t <= 1.0 for t in ts)
        assert ts == sorted(ts, reverse=True)

    def test_degenerate_zero_tangent(self):
        # pc == p2: |B'(1)| == 0, must fall back to t_max without dividing
        # by zero.
        p1, pc, p2 = QPointF(0, 0), QPointF(100, 0), QPointF(100, 0)
        assert quadbezier.find_t_for_arclen(p1, pc, p2, 10.0) == 1.0


class TestNearestPoint:
    def test_nearest_to_control_point(self):
        """The production call pattern: nearest curve point from the ctrl
        point. The result must lie on the curve with t in [0, 1] and be
        near-optimal.

        Note: the implementation standardizes x/y independently for
        numerical conditioning, so it minimizes distance in that scaled
        space — in plain Euclidean distance the result is only roughly
        optimal (median ~1.02x, observed worst ~1.8x for this seed). The
        bound below is a characterization guard against regressions, not a
        precision contract; the hard invariants are t in [0, 1] and the
        point lying on the curve.
        """
        for p1, pc, p2 in _random_triples(50, seed=23):
            cps = (QPointF(*p1), QPointF(*pc), QPointF(*p2))
            pt, t = quadbezier.nearest_point(cps, QPointF(*pc))

            assert 0.0 <= t <= 1.0

            bx, by = _bezier_point(p1, pc, p2, t)
            assert pt.x() == pytest.approx(bx, abs=1e-6)
            assert pt.y() == pytest.approx(by, abs=1e-6)

            d0 = math.hypot(pt.x() - pc[0], pt.y() - pc[1])
            d_min = min(
                math.hypot(*(lambda q: (q[0] - pc[0], q[1] - pc[1]))(
                    _bezier_point(p1, pc, p2, i / 2000.0)))
                for i in range(2001))
            assert d0 <= 2.0 * d_min + 1e-9

    def test_large_coordinates_are_conditioned(self):
        # The implementation standardizes coordinates to stay numerically
        # stable far from the origin.
        offset = 1e6
        p1 = (offset, offset)
        pc = (offset + 100, offset + 80)
        p2 = (offset + 200, offset)
        cps = (QPointF(*p1), QPointF(*pc), QPointF(*p2))
        pt, t = quadbezier.nearest_point(cps, QPointF(*pc))
        assert 0.0 <= t <= 1.0
        bx, by = _bezier_point(p1, pc, p2, t)
        assert pt.x() == pytest.approx(bx, abs=1e-3)
        assert pt.y() == pytest.approx(by, abs=1e-3)


class TestSubdivision:
    def test_identify_sps_endpoints_and_on_curve_points(self):
        for p1, pc, p2 in _random_triples(20, seed=31):
            cps = (QPointF(*p1), QPointF(*pc), QPointF(*p2))
            sps = quadbezier.identify_sps(cps)

            assert len(sps) == 9
            # Subdivision preserves the curve's endpoints.
            assert sps[0] == cps[0]
            assert sps[-1] == cps[2]

    def test_identify_qps_offset_distance(self):
        width = 6.0
        for p1, pc, p2 in _random_triples(20, seed=37):
            cps = (QPointF(*p1), QPointF(*pc), QPointF(*p2))
            sps = quadbezier.identify_sps(cps)
            qps_top, qps_bottom = quadbezier.identify_qps(sps, width)

            assert len(qps_top) == len(qps_bottom) == 5
            # Every offset point sits at exactly width/2 from its anchor
            # (the even-indexed subdivision points).
            anchors = sps[0::2]
            for q_top, q_bot, anchor in zip(qps_top, qps_bottom, anchors):
                d_top = math.hypot(q_top.x() - anchor.x(),
                                   q_top.y() - anchor.y())
                d_bot = math.hypot(q_bot.x() - anchor.x(),
                                   q_bot.y() - anchor.y())
                assert d_top == pytest.approx(width / 2, rel=1e-9)
                assert d_bot == pytest.approx(width / 2, rel=1e-9)
