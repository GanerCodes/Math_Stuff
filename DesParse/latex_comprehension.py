from latex_parse import (parse_latex, compile_latex, Peekable, Holder, ONE_CHAR_OPERATOR, BRACKET_PAIRS)

ITER_TYPES = {'int', 'prod', 'sum'}
SPLIT_OPERATORS = ONE_CHAR_OPERATOR

def TAKE_ENSURE(content, name):
    assert content and content.peek().name == name
    return content.next()

def ITERABLE_SCANNER(content):
    first = content.next()
    lower = TAKE_ENSURE(content, "subscript")
    upper = TAKE_ENSURE(content, "superscript")
    body = Holder()
    while p := content.peek():
        if p.name == "OPERATOR" and p.data[0] in SPLIT_OPERATORS:
            break
        body += content.next()
    
    return Holder("ITERABLE", [
        first,
        PARSE_INNER(lower),
        PARSE_INNER(upper),
        PARSE_INNER(body)])

def VAR_SCANNER(content):
    VAR = Holder("VAR", [content.next()])
    
    if not (r := content.peek()): return VAR
    if r.name == "subscript":
        VAR += content.next()
        if not (r := content.peek()): return VAR
    # maybe implement array variable type stuff here?
    if r.name == "SYMBOL" and r.data[0] == '.':
        if not (t := r.peek()): return VAR
        if t.name in {"VARIABLE", "SYMBOL"}:
            VAR += content.next() # add dot
            VAR += VAR_SCANNER(content).data # add the rest
    return VAR
    
def TOP(content, scope=None):
    if isinstance(content, list):
        content = Peekable(content)
    if scope is None:
        scope = Holder()
    
    while c := content.peek():
        name, data = c
        
        if name in {"VARIABLE", "SYMBOL"}:
            if name == "SYMBOL" and c.data[0] in ITER_TYPES:
                scope += ITERABLE_SCANNER(content)
            else:
                scope += VAR_SCANNER(content)
            continue
        if name in BRACKET_PAIRS['name']:
            scope += PARSE_INNER(content.next())
            continue
        
        scope += content.next()
        
    return scope

def PARSE_INNER(cell, func=TOP):
    return Holder(cell.name, func(cell.data).data)

def parse_abstract(s):
    return TOP(Peekable(parse_latex(s)))

if __name__ == "__main__":
    t = r"""\frac{1}{n!}\int_{ }^{t}d_{\gamma}\left(t-\gamma\right)^{n}f\left(\gamma\right)"""
    q = parse_abstract(t)
    print(q)
    print(compile_latex(q))