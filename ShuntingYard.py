# Reemplazamos epsilon con el símbolo @ por la facilidad de encontrar el símbolo en el teclado y la baja probabilidad de que sea parte del lenguaje

def get_precedence(c: str) -> int:
    precedence_map = {
        '(': 1,
        '|': 2,
        '.': 3,
        '?': 4,
        '*': 4,
        '+': 4,
        '^': 5
    }
    return precedence_map.get(c, 6)

def format_regex(regex: str) -> str:
    all_operators = {'|', '?', '+', '*', '^', ')'}
    binary_operators = {'|', '^'}
    result = ""
    i = 0
    while i < len(regex) - 1:
        c1 = regex[i]
        c2 = regex[i + 1]
        result += c1

        if c1 == '\\':
            i += 1
            result += c2
            i += 1
            continue

        if (c1 != '(' and c2 != ')' and
            c2 not in all_operators and
            c1 not in binary_operators):
            result += '.'
        i += 1

    if regex:
        result += regex[-1]
    return result

def expand_operators(regex: str) -> str:
    result = ""
    i = 0
    while i < len(regex):
        c = regex[i]

        if c == '\\':
            result += c
            if i + 1 < len(regex):
                result += regex[i + 1]
                i += 2
                continue

        elif c == '+':
            if not result:
                raise ValueError("No se puede usar + al inicio")
            prev = result[-1]
            result = result[:-1] + prev + '*' + prev

        elif c == '?':
            if not result:
                raise ValueError("No se puede usar ? al inicio")
            prev = result[-1]
            result = result[:-1] + '(' + prev + '|' + '@' + ')'

        else:
            result += c
        i += 1

    return result

def infix_to_postfix(regex: str) -> str:
    postfix = ""
    stack = []
    formatted = format_regex(regex)

    for c in formatted:
        if c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                postfix += stack.pop()
            if not stack:
                raise ValueError("Paréntesis desbalanceados")
            stack.pop()
        elif c in {'|', '.', '?', '*', '+', '^'}:
            while stack and get_precedence(stack[-1]) >= get_precedence(c):
                postfix += stack.pop()
            stack.append(c)
        else:
            postfix += c

    while stack:
        top = stack.pop()
        if top in {'(', ')'}:
            raise ValueError("Paréntesis desbalanceados")
        postfix += top

    return postfix

def convertir_expresion(expresion: str) -> str:
    expandida = expand_operators(expresion)
    postfix = infix_to_postfix(expandida)
    return postfix
