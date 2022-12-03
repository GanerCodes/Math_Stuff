from equation_parse import *

TRAVERSABLE = PARENTHESIS|ADDITIVE|FUNCTION|FRACTION|EXPONENT|PRODUCT

def clean(comp):
    if not isinstance(comp, TRAVERSABLE):
        return comp
    
    comp.terms = list(map(clean, comp.terms))
    for i, v in enumerate(comp.terms):
        comp.terms[i] = clean(v)
    
    q = None
    if isinstance(comp, ADDITIVE):
        q = ADDITIVE
    elif isinstance(comp, PRODUCT):
        q = PRODUCT
    
    if q:
        n = []
        for t in comp.terms:
            if isinstance(t, q):
                n += t.terms
            else:
                n.append(t)
        comp.terms = n
    
    if len(comp.terms) == 1:
        comp = comp.terms[0]
    
    return comp

def distribute(*terms):
    if len(terms) == 1:
        return terms[0]
    if len(terms) == 2:
        a, b = terms
        A, B = isinstance(a, ADDITIVE), isinstance(b, ADDITIVE)
        if not (A or B):
            return PRODUCT(terms)
        if A ^ B:
            m, s = (a, b) if A else (b, a)
            return ADDITIVE([
                distribute(s, t) for t in m])
        
        r = []
        for x in a:
            for y in b:
                r.append(distribute(x, y))
        return ADDITIVE(r)
            
    return distribute(terms[0], PRODUCT(terms[1:]))

def add_or_ins(d, v, n=1):
    if v in d:
        d[v] += n
    else:
        d[v] = n

def combine_additive_like_terms(comp):
    terms = {}
    for v in comp.terms:
        if isinstance(v, NUMBER):
            add_or_ins(terms, NUMBER(1), v.number)
            continue
        if isinstance(v, PRODUCT): # todo strip this out and use the product class method
            n, new_term = 1, []
            for k in v.terms:
                if isinstance(k, NUMBER):
                    n *= k.number
                else:
                    new_term.append(k)
            if not n:
                continue
            
            add_or_ins(terms, PRODUCT(new_term), n)
            continue
        add_or_ins(terms, v)
    
    res = []
    for t, n in terms.items():
        if not n:
            continue
        
        if isinstance(t, NUMBER):
            if not t.number:
                continue
            
            res.append(NUMBER(n * t.number))
        elif n == 1:
            res.append(t)
        else:
            res.append(
                PRODUCT(
                    [NUMBER(n), t]))
    
    return ADDITIVE(res)

def expand(comp):
    if isinstance(comp, TRAVERSABLE):
        comp.terms = [
            (expand(v) if isinstance(v, TRAVERSABLE) else v)
                for v in comp.terms]
    
    if not isinstance(comp, PRODUCT):
        return comp
    
    res = distribute(*comp.terms)
    res = clean(res)
    if isinstance(res, ADDITIVE):
        res = combine_additive_like_terms(res)
    return clean(res)

if __name__ == "__main__":
    # t = r"""\left(a+b\right)\left(c+d\right)"""
    # t = r"""\left(x^{2}-y^{2}\right)\left(\left(x-y^{2}+2\right)\left(a+b\right)\left(c-d\right)\right)"""
    # t = r"""\left(x^{2}+y\right)\left(y+2+\left(a+b\right)\left(c-d\right)\right)"""
    # t = r"""\left(x^{2}+y\right)\left(y+2+\left(a+b\right)\left(c-d\right)\right)69"""
    t = r"""\left(6-\lambda\right)\left(4-\lambda\right)-\left(-1\right)\left(5\right)"""
    print(t)
    print()
    print(k := Comp_Parser(t))
    print()
    print(o := expand(k))
    print()
    print(m := o.unparse())
    # print(m.pretty())
    print()
    print(compile_latex(m))