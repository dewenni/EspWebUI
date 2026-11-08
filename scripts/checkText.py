"""Check translation declarations against HTML and statically readable JS uses.

The JS reader handles property access and key parameters forwarded through named
functions/arrow functions, including conditional literal arguments. It does not
execute JavaScript or try to resolve runtime-generated keys.
"""

import ast
from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
import logging
from pathlib import Path
import re
import sys


TRANSLATION_OBJECTS = ("lib_translations", "user_translations")
_JS_TOKEN = re.compile(
    r"(?P<comment>//[^\n]*|/\*[\s\S]*?\*/)"
    r"|(?P<string>\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')"
    r"|(?P<name>[A-Za-z_$][\w$]*)|(?P<symbol>=>|\?\.|[^\s])"
)


def _js_tokens(source):
    """Ignore comments/template text, but retain code inside ${...}."""
    def read(pos, interpolation=False):
        tokens = []
        depth = 0
        while pos < len(source):
            if source[pos].isspace():
                pos += 1
                continue
            if source[pos] == "`":
                pos += 1
                text = ""
                dynamic = False
                while pos < len(source) and source[pos] != "`":
                    if source[pos] == "\\":
                        text += source[pos:pos + 2]
                        pos += 2
                    elif source.startswith("${", pos):
                        dynamic = True
                        nested, pos = read(pos + 2, True)
                        # Keep interpolation expressions separate from the key
                        # expression if this template is itself used as a key.
                        tokens.extend([("symbol", "("), *nested, ("symbol", ")")])
                    else:
                        text += source[pos]
                        pos += 1
                pos += 1
                tokens.append(("dynamic", "template") if dynamic else ("string", text))
                continue
            match = _JS_TOKEN.match(source, pos)
            if not match:
                pos += 1
                continue
            kind, value = match.lastgroup, match.group()
            pos = match.end()
            if kind == "comment":
                continue
            # A regex literal is data, not a translation access. Distinguish
            # common expression-start contexts from division after a value.
            previous = tokens[-1] if tokens else None
            regex_start = (previous is None
                           or previous[0] == "symbol" and previous[1] in
                           ("=", "(", "[", "{", ",", ":", ";", "!", "?", "=>", "&", "|")
                           or previous in (("name", "return"), ("name", "throw"), ("name", "case")))
            if value == "/" and regex_start:
                in_class = False
                while pos < len(source) and source[pos] not in "\r\n":
                    char = source[pos]
                    pos += 1
                    if char == "\\":
                        pos += 1
                    elif char == "[":
                        in_class = True
                    elif char == "]":
                        in_class = False
                    elif char == "/" and not in_class:
                        while pos < len(source) and source[pos].isalpha():
                            pos += 1
                        break
                tokens.append(("regex", ""))
                continue
            if interpolation and value == "}" and depth == 0:
                return tokens, pos
            if value == "{":
                depth += 1
            elif value == "}":
                depth -= 1
            if kind == "string":
                try:
                    value = ast.literal_eval(value)
                except (SyntaxError, ValueError):
                    value = value[1:-1]
            tokens.append((kind, value))
        return tokens, pos

    return read(0)[0]


def _pairs(tokens):
    result, stack = {}, []
    for i, (_, value) in enumerate(tokens):
        if tokens[i][0] != "symbol":
            continue
        if value in ("(", "[", "{"):
            stack.append(i)
        elif value in (")", "]", "}") and stack:
            if tokens[stack[-1]][1] == {")": "(", "]": "[", "}": "{"}[value]:
                start = stack.pop()
                result[start] = i
                result[i] = start
    return result


def _split(tokens, start, end, pairs, separator=","):
    parts, part, i = [], start, start
    while i < end:
        if tokens[i] == ("symbol", separator):
            parts.append((part, i))
            part = i + 1
        if i in pairs and pairs[i] > i:
            i = pairs[i]
        i += 1
    if part < end:
        parts.append((part, end))
    return parts


def _key_values(tokens, start, end, pairs):
    """Return literal alternatives and simple forwarded parameter names."""
    while start < end and tokens[start] == ("symbol", "(") and pairs.get(start) == end - 1:
        start, end = start + 1, end - 1
    if end == start + 1 and tokens[start][0] in ("string", "name"):
        return [tokens[start]]
    # Only the branches of a conditional are keys, never its condition strings.
    i = start
    while i < end:
        if tokens[i] == ("symbol", "?"):
            nesting, j = 0, i + 1
            while j < end:
                if tokens[j] == ("symbol", "?"):
                    nesting += 1
                elif tokens[j] == ("symbol", ":"):
                    if nesting == 0:
                        return (_key_values(tokens, i + 1, j, pairs)
                                + _key_values(tokens, j + 1, end, pairs))
                    nesting -= 1
                if j in pairs and pairs[j] > j:
                    j = pairs[j]
                j += 1
            return []
        if i in pairs and pairs[i] > i:
            i = pairs[i]
        i += 1
    return []


@dataclass
class _Function:
    name: str
    params: list
    start: int
    end: int
    scope: tuple = (0, 0)
    key_params: set = field(default_factory=set)


def javascript_keys(source):
    """Return declarations (including duplicates) and JS translation reads."""
    tokens = _js_tokens(source)
    pairs = _pairs(tokens)
    declarations, excluded = [], set()
    for i, token in enumerate(tokens):
        if token[0] != "name" or token[1] not in TRANSLATION_OBJECTS:
            continue
        if tokens[i + 1:i + 3] != [("symbol", "="), ("symbol", "{")]:
            continue
        end = pairs.get(i + 2)
        if end is None:
            continue
        excluded.update(range(i, end + 1))
        for a, b in _split(tokens, i + 3, end, pairs):
            if b > a + 1 and tokens[a][0] in ("name", "string") and tokens[a + 1] == ("symbol", ":"):
                declarations.append(tokens[a][1])

    functions, parameter_lists = [], set()
    for i, token in enumerate(tokens):
        if i in excluded:
            continue
        name, opening, body = None, None, None
        if token == ("name", "function"):
            if i + 2 < len(tokens) and tokens[i + 1][0] == "name":
                name, opening = tokens[i + 1][1], i + 2
            elif i >= 2 and tokens[i - 1] == ("symbol", "="):
                name, opening = tokens[i - 2][1], i + 1
            if opening in pairs:
                body = pairs[opening] + 1
        elif token == ("symbol", "=>"):
            opening = pairs.get(i - 1, i - 1)
            if opening >= 2 and tokens[opening - 1] == ("symbol", "="):
                name, body = tokens[opening - 2][1], i + 1
        if name is None or body is None or body >= len(tokens):
            continue
        if tokens[opening] == ("symbol", "("):
            params = [tokens[a][1] if b == a + 1 and tokens[a][0] == "name" else None
                      for a, b in _split(tokens, opening + 1, pairs[opening], pairs)]
            parameter_lists.add(opening)
        else:
            params = [tokens[opening][1]]
        if tokens[body] == ("symbol", "{"):
            end = pairs.get(body, body)
        else:
            end = body
            while end < len(tokens) and tokens[end] not in (("symbol", ";"), ("symbol", ","), ("symbol", ")"), ("symbol", "}")):
                end = pairs.get(end, end) + 1
        functions.append(_Function(name, params, body, end))
    for fn in functions:
        parents = [p for p in functions if p.start < fn.start and fn.end <= p.end]
        if parents:
            parent = min(parents, key=lambda p: p.end - p.start)
            fn.scope = (parent.start, parent.end)
        else:
            fn.scope = (0, len(tokens))

    used, reads, calls = set(), [], []
    for i, (kind, value) in enumerate(tokens):
        if i in excluded or kind != "name":
            continue
        if value in TRANSLATION_OBJECTS and i + 1 < len(tokens):
            if tokens[i + 1] == ("symbol", "[") and i + 1 in pairs:
                reads.append((i, i + 2, pairs[i + 1]))
            elif tokens[i + 1] in (("symbol", "."), ("symbol", "?.")) and i + 2 < len(tokens):
                if tokens[i + 2][0] == "name" and tokens[i + 3:i + 4] != [("symbol", "(")]:
                    used.add(tokens[i + 2][1])
        if tokens[i + 1:i + 2] == [("symbol", "(")] and i + 1 in pairs and i + 1 not in parameter_lists:
            if i and tokens[i - 1] in (("symbol", "."), ("symbol", "?.")):
                continue
            candidates = [fn for fn in functions if fn.name == value and fn.scope[0] <= i <= fn.scope[1]]
            if candidates:
                fn = min(candidates, key=lambda fn: fn.scope[1] - fn.scope[0])
                calls.append((i, fn, _split(tokens, i + 2, pairs[i + 1], pairs)))

    def consume(position, start, end):
        changed = False
        owners = [fn for fn in functions if fn.start <= position <= fn.end]
        owner = min(owners, key=lambda fn: fn.end - fn.start) if owners else None
        for kind, value in _key_values(tokens, start, end, pairs):
            if kind == "string":
                used.add(value)
            elif owner and value in owner.params:
                index = owner.params.index(value)
                if index not in owner.key_params:
                    owner.key_params.add(index)
                    changed = True
        return changed

    for position, start, end in reads:
        consume(position, start, end)
    # Resolve forwarding chains such as fail(key) -> translate(key) -> object[key].
    changed = True
    while changed:
        changed = False
        for position, fn, args in calls:
            for index in list(fn.key_params):
                if index < len(args):
                    changed |= consume(position, *args[index])
    return declarations, used


class _HtmlKeys(HTMLParser):
    def __init__(self):
        super().__init__()
        self.keys = set()

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == "data-i18n" and value:
                # Same syntax as localizePage: $literal text$ and ++suffix.
                value = value.split("++", 1)[0]
                self.keys.update(part for part in re.split(r"\$.*?\$", value) if part)


def check_translations(output_dir):
    output_dir = Path(output_dir)
    sources = []
    for name in ("lib.js", "user.js"):
        source = (output_dir / name).read_text(encoding="utf-8")
        expected = "lib_translations" if name == "lib.js" else "user_translations"
        tokens = _js_tokens(source)
        if not any(token == ("name", expected)
                   and tokens[i + 1:i + 3] == [("symbol", "="), ("symbol", "{")]
                   and i and tokens[i - 1] in (("name", "const"), ("name", "let"), ("name", "var"))
                   for i, token in enumerate(tokens)):
            logging.error("%s nicht in %s gefunden.", expected, output_dir / name)
            return False
        sources.append(source)
    # Helpers may live in lib.js while their callers live in user.js.
    declarations, js_keys = javascript_keys("\n".join(sources))
    html = _HtmlKeys()
    html.feed((output_dir / "index.html").read_text(encoding="utf-8"))
    declared = set(declarations)
    for key, count in sorted(Counter(declarations).items()):
        if count > 1:
            logging.warning("Doppelter Eintrag in lang.js: '%s' kommt %d mal vor", key, count)
    for key in sorted(declared - html.keys - js_keys):
        logging.warning("Schlüssel aus lang.js wird weder in HTML noch in JavaScript verwendet: '%s'", key)
    missing = (html.keys | js_keys) - declared
    for key in sorted(missing):
        location = "HTML und JavaScript" if key in html.keys and key in js_keys else "HTML" if key in html.keys else "JavaScript"
        logging.error("Schlüssel wird in %s verwendet, ist aber nicht in lang.js definiert: '%s'", location, key)
    return not missing


def main(web_dir="web", output_dir="output"):
    from SCons.Script import DefaultEnvironment

    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    project_dir = Path(DefaultEnvironment()["PROJECT_DIR"])
    if not check_translations(project_dir / web_dir / output_dir):
        sys.exit(1)


if __name__ == "__main__":
    main()
