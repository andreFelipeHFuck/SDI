"""
   Protocolo para envio (send) e recebimento (recv) de mensagens
   entre os nós de um Sistema Distribuído via multicast 
    
   Os tipos de mensagens que podem ser enviadas se encontram no Enum MessageEnum, sendo estas:
   
   SEND_NUM: envia um número para todos os nós do grupo
   TEST: utilizado para testes unitários no sistema 
"""


import socket
import struct
import json 
import logging

from middleware.message.MessageEnum import MessageEnum

logger = logging.getLogger(__name__)


"""
Conceitos:

    + Multicast: comunicação de dados para um grupo específico da rede, sendo a comunicação um para mutiplos nós

"""

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
    def __init__(self):
        # Criação do socket

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
        
        self.socket: socket = sock

    def send(self, message: bytes) -> bool:
        """
        Envia uma mensagem para todos os nós que pertecem ao grupo de multicast

        Args:
            message: a mensagem que será enviada para os outros nós por multicast
            
        Returns:
            bool: True se o envio da mensagem for sucesso, False caso contrário
        """
    
        # Configuração de endereço e porta multicast
        multicast_group: tuple = (MULTICAST_GROUP, MUSTICAST_PORT)
        
        try:
            # Envio de dados
            logger.info(f"⬆️ Mensagem enviando: {message}")
            sent: int = self.socket.sendto(message, multicast_group)
            
            logger.info("✅ Dados enviados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Não foi possível enviar os dados\nException:{e}")
            return False
        

    def recv(self) -> bytes:
        """
        Recebe uma mensagem enviada por um nó no sistema

        Args:
            sender: socket por onde a mensagem é recebida
            
        Returns:
            bytes: a resposta é devolvida no formato de bytes

        """
        
        data, _ = self.socket.recvfrom(1024)
        logger.info(f"⬇️ Mensagem Recebida: {message}")

        return data
    