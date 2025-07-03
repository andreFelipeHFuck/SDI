import time

from message.Message import Message, message, handle_message
from message.MessageEnum import MessageEnum
 
if __name__ == "__main__":
    while True:
            m: bytes = message(
                message_enum=MessageEnum.TEST,
                sender_id=1,
                payload="ping"
            )
            
            print(f"[PRODUTOR] Enviou uma mensagem!")
            
            Message.send_multicast(message=m)
            
            time.sleep(1)