from enum import Enum

class MessageEnum(Enum):
    TEST=          0
    SEND_NUM=      1
    
    # Algoritmo do Valentão
    ELECTION=      3
    ANSWER=        4
    COORDINATOR =  5
    
    # Detctor de Falhas
    HEARTBEAT =    6
    
    # Pesquisa do Líder
    LEADER_SEARCH = 7
    LEADER_ACK =    8
    
    # Bizantino
    BIZANTINE_PROPOSE = 9
    BIZANTINE_VOTE = 10
    BIZANTINE_DECIDE = 11