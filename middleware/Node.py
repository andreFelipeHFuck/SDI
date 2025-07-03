"""
    Classe que representa um Node (Nó) dentro da aplicação,
    abstrai para a aplicação o identificador único (id), o líder, 
    os outros nós (peers)
"""

import time 
import logging
import threading
import queue

from concurrent.futures import ThreadPoolExecutor

from message.Message import Message, MessageEnum, message, handle_message

logger = logging.getLogger(__name__)

class Node():
    def __init__(self, process_id: int, seconds: int, round: int = 0) -> None:
        self._process_id: int = process_id
        self._seconds: int = seconds
        self._round: int = round
        
        # Dicionário com os nós e o último heartbeat
        self._another_nodes: dict = {self._process_id: time.time()}
        
        #
        self._node: threading.Lock = threading.Lock()
        
        # Fila de mensagens entre listen_thread e thread Node padrão
        self._message_queue: queue.Queue = queue.Queue()
    
    
        logger.info(f"✅ Servidor ID {self._process_id}, Rodada {self._round} Iniciado com Sucesso!")
    
    def listen_thread(self) -> None:
        def receive_message(m: bytes):
            msg: dict = handle_message(m)
            
            self._message_queue.put(msg)
            
        Message.recv_multicast(receive_message)
        
    
    def main_node_loop_thread(self) -> None:
        while True:
            print("[CONSUMIDOR] escutando")
            time.sleep(1)
            
            try:
                msg: dict = self._message_queue.get(timeout=1)
                print(f"[CONSUMIDOR] Consumiu {msg}")
                self._message_queue.task_done()
            except:
                print(f"[CONSUMIDOR] Timeout, não foi possível receber nada necesse período de tempo")
                

    def main(self) -> None:
        main: threading.Thread = threading.Thread(target=self.main_node_loop_thread)
        listen: threading.Thread = threading.Thread(target=self.listen_thread)
        
        main.start()
        listen.start()
    
    
