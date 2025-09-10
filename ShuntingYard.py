OPERADORES = {
    '|', 
    '·', 
    '*', 
    '+', 
    '?'
    }
UNARIOS = {
    '*', 
    '+', 
    '?'
    }
PREC = {
    '|': 1, 
    '·': 2, 
    '*': 3, 
    '+': 3, 
    '?': 3
    }
ASOC = {
    '|': 
    'L', 
    '·': 
    'L', 
    '*': 
    'R', 
    '+': 
    'R', 
    '?': 
    'R'
    }


def _normalize(expr: str) -> str:
    # Reemplazamos epsilon por @ en la ejecución
    return expr.replace('ε', '@')

def _is_op(t: str) -> bool:
    return t in OPERADORES

def _is_literal(t: str) -> bool:
    return (len(t) == 2 and t[0] == '\\') or (len(t) == 1 and t not in OPERADORES and t not in {'(', ')'})



def _tokenize(expr: str):
    expr = _normalize(expr)
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch == '\\':
            if i + 1 >= n:
                raise ValueError("Escape incompleto: '\\' al final.")
            nxt = expr[i+1]
            tokens.append('\\' + nxt)
            i += 2
            continue

        if ch in OPERADORES or ch in {'(', ')'}:
            tokens.append(ch)
            i += 1
            continue
        if ch in {'{', '}'}:
            tokens.append(ch)
            i += 1
            continue
        tokens.append(ch)
        i += 1
    return tokens

def _insert_concat(tokens):
    if not tokens:
        return tokens
    res = [tokens[0]]
    for i in range(1, len(tokens)):
        a = res[-1]
        b = tokens[i]
        a_lit_or_close_or_unary = _is_literal(a) or a == ')' or a in UNARIOS
        b_lit_or_open = _is_literal(b) or b == '('
        if a_lit_or_close_or_unary and b_lit_or_open:
            res.append('·')

        res.append(b)
    return res

def infix_to_postfix(expr: str):
    tokens = _tokenize(expr)
    tokens = _insert_concat(tokens)

    output = []
    stack = []
    bal = 0

    for t in tokens:
        if _is_literal(t):
            output.append(t)

        elif t in OPERADORES:
            while stack:
                top = stack[-1]
                if top in OPERADORES:
                    if (ASOC[t] == 'L' and PREC[t] <= PREC[top]) or (ASOC[t] == 'R' and PREC[t] < PREC[top]):
                        output.append(stack.pop())
                        continue
                break
            stack.append(t)

        elif t == '(':
            stack.append(t)
            bal += 1

        elif t == ')':
            bal -= 1
            if bal < 0:
                raise ValueError("Paréntesis desbalanceados: ')' extra.")
            # volcar hasta '('
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if not stack:
                raise ValueError("Paréntesis desbalanceados: falta '('.")
            stack.pop()

        else:
            raise ValueError(f"Token inesperado: {t!r}")

    if bal != 0:
        raise ValueError("Paréntesis desbalanceados.")

    while stack:
        top = stack.pop()
        if top in {'(', ')'}:
            raise ValueError("Paréntesis desbalanceados.")
        output.append(top)

    return output

def expand_operators(expr: str) -> str:
    return _normalize(expr)

def convertir_expresion(expr: str) -> str:
    toks = infix_to_postfix(expr)

    out = []
    for t in toks:
        if len(t) == 2 and t[0] == '\\':
            out.append(t[1])
        else:
            out.append(t)
    return ''.join(out)