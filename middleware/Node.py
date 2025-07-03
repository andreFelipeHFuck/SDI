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
    def __init__(self, process_id: int, seconds: int, round: int = 0) -> None:
        self._process_id: int = process_id
        self._seconds: int = seconds
        self._round: int = round
        
        # Dicionário com os nós e o último heartbeat
        self._another_nodes: dict = {self._process_id: time.time()}
        
        # Lock para o dicionário dos heartbeat dos nós
        self._lock: threading.Lock = threading.Lock()
        
        # Fila de mensagens entre listen_thread e thread Node padrão
        self._message_queue: queue.Queue = queue.Queue()
        
        self._ele = Election(process_id=self._process_id)
        self._is_ele_in_progress: bool = False
    
    
        logger.info(f"✅ Servidor ID {self._process_id}, Rodada {self._round} Iniciado com Sucesso!")
        
        
    # LISTEN THREAD 

    
    def election_message(self, message: dict) -> bool:
        try:
            if message["type"] == MessageEnum.ELECTION.value and self._process_id > message["sender_id"]:
                with self._lock:
                    if self._ele.current_state.id == "normal":
                        self._ele.send("appley", message)
                            
                    elif self._ele.current_state.id == "candidate":
                        m_answer: bytes = message(
                                message_enum=MessageEnum.ANSWER,
                                sender_id=self._process_id,
                                payload="ANSWER_ACK"
                        )
            
                        Message.send_multicast(message=m_answer)
                
            # Algun nó com id maior pretende ser o coordenador 
            elif message["type"] == MessageEnum.ANSWER.value:
                with self._lock:
                    if self._ele.current_state.id == "candidate":
                        self._ele.send("lost")
                
            elif message["type"] == MessageEnum.COORDINATOR.value:
                with self._lock:
                    if self._ele.current_state.id == "normal":
                        self._ele.set_leader(message["sender_id"])
                
            return True
        except:
            pass            
            
            
        return False
        
        
    def handle_message(self, message: dict) -> None:
        """
        Processa as mensagens recebidas

        Args:
            message (dict): mensagem que foi recebida pelo sistema 
        """
        
        # Mensagens do prórpio id são ignoradas 
        if message.get("sender_id") == self._process_id:
            return
        
        elif not self.election_message(message):
            pass
     
        
    def listen_thread(self) -> None:
        def receive_message(m: bytes):
            message: dict = handle_message(m)
            
            self.handle_message(message)
            
        Message.recv_multicast(receive_message)
        
        
    # MAIN THREAD 
    
    
    def declare_victory(self) -> None:
        try:
            self._ele.send("win_election")
        except:
            pass
        
        
    def election_process(self, timeout: int) -> None:
        # Verifica se é o nó com o maior id
        # if self._process_id == max([id for id in self._another_nodes.keys()]):
        #     with self._lock:
        #         self.declare_victory()
        
        # else:
            time.sleep(timeout)
            
            with self._lock:
                if self._ele.current_state.id == "candidate":
                    self.declare_victory()
    
    
    def start_election(self, timeout: int) -> None:
        """
        

        Args:
            timeout (int): tempo que o nó vai esperar até declarar que é 
            líder no sistema
        """
        
        
        
        with self._lock:
            if self._ele.current_state.id == "normal":
                self._ele.send("start_election")
                
        self.election_process(timeout)
        
        
        
    def check_nodes(self):
        pass
    
    def main_node_loop_thread(self, leader_task, timeout: int) -> None:
        leader_not_exist: bool = False
        
        while True:
            
            self.check_nodes()
            
            # Função que indique que os nós estão conectados
            if False:
            
                with self._lock:
                    leader_not_exist = self._ele.is_not_in_election() and self._ele.get_leader() == None
                    
            if leader_not_exist:
                logger.info(f"🗳️ Servidor ID {self._process_id} inicia a eleição")

                self.start_election(timeout)
                

    def init_node(self, leader_task) -> None:
        main: threading.Thread = threading.Thread(target=self.main_node_loop_thread, args=(leader_task, 15))
        listen: threading.Thread = threading.Thread(target=self.listen_thread)
        
        main.start()
        listen.start()
    
    
