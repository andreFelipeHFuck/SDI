"""_summary_
"""

import logging

from time import sleep
from random import randint

from config.logger_config import setup_logger
from middleware import Node

logger = logging.getLogger(__name__)

class App(Node.Node):
    def __init__(self, seconds: int = 1):
        super().__init__(seconds)
        
    def leader_task(self):
        """
        Código executado em loop na aplicação
        
        Onde o nó líder gera um número aleátorio i e envia para todos
        os outros nós, os nós que recebm o i devem responde o processo líder 
        com i*i*process_id
        """
        
        pass

def main() -> None:
    """
    Inicia todas as configurações do sistema
    """
    
    # Setup logging system
    setup_logger()
    

    app = App()

if __name__ == "__main__":
    main()