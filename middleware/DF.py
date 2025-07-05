"""
    Classe que implementa o Detector de Falhas (DF) do sistema, sendo executada em uma 
    thread própria em cada nó. DF pode ser consultado para informar o estado de qualquer 
    processo P.
    
    Devolver dois possiveis valores:
        DF(P) = {Suspected(P), Unsuspected(P)}
        
    * Suspected(P): há indícios de que P esteja falho
    * Unsuspected(P): há indícios de que P esteja correto (ativo)
    
    Premissa:
        Seja d o tempo de latência esperado na rede
        
        * A cada t unidade de tempo DF, difunde uma mesnasgem HEARTBEAT para todos 
        os demais DFs nos nós do sistema
        
        * Se um DF no nó Q não receber um HEARTBEAT de um outro DF P após t + k*d desde
        a última mensagem de HEARTBEAT recebida, então registra que Suspected(P)
        
        * O processo de aplicação consulta o DF local, e recebe uma lista dos processos 
        Pi que estão so supeita de falhas (suspected(Pi))
    
    O algoritmo utiliza as seguintes mensagens:
 
        MULTICAST:
        * HEARTBEAT: mensagem enviada por um nó identificando que o processo está vivo
        
    Em sistemas síncronos os DF são sempre confiáveis,
        Adota-se t como o início da fase de comunicação
        d = tempo máximo de transmissão de msgs 
"""


import time 
import logging
import threading

from enum import Enum

from .message.Message import Message, MessageEnum, message, handle_message

logger = logging.getLogger(__name__)

class DFState(Enum):
    SUSPECTED = 0
    UNSUSPECTED = 1


class DF():
    def __init__(self, d: int, t: int, process_id: int, processes_list: list[int]) -> None:
        self._d = d
        self._t = t
        
        self._process_id: int = process_id
        self._processes_state: dict = {k: [time.time(), 0, DFState.SUSPECTED] for k in processes_list if k != process_id}
        
        self._lock: threading.Lock = threading.Lock()
                
        send_heartbeat_thread: threading.Thread = threading.Thread(target=self.__df_send_heartbeat_thread)
        send_heartbeat_thread.start()
        
        logger.info(f"✅ Detector de Falhas do Servidor ID {self._process_id} Iniciado com Sucesso" )

    
    def suspected_list(self) -> list[int]:
        """
        Indica se deteminados processo tem índicio de terem falhados

        Returns:
            list[int]: lista dos id suspeitos 
        """
        
        with self._lock:
            suspected_list: list[int] = list(
                map(
                    lambda v: v[0],
                    filter(
                        lambda i : i[1][2].value == DFState.SUSPECTED.value,
                        self._processes_state.items())
                )
            )
                        
        return suspected_list

    
    def __send_heartbeat(self) -> None:
        m: bytes = message(
            message_enum=MessageEnum.HEARTBEAT,
            sender_id=self._process_id,
            payload="HEARTBEAT"
        )
        
        Message.send_multicast(message=m)
      
        
    def __verify_processes_state(self) -> None:
        """
        Verifica a quanto tempo faz que outro processo não envia um HEARTBEAT para 
        esse processo.
        
        Se for maior que t + d, adiciona o contador de quantas vezes não foi respondido.
        Caso seja maior que 3 vezes altera para SUSPECTED
        """
        
        for p in self._processes_state.values():
            now = time.time()
                        
            if now - p[0] > self._t + self._d:
                p[1] += 1
                
            if p[1] > 3:
                p[2] = DFState.SUSPECTED 
    
    
    def __df_send_heartbeat_thread(self) -> None:
        """
        Thread que envia as mensagens de HEARTBEAT para todos os nós
        """
        
        while True:
            self.__send_heartbeat()
            
            self.__verify_processes_state()
            
            time.sleep(self._t)
            
            
    def handle_df_message(self, message: dict) -> None:
        if message["type"] == MessageEnum.HEARTBEAT.value and self._process_id != message["sender_id"]:
            print("Mensagem recebida")
            now = time.time()
            
            with self._lock:
                self._processes_state[message["sender_id"]] = [now, 0, DFState.UNSUSPECTED]
            
            
        
    