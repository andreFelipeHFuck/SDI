"""
Testes unitários para a classe Message, realizando a verificação da
troca de mensagens entre os nós
"""

import unittest

import threading
import queue

import time

from middleware.message.Message import Message, message, handle_message
from middleware.message.MessageEnum import MessageEnum

class TestMessageCommunication(unittest.TestCase):
    def test_send_messages_its_a_success(self):
        """
        Verifica se um nó é capaz de enviar uma mesagem multicast
        """
        
        m: bytes = message(
            message_enum=MessageEnum.TEST,
            sender_id=1,
            payload="ping"
        )
        
        node: Message = Message()
        
        res: bool = node.send(message=m)
                
        self.assertTrue(res)
        
    
    def test_message_exchange_between_client_and_services_returns_TEST(self):
        """
        Verifica se o servidor receve a mensagem TEST enviada pelo cliente
        """
        
        # Fila que devolve o valor da thread
        res_queue: queue.Queue = queue.Queue()
        
        # Função de resposta do servidor         
        def handler():
            # Servidor
            receiver: Message = Message()
            
            msg: dict = handle_message(receiver.recv())
                        
            res_queue.put(msg.get("type"))
            
        
        m: bytes = message(
            message_enum=MessageEnum.TEST,
            sender_id=1,
            payload="ping"
        )
        
        # Cliente
        sender: Message = Message()
        
        server_thead: threading.Thread = threading.Thread(
            target=handler
        )
        
        server_thead.start()
        
        time.sleep(0.2)
        
        # Envia a mesagem do cliente e recebe a resposta
        sender.send(message=m) 
        
        server_thead.join()   
        
        res: int = res_queue.get()    
        
        self.assertEqual(
            first=res,
            second=MessageEnum.TEST.value
        )        
                
  
    def test_message_exchange_between_client_and_services_returns_TEST_with_multicast(self):
        """
        Verifica se vários servidores (nós) recebem a mensagem TESTE enviada
        por um cliente 
        """   
        
        # Fila que devolve os valores recebido pelo servidor
        res_queue: queue.Queue = queue.Queue()  
        
        # Função de resposta do servidor         
        def handler():
            # Servidor
            receiver: Message = Message()
            
            msg: dict = handle_message(receiver.recv())
                        
            res_queue.put((msg.get("type"), msg.get("sender_id")))
            
        m: bytes = message(
            message_enum=MessageEnum.TEST,
            sender_id=1,
            payload="ping"
        )
        
        # Cliente
        sender: Message = Message()
        
        server_thead_1: threading.Thread = threading.Thread(target=handler)
        server_thead_2: threading.Thread = threading.Thread(target=handler)
        server_thead_3: threading.Thread = threading.Thread(target=handler)
        server_thead_4: threading.Thread = threading.Thread(target=handler)
        server_thead_5: threading.Thread = threading.Thread(target=handler)

        server_thead_1.start()
        time.sleep(0.2)
        
        server_thead_2.start()
        time.sleep(0.2)
        
        server_thead_3.start()
        time.sleep(0.2)
        
        server_thead_4.start()
        time.sleep(0.2)
        
        server_thead_5.start()
        time.sleep(0.2)
        
        # Envia a mesagem do cliente e recebe as respostas
        sender.send(message=m) 
        
        server_thead_1.join()   
        server_thead_2.join()  
        server_thead_3.join()  
        server_thead_4.join()  
        server_thead_5.join()  
        
        # Verifica se todas as respostas estão corretas 
        id: int = 1
        cont: int = 0
        
        while not res_queue.empty():
            res: int = res_queue.get()    

            # Verifica o tipo da mensagem 
            self.assertEqual(
                first=res[0],
                second=MessageEnum.TEST.value
            )     
            
            # Verifica o id
            self.assertEqual(
                first=res[1],
                second=1
            ) 
            
            cont += 1
            
        self.assertEqual(
            first=cont,
            second=5
        )
        
    
if __name__ == '__main__':
    unittest.main()