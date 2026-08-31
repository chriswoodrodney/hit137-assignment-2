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
