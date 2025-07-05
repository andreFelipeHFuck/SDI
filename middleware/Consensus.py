"""
    Classe Consensus
    ----------------
    Responsável por implementar o serviço de consenso entre os nós do sistema distribuído.
    O objetivo é garantir que todos os nós concordem em um único valor para cada rodada.

    # Estrutura e funcionamento sugeridos:

    1. O processo líder inicia uma rodada de consenso:
        - Gera um valor (ex: i = random())
        - Envia uma mensagem PROPOSE para todos os outros nós, contendo o valor proposto e o número da rodada.

    2. Cada nó participante, ao receber a mensagem PROPOSE:
        - Calcula seu próprio valor de resposta (ex: j = i * i * process_id)
        - Envia uma mensagem RESPONSE de volta ao líder, contendo o valor calculado e o número da rodada.

    3. O líder coleta todas as respostas (incluindo a sua própria):
        - Aguarda respostas de todos os nós ativos (pode usar a lista de nós não suspeitos do DF).
        - Define o valor de consenso (ex: max(j) ou outro critério definido).
        - Envia uma mensagem CONSENSUS_RESULT para todos os nós, informando o valor final acordado e o número da rodada.

    4. Todos os nós, ao receberem CONSENSUS_RESULT:
        - Registram/imprimem o valor de consenso para aquela rodada.

    # Pontos importantes para implementação:
    - O consenso deve ser feito para cada rodada (round), identificada por um número único.
    - O líder deve lidar com timeouts: se algum nó não responder, pode seguir com os valores recebidos ou marcar como falho.
    - O consenso deve ser robusto a falhas do líder: se o líder falhar no meio do processo, uma nova eleição deve ocorrer e a rodada pode ser reiniciada.
    - As mensagens devem conter o número da rodada para evitar confusão entre rodadas diferentes.
    - O consenso pode ser implementado de forma síncrona (aguardando todas as respostas) ou assíncrona (seguindo após timeout).
    - O resultado do consenso deve ser claramente comunicado e registrado em todos os nós.

    # Mensagens sugeridas:
    - PROPOSE: enviada pelo líder para propor um valor.
    - RESPONSE: enviada pelos nós participantes com seu valor calculado.
    - CONSENSUS_RESULT: enviada pelo líder com o valor final acordado.

    # Exemplo de uso:
    - consensus = Consensus(process_id, df_instance)
    - consensus.start_round(round_number, proposed_value)
    - consensus.handle_message(message)
    - consensus.get_result(round_number)

    # Implementação detalhada deve seguir estes comentários.
"""

import threading
import time
import logging
import json
from message.Message import Message, MessageEnum, message, handle_message

logger = logging.getLogger(__name__)

class Consensus:
    def __init__(self, process_id: int, df_instance, is_leader: bool = False):
        self._process_id: int = process_id
        self._df = df_instance  # Detector de Falhas
        self._is_leader: bool = is_leader
        self._lock: threading.Lock = threading.Lock()
        self._round_results: dict = {}  # round_number -> consensus result
        self._pending_responses: dict = {}  # round_number -> {pid: value}
        self._current_round: int = 0
        self._proposed_value = None

    def start_round(self, round_number: int, proposed_value):
        """
        Inicia uma nova rodada de consenso (apenas o líder chama).
        Envia PROPOSE para todos os nós não suspeitos.
        """
        with self._lock:
            self._current_round = round_number
            self._proposed_value = proposed_value
            self._pending_responses[round_number] = {self._process_id: self._calculate_response(proposed_value)}
        
        msg = message(
            message_enum=MessageEnum.PROPOSE,
            sender_id=self._process_id,
            payload=json.dumps({"round": round_number, "value": proposed_value})
        )
        Message.send_multicast(message=msg)
        logger.info(f"[Consensus] Líder enviou PROPOSE para round {round_number} com valor {proposed_value}")

    def handle_message(self, msg: dict):
        """
        Processa mensagens de consenso (PROPOSE, RESPONSE, CONSENSUS_RESULT).
        """
        msg_type = msg.get("type")
        sender_id = msg.get("sender_id")
        payload = msg.get("payload")
        if msg_type == MessageEnum.PROPOSE.value:
            data = json.loads(payload)
            round_number = data["round"]
            proposed_value = data["value"]
            response_value = self._calculate_response(proposed_value)
            response_msg = message(
                message_enum=MessageEnum.RESPONSE,
                sender_id=self._process_id,
                payload=json.dumps({"round": round_number, "value": response_value})
            )
            Message.send_unicast(response_msg, port=5005)  # Ajuste para porta do líder
            logger.info(f"[Consensus] Nó {self._process_id} enviou RESPONSE para round {round_number}")
        elif msg_type == MessageEnum.RESPONSE.value:
            data = json.loads(payload)
            round_number = data["round"]
            value = data["value"]
            with self._lock:
                if round_number not in self._pending_responses:
                    self._pending_responses[round_number] = {}
                self._pending_responses[round_number][sender_id] = value
        elif msg_type == MessageEnum.CONSENSUS_RESULT.value:
            data = json.loads(payload)
            round_number = data["round"]
            result = data["result"]
            with self._lock:
                self._round_results[round_number] = result
            logger.info(f"[Consensus] Nó {self._process_id} recebeu CONSENSUS_RESULT para round {round_number}: {result}")

    def check_and_finalize_round(self, round_number: int, timeout: int = 3):
        """
        (Líder) Aguarda respostas dos nós não suspeitos e finaliza o consenso.
        """
        start = time.time()
        while time.time() - start < timeout:
            with self._lock:
                expected = set(self._df.suspected_list())
                all_nodes = set(self._pending_responses[round_number].keys())
                if expected.issubset(all_nodes):
                    break
            time.sleep(0.2)
        with self._lock:
            values = list(self._pending_responses[round_number].values())
            result = max(values) if values else None
            self._round_results[round_number] = result
        # Envia resultado para todos
        result_msg = message(
            message_enum=MessageEnum.CONSENSUS_RESULT,
            sender_id=self._process_id,
            payload=json.dumps({"round": round_number, "result": result})
        )
        Message.send_multicast(result_msg)
        logger.info(f"[Consensus] Líder enviou CONSENSUS_RESULT para round {round_number}: {result}")

    def get_result(self, round_number: int):
        """
        Retorna o resultado do consenso para a rodada.
        """
        with self._lock:
            return self._round_results.get(round_number)

    def _calculate_response(self, proposed_value):
        """
        Calcula o valor de resposta do nó para o consenso.
        """
        return proposed_value * proposed_value * self._process_id
