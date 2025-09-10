# AFN.py
from typing import Set, Dict, List, Optional
from ShuntingYard import infix_to_postfix, expand_operators

class Estado:
    def __init__(self, id_estado: int):
        self.id = id_estado
        self.transiciones: Dict[str, List["Estado"]] = {}
        self.es_final = False

    def agregar_transicion(self, simbolo: str, estado_destino: "Estado"):
        if simbolo not in self.transiciones:
            self.transiciones[simbolo] = []
        self.transiciones[simbolo].append(estado_destino)

class AFN:
    def __init__(self):
        self.estados: Dict[int, Estado] = {}
        self.estado_inicial: Optional[Estado] = None
        self.estados_finales: Set[int] = set()
        self.contador_estados = 0
        self.alfabeto: Set[str] = set()

    def crear_estado(self) -> Estado:
        estado = Estado(self.contador_estados)
        self.estados[self.contador_estados] = estado
        self.contador_estados += 1
        return estado

    def establecer_inicial(self, estado: Estado):
        self.estado_inicial = estado

    def establecer_final(self, estado: Estado):
        estado.es_final = True
        self.estados_finales.add(estado.id)

    def agregar_simbolo_alfabeto(self, simbolo: str):
        if simbolo != '@': 
            self.alfabeto.add(simbolo)

def construir_afn_simbolo(simbolo: str) -> AFN:
    afn = AFN()
    q0 = afn.crear_estado()
    qf = afn.crear_estado()
    afn.establecer_inicial(q0)
    afn.establecer_final(qf)
    q0.agregar_transicion(simbolo, qf)
    afn.agregar_simbolo_alfabeto(simbolo)
    return afn

def construir_afn_concatenacion(afn1: AFN, afn2: AFN) -> AFN:
    afn = AFN()
    map1: Dict[int, Estado] = {}
    for e_id, _ in afn1.estados.items():
        map1[e_id] = afn.crear_estado()
    map2: Dict[int, Estado] = {}
    for e_id, _ in afn2.estados.items():
        map2[e_id] = afn.crear_estado()

    for e_id, e in afn1.estados.items():
        for s, ds in e.transiciones.items():
            for d in ds:
                map1[e_id].agregar_transicion(s, map1[d.id])
                afn.agregar_simbolo_alfabeto(s)
    for e_id, e in afn2.estados.items():
        for s, ds in e.transiciones.items():
            for d in ds:
                map2[e_id].agregar_transicion(s, map2[d.id])
                afn.agregar_simbolo_alfabeto(s)

    afn.establecer_inicial(map1[afn1.estado_inicial.id])

    for f_id in afn1.estados_finales:
        map1[f_id].agregar_transicion('@', map2[afn2.estado_inicial.id])

    for f_id in afn2.estados_finales:
        afn.establecer_final(map2[f_id])

    afn.alfabeto = afn1.alfabeto.union(afn2.alfabeto)
    return afn

def obtener_cerradura_epsilon(estado: Estado, visitados: Optional[Set[int]] = None) -> Set[Estado]:
    if visitados is None:
        visitados = set()
    if estado.id in visitados:
        return set()
    visitados.add(estado.id)
    cerr = {estado}
    if '@' in estado.transiciones:
        for d in estado.transiciones['@']:
            cerr.update(obtener_cerradura_epsilon(d, visitados))
    return cerr

def construir_afn_desde_expresion(expresion: str) -> AFN:
    expandida = expand_operators(expresion)

    postfijo_tokens = infix_to_postfix(expandida)


    OPERADORES = {'·', '|', '*', '+', '?'}

    pila: List[AFN] = []

    for tok in postfijo_tokens:

        if len(tok) == 2 and tok[0] == '\\':
            pila.append(construir_afn_simbolo(tok[1]))
            continue

        # Operadores
        if tok in OPERADORES:
            if tok in {'·', '|'}:
                if len(pila) < 2:
                    raise ValueError(f"Postfix inválido: faltan operandos para '{tok}'.")
                b = pila.pop()
                a = pila.pop()
                pila.append(construir_afn_concatenacion(a, b) if tok == '·' else construir_afn_union(a, b))
            elif tok == '*':
                if len(pila) < 1:
                    raise ValueError("Postfix inválido: falta operando para '*'.")
                a = pila.pop()
                pila.append(construir_afn_kleene(a))
            elif tok == '+':
                if len(pila) < 1:
                    raise ValueError("Postfix inválido: falta operando para '+'.")
                a = pila.pop()
                pila.append(construir_afn_positivo(a))
            elif tok == '?':
                if len(pila) < 1:
                    raise ValueError("Postfix inválido: falta operando para '?'.")
                a = pila.pop()
                pila.append(construir_afn_opcional(a))
            continue

        if len(tok) == 1:
            pila.append(construir_afn_simbolo(tok))
            continue

        raise ValueError(f"Token inesperado en postfix: {tok!r}")

    if len(pila) != 1:
        raise ValueError("Expresión mal formada (postfix): pila no quedó con 1 elemento.")
    return pila[0]


def simular_afn(afn: AFN, cadena: str) -> bool:
    if afn.estado_inicial is None:
        return False
    actuales = obtener_cerradura_epsilon(afn.estado_inicial)
    for s in cadena:
        nuevos: Set[Estado] = set()
        for e in actuales:
            if s in e.transiciones:
                for d in e.transiciones[s]:
                    nuevos.update(obtener_cerradura_epsilon(d))
        actuales = nuevos
        if not actuales:
            return False
    return any(afn.estados[e.id].es_final for e in actuales)

def construir_afn_union(afn1: AFN, afn2: AFN) -> AFN:
    afn = AFN()
    ni = afn.crear_estado()
    nf = afn.crear_estado()
    afn.establecer_inicial(ni)
    afn.establecer_final(nf)

    map1: Dict[int, Estado] = {e_id: afn.crear_estado() for e_id in afn1.estados}
    for e_id, e in afn1.estados.items():
        for s, ds in e.transiciones.items():
            for d in ds:
                map1[e_id].agregar_transicion(s, map1[d.id])
                afn.agregar_simbolo_alfabeto(s)

    map2: Dict[int, Estado] = {e_id: afn.crear_estado() for e_id in afn2.estados}
    for e_id, e in afn2.estados.items():
        for s, ds in e.transiciones.items():
            for d in ds:
                map2[e_id].agregar_transicion(s, map2[d.id])
                afn.agregar_simbolo_alfabeto(s)


    ni.agregar_transicion('@', map1[afn1.estado_inicial.id])
    ni.agregar_transicion('@', map2[afn2.estado_inicial.id])
    for f_id in afn1.estados_finales:
        map1[f_id].agregar_transicion('@', nf)
    for f_id in afn2.estados_finales:
        map2[f_id].agregar_transicion('@', nf)

    afn.alfabeto = afn1.alfabeto.union(afn2.alfabeto)
    return afn

def construir_afn_kleene(afn0: AFN) -> AFN:
    afn = AFN()
    ni = afn.crear_estado()
    nf = afn.crear_estado()
    afn.establecer_inicial(ni)
    afn.establecer_final(nf)
    mapa: Dict[int, Estado] = {e_id: afn.crear_estado() for e_id in afn0.estados}

    for e_id, e in afn0.estados.items():
        for s, ds in e.transiciones.items():
            for d in ds:
                mapa[e_id].agregar_transicion(s, mapa[d.id])
                afn.agregar_simbolo_alfabeto(s)

    ni.agregar_transicion('@', mapa[afn0.estado_inicial.id])
    ni.agregar_transicion('@', nf)
    for f_id in afn0.estados_finales:
        mapa[f_id].agregar_transicion('@', nf)
        mapa[f_id].agregar_transicion('@', mapa[afn0.estado_inicial.id])

    afn.alfabeto = afn0.alfabeto.copy()
    return afn


def construir_afn_positivo(afn0: AFN) -> AFN:
    return construir_afn_concatenacion(afn0, construir_afn_kleene(afn0))


def construir_afn_opcional(afn0: AFN) -> AFN:
    afn_eps = construir_afn_simbolo('@')
    return construir_afn_union(afn0, afn_eps)
