# Módulo principal
import sys
from ShuntingYard import convertir_expresion
from AFN import construir_afn_desde_expresion, simular_afn
from AFD import convertir_afn_a_afd, simular_afd

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

def procesar_archivo(nombre_archivo: str):
    try:
        print(f"Leyendo archivo: {nombre_archivo}")
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            lineas = f.readlines()

        for num_linea, linea in enumerate(lineas, 1):
            expr, cadena = parse_linea(linea)
            if expr is None:
                continue

            print(f"\nLINEA {num_linea}")
            print(f"Expresión: {expr}")
            print(f"Cadena: {repr(cadena) if cadena != '' else '(vacía)'}")

            postfix = convertir_expresion(expr)
            print(f"Postfix: {postfix}")

            afn = construir_afn_desde_expresion(expr)
            print(f"AFN: estados={len(afn.estados)}, inicial={afn.estado_inicial.id}, finales={sorted(list(afn.estados_finales))}, alfabeto={sorted(list(afn.alfabeto))}")

            afd = convertir_afn_a_afd(afn)
            print(f"AFD: estados={len(afd.estados)}, inicial={afd.estado_inicial}, finales={sorted(list(afd.estados_finales))}, alfabeto={sorted(list(afd.alfabeto))}")

            print(f"Simulación de AFN  {'La cadena es aceptada' if simular_afn(afn, cadena) else 'La cadena no es aceptada'}")
            print(f"Simulación de AFD  {'La cadena es aceptada' if simular_afd(afd, cadena) else 'La cadena no es aceptada'}")

    except FileNotFoundError:
        print(f"Error al encontrar el archivo '{nombre_archivo}'")
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")

if __name__ == "__main__":
    archivo = "expresiones.txt"
    procesar_archivo(archivo)
