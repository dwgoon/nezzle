# -*- coding: utf-8 -*-
"""Tests for the interaction-aware render quality toggle in GraphicsView:
antialiasing is suspended during continuous interaction and restored (with a
full-quality repaint) after the input goes idle.
"""
import time

import pytest
from qtpy.QtGui import QPainter

from nezzle.graphics.screen import GraphicsScene, GraphicsView


def _aa_enabled(view):
    return bool(view.renderHints() & QPainter.Antialiasing)


@pytest.fixture
def view(qapp):
    v = GraphicsView()
    v.setScene(GraphicsScene())
    # Shorten the restore delay so the idle test stays fast.
    v._aa_restore_timer.setInterval(50)
    yield v
    v._aa_restore_timer.stop()
    v.setScene(None)


def _wait_until(qapp, predicate, timeout_s=2.0):
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        qapp.processEvents()
        if predicate():
            return True
    return predicate()


def test_antialiasing_is_on_by_default(view):
    assert _aa_enabled(view)
    assert not view._aa_restore_timer.isActive()


def test_enter_fast_mode_drops_aa_and_arms_timer(view):
    view._enter_fast_render_mode()
    assert not _aa_enabled(view)
    assert view._aa_restore_timer.isActive()


def test_enter_fast_mode_is_idempotent_during_burst(view):
    view._enter_fast_render_mode()
    view._enter_fast_render_mode()
    view._enter_fast_render_mode()
    assert not _aa_enabled(view)
    assert view._aa_restore_timer.isActive()


def test_quality_restored_after_idle(qapp, view):
    view._enter_fast_render_mode()
    assert not _aa_enabled(view)
    assert _wait_until(qapp, lambda: _aa_enabled(view)), \
        "antialiasing was not restored after the idle delay"
    assert not view._aa_restore_timer.isActive()


def test_restore_is_immediate_on_release(view):
    view._enter_fast_render_mode()
    assert not _aa_enabled(view)
    view._restore_render_quality()  # the mouse-release path
    assert _aa_enabled(view)
    assert not view._aa_restore_timer.isActive()


def test_restore_without_fast_mode_is_noop(view):
    view._restore_render_quality()
    assert _aa_enabled(view)


def test_text_antialiasing_is_never_dropped(view):
    view._enter_fast_render_mode()
    assert bool(view.renderHints() & QPainter.TextAntialiasing)
    view._restore_render_quality()
    assert bool(view.renderHints() & QPainter.TextAntialiasing)
