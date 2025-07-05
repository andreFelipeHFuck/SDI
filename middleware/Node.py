"""
    Classe que representa um Node (Nó) dentro da aplicação,
    abstrai para a aplicação o identificador único (id), o líder, 
    os outros nós (peers)
"""

import logging
import threading
import queue
import time

from message.Message import Message, MessageEnum, message, handle_message
from DF import DF
from Election import Election

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
        self._round: int = round
        
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
        
        self._stop_event: threading.Event = threading.Event()
        
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
        
    
    # Thread métodos
    
    def __main_thread_start(self) -> None:
        self._main_thread.start() 
        
        
    def __listen_thread_start(self) -> None:
        self._listen_thread.start()
        
    def __stop(self) -> None:
        if self._df != None:
            self._df._DF__stop()
        
        self._stop_event.set()
        self._main_thread.join(timeout=0.1)
        print("Thread main parada")
        
        self._listen_thread.join(timeout=0.1)
        print("Thread listen parada")
        
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
        self._ele.handle_election_message(message)
     
        
    def __listen_thread(self) -> None:
        def receive_message(m: bytes):
            message: dict = handle_message(m)
            
            self.__handle_message(message)
        
        Message.recv_multicast(receive_message)

        
    # MAIN THREAD 
    
    def __main_node_loop_thread(self, leader_task) -> None:        
        while True:
            
            # Só inicia a tarefa se houver mais de um nó conectado a rede
            try:
                if self.__num_active_processes() >= 1:
                    if not self.__leader_is_active():                        
                        res = self._ele.start()
                        
                    else:
                        print(f"Nó {self._ele.get_leader()} é o atual líder")
                    
            except Exception as e:
                print(f"error: {e}")
                logger.warning(f"⚠️ Detctor de falhas não foi iniciado, não é possível iniciar a tarefa do nó")
                
                
            
            
            print(f"Nó {self._process_id} está conectado a {self.__num_active_processes()} outros nós")
            
            time.sleep(2)
            
                
    # Métodos para o APP

    def init_node(self, leader_task) -> None:
        # Inicia o detector de falhas
        self._df = DF(
            d=self._df_d,
            t=self._df_t,
            process_id=self._process_id,
            processes_list=self._processes_id
        )
        
        self._main_thread = threading.Thread(target=self.__main_node_loop_thread, args=(leader_task,))
        self._listen_thread = threading.Thread(target=self.__listen_thread)
        
        self.__main_thread_start()
        self.__listen_thread_start()


    def node_is_leader(self) -> bool:
        return self._ele.get_leader() == self._processes_id()
    
    
    def consensus(self) -> int:
        pass


if __name__ == "__main__":
    import argparse
    
    processes_id: list[int] = [1, 2, 3, 4, 5]
    d: int = 5
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
        election_timeout=5
    )
    
    node.init_node(None)