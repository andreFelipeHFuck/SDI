import time

from message.Message import Message, message, handle_message
from message.MessageEnum import MessageEnum
 
if __name__ == "__main__":
    while True:
            process_id: int = 2
            
            m: bytes = message(
                message_enum=MessageEnum.HEARTBEAT,
                sender_id=process_id,
                payload="HEARTBEAT"
            )
            
            print(f"[PRODUTOR] Enviou uma mensagem! ID: {process_id}")
            
            Message.send_multicast(message=m)
            
            time.sleep(1)