"""
Testes unitários para a classe Node
"""

import unittest

import threading
import queue

import time

from middleware.Node import Node

class TestNode(unittest.TestCase):
    """
    Testes para os métodos internos da classe Node
    """
    
    def test__num_active_processes(self):
        """
        Verifica se devolve o número de processos ativos correo
        """
        
        process_id: int = 1
        processes_id: list[int] = [1, 2, 3, 4, 5]
        
        node: Node = Node(
            process_id=process_id,
            processes_id=processes_id,
            df_d=0,
            df_t=0,
            election_timeout=0,
        )
                
        self.assertRaises()

class TestNodeDF(unittest.TestCase):
    pass