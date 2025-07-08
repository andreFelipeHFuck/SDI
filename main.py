"""

"""

import logging
import argparse
from time import sleep, time
from random import randint

from config.logger_config import setup_logger
from middleware import Node
from middleware.message.MessageEnum import MessageEnum

logger = logging.getLogger(__name__)

class App(Node.Node):
    def __init__(self, process_id: int, processes_id: list[int], df_d: int, df_t, election_timeout: int):
        super().__init__(
            process_id=process_id,
            processes_id=processes_id,
            df_d=df_d,
            df_t=df_t,
            election_timeout=election_timeout
        )

    def main(self) -> None:
        self.init_node()

def main(id: int = 1) -> None:
    """
    Inicia todas as configurações do sistema
    """
    
    setup_logger(id)
    
    d: int = 2
    t: int = 1
    election_timeout: int = 5
    
    processes_id: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    app = App(
        process_id=id,
        processes_id=processes_id,
        df_d=d,
        df_t=t,
        election_timeout=election_timeout
    )
    
    app.main()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Identificador de processo para o sistema")
    parser.add_argument("--id", type=int, help="Identificador de processo (id)", default=0)
    args = parser.parse_args()
    
    main(args.id)