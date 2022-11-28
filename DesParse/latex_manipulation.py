from latex_comprehension import *

def ins_add(d, t, n=1):
    if t in d:
        d[t] += n
    else:
        d[t] = n

def seperate_types(terms, *types):
    r = []
    for i, v in list(enumerate(terms))[::-1]:
        if v.name in types:
            r.append(terms.pop(i))
    return r

# 🠒 coeff, term
def collect_linear_term(content):
    number = 1
    while c := content.peek():
        if c.name != "OPERATOR": break
        if c.data[0] not in {'-', '+'}: break
        if c.data[0] == '-':
            number *= -1
        content.next()
    
    term = []
    while c := content.peek():
        if c.name == "OPERATOR" and c.data[0] in {'-', '+'}:
            break
        if c.name == "NUMBER":
            number *= float(c.data[0])
            content.next()
            continue
        term.append(content.next())
    
    if abs(number - int(number)) < (10**-15):
        number = int(number)
    
    return number, term

def join_like_terms(content, terms=None):
    terms = terms or {}
    while c := content.peek():
        num, term = collect_linear_term(content)
        term = Holder(data=sorted(term))
        ins_add(terms, term, num)
    return terms

def merge_terms(content):
    t = []
    while c := content.next():
        term, coeff = c
        if coeff < 0:
            coeff *= -1
            t.append(Holder("OPERATOR", ['-']))
        
        if not (coeff == 1 and term.data):
            t.append(Holder("NUMBER", [str(coeff)]))
        t += term.data
        if content.peek() and content.peek()[1] > 0:
            t.append(Holder("OPERATOR", ['+']))
    return t

if __name__ == "__main__":
    t = r"""5x-2+2y+4-x^{2}"""
    q = Parser(t)
    q = Peekable(q.data)
    q = join_like_terms(q).items()
    q = Peekable(list(q))
    q = merge_terms(q)
    print(q)
    print(compile_latex(q))