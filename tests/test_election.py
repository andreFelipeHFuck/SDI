"""
Testes unitários para a classe Election, do qual oferece uma máquina de 
estados para as operações do algoritmo de eleição do valentão
"""

import sys
import os
import unittest

import threading
import queue

import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from middleware.Election import Election

from middleware.message.Message import Message, message, handle_message
from middleware.message.MessageEnum import MessageEnum


class TestElection(unittest.TestCase):
    def test_star_election_produces_ELECTION_message_to_other_nodes(self):
        """
        Quando um nó inicia uma eleição este envia uma mensagem em multicast para 
        todos os outros nós com o tipo ELECTION
        """
        
        res_queue: queue.Queue = queue.Queue()
        
        def handler():
            def f(m: bytes):
                msg: dict = handle_message(m)
                
                res_queue.put(msg)
                
                exit()
            
            Message.recv_multicast(f)
            
        server_thead: threading.Thread = threading.Thread(
            target=handler
        )
        
        server_thead.start()
        
        time.sleep(0.2)
        
        # Cria a máquina de estados e realiza a transição
        ele = Election(process_id=5)
        ele.send("start_election")
        
        server_thead.join()
        
        res: dict = res_queue.get()
        
        self.assertEqual(
            first=res.get("type"),
            second=MessageEnum.ELECTION.value
        )  
        
        self.assertEqual(
            first=res.get("sender_id"),
            second=5
        )  
        
        self.assertEqual(
            first=res.get("payload"),
            second="ELECTION"
        )  


    def test_if_no_one_answers_the_node_wins_the_election(self):
        """
        Quando o nó inicia a eleição outros nós podem responde-lo em um certo
        período de tempo, caso contrário o nó ganha a eleição
        """
        
        res_queue: queue.Queue = queue.Queue()
        
        def handler():
            def f(m: bytes):
                msg: dict = handle_message(m)
                
                
                if msg["type"] == MessageEnum.COORDINATOR.value:
                    res_queue.put(msg)
                
                    exit()
            
            Message.recv_multicast(f)
            
        server_thead: threading.Thread = threading.Thread(
            target=handler
        )
        
        server_thead.start()
        
        time.sleep(0.2)
        
        # Cria a máquina de estados e realiza a transição
        ele = Election(process_id=5)
        ele.send("start_election")
        
        time.sleep(2)
        
        ele.send("win_election")
        
        server_thead.join()
        
        res: dict = res_queue.get()
        
        self.assertEqual(
            first=res.get("type"),
            second=MessageEnum.COORDINATOR.value
        )  
        
        self.assertEqual(
            first=res.get("sender_id"),
            second=5
        )  
        
        self.assertEqual(
            first=res.get("payload"),
            second="COORDINATOR"
        )  
        

    def node_responds_to_ELECTION_message(self):
        """
        O nó com maior id responde o um nó de menor id que enviou a
        mensagem ELECTION, seu estado deve ser candidate após essa operação
        """
        
        res_queue: queue.Queue = queue.Queue()
        
        def handler():
            def f(m: bytes):
                msg: dict = handle_message(m)
                
                res_queue.put(msg)
                if msg["type"] == MessageEnum.ELECTION.value and msg["sender_id"] == 6:                
                    exit()
            
            Message.recv_multicast(f)
            
        server_thead: threading.Thread = threading.Thread(
            target=handler
        )
        
        server_thead.start()
        
        time.sleep(0.2)
        
        # Cria a máquina de estados e realiza a transição
        ele_1 = Election(process_id=5)
        ele_2 = Election(process_id=6)
        
        ele_1.send("start_election")
        
        message = res_queue.get()
        
        # Verifica se a mensagem enviada foi ELECTION com id 5
        self.assertEqual(
            first=message.get("type"),
            second=MessageEnum.ELECTION.value
        )  
        
        self.assertEqual(
            first=message.get("sender_id"),
            second=5
        )  
        
        self.assertEqual(
            first=message.get("payload"),
            second="ELECTION"
        )  
        
        ele_2.send("appley", message)
        
        
        res: dict = res_queue.get()
        
        self.assertEqual(
            first=res.get("type"),
            second=MessageEnum.ANSWER.value
        )  
        
        self.assertEqual(
            first=res.get("sender_id"),
            second=6
        )  
        
        self.assertEqual(
            first=res.get("payload"),
            second="ANSWER_ACK"
        )  
        
        ele_1.send("lost")
        
        server_thead.join()
        
        res = res_queue.get()
                
        self.assertEqual(
            first=res.get("type"),
            second=MessageEnum.ELECTION.value
        )  
        
        self.assertEqual(
            first=res.get("sender_id"),
            second=6
        )  
        
        self.assertEqual(
            first=res.get("payload"),
            second="ELECTION"
        )  
        
        # Verifica se os ele estão nos estados corretos
        self.assertEqual(
            first=ele_1.current_state.id,
            second="normal"
        )
        
        self.assertEqual(
            first=ele_2.current_state.id,
            second="candidate"
        )