# Visualización de autómatas generando imágenes 
import os
import math
from typing import Dict, Set, List, Tuple, Optional
from AFN import AFN
from AFD import AFD

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import FancyBboxPatch, Circle
    import numpy as np
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False
    print("Advertencia: matplotlib no está instalado.")
    print("Instala con: pip install matplotlib")

def calcular_posiciones_estados(num_estados: int, radio_circulo: float = 3.0) -> Dict[int, Tuple[float, float]]:
    """Calcula posiciones en círculo para los estados"""
    if num_estados == 1:
        return {0: (0, 0)}
    
    posiciones = {}
    for i in range(num_estados):
        angulo = 2 * math.pi * i / num_estados
        x = radio_circulo * math.cos(angulo)
        y = radio_circulo * math.sin(angulo)
        posiciones[i] = (x, y)
    
    return posiciones

def calcular_posiciones_mejoradas(estados: List[int]) -> Dict[int, Tuple[float, float]]:
    """Calcula posiciones optimizadas para minimizar cruces de aristas"""
    n = len(estados)
    if n == 0:
        return {}
    if n == 1:
        return {estados[0]: (0, 0)}
    
    posiciones = {}
    
    if n <= 6:
        # Disposición circular para pocos estados
        for i, estado in enumerate(estados):
            angulo = 2 * math.pi * i / n - math.pi / 2  # Comenzar desde arriba
            radio = 2.5 if n <= 3 else 3.0
            x = radio * math.cos(angulo)
            y = radio * math.sin(angulo)
            posiciones[estado] = (x, y)
    else:
        # Para muchos estados, usar disposición en capas
        capas = int(math.ceil(math.sqrt(n)))
        estados_por_capa = math.ceil(n / capas)
        
        for i, estado in enumerate(estados):
            capa = i // estados_por_capa
            pos_en_capa = i % estados_por_capa
            total_en_capa = min(estados_por_capa, n - capa * estados_por_capa)
            
            radio = 1.5 + capa * 1.5
            angulo = 2 * math.pi * pos_en_capa / total_en_capa - math.pi / 2
            
            x = radio * math.cos(angulo)
            y = radio * math.sin(angulo)
            posiciones[estado] = (x, y)
    
    return posiciones

def dibujar_flecha_curva(ax, start: Tuple[float, float], end: Tuple[float, float], 
                        label: str, curvatura: float = 0.3, color: str = 'black'):
    """Dibuja una flecha curva entre dos puntos"""
    x1, y1 = start
    x2, y2 = end
    
    # Calcular punto medio y punto de control para la curva
    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
    
    # Vector perpendicular para la curvatura
    dx, dy = x2 - x1, y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    if length == 0:
        return  # Evitar división por cero
    
    # Normalizar y rotar 90 grados
    perp_x, perp_y = -dy / length, dx / length
    
    # Punto de control para la curva Bézier
    ctrl_x = mid_x + curvatura * perp_x
    ctrl_y = mid_y + curvatura * perp_y
    
    # Crear la curva Bézier
    t = np.linspace(0, 1, 100)
    curve_x = (1-t)**2 * x1 + 2*(1-t)*t * ctrl_x + t**2 * x2
    curve_y = (1-t)**2 * y1 + 2*(1-t)*t * ctrl_y + t**2 * y2
    
    # Dibujar la curva
    ax.plot(curve_x, curve_y, color=color, linewidth=1.5)
    
    # Añadir punta de flecha
    # Calcular dirección en el extremo
    end_t = 0.95
    arrow_x = (1-end_t)**2 * x1 + 2*(1-end_t)*end_t * ctrl_x + end_t**2 * x2
    arrow_y = (1-end_t)**2 * y1 + 2*(1-end_t)*end_t * ctrl_y + end_t**2 * y2
    
    # Dirección de la flecha
    dir_x = x2 - arrow_x
    dir_y = y2 - arrow_y
    dir_length = math.sqrt(dir_x*dir_x + dir_y*dir_y)
    if dir_length > 0:
        dir_x /= dir_length
        dir_y /= dir_length
        
        # Dibujar punta de flecha
        arrow_size = 0.15
        ax.annotate('', xy=(x2, y2), xytext=(x2 - arrow_size*dir_x, y2 - arrow_size*dir_y),
                   arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
    
    # Añadir etiqueta en el punto medio de la curva
    label_x = (1-0.5)**2 * x1 + 2*(1-0.5)*0.5 * ctrl_x + 0.5**2 * x2
    label_y = (1-0.5)**2 * y1 + 2*(1-0.5)*0.5 * ctrl_y + 0.5**2 * y2
    
    # Fondo blanco para la etiqueta
    ax.text(label_x, label_y, label, ha='center', va='center', 
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='none', alpha=0.8),
           fontsize=10, weight='bold')

def dibujar_auto_loop(ax, pos: Tuple[float, float], label: str, color: str = 'black'):
    """Dibuja un auto-loop (transición de un estado a sí mismo)"""
    x, y = pos
    
    # Crear un círculo pequeño arriba del estado
    loop_radius = 0.4
    loop_center_x = x
    loop_center_y = y + 0.8
    
    # Dibujar el círculo del loop
    circle = Circle((loop_center_x, loop_center_y), loop_radius, 
                   fill=False, color=color, linewidth=1.5)
    ax.add_patch(circle)
    
    # Añadir flecha
    arrow_x = loop_center_x + loop_radius * 0.7
    arrow_y = loop_center_y
    ax.annotate('', xy=(arrow_x, arrow_y), 
               xytext=(arrow_x - 0.1, arrow_y),
               arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
    
    # Etiqueta
    ax.text(loop_center_x, loop_center_y + loop_radius + 0.3, label, 
           ha='center', va='center', 
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='none', alpha=0.8),
           fontsize=10, weight='bold')

def generar_imagen_afn(afn: AFN, nombre_archivo: str, titulo: str = "AFN"):
    """Genera imagen PNG del AFN"""
    if not MATPLOTLIB_DISPONIBLE:
        print("No se puede generar imagen: matplotlib no disponible")
        return False
    
    try:
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.set_aspect('equal')
        ax.set_title(titulo, fontsize=16, weight='bold', pad=20)
        
        # Obtener lista de estados
        estados_ids = list(afn.estados.keys())
        posiciones = calcular_posiciones_mejoradas(estados_ids)
        
        # Dibujar estados
        for estado_id in estados_ids:
            x, y = posiciones[estado_id]
            estado = afn.estados[estado_id]
            
            # Determinar el estilo del estado
            if estado.es_final:
                # Estado final - doble círculo
                outer_circle = Circle((x, y), 0.4, fill=True, facecolor='lightblue', 
                                    edgecolor='black', linewidth=2)
                inner_circle = Circle((x, y), 0.3, fill=False, edgecolor='black', linewidth=2)
                ax.add_patch(outer_circle)
                ax.add_patch(inner_circle)
            else:
                # Estado normal
                circle = Circle((x, y), 0.35, fill=True, facecolor='lightgray', 
                              edgecolor='black', linewidth=2)
                ax.add_patch(circle)
            
            # Etiqueta del estado
            ax.text(x, y, str(estado_id), ha='center', va='center', 
                   fontsize=12, weight='bold')
        
        # Dibujar flecha del estado inicial
        if afn.estado_inicial:
            inicial_pos = posiciones[afn.estado_inicial.id]
            start_x = inicial_pos[0] - 1.0
            start_y = inicial_pos[1]
            ax.annotate('', xy=inicial_pos, xytext=(start_x, start_y),
                       arrowprops=dict(arrowstyle='->', lw=2, color='red'))
            ax.text(start_x - 0.3, start_y, 'Inicio', ha='center', va='center', 
                   fontsize=10, weight='bold', color='red')
        
        # Agrupar transiciones
        transiciones_agrupadas = {}
        
        for estado_id, estado in afn.estados.items():
            for simbolo, destinos in estado.transiciones.items():
                for destino in destinos:
                    clave = (estado_id, destino.id)
                    if clave not in transiciones_agrupadas:
                        transiciones_agrupadas[clave] = set()
                    transiciones_agrupadas[clave].add(simbolo)
        
        # Dibujar transiciones
        for (origen, destino), simbolos in transiciones_agrupadas.items():
            simbolos_str = ','.join(sorted(simbolos)).replace('@', 'ε')
            
            if origen == destino:
                # Auto-loop
                dibujar_auto_loop(ax, posiciones[origen], simbolos_str)
            else:
                # Transición normal
                start_pos = posiciones[origen]
                end_pos = posiciones[destino]
                
                # Ajustar posiciones para no sobreponer los círculos
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist > 0:
                    # Normalizar
                    dx /= dist
                    dy /= dist
                    
                    # Ajustar inicio y fin
                    radio = 0.35
                    start_adj = (start_pos[0] + radio*dx, start_pos[1] + radio*dy)
                    end_adj = (end_pos[0] - radio*dx, end_pos[1] - radio*dy)
                    
                    dibujar_flecha_curva(ax, start_adj, end_adj, simbolos_str)
        
        # Configurar ejes
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('')
        ax.set_ylabel('')
        
        # Guardar imagen
        plt.tight_layout()
        plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return True
        
    except Exception as e:
        print(f"Error al generar imagen AFN: {e}")
        return False

def generar_imagen_afd(afd: AFD, nombre_archivo: str, titulo: str = "AFD"):
    """Genera imagen PNG del AFD"""
    if not MATPLOTLIB_DISPONIBLE:
        print("No se puede generar imagen: matplotlib no disponible")
        return False
    
    try:
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.set_aspect('equal')
        ax.set_title(titulo, fontsize=16, weight='bold', pad=20)
        
        # Obtener lista de estados
        estados_ids = list(afd.estados.keys())
        posiciones = calcular_posiciones_mejoradas(estados_ids)
        
        # Dibujar estados
        for estado_id in estados_ids:
            x, y = posiciones[estado_id]
            
            # Determinar el estilo del estado
            if estado_id in afd.estados_finales:
                # Estado final - doble círculo
                outer_circle = Circle((x, y), 0.4, fill=True, facecolor='lightgreen', 
                                    edgecolor='black', linewidth=2)
                inner_circle = Circle((x, y), 0.3, fill=False, edgecolor='black', linewidth=2)
                ax.add_patch(outer_circle)
                ax.add_patch(inner_circle)
            else:
                # Estado normal
                circle = Circle((x, y), 0.35, fill=True, facecolor='lightblue', 
                              edgecolor='black', linewidth=2)
                ax.add_patch(circle)
            
            # Etiqueta del estado (mostrar IDs originales si es minimizado)
            if hasattr(afd, 'estados') and estado_id in afd.estados:
                ids_originales = afd.estados[estado_id]
                if isinstance(ids_originales, frozenset) and len(ids_originales) > 1:
                    label = '{' + ','.join(map(str, sorted(ids_originales))) + '}'
                else:
                    label = str(estado_id)
            else:
                label = str(estado_id)
            
            ax.text(x, y, label, ha='center', va='center', 
                   fontsize=10 if len(label) > 3 else 12, weight='bold')
        
        # Dibujar flecha del estado inicial
        if afd.estado_inicial is not None:
            inicial_pos = posiciones[afd.estado_inicial]
            start_x = inicial_pos[0] - 1.0
            start_y = inicial_pos[1]
            ax.annotate('', xy=inicial_pos, xytext=(start_x, start_y),
                       arrowprops=dict(arrowstyle='->', lw=2, color='red'))
            ax.text(start_x - 0.3, start_y, 'Inicio', ha='center', va='center', 
                   fontsize=10, weight='bold', color='red')
        
        # Agrupar transiciones
        transiciones_agrupadas = {}
        
        for origen, transiciones in afd.transiciones.items():
            for simbolo, destino in transiciones.items():
                clave = (origen, destino)
                if clave not in transiciones_agrupadas:
                    transiciones_agrupadas[clave] = set()
                transiciones_agrupadas[clave].add(simbolo)
        
        # Dibujar transiciones
        for (origen, destino), simbolos in transiciones_agrupadas.items():
            simbolos_str = ','.join(sorted(simbolos))
            
            if origen == destino:
                # Auto-loop
                dibujar_auto_loop(ax, posiciones[origen], simbolos_str)
            else:
                # Transición normal
                start_pos = posiciones[origen]
                end_pos = posiciones[destino]
                
                # Ajustar posiciones para no sobreponer los círculos
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist > 0:
                    # Normalizar
                    dx /= dist
                    dy /= dist
                    
                    # Ajustar inicio y fin
                    radio = 0.35
                    start_adj = (start_pos[0] + radio*dx, start_pos[1] + radio*dy)
                    end_adj = (end_pos[0] - radio*dx, end_pos[1] - radio*dy)
                    
                    dibujar_flecha_curva(ax, start_adj, end_adj, simbolos_str)
        
        # Configurar ejes
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('')
        ax.set_ylabel('')
        
        # Guardar imagen
        plt.tight_layout()
        plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return True
        
    except Exception as e:
        print(f"Error al generar imagen AFD: {e}")
        return False

def visualizar_automatas(afn: AFN, afd: AFD, afd_min: AFD, expresion: str, numero_linea: int):
    """Genera visualizaciones para todos los autómatas"""
    if not MATPLOTLIB_DISPONIBLE:
        print("   matplotlib no disponible - saltando generación de imágenes")
        return
    
    # Limpiar expresión para usar en nombres de archivo
    expr_limpia = limpiar_nombre_archivo(expresion)
    
    resultados = []
    
    # AFN
    nombre_afn = f"graficos/AFN_L{numero_linea:03d}_{expr_limpia}.png"
    if generar_imagen_afn(afn, nombre_afn, f"AFN - Línea {numero_linea}: {expresion}"):
        resultados.append(f"AFN: {nombre_afn}")
    
    # AFD
    nombre_afd = f"graficos/AFD_L{numero_linea:03d}_{expr_limpia}.png"
    if generar_imagen_afd(afd, nombre_afd, f"AFD - Línea {numero_linea}: {expresion}"):
        resultados.append(f"AFD: {nombre_afd}")
    
    # AFD Minimizado
    nombre_afd_min = f"graficos/AFD_MIN_L{numero_linea:03d}_{expr_limpia}.png"
    if generar_imagen_afd(afd_min, nombre_afd_min, f"AFD Minimizado - Línea {numero_linea}: {expresion}"):
        resultados.append(f"AFD Minimizado: {nombre_afd_min}")
    
    # Mostrar resultados
    for resultado in resultados:
        print(f"   ✓ {resultado}")

def limpiar_nombre_archivo(nombre: str) -> str:
    """Limpia un string para usarlo como nombre de archivo"""
    caracteres_invalidos = '<>:"/\\|?*()[]{}^$+.?*'
    for char in caracteres_invalidos:
        nombre = nombre.replace(char, '_')
    return nombre[:30]  # Limitar longitud

def crear_directorio_graficos():
    """Crea el directorio para guardar gráficos si no existe"""
    if not os.path.exists('graficos'):
        os.makedirs('graficos')
        print("Directorio 'graficos' creado.")
