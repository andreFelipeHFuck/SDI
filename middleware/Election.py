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
import threading

from .message.Message import Message, message, handle_message
from .message.MessageEnum import MessageEnum

from statemachine import StateMachine, State

logger = logging.getLogger(__name__)

class Election(StateMachine):
    # Estados
    normal: State = State(initial=True)
    candidate: State = State()
    elected: State = State(final=True)
    
    start_election = normal.to(candidate, cond="cond_start_election")
    apply  = normal.to(candidate, cond="cond_has_highest_id")
    lost = candidate.to(normal)
    win_election = candidate.to(elected)
    
    
    def __init__(self, process_id: int, processes_id: list[int], leader: int | None = None, timeout: int = 5):
        super().__init__()
        self._process_id: int = process_id
        self._processes_id: list[int] = processes_id
        
        self._leader: int = leader
        
        self._timeout: int = timeout
        
        self._lock: threading.Lock = threading.Lock()

    
    # Métodos contendo metadados
    
    def get_process_id(self) -> int:
      return self._process_id
    
    
    def set_leader(self, leader_id: int) -> None:
      with self._lock:
          print(f"N: {self._leader}, L: {leader_id}")
          if leader_id != None:
            logger.info(f"📝 Servidor ID {self._process_id} identificou que o Servido ID {leader_id} é o nó líder")
            
            self._leader = int(leader_id)
          else:
            self._leader = leader_id
          
            
    def __set_leader(self, leader_id: int) -> None:
      logger.info(f"🏆 Servidor ID {leader_id} ganhou a eleição")
      if leader_id != None:
        self._leader = int(leader_id)
      else:
        self._leader = leader_id
      
      
    def get_leader(self) -> int | None:
      with self._lock:
        leader: int = self._leader
        
      return leader
  
    
    def is_leader(self) -> bool:
     with self._lock:
       is_leader: bool = self._process_id == self._leader
       
     return is_leader
   
   
    def leader_is_alive(self) -> bool:
      """
      Verifica se o líder está vivo

      Returns:
          bool: caso esteja vivo True, caso contrário False
      """
      
      with self._lock:
        is_alive: bool = self._leader != None
        
      return is_alive
   
   
    def __leader_is_alive(self) -> bool:
      """
      Verifica se o líder está vivo

      Returns:
          bool: caso esteja vivo True, caso contrário False
      """
      
      return self._leader != None
   
   
    def is_in_election(self) -> bool:
      with self._lock:
        is_in_election: bool = self.current_state.id == "candidate"
        
      return is_in_election
    
    
    def __send_ELECTION_message(self) -> None:
      m: bytes = message(
              message_enum=MessageEnum.ELECTION,
              sender_id=self._process_id,
              payload="ELECTION"
      )
      
      Message.send_multicast(message=m)
      
    
    def __resend_ELECTION_message(self) -> None:
      """
      Se eleição estiver no estado candidate a mensagem ELECTION é reenviada no sistema
      """
      
      if self.is_in_election():
        self.__send_ELECTION_message()
        
      
   
    def __send_ANSWER_message(self) -> None:
      m_answer: bytes = message(
              message_enum=MessageEnum.ANSWER,
              sender_id=self._process_id,
              payload="ANSWER_ACK"
      )
      
      Message.send_multicast(message=m_answer)
      
    
    def __send_COORDINATOR_message(self):
      m: bytes = message(
              message_enum=MessageEnum.COORDINATOR,
              sender_id=self._process_id,
              payload="COORDINATOR"
      )
      
      Message.send_multicast(message=m)
    
    # Transições e Condições da Máquina de Estados 
    
    def cond_start_election(self) -> bool:
      return not self.__leader_is_alive()
   
   
    def before_start_election(self) -> None:
      """
      Envia a mensagem de eleição para todos os nós com id maior
      """
      
      logger.info(f"🗳️ Servidor ID {self._process_id} inicia a eleição")
      
      self.__send_ELECTION_message()
      
      
    def cond_has_highest_id(self, message: dict) -> bool:
      print(f"Teste: {self._process_id > message["sender_id"]}")
      return self._process_id > message["sender_id"] 
    
    
    def before_apply(self) -> None:
      """
      Quando um nó se candidata como possível candidato a coordenador 
      envia a mensagem ANSWER para o nó que iniciou a eleição,
      após isso envia uma mensagem ELECTION para iniciar uma nova 
      eleição
      """
            
      self.__send_ANSWER_message()
      
      logger.info(f"🗳️ Servidor ID {self._process_id} inicia a eleição após ANSWER")
      
      self.__send_ELECTION_message()
                  
    
    def before_lost(self) -> None:
      pass
              
    
    def before_win_election(self) -> None:
      
      logger.info(f"🏆 Servidor ID {self._process_id} ganhou a eleição")
      print(f"🏆 Servidor ID {self._process_id} ganhou a eleição")
      
      
      self.__send_COORDINATOR_message()
      
      self._leader = self._process_id
      
    # Métodos contendo uma interface para as eleições 
    
    def __election_process(self) -> bool:
      """
      Realiza o processo de eleição no sistema, verifica se o n
      
      Args:
          timeout (int): tempo que nó vai esperar até declarar que é o líder do sistema

      Returns:
          bool: se o processo de eilação ocorrer normalmente retorna True, caso contrário False
      """
      
      logger.info(f"✍️ Servidor ID {self._process_id} iniciou o processos de eleição")
      
      try:
        if self._process_id == max(self._processes_id):
          with self._lock:
            if self.current_state.id == "candidate":
              self.send("win_election")
            
            else:
              return False
            
        else:
          time.sleep(self._timeout)
          
          with self._lock:
            """ 
            Se após o timeout a máquina de estados estiver em candidate faz a transição 
            para o estado elected
            """
            if self.current_state.id == "candidate":
              self.send("win_election")
        
        return True
      except Exception as e:
        print(f"error: {e}")
        return False
      
    
    def start(self) -> bool:
      """
      Método para iniciar uma eleição no sistema distribuído

      Args:
          timeout (int): tempo que nó vai esperar até declarar que é o líder do sistema
          
      Returns:
          bool: se o processo de eilação ocorrer normalmente retorna True, caso contrário False
      """
      
      try:
         with self._lock:
           if self.current_state.id == "normal":
             self.send("start_election")
           
      except Exception as e:
         logger.error(f"Estado inconsistente, error: {e}")
         return False
       
       
      res: bool = self.__election_process()
      
      return res
      
          
    def __message_ELECTION(self, message: bytes) -> None:
       sender_id_is_greater_than_id: bool = False
       with self._lock:
            if self.current_state.id == "normal":
              logger.info(f"🙋 Servidor ID {self._process_id} envia ANSWER para o Servidor {message["sender_id"]} que requesitou a eleição")
              self.send("apply", message)
            
            elif self.current_state.id == "candidate":
              sender_id_is_greater_than_id = True

       if sender_id_is_greater_than_id:
          logger.info(f"🙋 Servidor ID {self._process_id} possui um ID maior que o Servidor {message["sender_id"]}, então envia ANSWER para quem requesitou a eleição")
          self.__send_ANSWER_message()
              
              
    def __message_ANSWER(self, message: bytes) -> None:
      with self._lock:
            if self.current_state.id == "candidate":
              logger.info(f"🤦 Servidor ID {self._process_id} perdeu a eleição para o Nó {message["sender_id"]}")       
              self.send("lost")

              
    def __message_COORDINATOR(self, message: bytes) -> None:
       with self._lock:
            if self.current_state.id == "normal":
              self.__set_leader(int(message["sender_id"]))
            
            if self.current_state.id == "candidate":
              logger.info(f"🤦 Servidor ID {self._process_id} perdeu a eleição para o Nó {message["sender_id"]}")       
              self.send("lost")
              self.__set_leader(int(message["sender_id"]))

              

    def handle_election_message(self, message: dict) -> None:
      try:
        if message["type"] == MessageEnum.ELECTION.value and self._process_id > message["sender_id"]:
          self.__message_ELECTION(message)
           
              
        # Algum nó com id maior pretende ser o coordenador 
        elif message["type"] == MessageEnum.ANSWER.value and self._process_id < message["sender_id"]:
          self.__message_ANSWER(message)
              
              
        elif message["type"] == MessageEnum.COORDINATOR.value:
          self.__message_COORDINATOR(message)
              
  
      except Exception as e:
        print(f"error: {e}")
        
      # Reenvia a mensagem ELECTIO se o nó estiver como candidato
      self.__resend_ELECTION_message()


  
  
  
  
     
     
   
   
  


        
    
    

    
    