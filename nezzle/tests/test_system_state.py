

from nezzle.systemstate import get_system_state
from nezzle.constants import Lock


def test_system_state_lock():

    ss = get_system_state()

    # Nodes
    ss.set_locked(Lock.NODES, True)
    assert(ss.is_locked(Lock.NODES))

    ss.set_locked(Lock.NODES, False)
    assert(not ss.is_locked(Lock.NODES))

    # Edges
    ss.set_locked(Lock.EDGES, True)
    assert(ss.is_locked(Lock.EDGES))

    ss.set_locked(Lock.EDGES, False)
    assert(not ss.is_locked(Lock.EDGES))

    # Labels
    ss.set_locked(Lock.LABELS, True)
    assert(ss.is_locked(Lock.LABELS))

    ss.set_locked(Lock.LABELS, False)
    assert(not ss.is_locked(Lock.LABELS))

    # Setting all locked
    ss.set_locked(Lock.NODES, True)
    ss.set_locked(Lock.EDGES, True)
    ss.set_locked(Lock.LABELS, True)

    assert(ss.is_locked(Lock.NODES))
    assert(ss.is_locked(Lock.EDGES))
    assert(ss.is_locked(Lock.LABELS))

    ss.set_locked(Lock.NODES, False)
    assert(not ss.is_locked(Lock.NODES))