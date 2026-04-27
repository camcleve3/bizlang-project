import re


TOKEN_SPECIFICATION = [
    ("LOAD", r"LOAD\b"),
    ("FILTER", r"FILTER\b"),
    ("AND", r"AND\b"),
    ("BY", r"BY\b"),
    ("SUM", r"SUM\b"),
    ("AVG", r"AVG\b"),
    ("COUNT", r"COUNT\b"),
    ("MIN", r"MIN\b"),
    ("MAX", r"MAX\b"),
    ("PLOT", r"PLOT\b"),
    ("BAR", r"BAR\b"),
    ("LINE", r"LINE\b"),
    ("EXPORT", r"EXPORT\b"),
    ("OPERATOR", r"=|>|<"),
    ("NUMBER", r"\d+(\.\d+)?"),
    ("STRING", r'"[^"]*"'),
    ("IDENTIFIER", r"[A-Za-z_][A-Za-z0-9_.]*"),
    ("SKIP", r"[ \t\n]+"),
    ("MISMATCH", r"."),
]

TOKEN_REGEX = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPECIFICATION)


def tokenize(code):
    tokens = []
    for match in re.finditer(TOKEN_REGEX, code):
        kind = match.lastgroup
        value = match.group()

        if kind == "SKIP":
            continue
        elif kind == "STRING":
            tokens.append((kind, value[1:-1]))
        elif kind == "NUMBER":
            if "." in value:
                tokens.append((kind, float(value)))
            else:
                tokens.append((kind, int(value)))
        elif kind == "MISMATCH":
            raise SyntaxError(f"Unexpected character: {value}")
        else:
            tokens.append((kind, value))

    return tokens