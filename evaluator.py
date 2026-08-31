import os
import sys

# ----------------------------------------------------------------------
# Tokenizer
# ----------------------------------------------------------------------

NUM, OP, LPAREN, RPAREN, END = "NUM", "OP", "LPAREN", "RPAREN", "END"

_OPERATORS = set("+-*/%^")


def tokenize(expr: str):
    tokens = []
    i = 0
    n = len(expr)

    while i < n:
        ch = expr[i]

        if ch.isspace():
            i += 1
            continue

        if ch.isdigit():
            start = i
            while i < n and expr[i].isdigit():
                i += 1
            if i < n and expr[i] == '.':
                i += 1
                if i >= n or not expr[i].isdigit():
                    return None  
                while i < n and expr[i].isdigit():
                    i += 1
            tokens.append((NUM, expr[start:i]))
            continue

        if ch in _OPERATORS:
            tokens.append((OP, ch))
            i += 1
            continue

        if ch == '(':
            tokens.append((LPAREN, '('))
            i += 1
            continue

        if ch == ')':
            tokens.append((RPAREN, ')'))
            i += 1
            continue

        return None  

    tokens.append((END, ''))
    return tokens


def tokens_to_string(tokens) -> str:
    parts = []
    for ttype, value in tokens:
        if ttype == END:
            parts.append("[END]")
        else:
            parts.append(f"[{ttype}:{value}]")
    return " ".join(parts)



# Parser (recursive descent) -> builds a tuple-based parse tree


class ParseError(Exception):
    pass


def _peek(tokens, pos):
    return tokens[pos]


def parse(tokens):
    tree, pos = _parse_expr(tokens, 0)
    if tokens[pos][0] != END:
        raise ParseError(f"Unexpected token {tokens[pos]} after expression")
    return tree


def _parse_expr(tokens, pos):
    left, pos = _parse_term(tokens, pos)
    while True:
        ttype, value = _peek(tokens, pos)
        if ttype == OP and value in ('+', '-'):
            pos += 1
            right, pos = _parse_term(tokens, pos)
            left = (value, left, right)
        else:
            break
    return left, pos


def _parse_term(tokens, pos):
    left, pos = _parse_unary(tokens, pos)
    while True:
        ttype, value = _peek(tokens, pos)
        if ttype == OP and value in ('*', '/', '%'):
            pos += 1
            right, pos = _parse_unary(tokens, pos)
            left = (value, left, right)
        elif ttype == LPAREN:
            right, pos = _parse_unary(tokens, pos)
            left = ('*', left, right)
        else:
            break
    return left, pos


def _parse_unary(tokens, pos):
    ttype, value = _peek(tokens, pos)
    if ttype == OP and value == '-':
        pos += 1
        operand, pos = _parse_unary(tokens, pos)
        return ('neg', operand), pos
    if ttype == OP and value == '+':
        raise ParseError("Unary '+' is not supported")
    return _parse_power(tokens, pos)


def _parse_power(tokens, pos):
    base, pos = _parse_primary(tokens, pos)
    ttype, value = _peek(tokens, pos)
    if ttype == OP and value == '^':
        pos += 1
        exponent, pos = _parse_unary(tokens, pos)
        return ('^', base, exponent), pos
    return base, pos


def _parse_primary(tokens, pos):
    ttype, value = _peek(tokens, pos)

    if ttype == NUM:
        return ('num', float(value)), pos + 1

    if ttype == LPAREN:
        inner, pos = _parse_expr(tokens, pos + 1)
        ttype2, _ = _peek(tokens, pos)
        if ttype2 != RPAREN:
            raise ParseError("Expected ')'")
        return inner, pos + 1

    raise ParseError(f"Unexpected token {tokens[pos]}")


# ----------------------------------------------------------------------
# Evaluation
# ----------------------------------------------------------------------

class EvalError(Exception):
    pass


def evaluate(tree):
    kind = tree[0]

    if kind == 'num':
        return tree[1]

    if kind == 'neg':
        return -evaluate(tree[1])

    if kind in ('+', '-', '*', '/', '%', '^'):
        left = evaluate(tree[1])
        right = evaluate(tree[2])
        if kind == '+':
            return left + right
        if kind == '-':
            return left - right
        if kind == '*':
            return left * right
        if kind == '/':
            if right == 0:
                raise EvalError("Division by zero")
            return left / right
        if kind == '%':
            if right == 0:
                raise EvalError("Modulo by zero")
            return left % right
        if kind == '^':
            return left ** right

    raise EvalError(f"Unknown node {tree!r}")


# ----------------------------------------------------------------------
# Formatting
# ----------------------------------------------------------------------

def format_number(value: float) -> str:
    if value == int(value):
        return str(int(value))
    rounded = round(value, 4)
    text = f"{rounded:.4f}".rstrip('0').rstrip('.')
    return text if text else "0"


def tree_to_string(tree) -> str:
    kind = tree[0]
    if kind == 'num':
        return format_number(tree[1])
    if kind == 'neg':
        return f"(neg {tree_to_string(tree[1])})"
    op, left, right = tree
    return f"({op} {tree_to_string(left)} {tree_to_string(right)})"


# ----------------------------------------------------------------------
# Per-line processing
# ----------------------------------------------------------------------

def process_line(original: str) -> dict:
    tokens = tokenize(original)

    if tokens is None:
        return {
            "input": original,
            "tree": "ERROR",
            "tokens": "ERROR",
            "result": "ERROR",
        }

    tokens_str = tokens_to_string(tokens)

    try:
        tree = parse(tokens)
    except ParseError:
        return {
            "input": original,
            "tree": "ERROR",
            "tokens": tokens_str,
            "result": "ERROR",
        }

    tree_str = tree_to_string(tree)

    try:
        value = evaluate(tree)
    except (EvalError, ZeroDivisionError, OverflowError, ValueError):
        return {
            "input": original,
            "tree": tree_str,
            "tokens": tokens_str,
            "result": "ERROR",
        }

    return {
        "input": original,
        "tree": tree_str,
        "tokens": tokens_str,
        "result": value,
    }


def _result_to_string(result) -> str:
    if result == "ERROR":
        return "ERROR"
    return format_number(result)


# ----------------------------------------------------------------------
# Public interface
# ----------------------------------------------------------------------

def evaluate_file(input_path: str) -> list:
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    records = []
    for raw_line in lines:
        line = raw_line.rstrip('\n').rstrip('\r')
        if line.strip() == "":
            continue
        records.append(process_line(line))

    directory = os.path.dirname(os.path.abspath(input_path))
    output_path = os.path.join(directory, "output.txt")

    blocks = []
    for rec in records:
        block = (
            f"Input: {rec['input']}\n"
            f"Tree: {rec['tree']}\n"
            f"Tokens: {rec['tokens']}\n"
            f"Result: {_result_to_string(rec['result'])}"
        )
        blocks.append(block)

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.write("\r\n\r\n".join(b.replace("\n", "\r\n") for b in blocks))
        if blocks:
            f.write("\r\n")

    return records

def main():
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        candidates = ["sample_input.txt", "input.txt"]
        input_path = next((c for c in candidates if os.path.exists(c)), candidates[0])
    evaluate_file(input_path)
    print(f"Done. See output.txt next to '{input_path}'.")


if __name__ == "__main__":
    main()