"""_summary_
"""

import logging
from time import sleep
from random import random

from config.logger_config import setup_logger
import middleware


class App():
    def __init__(self, second: float):
        # self._process_id
        self._leader: bool = False
        self._second: float = second
        
    def program(self):
        """_summary_
        Código executado em loop na aplicação
        
        Onde o nó líder gera um número aleátorio i e envia para todos
        os outros nós, os nós que recebm o i devem responde o processo líder 
        com i*i*process_id
        """
        
        pass




def main() -> None:
    """Setup all configs and init App
    """
    
    # Setup logging system
    setup_logger()


if __name__ == "__main__":
    main()