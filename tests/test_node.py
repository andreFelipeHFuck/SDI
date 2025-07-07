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
    
    def test__num_active_processes_when_df_is_None(self) -> None:
        """
        Sem ativar o DF a função deve devolver um exceção
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
                        
        with self.assertRaises(Exception):
            node._Node__num_active_processes()


    def test__num_active_processe_when_df_active_but_only_one_process_is_active(self) -> None:
        """
        Com o detctor de falhas ativo o processo deve devolver que 0 processos estão ativos
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
        
        node.init_node(None)
        
        time.sleep(1)
        
        node._Node__stop()
                        
        self.assertEqual(node._Node__num_active_processes(), 0)
                
class TestNodeDF(unittest.TestCase):
    pass