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

from middleware.message.Message import Message, message, handle_message
from middleware.message.MessageEnum import MessageEnum

class Election():
    def __init__(self, process_id: int, leader: int):
        self._process_id: int = process_id
        self._leader: int = leader
        
        
    def get_leader(self) -> int:
      return self._leader
    
    
    def is_leader(self) -> bool:
     return self._id == self._leader
   
   
  


        
    
    

    
    