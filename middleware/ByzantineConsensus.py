import time
import queue
from random import randint
from middleware.message.MessageEnum import MessageEnum
from middleware.message.Message import Message, message

class ByzantineConsensus:
    def __init__(self, node):
        self.node = node
        self.votes = {}

    def run_leader_consensus(self):
        """
        Leader proposes a value, collects votes, and broadcasts the consensus value.
        """
        proposal = randint(1, 100)
        m = message(
            message_enum=MessageEnum.BIZANTINE_PROPOSE,
            sender_id=self.node._process_id,
            payload=str(proposal)
        )
        Message.send_multicast(m)

        self.votes = {self.node._process_id: proposal * proposal * self.node._process_id}
        start_time = time.time()
        timeout = 3  # seconds
        while time.time() - start_time < timeout:
            try:
                msg = self.node._message_queue.get(timeout=timeout - (time.time() - start_time))
                if msg.get("type") == MessageEnum.BIZANTINE_VOTE.value:
                    sender = int(msg["sender_id"])
                    vote = int(msg["payload"])
                    self.votes[sender] = vote
            except queue.Empty:
                break

        consensus_value = max(self.votes.values()) if self.votes else None
        if consensus_value is not None:
            m = message(
                message_enum=MessageEnum.BIZANTINE_DECIDE,
                sender_id=self.node._process_id,
                payload=str(consensus_value)
            )
            Message.send_multicast(m)
        return consensus_value

    def handle_message(self, message):
        if message.get("type") == MessageEnum.BIZANTINE_PROPOSE.value:
            proposal = int(message["payload"])
            vote = proposal * proposal * self.node._process_id
            m = message(
                message_enum=MessageEnum.BIZANTINE_VOTE,
                sender_id=self.node._process_id,
                payload=str(vote)
            )
            Message.send_multicast(m)
        elif message.get("type") == MessageEnum.BIZANTINE_DECIDE.value:
            consensus_value = int(message["payload"])
            self.node.logger.info(f"[BIZANTINE] Node {self.node._process_id} received consensus value: {consensus_value}")
