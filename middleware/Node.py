"""
    Classe que representa um Node (Nó) dentro da aplicação,
    abstrai para a aplicação o identificador único (id), o líder, 
    os outros nós (peers)
"""

import logging
import threading
import queue
import time
from random import randint

from .message.Message import Message, MessageEnum, message, handle_message
from .DF import DF
from .Election import Election
from .Consensus import Consensus

logger = logging.getLogger(__name__)

class Node():
    def __init__(self, 
                 process_id: int, 
                 processes_id: list[int],
                 df_d: int,
                 df_t: int,
                 election_timeout: int,
                 round: int = 0) -> None:
        
        # Eliminas as falhas bizatinas
        assert(process_id in processes_id)
        
        self._process_id: int = process_id
        self._processes_id: list[int] = [id for id in processes_id if id != self._process_id]
        self.round: int = 0
        
        self._df_d: int = df_d
        self._df_t: int = df_t
        self._election_timeout: int = election_timeout
        
        # Sistema de Detecção de Falhas (DF)
        self._df: DF = None
        
        # Sistema de Eleição utilizando o Algoritmo do Valentão
        self._ele: Election = Election(
            process_id=process_id,
            processes_id=processes_id,
            timeout=election_timeout,
        )
        
        # Threads do sistema 
        self._main_thread: threading.Thread = None        
        self._listen_thread: threading.Thread = None
        
        self._is_send_leader_search_message: bool = False
        self._send_leader_search_message_lock: threading.Lock = threading.Lock()
        
        # Módulo de Consenso
        self.consensus_module = Consensus(self)
        self._is_send_request_value: bool = False   
        self._send_request_value_lock: threading.Lock = threading.Lock()
        
        # Contador de resposta de valores 
        self._cont_answer_value: int = 0
        
                        
        # Fila de mensagens entre listen_thread e thread Node padrão
        self._message_queue: queue.Queue = queue.Queue()
            
        self.logger = logger
        logger.info(f"✅ Servidor ID {self._process_id}, Rodada {self.round}, Iniciado com Sucesso!")
     
     
    # Métodos internos do Node

    def get_node_vote(self) -> int:
        """
        Retorna o voto do nó atual, que é o produto do quadrado do id do nó com o id do nó

        Returns:
            int: voto do nó atual
        """
        i = randint(1, 100)
        vote_value = i * i * self._process_id

        logger.info(f"🔢 Round {self.round}: Servidor {self._process_id} gera o número {i} para o consenso, com total = {vote_value}")
        return vote_value
    
    def __num_active_processes(self) -> int:
        """
        Retorna o número de processos ativos 

        Returns:
            int: número de processos ativos 
        """
        
        if self._df == None:
            raise Exception("Detctor de falhas não foi iniciado")
        
        return len(self._processes_id) - len(self._df.suspected_list())
    
    
    def __list_active_processes(self) -> list[int]:
        """
        Retorna a lista de todos os processos ativos no momento

        Returns:
            list[int]: lista de processos que estão ativos 
        """
        
        if self._df == None:
            raise Exception("Detctor de falhas não foi iniciado")
        
        return list(set(self._processes_id).difference(set(self._df.suspected_list())))
        
    
    def __leader_is_active(self) -> bool:
        """
        Retorna se o atual processo líder está ativo, caso o nó tenha perdido a eleição
        eventualmente algum nó será eleito como líder

        Returns:
            bool: se o processo líder está ativo True, caso contrário False
        """
        
        if self._df == None:
            raise Exception("Detctor de falhas não foi iniciado")
        
       
        leader: int | None = self._ele.get_leader()
        suspected: list[int] = self._df.suspected_list()
        
        # Se nenhum líder foi declarado
        if leader == None:
            return False
            
        # Se o líde estiver entre os processos suspeitos 
        
        elif leader in suspected:
            return False
        

        return True
        
    # Thread métodos
    
    def __main_thread_start(self) -> None:
        self._main_thread.start() 
        
        
    def __listen_thread_start(self) -> None:
        self._listen_thread.start()
        
        
    # LISTEN THREAD 
    
    def __send_leader_search_message(self, timeout: int) -> None:
        logger.info(f"❔ Servidor {self._process_id} pergunta para o sitema quem é o líder")
        
        with self._send_leader_search_message_lock:
            self._is_send_leader_search_message = True
        
        time.sleep(timeout)
        
        with self._send_leader_search_message_lock:
            self._is_send_leader_search_message = False
        
    
    def __send_LEADER_SEARCH(self) -> None:
        m: bytes = message(
                    message_enum=MessageEnum.LEADER_SEARCH,
                    sender_id=self._process_id,
                    payload="LEADER_SEARCH"
                )
        
        Message.send_multicast(m)
        
    
    def __send_LEADER_ACK(self) -> None:
        logger.info(f"⬆️ Servidor ID {self._process_id} envia uma mensagem identificando que é o líder")
                
        m_answer: bytes = message(
            message_enum=MessageEnum.LEADER_ACK,
            sender_id=self._process_id,
            payload=f"LEADER_ACK:{self._ele.get_leader()}"
        )
                
        Message.send_multicast(m_answer)
        
    def __send_request_value_message(self, timeout: int) -> None:
        """
        Requisita um valor para todos os outros servidores

        Args:
            timeout (int): tempo em que a mesagem será difundida pelo sistema
        """
        
        logger.info(f"🔢 Servidor {self._process_id} requisita os valores computados pelos outros servidores")
        
        with self._send_request_value_lock:
            self._is_send_request_value = True
        
        time.sleep(timeout)
        
        with self._send_request_value_lock:
            self._is_send_request_value = False
        
    
    def __diffusion_send_LEADER_SEARCH(self):
        search: bool = False
        with self._send_leader_search_message_lock:
            search = self._is_send_leader_search_message
            
        if search:
            self.__send_LEADER_SEARCH()
        
    def __handle_leader_search_message(self, m: dict) -> None:
        """
        Processa as mensagens recebidas sobre o serviço de pesquisa de líder 

        Args:
            message (bytes): messagem recebida pela rede como o type LEADER_SEARCH ou LEADER_ACK 
        """
        
        if m["type"] == MessageEnum.LEADER_SEARCH.value:
            if self._ele.leader_is_alive():
               self.__send_LEADER_ACK()
               
        
        # Se um Servidor pedir eleição mas líder está vivo    
        # if m["type"] == MessageEnum.ELECTION.value and self._ele.leader_is_alive():
        #     if self._ele.leader_is_alive():
        #         self.__send_LEADER_ACK()
                
                
        elif m["type"] == MessageEnum.LEADER_ACK.value and not self._ele.leader_is_alive():
            leader_id: int = m["payload"].split(":")[1]
            self._ele.set_leader(leader_id)
            logger.info(f"⬇️ Servidor ID {self._process_id} detctou que o Servidor {leader_id} é o atual líder")
            
            with self._send_leader_search_message_lock:
                self._is_send_leader_search_message = False
                
                
    def __handle_message(self, message: dict) -> None:
        """
        Processa as mensagens recebidas pela camada de transporte

        Args:
            message (dict): mensagem que foi recebida pelo sistema 
            addr (tuple): endereço do remetente (host, port)
        """
        # Mensagens do prórpio id são ignoradas 
        if message.get("sender_id") == self._process_id:
            return
        
        
        self._df.handle_df_message(message)
        self.__handle_leader_search_message(message)
        
        self.__diffusion_send_LEADER_SEARCH()
            
        self._ele.handle_election_message(message)
        
        # Put consensus-related messages in the queue for the leader to process
        if message.get("type") in [
            MessageEnum.BIZANTINE_START.value,
            MessageEnum.BIZANTINE_VOTE.value,
            MessageEnum.BIZANTINE_DECIDE.value,
        ]:
            self._message_queue.put(message)
        self.consensus_module.handle_message(message)
        
    def __listen_thread(self) -> None:
        def receive_message(m: bytes):
            message: dict = handle_message(m)
            
            self.__handle_message(message)
        
        Message.recv_multicast(receive_message)

        
    # MAIN THREAD 
    
    def __main_node_loop_thread(self) -> None:   
        self.__send_leader_search_message(2)
        while True:
            try:
                if self.__num_active_processes() >= 1:
                    if not self.__leader_is_active():  
                        self._ele.set_leader(None)
                        self._ele.start()
                    else:
                        logger.info(f"🫡 Nó {self._ele.get_leader()} é o atual líder")
                        if self._ele.is_leader():
                            self.consensus_module.run_leader_consensus()
                
                else:
                    self._ele.set_leader(None)
            except Exception as e:
                print(f"error: {e}")
                logger.warning(f"⚠️ Detector de falhas não foi iniciado, não é possível iniciar a tarefa do Servidor")
            logger.info(f"🤝 Servidor {self._process_id} está conectado a {self.__num_active_processes()} outros Servidores")
            time.sleep(2)
                
    # Métodos para o APP

    def init_node(self) -> None:
        # Inicia o detector de falhas
        self._df = DF(
            d=self._df_d,
            t=self._df_t,
            process_id=self._process_id,
            processes_list=self._processes_id
        )
        
        self._main_thread = threading.Thread(target=self.__main_node_loop_thread)
        self._listen_thread = threading.Thread(target=self.__listen_thread)
        
        self.__main_thread_start()
        self.__listen_thread_start()


    def node_is_leader(self) -> bool:
        return self._ele.get_leader() == self._processes_id()
    
    def consensus(self):
        return self.consensus_module.run_leader_consensus()

    def get_vote_value(self):
        i = randint(1, 100)
        return i * i * self._process_id


if __name__ == "__main__":
    import argparse
    
    processes_id: list[int] = [1, 2, 3, 4, 5]
    d: int = 3
    t: int = 2
    
    parser = argparse.ArgumentParser(description="Identificador de processo para o sistema")
    parser.add_argument("--id", type=int, help="Identificador de processo (id)", default=0)
    args = parser.parse_args()
    
    assert(args.id in processes_id)
    
    node: Node = Node(
        process_id=args.id,
        processes_id=processes_id,
        df_d=d,
        df_t=t,
        election_timeout=7
    )
    
    node.init_node(None)