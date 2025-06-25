"""
    Classe que representa um Node (Nó) dentro da aplicação,
    abstrai para a aplicação o identificador único (id), o líder, 
    os outros nós (peers)
"""

import time 
import logging
import threading

from .message.Message import *

logger = logging.getLogger(__name__)

class Node():
    def __init__(self, process_id: int, seconds: int, round: int = 0):
        self._process_id: int = process_id
        self._leader: int = None
        self._seconds: int = seconds
        self._round: int = round
    
    
        logger.info(f"✅ Servidor ID {self._process_id}, Rodada {self._round} Iniciado com Sucesso!")
    
    def __str__(self):
        pass