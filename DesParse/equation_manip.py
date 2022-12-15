from equation_parse import *
from util import instance_intersection

TRAVERSABLE = ADDITIVE|FUNCTION|FRACTION|EXPONENT|PRODUCT

def prod(l, start=1): # todo do the ittertools operation whtaever
    for i in l:
        start *= i
    return start

def flatten(comp):
    if isinstance(comp, TRAVERSABLE):
        flat = [k for t in comp.terms if (k := flatten(t))]
        
        if not flat:
            return None
        
        typ = instance_intersection(ADDITIVE|PRODUCT, comp)
        if typ:
            new_terms = []
            for t in flat:
                if isinstance(t, typ) or (isinstance(t, TRAVERSABLE) and len(t.terms) == 1):
                    new_terms += t.terms
                else:
                    new_terms.append(t)
            flat = new_terms
        
        if len(flat) == 1:
            return flat[0]
        
        comp.terms = flat
    else:
        return comp
    
    typ = instance_intersection(ADDITIVE|PRODUCT, comp)
    if not typ:
        return comp
    
    terms, numbers = [], []
    for t in comp.terms:
        if isinstance(t, NUMBER):
            numbers.append(t.number)
        else:
            terms.append(t)
    
    if typ == ADDITIVE:
        num = sum(numbers)
        if not terms:
            if num == 0:
                return None
            else:
                return NUMBER(num)
        elif num == 0:
            return terms[0] if len(terms) == 1 else typ(terms)
    elif typ == PRODUCT:
        if len(numbers):
            num = prod(numbers)
            if num == 0:
                return None
            if num == 1:
                if not terms:
                    return NUMBER(1)
                return terms[0] if len(terms) == 1 else typ(terms)
            if not terms:
                return NUMBER(num)
        elif terms:
            return terms[0] if len(terms) == 1 else typ(terms)
    
    return typ([ NUMBER(num), *terms ])

def distribute(*terms):
    if len(terms) == 1:
        return terms[0]
    if len(terms) == 2:
        a, b = terms
        A, B = isinstance(a, ADDITIVE), isinstance(b, ADDITIVE)
        if not (A or B):
            return PRODUCT([a, b])
        if A ^ B:
            m, s = (a, b)[::2*A-1] # stay mad
            return ADDITIVE([distribute(s, t) for t in m])
        
        return ADDITIVE([distribute(x, y) for x in a for y in b])
    
    return distribute(terms[0], distribute(*terms[1:]))

def combine_additive_like_terms(comp):
    if isinstance(comp, TRAVERSABLE):
        comp.terms = [combine_additive_like_terms(t) for t in comp.terms]
    if not isinstance(comp, ADDITIVE):
        return comp
    
    terms = comp.gather_terms()
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

def combine_multiplicative_like_terms(comp):
    if isinstance(comp, TRAVERSABLE):
        comp.terms = [combine_multiplicative_like_terms(t) for t in comp.terms]
    if not isinstance(comp, PRODUCT):
        return comp
    
    terms = comp.gather_terms()
    new_terms, res = {}, []
    
    for k, v in terms.items():
        if isinstance(k, NUMBER):
            res.append(NUMBER(v))
            continue
        
        if isinstance(k, EXPONENT):
            k, v = k.base(), ADDITIVE([NUMBER(v), k.exp()])
        else:
            v = NUMBER(v)
        
        if k in new_terms:
            new_terms[k].terms.append(v)
        else:
            new_terms[k] = ADDITIVE([v])
    for k, v in new_terms.items():
        k, v = flatten(k), flatten(v)
        if isinstance(v, NUMBER) and v.number == 1:
            res.append(k)
        else:
            res.append(EXPONENT(k, v))
    
    return PRODUCT(res)

def expand(comp):
    if isinstance(comp, TRAVERSABLE):
        comp.terms = [k for t in comp.terms if (k := expand(t))]
    else:
        return comp
    
    if not isinstance(comp, PRODUCT):
        return flatten(comp)
    
    res = distribute(*comp.terms)
    res = flatten(res)
    res = combine_additive_like_terms(res)
    res = combine_multiplicative_like_terms(res)
    return res

if __name__ == "__main__":
    # t = r"""\left(a+b\right)\left(c+d\right)"""
    # t = r"""\left(x^{2}-y^{2}\right)\left(\left(x-y^{2}+2\right)\left(a+b\right)\left(c-d\right)\right)"""
    # t = r"""\left(x^{2}+y\right)\left(y+2+\left(a+b\right)\left(c-d\right)\right)"""
    # t = r"""\left(x^{2}+y\right)\left(y+2+\left(a+b\right)\left(c-d\right)\right)69"""
    # t = r"""\left(6-\lambda\right)\left(4-\lambda\right)-\left(-1\right)\left(5\right)"""
    # t = r"""\left(x^{2}\frac{\left(x^{2y}-2\right)^{2}}{\left(10x-\left(5+5x\right)y\sin\left(\operatorname{mod}\left(x,2\right),y\right)\right)}\right)"""
    # t = r"""\left(6-\lambda\right)\left(4-\lambda\right)\left(4-\lambda\right)\left(4-\lambda\right)-\left(-1\right)\left(5\right)"""
    # t = r"""\left(3-\lambda\right)\left(7-\lambda\right)-\left(4\right)\left(8\right)"""
    # t = r"""\left(r_{1}\left[1\right]^{2}+2\right)"""
    # t = r"""\left(3-\lambda\right)\left(7-\lambda\right)\left(7-\lambda\right)-\left(4\right)\left(8\right)\left(7-\lambda\right)"""
    t = r"""\left(2-i\right)\left(-2-i\right)"""
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