# AFD.py
from typing import Set, Dict, List, Optional
from AFN import AFN, Estado, obtener_cerradura_epsilon

class AFD:
    def __init__(self):
        self.estados: Dict[int, frozenset[int]] = {}
        self.transiciones: Dict[int, Dict[str, int]] = {}
        self.estado_inicial: Optional[int] = None
        self.estados_finales: Set[int] = set()
        self._contador: int = 0
        self.alfabeto: Set[str] = set()

    def crear_estado(self, conjunto_ids: frozenset[int], es_final: bool) -> int:
        qid = self._contador
        self._contador += 1
        self.estados[qid] = conjunto_ids
        if es_final:
            self.estados_finales.add(qid)
        return qid

    def agregar_transicion(self, q_origen: int, simbolo: str, q_destino: int):
        if simbolo == '@':
            return
        if q_origen not in self.transiciones:
            self.transiciones[q_origen] = {}
        self.transiciones[q_origen][simbolo] = q_destino
        self.alfabeto.add(simbolo)

def cerradura_epsilon_conjunto(estados: Set[Estado]) -> Set[Estado]:
    res: Set[Estado] = set()
    visitados: Set[int] = set()
    for e in estados:
        res.update(obtener_cerradura_epsilon(e, visitados))
    return res

def mover(estados: Set[Estado], simbolo: str) -> Set[Estado]:
    alcanzados: Set[Estado] = set()
    for e in estados:
        if simbolo in e.transiciones:
            for d in e.transiciones[simbolo]:
                alcanzados.add(d)
    return alcanzados

def convertir_afn_a_afd(afn: AFN) -> AFD:
    afd = AFD()

    S0 = cerradura_epsilon_conjunto({afn.estado_inicial})
    S0_ids = frozenset(s.id for s in S0)
    es_final_S0 = any(afn.estados[sid].es_final for sid in S0_ids)
    q0 = afd.crear_estado(S0_ids, es_final_S0)
    afd.estado_inicial = q0

    indice: Dict[frozenset[int], int] = {S0_ids: q0}
    pendientes: List[frozenset[int]] = [S0_ids]

    while pendientes:
        T_ids = pendientes.pop()
        qT = indice[T_ids]
        T_obj = {afn.estados[sid] for sid in T_ids}

        for a in sorted(afn.alfabeto):
            U = cerradura_epsilon_conjunto(mover(T_obj, a))
            if not U:
                continue
            U_ids = frozenset(s.id for s in U)
            if U_ids not in indice:
                es_final_U = any(afn.estados[sid].es_final for sid in U_ids)
                qU = afd.crear_estado(U_ids, es_final_U)
                indice[U_ids] = qU
                pendientes.append(U_ids)
            else:
                qU = indice[U_ids]
            afd.agregar_transicion(qT, a, qU)

    return afd

def simular_afd(afd: AFD, cadena: str) -> bool:
    if afd.estado_inicial is None:
        return False
    q = afd.estado_inicial
    for c in cadena:
        q = afd.transiciones.get(q, {}).get(c, None)
        if q is None:
            return False
    return q in afd.estados_finales
