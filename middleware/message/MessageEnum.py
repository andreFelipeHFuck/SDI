from enum import Enum

class MessageEnum(Enum):
    TEST=         0
    SEND_NUM=     1
    
    # Algoritmo do Valentão
    ELECTION=     3
    ANSWER=       4
    COORDINATOR = 5
    
    # Detctor de Falhas
    HEARTBEAT =   6
    
    # Consenso
    PROPOSE = 7
    RESPONSE = 8
    CONSENSUS_RESULT = 9