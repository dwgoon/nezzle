# -*- coding: utf-8 -*-
"""Headless tests for the Cytoscape.js JSON (.cyjs) importer/exporter."""
import json

import pytest
from qtpy.QtCore import QPointF

from nezzle.io import read_network, read_metadata, write_network
from nezzle.io.cytoscape import read_cyjs, write_cyjs, read_metadata_from_cyjs
from nezzle.graphics import (
    Network, NodeClassFactory, EdgeClassFactory, LabelClassFactory)


# --- sample documents -------------------------------------------------------

def _standard_doc():
    return {
        "format_version": "1.0",
        "generated_by": "cytoscape-3.10.0",
        "data": {"name": "sample-net", "shared_name": "sample-net"},
        "elements": {
            "nodes": [
                {"data": {"id": "1", "name": "EGFR", "SUID": 1},
                 "position": {"x": -100.0, "y": -50.0}},
                {"data": {"id": "2", "name": "GRB2", "SUID": 2},
                 "position": {"x": 120.5, "y": 30.0}},
                {"data": {"id": "3", "name": "SOS1", "SUID": 3},
                 "position": {"x": 0.0, "y": 140.0}},
            ],
            "edges": [
                {"data": {"id": "10", "source": "1", "target": "2",
                          "interaction": "activates"}},
                {"data": {"id": "11", "source": "2", "target": "1",
                          "interaction": "inhibits"}},
                {"data": {"id": "12", "source": "2", "target": "3",
                          "interaction": "activates"}},
                {"data": {"id": "13", "source": "3", "target": "3",
                          "interaction": "binds"}},
            ],
        },
    }


def _write(tmp_path, doc, name="net.cyjs"):
    fpath = tmp_path / name
    fpath.write_text(json.dumps(doc), encoding="utf-8")
    return str(fpath)


@pytest.fixture
def standard_file(qapp, tmp_path):
    return _write(tmp_path, _standard_doc())


# --- metadata ---------------------------------------------------------------

class TestMetadata:
    def test_name_and_interaction_counts(self, standard_file):
        md = read_metadata_from_cyjs(standard_file)
        assert md["NETWORK_NAME"] == "sample-net"
        assert dict(md["INTERACTIONS"]) == {
            "activates": 2, "inhibits": 1, "binds": 1}

    def test_dispatched_by_extension(self, standard_file):
        # read_metadata routes .cyjs to the cytoscape reader.
        md = read_metadata(standard_file)
        assert md["NETWORK_NAME"] == "sample-net"

    def test_name_falls_back_to_filename(self, qapp, tmp_path):
        doc = _standard_doc()
        doc.pop("data")
        fpath = _write(tmp_path, doc, name="no_name.cyjs")
        md = read_metadata_from_cyjs(fpath)
        assert md["NETWORK_NAME"] == "no_name.cyjs"


# --- reading ----------------------------------------------------------------

class TestRead:
    def test_counts(self, standard_file):
        net = read_network(standard_file)
        assert len(net.nodes) == 3
        assert len(net.edges) == 4
        assert len(net.labels) == 3

    def test_positions_preserved(self, standard_file):
        net = read_network(standard_file)
        assert net.nodes["1"].pos() == QPointF(-100.0, -50.0)
        assert net.nodes["2"].pos() == QPointF(120.5, 30.0)

    def test_identity_is_id_name_is_human_readable(self, standard_file):
        net = read_network(standard_file)
        # iden stays the Cytoscape id (so edges resolve), name is the label.
        assert set(net.nodes) == {"1", "2", "3"}
        assert net.nodes["1"].name == "EGFR"

    def test_label_text_uses_human_name(self, standard_file):
        net = read_network(standard_file)
        by_node = {lb.parentItem().iden: lb.text for lb in net.labels.values()}
        assert by_node == {"1": "EGFR", "2": "GRB2", "3": "SOS1"}

    def test_edge_map_assigns_arrow_heads(self, standard_file):
        net = read_network(standard_file, edge_map={
            "activates": "TRIANGLE", "inhibits": "HAMMER", "binds": "None"})
        heads = {e.name: (type(e.head).__name__ if e.head else None)
                 for e in net.edges.values()}
        assert heads["activates"] == "Triangle"
        assert heads["inhibits"] == "Hammer"
        assert heads["binds"] is None

    def test_no_edge_map_means_no_heads(self, standard_file):
        net = read_network(standard_file)
        assert all(e.head is None for e in net.edges.values())

    def test_undefined_interaction_raises_with_edge_map(self, standard_file):
        with pytest.raises(ValueError):
            read_network(standard_file, edge_map={"activates": "TRIANGLE"})

    def test_self_loop_detected(self, standard_file):
        net = read_network(standard_file)
        kinds = {e.iden: e.ITEM_TYPE for e in net.edges.values()}
        assert kinds["13"] == "SELFLOOP_EDGE"
        assert kinds["10"] == "CURVED_EDGE"

    def test_reciprocal_edges_are_curved_apart(self, standard_file):
        net = read_network(standard_file)
        # 1<->2 is a reciprocal pair, so the control points must be displaced
        # off the chord (a straight CurvedEdge keeps its ctrl at the midpoint).
        for e in net.edges.values():
            if e.ITEM_TYPE == "SELFLOOP_EDGE":
                continue
            if {e.source.iden, e.target.iden} == {"1", "2"}:
                assert not e.is_straight()


# --- structural variants ----------------------------------------------------

class TestVariants:
    def test_flat_element_list(self, qapp, tmp_path):
        doc = [
            {"group": "nodes", "data": {"id": "a", "name": "Alpha"},
             "position": {"x": 10, "y": 20}},
            {"group": "nodes", "data": {"id": "b", "name": "Beta"},
             "position": {"x": 30, "y": 40}},
            {"group": "edges", "data": {"id": "e1", "source": "a",
                                        "target": "b", "interaction": "pp"}},
        ]
        net = read_cyjs(_write(tmp_path, doc, name="flat.cyjs"))
        assert set(net.nodes) == {"a", "b"}
        assert len(net.edges) == 1
        assert net.nodes["a"].pos() == QPointF(10, 20)

    def test_bare_nodes_edges_object(self, qapp, tmp_path):
        doc = {
            "nodes": [{"data": {"id": "x", "name": "X"},
                       "position": {"x": 5.5, "y": -5.5}},
                      {"data": {"id": "y", "name": "Y"},
                       "position": {"x": 50, "y": 60}}],
            "edges": [{"data": {"source": "x", "target": "y"}}],
        }
        net = read_cyjs(_write(tmp_path, doc, name="bare.cyjs"))
        assert set(net.nodes) == {"x", "y"}
        # Edge with no interaction key gets the "None" placeholder name.
        assert list(net.edges.values())[0].name == "None"

    def test_missing_position_gets_a_finite_fallback(self, qapp, tmp_path):
        doc = {"elements": {
            "nodes": [{"data": {"id": "n1", "name": "N1"}}],  # no position
            "edges": []}}
        net = read_cyjs(_write(tmp_path, doc, name="nopos.cyjs"))
        p = net.nodes["n1"].pos()
        import math
        assert math.isfinite(p.x()) and math.isfinite(p.y())

    def test_edge_to_unknown_node_is_skipped(self, qapp, tmp_path):
        doc = {"elements": {
            "nodes": [{"data": {"id": "n1", "name": "N1"},
                       "position": {"x": 0, "y": 0}}],
            "edges": [{"data": {"source": "n1", "target": "ghost"}}]}}
        net = read_cyjs(_write(tmp_path, doc, name="dangling.cyjs"))
        assert len(net.nodes) == 1
        assert len(net.edges) == 0

    def test_numeric_ids_are_coerced(self, qapp, tmp_path):
        doc = {"elements": {
            "nodes": [{"data": {"id": 1, "name": "One"},
                       "position": {"x": 0, "y": 0}},
                      {"data": {"id": 2, "name": "Two"},
                       "position": {"x": 1, "y": 1}}],
            "edges": [{"data": {"source": 1, "target": 2}}]}}
        net = read_cyjs(_write(tmp_path, doc, name="numids.cyjs"))
        assert set(net.nodes) == {"1", "2"}
        assert len(net.edges) == 1


# --- writing / round-trip ---------------------------------------------------

class TestWriteRoundTrip:
    def test_write_emits_positions_and_names(self, standard_file, tmp_path):
        net = read_network(standard_file)
        out = str(tmp_path / "out.cyjs")
        write_cyjs(net, out)
        doc = json.loads((tmp_path / "out.cyjs").read_text(encoding="utf-8"))
        nodes = {n["data"]["id"]: n for n in doc["elements"]["nodes"]}
        assert nodes["1"]["data"]["name"] == "EGFR"
        assert nodes["1"]["position"] == {"x": -100.0, "y": -50.0}

    def test_round_trip_preserves_graph(self, standard_file, tmp_path):
        emap = {"activates": "TRIANGLE", "inhibits": "HAMMER", "binds": "None"}
        net = read_network(standard_file, edge_map=emap)
        out = str(tmp_path / "rt.cyjs")
        write_network(net, out)
        net2 = read_network(out, edge_map=emap)

        assert set(net.nodes) == set(net2.nodes)
        assert len(net.edges) == len(net2.edges)
        for iden in net.nodes:
            p1, p2 = net.nodes[iden].pos(), net2.nodes[iden].pos()
            assert p1.x() == pytest.approx(p2.x())
            assert p1.y() == pytest.approx(p2.y())
            assert net.nodes[iden].name == net2.nodes[iden].name

    def test_write_handles_self_loop(self, qapp, tmp_path):
        net = Network("sl")
        NodeClass = NodeClassFactory.create("ELLIPSE_NODE")
        n = NodeClass("n", 40, 40, pos=QPointF(0, 0))
        net.add_node(n)
        EdgeClass = EdgeClassFactory.create("SELFLOOP_EDGE")
        e = EdgeClass(iden="loop", name="binds", node=n)
        n.add_edge(e)
        net.add_edge(e)

        out = str(tmp_path / "sl.cyjs")
        write_cyjs(net, out)
        doc = json.loads((tmp_path / "sl.cyjs").read_text(encoding="utf-8"))
        edge = doc["elements"]["edges"][0]["data"]
        assert edge["source"] == edge["target"] == "n"
