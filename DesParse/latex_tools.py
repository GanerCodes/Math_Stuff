from latex_parse import Holder, Peekable, BRACKET_PAIRS, ONE_ARG_FUNCS, TWO_ARG_FUNCS
from latex_comprehension import parse_abstract, SPLIT_OPERATORS, PARSE_INNER

def remove_extra_chained_operators(content):
    t = []
    
    while c := content.peek():
        if c.name == "OPERATOR" and c.data[0] in SPLIT_OPERATORS:
            t.append(content.next())
        else:
            break
    
    if not t:
        return
    if len(t) == 1:
        return t[0]
    
    minus_count = sum(i.data[0] == '-' for i in t)
    return Holder("OPERATOR", '+-'[minus_count % 2])

SIMPLE_RECURSIVE_CONDITIONS = { *BRACKET_PAIRS['name'], *ONE_ARG_FUNCS }
def multiplication_grouper(content):
    group = []
    while c := content.peek():
        if c.name == "OPERATOR" and c.data[0] in SPLIT_OPERATORS:
            break
        else:
            v = content.next()
            
            elements_to_recurse = []
            if v.name in SIMPLE_RECURSIVE_CONDITIONS:
                elements_to_recurse = [v]
            elif v.name in TWO_ARG_FUNCS:
                elements_to_recurse = v.data
            elif v.name == "ITERABLE":
                elements_to_recurse = [v.data[1], v.data[2], v.data[3].data[0]]
            
            print(elements_to_recurse)
            for i in elements_to_recurse:
                i.data = apply_scanner(i.data, multiplication_grouper).data
            
            group.append(v)
    return Holder("MULT", group)

def apply_scanner(content, scanner, scope=None):
    if isinstance(content, list):
        content = Peekable(content)
    elif isinstance(content, Holder):
        content = Peekable(content.data)
    if scope is None:
        scope = Holder()
    
    while content.peek():
        if Q := scanner(content):
            scope += Q
            continue
        
        scope += content.next()
    
    return scope

def parse(content):
    content = apply_scanner(content, remove_extra_chained_operators)
    content = apply_scanner(content, multiplication_grouper)
    return content

if __name__ == "__main__":
    # t = r"""2+-+-23"""
    t = r"""\frac{1}{n!}\int_{ }^{t}d_{\gamma}\left(t-\gamma\right)^{n}f\left(\gamma\right)"""
    q = parse_abstract(t)
    print(q)
    print(parse(q.data))