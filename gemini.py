# server.py
import socket
import threading
import time
import json
import random
import sys

# --- Constantes de Configuração ---
MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT = 5007
HEARTBEAT_INTERVAL = 2  # segundos
PEER_TIMEOUT = 5        # segundos para considerar um peer como morto
ELECTION_TIMEOUT = 5    # segundos para esperar por uma resposta em uma eleição

class Server:
    def __init__(self, process_id):
        self.process_id = process_id
        self.peers = {self.process_id: time.time()} # Dicionário de peers e o último heartbeat
        self.leader = None
        self.is_election_in_progress = False
        self.responses_for_consensus = {}
        self.lock = threading.Lock()

        # Configuração do Socket Multicast
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', MULTICAST_PORT))
        mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        print(f"Servidor {self.process_id} iniciado.")

    def send_message(self, msg_type, payload={}):
        """Envia uma mensagem para o grupo multicast."""
        message = {
            "type": msg_type,
            "sender_id": self.process_id,
            "payload": payload
        }
        self.sock.sendto(json.dumps(message).encode('utf-8'), (MULTICAST_GROUP, MULTICAST_PORT))

    def listen_thread(self):
        """Thread que escuta por mensagens multicast."""
        while True:
            try:
                data, _ = self.sock.recvfrom(1024)
                message = json.loads(data.decode('utf-8'))
                self.handle_message(message)
            except json.JSONDecodeError:
                pass # Ignora mensagens malformadas

    def handle_message(self, message):
        """Processa as mensagens recebidas."""
        msg_type = message.get("type")
        sender_id = message.get("sender_id")

        if sender_id == self.process_id:
            return # Ignora as próprias mensagens

        # --- Lógica de Detecção de Falhas ---
        if msg_type == "HEARTBEAT":
            with self.lock:
                self.peers[sender_id] = time.time()

        # --- Lógica de Eleição (Valentão) ---
        elif msg_type == "ELECTION":
            # Se o meu ID é maior, eu respondo e começo minha própria eleição
            if self.process_id > sender_id:
                self.send_message("ELECTION_ACK")
                self.start_election()
        
        elif msg_type == "ELECTION_ACK":
            # Se recebo um ACK, significa que alguém maior está na disputa. Eu paro.
            with self.lock:
                self.is_election_in_progress = False

        elif msg_type == "VICTORY":
            with self.lock:
                self.leader = sender_id
                self.is_election_in_progress = False
            print(f"Servidor {self.process_id}: Novo líder eleito é {self.leader}")

        # --- Lógica da Aplicação e Consenso ---
        elif msg_type == "PROPOSE":
            # Líder propôs um valor 'i'. Calculo 'j' e respondo.
            if self.leader == sender_id:
                i = message["payload"]["i"]
                j = (i * i * self.process_id)
                print(f"Servidor {self.process_id}: Recebi i={i}, calculando j={j}")
                self.send_message("RESPONSE", {"j": j})

        elif msg_type == "RESPONSE":
            # Só o líder processa respostas
            if self.is_leader():
                j = message["payload"]["j"]
                with self.lock:
                    self.responses_for_consensus[sender_id] = j
    
    def main_loop_thread(self):
        """Thread principal que envia heartbeats, verifica peers e lidera."""
        while True:
            self.send_message("HEARTBEAT")
            self.check_peers()
            
            with self.lock:
                if self.leader is None and not self.is_election_in_progress:
                    print(f"Servidor {self.process_id}: Nenhum líder detectado. Iniciando eleição.")
                    self.start_election()

            if self.is_leader():
                self.run_leader_tasks()

            time.sleep(HEARTBEAT_INTERVAL)

    def check_peers(self):
        """Verifica se algum peer está inativo e remove da lista."""
        with self.lock:
            now = time.time()
            dead_peers = [pid for pid, last_seen in self.peers.items() if now - last_seen > PEER_TIMEOUT]
            
            for pid in dead_peers:
                print(f"Servidor {self.process_id}: Peer {pid} está inativo (timeout).")
                del self.peers[pid]
                
                # Se o líder morreu, limpa o líder e inicia uma eleição
                if pid == self.leader:
                    print(f"Servidor {self.process_id}: O LÍDER {self.leader} MORREU!")
                    self.leader = None
                    self.start_election()

    def start_election(self):
        """Inicia uma eleição usando o algoritmo do Valentão."""
        with self.lock:
            if self.is_election_in_progress:
                return
            self.is_election_in_progress = True
        
        print(f"Servidor {self.process_id}: Iniciando uma eleição.")
        
        # Envia mensagem de eleição para todos com ID maior
        higher_peers = [pid for pid in self.peers if pid > self.process_id]
        if not higher_peers:
            # Se não há ninguém maior, eu sou o líder
            self.declare_victory()
            return

        self.send_message("ELECTION")
        
        # Espera por um ACK. Se ninguém maior responder, eu ganho.
        time.sleep(ELECTION_TIMEOUT)
        
        with self.lock:
            if self.is_election_in_progress: # Se ninguém me parou (enviando ACK)
                self.declare_victory()

    def declare_victory(self):
        """Declara-se como o novo líder."""
        print(f"Servidor {self.process_id}: Eu venci a eleição!")
        with self.lock:
            self.leader = self.process_id
            self.is_election_in_progress = False
        self.send_message("VICTORY")
    
    def is_leader(self):
        """Verifica se este processo é o líder."""
        with self.lock:
            return self.leader == self.process_id

    def run_leader_tasks(self):
        """Executa a lógica da aplicação que só o líder faz."""
        print(f"--- LÍDER {self.process_id}: Rodada da aplicação ---")
        
        # i. sleep(N)
        # (A espera já acontece naturalmente no loop principal)
        
        # iii. i = random()
        i = random.randint(1, 100)
        
        # iv. send(i) for all
        print(f"Líder {self.process_id}: Propondo o valor i = {i}")
        with self.lock:
            self.responses_for_consensus = {} # Limpa respostas antigas
            # O líder também calcula seu próprio j
            self.responses_for_consensus[self.process_id] = (i * i * self.process_id)

        self.send_message("PROPOSE", {"i": i})
        
        # v. get(j) from all (if possible)
        # Espera um tempo para receber as respostas
        time.sleep(3) 
        
        # b. O processo líder imprimirá o valor recebido e definido como resposta correta (resultado do consenso)
        with self.lock:
            print("="*30)
            print(f"LÍDER {self.process_id}: RESULTADO DO CONSENSO")
            print(f"Valor de 'i' proposto: {i}")
            print("Valores 'j' recebidos (incluindo o meu):")
            for pid, j_val in self.responses_for_consensus.items():
                print(f"  - Servidor {pid}: j = {j_val}")
            print("="*30)
            # Limpa para a próxima rodada
            self.responses_for_consensus = {}

    def start(self):
        """Inicia as threads do servidor."""
        threading.Thread(target=self.listen_thread, daemon=True).start()
        threading.Thread(target=self.main_loop_thread, daemon=True).start()
        
        # Mantém a thread principal viva
        while True:
            time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python server.py <ID_DO_PROCESSO>")
        print("O ID deve ser um número inteiro (ex: 10, 20, 30).")
        sys.exit(1)
    
    try:
        process_id = int(sys.argv[1])
        server = Server(process_id)
        server.start()
    except ValueError:
        print("O ID do processo deve ser um número inteiro.")
    except KeyboardInterrupt:
        print(f"\nServidor {process_id} encerrado.")