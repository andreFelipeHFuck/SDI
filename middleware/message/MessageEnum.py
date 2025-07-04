from enum import Enum

class MessageEnum(Enum):
    TEST=        0
    SEND_NUM=    1
    
    # Bully Algorithm
    ELECTION=    3
    ANSWER=      4
    COORDINATOR= 5
    
    WHO_IS_THERE = 6
    I_AM = 7