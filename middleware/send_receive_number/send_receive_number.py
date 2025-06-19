"""_summary_ 
    
    Protocolo para envio (send) e recebimento (recv) de números 
    entre os nós de um Sistema Distribuído via multicast
"""

import socket

def send_for_all(num: int | float, multicast_group: str) -> bool:
    """Envia o número para todos os nós que pertecem ao grupo de multicast

    Args:
        num (int | float): número que será enviado para todos os nós 
        incluindo o próprio nó (multicast)
        
        multicast_group (str): endereço ip do grupo multicast para onde a mensagem será enviada
        
    Returns:
        bool: True if successful, False otherwise 
    """
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send(num: int | float, ip: str):
    """_summary_

    Args:
        num (int | float): número que será enviado para um nó especifico
        
        ip (str): endereço ip do nó para onde a mensagem será enviada
    """
    
    pass

def recv() -> int | float:
    """_summary_

    Returns:
        int | float: _description_
    """
    
    pass