"""
Algoritmo que elege um novo líder entre os nós por meio
do algoritmo do valentão.

Suposições:

 * Processo pode falhar a qualquer momento, inclusive durante a execução do algoritmo
 * Um processo falha por omissão de porcesso e retorna ao reiniciar
 * Cada processo sabe o seu id de processo e o seu endereço, e o de todos os outros 
 processos

O algoritmo utiliza as seguintes mensagens:
 
  MULTICAST:
  *  ELECTION: anuncia o uma eleição
  *  ANSWER: responde a mensagem ELECTION  
  *  COORDINATOR: mensagem enviada pelo vencedor para anunciar a sua vitória
  
  Quando um processo P detectar que o coordenador atual falhou, P executa 
  as seguintes ações:
  
  1. Se P tiver o maior id, este envia uma mensagem COORDINATOR para
  todos os outros processos e se tornará o novo líder. Caso contrário, 
  P transmite uma mensagem de ELECTION para todos os outros processos 
  com id de valor mais alto do que ele.
  
  2. Se P não receber nenhuma resposta depois de enviar uma mensagem
  de ELECTION, ele transmitirá uma mensagem de COORDINATOR a todos os outros
  processo e se tornará o líder
  
  3. Se P receber uma resposta de um processo com id superior, ele não 
  enviarár mais mensagens para essa eleição e aguardará uma mensgem 
  de COORDINATOR.
    * Se não houver nenhuma mensagem de COORDINATOR após um período de tempo,
    o processo será reiniciado no começo
  
  4. Se P receber uma mensagem de ELECTION de outro processo com id inferior,
  este envia uma mensagem ANSWER de volta e, se ainda não tiver 
  iniciado uma eleição, ele iniciará o processo de eleição desde
  o ínicio, enviando uma mensagem ELECTION para o processos com
  números mais altos.
  
  5. Se P receber uma mensagem COORDINATOR, este tatará o remetente
  como o líder.
"""

import time
import logging
import queue

from .message.Message import Message, message, handle_message
from .message.MessageEnum import MessageEnum

from statemachine import StateMachine, State

logger = logging.getLogger(__name__)

class Election(StateMachine):
    # Estados
    normal: State = State(initial=True)
    candidate: State = State()
    elected: State = State(final=True)
    
    start_election = normal.to(candidate)
    appley  = normal.to(candidate, cond="cond_has_highest_id")
    lost = candidate.to(normal)
    win_election = candidate.to(elected)
    
    
    def __init__(self, process_id: int, leader: int | None = None):
        super().__init__()
        self._process_id: int = process_id
        self._leader: int = leader
        
        
    def get_process_id(self) -> int:
      return self._process_id
        
    def set_leader(self, leader_id: int) -> None:
      logger.info(f"🗳️ Servidor ID {leader_id} ganhou a eleição")
      self._leader = leader_id
      
      
    def get_leader(self) -> int:
      return self._leader
  
    
    def is_leader(self) -> bool:
     return self._id == self._leader
   
   
    def is_not_in_election(self) -> bool:
      return self.current_state.id == "normal"
   
    def before_start_election(self) -> None:
      """
      Envia a mensagem de eleição para todos os nós com id maior
      """
      
      logger.info(f"🗳️ Servidor ID {self._process_id} inicia a eleição")
      print(f"🗳️ Servidor ID {self._process_id} inicia a eleição")
      
      m: bytes = message(
              message_enum=MessageEnum.ELECTION,
              sender_id=self._process_id,
              payload="ELECTION"
      )
      
      Message.send_multicast(message=m)
      
      
    def cond_has_highest_id(self, message: dict) -> bool:
      return self._process_id > message["sender_id"]
    
    def before_appley(self) -> None:
      """
      Quando um nó se candidata como possível candidato a coordenador 
      envia a mensagem ANSWER para o nó que iniciou a eleição,
      após isso envia uma mensagem ELECTION para iniciar uma nova 
      eleição
      """
      
      logger.info(f"🙋 Servidor ID {self._process_id} envia ANSWER para quem requesitou a eleição")
      print(f"🙋 Servidor ID {self._process_id} envia ANSWER para quem requesitou a eleição")
      
      m_answer: bytes = message(
              message_enum=MessageEnum.ANSWER,
              sender_id=self._process_id,
              payload="ANSWER_ACK"
      )
      
      Message.send_multicast(message=m_answer)
      
      logger.info(f"🗳️ Servidor ID {self._process_id} inicia a eleição")
      print(f"🗳️ Servidor ID {self._process_id} inicia a eleição")
      
      m: bytes = message(
              message_enum=MessageEnum.ELECTION,
              sender_id=self._process_id,
              payload="ELECTION"
      )
      
      Message.send_multicast(message=m)
      
    
    def before_lost(self) -> None:
       logger.info(f"🤦 Servidor ID {self._process_id} perdeu a eleição")
       print(f"🤦 Servidor ID {self._process_id} perdeu a eleição")
       
    
    def before_win_election(self) -> None:
      
      logger.info(f"🙆 Servidor ID {self._process_id} ganhou a eleição")
      print(f"🙆 Servidor ID {self._process_id} ganhou a eleição")
      
      m: bytes = message(
              message_enum=MessageEnum.COORDINATOR,
              sender_id=self._process_id,
              payload="COORDINATOR"
      )
      
      Message.send_multicast(message=m)
      
      self._leader = self._process_id
      


if __name__ == "__main__":  
  ele = Election(process_id=1)
  
  img_path = "readme_election.png"
  ele._graph().write_png(img_path)
  
  ele.send("start_election")
  ele.send("win_election")
  
  
  
     
     
   
   
  


        
    
    

    
    