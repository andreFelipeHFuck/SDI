import time
import threading

from message.Message import handle_message, Message

from DF import DF

def listen_thread(df: DF) -> None:
    print("Escutador iniciado")
    def receive_message(m: bytes):
        message: dict = handle_message(m)
        
        df.handle_df_message(message)
        
    Message.recv_multicast(receive_message)

if __name__ == "__main__":
    d: int = 5
    t: int = 2
    
    processes_list: list[int] = [1, 2, 3, 4, 5]
    process_id: int = 1
        
    df: DF = DF(
        d=d,
        t=t,
        process_id=process_id,
        process_list=processes_list
    )
    
    listen_thread: threading.Thread = threading.Thread(target=listen_thread, args=(df, ))
    
    listen_thread.start()
    
    while True:
        time.sleep(2) 
        
        print(f"Processos Suspeitos: {df.suspected_list()}")