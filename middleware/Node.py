"""
    Classe que representa um Node (Nó) dentro da aplicação,
    abstrai para a aplicação o identificador único (id), o líder, 
    os outros nós (peers)
"""

import logging
import threading
import queue

from .message.Message import Message, MessageEnum, message, handle_message
from .DF import DF
from .Election import Election

logger = logging.getLogger(__name__)

class Node():
    def __init__(self, 
                 process_id: int, 
                 processes_id: list[int],
                 df_d: int,
                 df_t: int,
                 election_timeout: int,
                 round: int = 0) -> None:
        
        
        self._process_id: int = process_id
        self._processes_id: list[int] = [id for id in processes_id if id != self._process_id]
        self._round: int = round
        
        self._df_d: int = df_d
        self._df_t: int = df_t
        self._election_timeout: int = election_timeout
        
        # Sistema de Detecção de Falhas (DF)
        self._df: DF = None
        
        # Sistema de Eleição utilizando o Algoritmo do Valentão
        self._ele: Election = Election(process_id=process_id)
        
        # Fila de mensagens entre listen_thread e thread Node padrão
        self._message_queue: queue.Queue = queue.Queue()
            
    
        logger.info(f"✅ Servidor ID {self._process_id}, Rodada {self._round}, Iniciado com Sucesso!")
     
     
    # Métodos internos do Node
    
    def __num_active_processes(self) -> int:
        """
        Retorna o número de processos ativos 

        Returns:
            int: número de processos ativos 
        """
        
        if self._df == None:
            raise Exception("Detctor de falhas não foi iniciado")
        
        return len(self._processes_id) - len(self._df.suspected_list())
    
    
    def __leader_is_active(self) -> bool:
        """
        Retorna se o atual processo líder está ativo 

        Returns:
            bool: se o processo líder está ativo True, caso contrário False
        """
        
        if self._df == None:
            raise Exception("Detctor de falhas não foi iniciado")
        
        leader: int | None = self._ele.get_leader()
        
        # Se nenhum líder foi declarado
        if  leader == None:
            return False
        
        # Se o líde estiver entre os processos suspeitos 
        elif leader in self._df.suspected_list():
            return False
        
        
        return True
        
        
        
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
        
        self._df.handle_df_message(message)
     
        
    def __listen_thread(self) -> None:
        def receive_message(m: bytes):
            message: dict = handle_message(m)
            
            self.__handle_message(message)
        
        Message.recv_multicast(receive_message)

        
    # MAIN THREAD 
    
    def __main_node_loop_thread(self, leader_task, timeout: int) -> None:        
        while True:
            
            pass
                
    # Métodos para o APP

    def init_node(self, leader_task) -> None:
        # Inicia o detector de falhas
        self._df = DF(
            d=self._df_d,
            t=self._df_t,
            process_id=self._process_id,
            processes_list=self._processes_id
        )
        
        main: threading.Thread = threading.Thread(target=self.__main_node_loop_thread, args=(leader_task, 15))
        listen: threading.Thread = threading.Thread(target=self.__listen_thread)
        
        main.start()
        listen.start()


    def node_is_leader(self) -> bool:
        return self._ele.get_leader() == self._processes_id()
    
    
    def consensus(self) -> int:
        pass
