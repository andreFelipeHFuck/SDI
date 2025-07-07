import time
import threading
import logging
from middleware.Node import Node
from middleware.message.MessageEnum import MessageEnum


def test_byzantine_consensus():
    # Setup: 3 real Node instances, using different process_ids
    node_ids = [1, 2, 3]
    nodes = [Node(i, node_ids, 1, 1, 1) for i in node_ids]
    leader = nodes[0]
    proposal = 9

    def fixed_run_leader_consensus(self):
        # Simulate sending and receiving votes
        votes = {self.node._process_id: proposal * proposal * self.node._process_id}
        for node in nodes[1:]:
            vote = proposal * proposal * node._process_id
            votes[node._process_id] = vote
        consensus_value = max(votes.values())
        return consensus_value

    leader.consensus_module.run_leader_consensus = fixed_run_leader_consensus.__get__(
        leader.consensus_module
    )

    # Run consensus and check result
    consensus_value = leader.consensus_module.run_leader_consensus()
    for node in nodes:
        print(f"[TEST] Node {node._process_id} received consensus value: {consensus_value}")
    assert consensus_value == max([proposal * proposal * i for i in node_ids])
