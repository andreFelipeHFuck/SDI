"""
   Protocolo para envio (send) e recebimento (recv) de mensagens
   entre os nós de um Sistema Distribuído via unicast e multicast 
    
   Os tipos de mensagens que podem ser enviadas se encontram no Enum MessageEnum, sendo estas:
   
   * SEND_NUM: envia um número para todos os nós do grupo
   * TEST: utilizado para testes unitários no sistema 
"""


import socket
import struct
import json 
import logging
import time

from typing import Callable

from .MessageEnum import MessageEnum

logger = logging.getLogger(__name__)


"""
Conceitos:

    + Multicast: comunicação de dados para um grupo específico da rede, sendo a comunicação um para mutiplos nós

"""

UNICAST_IP: str = "127.0.0.1"
UNICAST_PORT: int = 5005

MULTICAST_GROUP: str = '224.1.1.1'
MUSTICAST_PORT: int = 5007

def message(message_enum: MessageEnum, sender_id, payload: str) -> bytes:
    return json.dumps({
        "type": message_enum.value,
        "sender_id": sender_id,
        "payload": payload
    }).encode('utf-8')
    

def handle_message(message: bytes) -> dict:
    return json.loads(message.decode('utf-8'))
    
        
class Message():
    """
    
    """
  

    @staticmethod
    def create_socket_multicast() -> socket:
        """
        Método estático que cria um socket multicast
        
        Returns:
            socket: socket multicast 
        """
        
        # Criação do socket multicast 

        # Configuração de porta multicast
        server_address = ('', MUSTICAST_PORT)
        
        sock: socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Configuração de opções do socket 
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Vinculação ao endereço do servidor
        sock.bind(server_address)

        # Participação no grupo multicast
        group = socket.inet_aton(MULTICAST_GROUP)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        return sock   
        
        
    @staticmethod
    def send_unicast(message: bytes, port: int) -> bool:
        """
        Envia uma messagem para apenas um nó do sistema

        Args:
            message (bytes): a mensagem que será enviada para o outro nó
            port (int): porta do nó onde será enviada a mensagem

        Returns:
            bool: True se o envio da mensagem for sucesso, False caso contrário
        """
        
        sock: socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            logger.info(f"⬆️ Mensagem Unicast Enviando: {message}")
            sock.sendto(message, (UNICAST_IP, port))
            logger.info("✅ Dados Enviados com Sucesso")

            return True
        
        except Exception as e:
            logger.error(f"❌ Não foi possível enviar os dados\nException:{e}")
            return False
        
        finally:
            sock.close()
            
    
    @staticmethod
    def recv_unicast(f: Callable[[bytes], None], port: int) -> None:
        """
        Recebe uma mensagem enviada por um nó do sistema por multcast

        Args:
            f (Callable): função de primeira ordem com as operações que devem
            ser feita com essa mensagem
            port (int): porta do nó onde será enviada a mensagem
            
        Returns:
            None: não retorna nada
        """
        
        s: socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        s.bind((UNICAST_IP, port))
        
        while True:
            data, _ = s.recvfrom(1024)

            logger.info(f"⬇️ Mensagem Unicast Recebida: {message}")
            
            f(data)


    @staticmethod
    def send_multicast(message: bytes) -> bool:
        """
        Envia uma mensagem para todos os nós que pertecem ao grupo de multicast

        Args:
            message (bytes): a mensagem que será enviada para os outros nós por multicast
            
        Returns:
            bool: True se o envio da mensagem for sucesso, False caso contrário
        """
    
        # Configuração de endereço e porta multicast
        multicast_group: tuple = (MULTICAST_GROUP, MUSTICAST_PORT)
        
        try:
            # Envio de dados
            logger.info(f"⬆️ Mensagem Multicast Enviando: {message}")
            s: socket = Message.create_socket_multicast()
            sent: int = s.sendto(message, multicast_group)
            
            logger.info("✅ Dados Enviados com Sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Não foi possível enviar os dados\nException:{e}")
            return False
        
        finally:
            s.close()
        

    @staticmethod
    def recv_multicast(f: Callable[[bytes], None]) -> None:
        """
        Recebe uma mensagem enviada por um nó do sistema por multcast

        Args:
            f (Callable): função de primeira ordem com as operações que devem
            ser feita com essa mensagem
            
        Returns:
            None: não retorna nada
        """
        
        s: socket = Message.create_socket_multicast()
        
        while True:
            data, _ = s.recvfrom(1024)
        
            logger.info(f"⬇️ Mensagem Multicast Recebida: {message}")
            
            f(data)
        