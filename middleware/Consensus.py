import time
import queue
from random import randint
from middleware.message.MessageEnum import MessageEnum
from middleware.message.Message import Message, message

class Consensus:
    def __init__(self, node):
        self.node = node
        self.votes = {}

    def run_leader_consensus(self):
        """
        Leader starts consensus round, collects votes, and broadcasts the consensus value.
        """
        self.node.round += 1

        m = message(
            message_enum=MessageEnum.BIZANTINE_START,
            sender_id=self.node._process_id,
            payload=str(self.node.round)
        )
        Message.send_multicast(m)

        self.votes = {self.node._process_id: self.node.get_node_vote()}

        start_time = time.time()
        timeout = 3  # seconds
        while time.time() - start_time < timeout:
            try:
                msg = self.node._message_queue.get(timeout=timeout - (time.time() - start_time))
                if msg.get("type") == MessageEnum.BIZANTINE_VOTE.value:
                    sender = int(msg["sender_id"])
                    vote = int(msg["payload"].split(":")[1])  # Extract the vote from the payload
                    if sender not in self.votes and msg["payload"] == self.node.round:  # Avoid overwriting existing votes
                        self.node.logger.info(f"[BIZANTINE] Node {self.node._process_id} received vote from {sender}: {vote}")
                    # Store the vote in the votes dictionary
                    self.votes[sender] = vote
            except queue.Empty:
                break

        consensus_value = max(self.votes.values()) if self.votes else None
        if consensus_value is not None:
            self.node.logger.info(f"[BIZANTINE] Leader {self.node._process_id} decided consensus value: {consensus_value}")
            m = message(
                message_enum=MessageEnum.BIZANTINE_DECIDE,
                sender_id=self.node._process_id,
                payload=str(consensus_value)
            )
            Message.send_multicast(m)
        return consensus_value

    def handle_message(self, msg):
        if msg.get("type") == MessageEnum.BIZANTINE_START.value:
            if(int(msg["payload"]) > self.node.round):
                self.node.round = int(msg["payload"])
                self.node.logger.info(f"[BIZANTINE] Node {self.node._process_id} updated round to {self.node.round}")

            m = message(
                message_enum=MessageEnum.BIZANTINE_VOTE,
                sender_id=self.node._process_id,
                payload=str(f"{msg["payload"]}:{self.node.get_node_vote()}")
            )
            Message.send_multicast(m)
        elif msg.get("type") == MessageEnum.BIZANTINE_DECIDE.value:
            consensus_value = int(msg["payload"])
            self.node.logger.info(f"[BIZANTINE] Node {self.node._process_id} received consensus value: {consensus_value}")
