# main.py
import sys
from ShuntingYard import infix_to_postfix as convertir_expresion
from AFN import construir_afn_desde_expresion, simular_afn
from AFD import convertir_afn_a_afd, simular_afd
from minimizacion import minimizar_afd, obtener_info_minimizacion
from visualizacion import visualizar_automatas, crear_directorio_graficos

SEPARADORES = ['=>', ';', '\t']

def parse_linea(linea: str):
    raw = linea.strip()
    if not raw or raw.startswith('#'):
        return None, None

    expr = None
    cad = ""

    for sep in SEPARADORES:
        if sep in raw:
            partes = raw.split(sep, 1)
            expr = partes[0].strip()
            cad = partes[1].strip()
            break

    if expr is None:
        expr = raw
        cad = ""

    if cad in ('@', 'ε'):
        cad = ""

    return expr, cad

def mostrar_estadisticas_automata(automata, tipo: str):
    """Muestra estadísticas básicas del autómata"""
    if tipo == "AFN":
        print(f"{tipo}: estados={len(automata.estados)}, inicial={automata.estado_inicial.id if automata.estado_inicial else 'None'}, finales={sorted(list(automata.estados_finales))}, alfabeto={sorted(list(automata.alfabeto))}")
    else:  # AFD
        print(f"{tipo}: estados={len(automata.estados)}, inicial={automata.estado_inicial}, finales={sorted(list(automata.estados_finales))}, alfabeto={sorted(list(automata.alfabeto))}")

def simular_todos_automatas(afn, afd, afd_min, cadena: str):
    """Simula la cadena en todos los autómatas y muestra resultados"""
    resultado_afn = simular_afn(afn, cadena)
    resultado_afd = simular_afd(afd, cadena)
    resultado_afd_min = simular_afd(afd_min, cadena)
    
    print(f"Simulación AFN:           {'ACEPTA' if resultado_afn else 'RECHAZA'}")
    print(f"Simulación AFD:           {'ACEPTA' if resultado_afd else 'RECHAZA'}")
    print(f"Simulación AFD minimizado:{'ACEPTA' if resultado_afd_min else 'RECHAZA'}")
    
    return resultado_afn, resultado_afd, resultado_afd_min


def procesar_archivo(nombre_archivo: str, generar_graficos: bool = True):    
    if generar_graficos:
        crear_directorio_graficos()
    
    try:
        print(f"Leyendo archivo: {nombre_archivo}")
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            lineas = f.readlines()

        estadisticas_globales = {
            'total_procesadas': 0,
            'total_aceptadas': 0,
            'total_rechazadas': 0,
            'errores': 0
        }

        for num_linea, linea in enumerate(lineas, 1):
            try:
                expr, cadena = parse_linea(linea)
                if expr is None:
                    continue

                print(f"\n{'='*60}")
                print(f"LÍNEA {num_linea}")
                print(f"{'='*60}")
                print(f"Expresión regular: {expr}")
                print(f"Cadena a evaluar: {repr(cadena) if cadena != '' else '(cadena vacía)'}")

                #Conversión a postfix
                print(f"\n1. CONVERSIÓN A POSTFIX:")
                postfix = convertir_expresion(expr)
                print(f"   Postfix: {postfix}")

                #Construcción de AFN
                print(f"\n2. CONSTRUCCIÓN DE AFN (Thompson):")
                afn = construir_afn_desde_expresion(expr)
                mostrar_estadisticas_automata(afn, "AFN")

                #Conversión a AFD
                print(f"\n3. CONSTRUCCIÓN DE AFD (Subconjuntos):")
                afd = convertir_afn_a_afd(afn)
                mostrar_estadisticas_automata(afd, "AFD")

                # Minimización de AFD
                print(f"\n4. MINIMIZACIÓN DE AFD:")
                afd_minimizado = minimizar_afd(afd)
                mostrar_estadisticas_automata(afd_minimizado, "AFD minimizado")
                
                # Información adicional sobre minimización
                info_min = obtener_info_minimizacion(afd, afd_minimizado)
                print(info_min)

                #Simulación
                print(f"\n5. SIMULACIÓN:")
                resultado_afn, resultado_afd, resultado_afd_min = simular_todos_automatas(
                    afn, afd, afd_minimizado, cadena
                )

                #Generación de gráficos
                if generar_graficos:
                    print(f"\n6. GENERACIÓN DE GRÁFICOS:")
                    try:
                        visualizar_automatas(afn, afd, afd_minimizado, expr, num_linea)
                        print("   Gráficos generados exitosamente")
                    except Exception as e:
                        print(f"   Error al generar gráficos: {e}")

                #Actualizar resumen
                estadisticas_globales['total_procesadas'] += 1
                if resultado_afn:
                    estadisticas_globales['total_aceptadas'] += 1
                else:
                    estadisticas_globales['total_rechazadas'] += 1

            except Exception as e:
                print(f"\n❌ ERROR en línea {num_linea}: {e}")
                estadisticas_globales['errores'] += 1
                continue

        # Mostrar estadísticas finales
        print(f"\n{'='*60}")
        print("ESTADÍSTICAS FINALES")
        print(f"{'='*60}")
        print(f"Total procesadas: {estadisticas_globales['total_procesadas']}")
        print(f"Cadenas aceptadas: {estadisticas_globales['total_aceptadas']}")
        print(f"Cadenas rechazadas: {estadisticas_globales['total_rechazadas']}")
        print(f"Errores encontrados: {estadisticas_globales['errores']}")

    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo '{nombre_archivo}'")
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")

if __name__ == "__main__":
    # Procesar argumentos del archivo
    archivo = "expresiones.txt"
    generar_graficos = True
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if not arg.startswith("--") and arg.endswith(".txt"):
                archivo = arg
                break
        
        if "--no-graficos" in sys.argv:
            generar_graficos = False
    
    print("=== ANALIZADOR LÉXICO - TEORÍA DE LA COMPUTACIÓN ===")
    print(f"Procesando archivo: {archivo}")
    if generar_graficos:
        print("Generación de gráficos: HABILITADA")
    else:
        print("Generación de gráficos: DESHABILITADA")
    
    procesar_archivo(archivo, generar_graficos)