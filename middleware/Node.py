"""
    Classe que representa um Node (Nó) dentro da aplicação,
    abstrai para a aplicação o identificador único (id), o líder, 
    os outros nós (peers)
"""

import time 
import logging
import threading

from .election.ElectionEnum import ElectionEnum
from .message.Message import *

logger = logging.getLogger(__name__)

class Node():
    def __init__(self, seconds: int):
        self._process_id = 1 # process_id será atribuído com um número único
        self._leader: ElectionEnum = ElectionEnum.NONE
        self._seconds: int = seconds
    
    
        logger.info(f"✅ Servidor ID {self._process_id} Iniciado com Sucesso!")
    
    def __str__(self):
        pass