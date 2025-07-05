"""
    Classe que representa um Node (Nó) dentro da aplicação,
    abstrai para a aplicação o identificador único (id), o líder, 
    os outros nós (peers)
"""

import time 
import logging
import threading
import queue

from .message.Message import Message, MessageEnum, message, handle_message
from .Election import Election

logger = logging.getLogger(__name__)

class Node():
    def __init__(self, 
                 seconds: int, 
                 process_id: int, 
                 processes_id: list[int],
                 round: int = 0) -> None:
        
        
        self._process_id: int = process_id
        self._seconds: int = seconds
        self._round: int = round
        
        # Fila de mensagens entre listen_thread e thread Node padrão
        self._message_queue: queue.Queue = queue.Queue()
            
    
        logger.info(f"✅ Servidor ID {self._process_id}, Rodada {self._round}, Iniciado com Sucesso!")
        
        
    # LISTEN THREAD 
        
    def __handle_message(self, message: dict) -> None:
        """
        Processa as mensagens recebidas

        Args:
            message (dict): mensagem que foi recebida pelo sistema 
            addr (tuple): endereço do remetente (host, port)
        """
        
        # Mensagens do prórpio id são ignoradas 
        if message.get("sender_id") == self._process_id:
            return
     
        
    def __listen_thread(self) -> None:
        def receive_message(m: bytes):
            message: dict = handle_message(m)
            
            self.handle_message(message)
        
        Message.recv_multicast(receive_message)

        
    # MAIN THREAD 
    
    def __main_node_loop_thread(self, leader_task, timeout: int) -> None:        
        while True:
            
            pass
                

    def init_node(self, leader_task) -> None:
        main: threading.Thread = threading.Thread(target=self.__main_node_loop_thread, args=(leader_task, 15))
        listen: threading.Thread = threading.Thread(target=self.__listen_thread)
        
        main.start()
        listen.start()
