# Minimización de AFD usando el algoritmo de partición de estados
from typing import Set, Dict, List, Tuple, FrozenSet
from AFD import AFD

def minimizar_afd(afd: AFD) -> AFD:
    if not afd.estados or afd.estado_inicial is None:
        return afd
    
    #Eliminar estados inaccesibles
    estados_accesibles = obtener_estados_accesibles(afd)
    
    #Partición inicial - separar estados finales de no finales
    finales = set(afd.estados_finales) & estados_accesibles
    no_finales = estados_accesibles - finales
    
    if not finales and not no_finales:
        return afd
    
    #Inicializar particiones
    particiones = []
    if no_finales:
        particiones.append(no_finales)
    if finales:
        particiones.append(finales)
    
    #Refinar particiones hasta que no cambien
    cambio = True
    while cambio:
        cambio = False
        nuevas_particiones = []
        
        for particion in particiones:
            #Intentar dividir esta partición
            subparticiones = dividir_particion(particion, particiones, afd)
            if len(subparticiones) > 1:
                cambio = True
            nuevas_particiones.extend(subparticiones)
        
        particiones = nuevas_particiones
    
    #Construir el AFD minimizado
    return construir_afd_minimizado(afd, particiones)

def obtener_estados_accesibles(afd: AFD) -> Set[int]:
    if afd.estado_inicial is None:
        return set()
    
    accesibles = set()
    pendientes = [afd.estado_inicial]
    
    while pendientes:
        estado = pendientes.pop()
        if estado in accesibles:
            continue
        
        accesibles.add(estado)
        
        #Agregar estados alcanzables
        if estado in afd.transiciones:
            for destino in afd.transiciones[estado].values():
                if destino not in accesibles:
                    pendientes.append(destino)
    
    return accesibles

def dividir_particion(particion: Set[int], todas_particiones: List[Set[int]], afd: AFD) -> List[Set[int]]:
    if len(particion) <= 1:
        return [particion]
    
    #Mapear cada estado 
    firmas: Dict[Tuple, Set[int]] = {}
    
    for estado in particion:
        firma = []
        #Símbolo del alfabeto
        for simbolo in sorted(afd.alfabeto):
            destino = afd.transiciones.get(estado, {}).get(simbolo)
            if destino is not None:
                #Encontrar a qué partición pertenece
                particion_destino = -1
                for i, part in enumerate(todas_particiones):
                    if destino in part:
                        particion_destino = i
                        break
                firma.append(particion_destino)
            else:
                firma.append(-1)  
        
        firma_tuple = tuple(firma)
        if firma_tuple not in firmas:
            firmas[firma_tuple] = set()
        firmas[firma_tuple].add(estado)
    
    return list(firmas.values())

def construir_afd_minimizado(afd_original: AFD, particiones: List[Set[int]]) -> AFD:
    afd_min = AFD()
    
    #Mapear cada estado original a su representante 
    estado_a_particion: Dict[int, int] = {}
    for i, particion in enumerate(particiones):
        for estado in particion:
            estado_a_particion[estado] = i
    
    #Crear estados en el AFD minimizado
    for i, particion in enumerate(particiones):
        ids_originales = frozenset(particion)
        
        es_final = any(estado in afd_original.estados_finales for estado in particion)
        afd_min.crear_estado(ids_originales, es_final)
    
    #Establecer estado inicial
    if afd_original.estado_inicial is not None:
        afd_min.estado_inicial = estado_a_particion[afd_original.estado_inicial]
    
    #Crear transiciones
    for i, particion in enumerate(particiones):
        representante = next(iter(particion))
        
        if representante in afd_original.transiciones:
            for simbolo, destino in afd_original.transiciones[representante].items():
                destino_particion = estado_a_particion[destino]
                afd_min.agregar_transicion(i, simbolo, destino_particion)
    
    afd_min.alfabeto = afd_original.alfabeto.copy()
    
    return afd_min

def obtener_info_minimizacion(afd_original: AFD, afd_minimizado: AFD) -> str:
    estados_originales = len(afd_original.estados)
    estados_minimizados = len(afd_minimizado.estados)
    estados_eliminados = estados_originales - estados_minimizados
    
    info = f"Minimización completada:\n"
    info += f"  Estados originales: {estados_originales}\n"
    info += f"  Estados minimizados: {estados_minimizados}\n"
    info += f"  Estados eliminados: {estados_eliminados}\n"
    
    return info