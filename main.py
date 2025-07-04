"""_summary_
"""

import logging
import argparse
import socket
import json
import select
from time import sleep, time
from random import randint

from config.logger_config import setup_logger
from middleware import Node
from middleware.message.MessageEnum import MessageEnum

logger = logging.getLogger(__name__)

MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT = 5007

class App(Node.Node):
    def __init__(self, process_id: int, seconds: int = 1):
        super().__init__(process_id=process_id, seconds=seconds)
        
        
    def leader_task(self) -> None:
        """
        Código executado em loop na aplicação
        
        Onde o nó líder gera um número aleátorio i e envia para todos
        os outros nós, os nós que recebm o i devem responde o processo líder 
        com i*i*process_id
        
        O sistema realiza o consenso de que possui o maior valor 
        """
        
        pass
    
    def main(self) -> None:
        self.init_node(leader_task=self.leader_task)

def discover_id(timeout=1.0):
    """
    Multicast a WHO_IS_THERE message and collect responses to determine the highest id.
    Returns the new id (highest found + 1) or 1 if none found.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)
    sock.bind(('', 0))  # Bind to any available port

    # Join multicast group
    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Send WHO_IS_THERE using enum
    msg = json.dumps({"type": MessageEnum.WHO_IS_THERE.value}).encode('utf-8')
    sock.sendto(msg, (MULTICAST_GROUP, MULTICAST_PORT))

    found_ids = set()
    start = time()
    while time() - start < timeout:
        try:
            ready = select.select([sock], [], [], timeout - (time() - start))
            if ready[0]:
                data, _ = sock.recvfrom(1024)
                try:
                    resp = json.loads(data.decode('utf-8'))
                    if resp.get("type") == MessageEnum.I_AM.value and "id" in resp:
                        found_ids.add(int(resp["id"]))
                except Exception:
                    pass
        except socket.timeout:
            break
    sock.close()
    return max(found_ids) + 1 if found_ids else 1

def main(id: int = 1) -> None:
    """
    Inicia todas as configurações do sistema
    """
    
    # Setup logging system
    setup_logger()
    

    app = App(id)
    app.main()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Identificador de processo para o sistema")
    parser.add_argument("--id", type=int, help="Identificador de processo (id)", default=0)
    args = parser.parse_args()

    # If no id is provided, discover it
    if not args.id:
        args.id = discover_id(timeout=1.0)
        print(f"[BOOT] Assigned id: {args.id}")

    main(args.id)