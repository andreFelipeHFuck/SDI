"""
Algoritmo que realiza o consenso entre os nós de um sistema 
distribuído.

Requisitos do algoritmo:

    * Terminação: Em algum momento, cada processo correto atinge o estado
      DECIDED e atribui um valor à variavel de decisão d_i
      
    * Acordo: Todos os processos corretos atribuem o mesmo valor para a 
    variável de decisão
    
    * Integridade: Se todos os processo corretos propuseram o mesmo valor v_i = v,
    então qq processo correto no estado DECIDED terár decidido d_v = v
    
Algortimo para falhas de colapso: 

    * Presume-se que até f dos N processo apresentam falhas por colapso

"""

from enum import Enum

class ConsensusState(Enum):
    DECIDED = 0
    UNDECIDED = 1

import time
import logging
import threading

from collections import Counter

from .message.Message import Message, message, handle_message
from .message.MessageEnum import MessageEnum

logger = logging.getLogger(__name__)


# Função determinica que permite o acordo e a integridade
def majority(values: list[int]) -> int | None:
    """
    Devolver o valor que mais aparece na lista

    Args:
        list_n (list[int]): lista de valores

    Returns:
        int | None: se houver um valor majoritário devolve o valor,
        se não houver devolve None
    """
    
    count_values: Counter = Counter(values)
    
    max_counter = max(count_values.values())
    
    moda: list[int] = [k for k, v in count_values.items() if v == max_counter]
    
    return moda[0] if len(moda) == 1 else None


class Consensus():
    def __init__(self, process_id: int, processes_list: list[int], f: int):
        self._process_id: int = process_id
        self._processes_list: list[int] = processes_list
        
        # Número de rodadas que o algoritmo irá realizar
        self._rounds_limit: int = f + 1
        
        # Conjunto de mensagens válidas recebidas 
        self._received_values: set = set()
       
    def __send():
        pass
        
    def __dolev_strong(self, value: tuple[int, int]) -> tuple[int, int] | None:
        """
        Algoritmo de consenso que suporta até f falhas por colapso

        Args:
            value (tuple[int, int]): _description_

        Returns:
            tuple[int, int] | None: _description_
        """
    
    
    
    def consensus(self, value: tuple[int, int]) -> tuple[int, int] | None:
        pass
        
        