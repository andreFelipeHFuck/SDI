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
    # UNICAST
    def test_send_unicast_messages_its_a_success(self):
        """
        Verifica se um nó é capaz de enviar uma mesagem unicast
        """
        
        m: bytes = message(
            message_enum=MessageEnum.TEST,
            sender_id=1,
            payload="ping"
        )
        
        port: int = 5005
        
        res: bool = Message.send_unicast(
                                            message=m,
                                            port=port
                                        )
        
        self.assertTrue(res)
        
    
    def test_sends_unicast_message_to_a_client_with_the_TEST_message(self):
        """
        Verifica se o servidor receve a mensagem TEST enviada pelo cliente via unicast
        """
        
        # Fila que devolve o valor da thread
        res_queue: queue.Queue = queue.Queue()
        
        port: int = 5005

        # Função de resposta do servidor         
        def handler():
            def f(m: bytes):
                msg: dict = handle_message(m)
                
                res_queue.put(msg.get("type"))
                
                exit()
                 
                 
            # Servidor            
            Message.recv_unicast(
                f=f,
                port=port
            )
            
            
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
        Message.send_unicast(
                                message=m,
                                port=port
                            ) 
                
        server_thead.join()   
          
        res: int = res_queue.get()    
        
        self.assertEqual(
            first=res,
            second=MessageEnum.TEST.value
        )   


    def test_sends_unicast_message_to_multiple_clients_with_TEST_message(self):
        """
        Verifica se vários servidores (nós) recebem a mensagem TESTE enviada por um cliente
        """
        
        port: int = 5005

        # Fila que devolve os valores recebido pelo servidor
        res_queue: queue.Queue = queue.Queue()
        
        def handler(port: int):
           def f(m: bytes):
                msg: dict = handle_message(m)
                
                res_queue.put((msg.get("type"), msg.get("sender_id")))
                
                exit()
                 
                 
           # Servidor            
           Message.recv_unicast(f=f, port=port)
           
           
        m: bytes = message(
            message_enum=MessageEnum.TEST,
            sender_id=1,
            payload="ping"
        )
        
        server_thead_1: threading.Thread = threading.Thread(target=handler, args=(port,))
        server_thead_2: threading.Thread = threading.Thread(target=handler, args=(port + 1,))
        server_thead_3: threading.Thread = threading.Thread(target=handler, args=(port + 2,))
        server_thead_4: threading.Thread = threading.Thread(target=handler, args=(port + 3,))
        server_thead_5: threading.Thread = threading.Thread(target=handler, args=(port + 4,))

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
        Message.send_unicast(message=m, port=port) 
        Message.send_unicast(message=m, port=port + 1) 
        Message.send_unicast(message=m, port=port + 2) 
        Message.send_unicast(message=m, port=port + 3) 
        Message.send_unicast(message=m, port=port  + 4) 
        
        server_thead_1.join()   
        server_thead_2.join()  
        server_thead_3.join()  
        server_thead_4.join()  
        server_thead_5.join()  
        
        # Verifica se todas as respostas estão corretas 
        id: int = 1
        cont: int = 0
        
        while not res_queue.empty():
            res: tuple = res_queue.get()  
            
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
            print(cont, res[0])
        
        self.assertEqual(
            first=cont,
            second=5
        )
        
        
    # MULTICAST
    def test_send_multicast_messages_its_a_success(self):
        """
        Verifica se um nó é capaz de enviar uma mesagem multicast
        """
        
        m: bytes = message(
            message_enum=MessageEnum.TEST,
            sender_id=1,
            payload="ping"
        )
                
        res: bool = Message.send_multicast(message=m)
                
        self.assertTrue(res)
        
    
    def test_sends_multicast_message_to_a_client_with_the_TEST_message(self):
        """
        Verifica se o servidor receve a mensagem TEST enviada pelo cliente via multicast
        """
        
        # Fila que devolve o valor da thread
        res_queue: queue.Queue = queue.Queue()
        
        # Função de resposta do servidor         
        def handler():
            def f(m: bytes):
                msg: dict = handle_message(m)
                
                res_queue.put(msg.get("type"))
                
                exit()
                 
                 
            # Servidor            
            Message.recv_multicast(f)
               
            
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
        Message.send_multicast(message=m) 
                
        server_thead.join()   
          
        res: int = res_queue.get()    
        
        self.assertEqual(
            first=res,
            second=MessageEnum.TEST.value
        )   
        
                
    def test_sends_multicast_message_to_multiple_clients_with_TEST_message(self):
        """
        Verifica se vários servidores (nós) recebem a mensagem TESTE enviada
        por um cliente 
        """   
        
        # Fila que devolve os valores recebido pelo servidor
        res_queue: queue.Queue = queue.Queue()  
        
        # Função de resposta do servidor         
        def handler():
           def f(m: bytes):
                msg: dict = handle_message(m)
                
                res_queue.put((msg.get("type"), msg.get("sender_id")))
                
                exit()
                 
                 
           # Servidor            
           Message.recv_multicast(f)
            
            
        m: bytes = message(
            message_enum=MessageEnum.TEST,
            sender_id=1,
            payload="ping"
        )
        
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
        Message.send_multicast(message=m) 
        
        server_thead_1.join()   
        server_thead_2.join()  
        server_thead_3.join()  
        server_thead_4.join()  
        server_thead_5.join()  
        
        # Verifica se todas as respostas estão corretas 
        id: int = 1
        cont: int = 0
        
        while not res_queue.empty():
            res: tuple = res_queue.get()  
            
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