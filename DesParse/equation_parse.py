from latex_comprehension import Parser, compile_latex, Holder, Peekable, SYMBOL_MAP, PSEUDO_CLOSURES

def get_first_non_pseudo(c):
    while isinstance(c, Holder) and c.name in PSEUDO_CLOSURES and c.data:
        c = c.data[0]
    return c

def add_or_ins(d, v, n=1):
    if v in d:
        d[v] += n
    else:
        d[v] = n

class Term:
    def __eq__(self, other):
        return type(self) == type(other)
    
class Closure(Term):
    def __init__(self, terms=None):
        self.terms = terms or []
    def __iter__(self):
        return iter(self.terms)
    def __repr__(self):
        return "{%s}" % (' | '.join(map(str, self.terms)))
    def __len__(self):
        return len(self.terms)
    def __getitem__(self, i):
        return self.terms[i]
    def __eq__(self, other):
        return type(self) == type(other) and self.terms == other.terms
    def unparse_terms(self):
        return [c.unparse() for c in self]

class Commutative_set(Closure):
    def __eq__(self, other):
        return type(self) == type(other) and self.gather_terms() == other.gather_terms()
    def __repr__(self):
        return "(%s)" % (' # '.join(map(str, self.terms)))
    def __hash__(self):
        return 0
    def gather_terms(self):
        terms = {}
        for v in self.terms:
            if isinstance(v, NUMBER):
                add_or_ins(terms, NUMBER(1), v.number)
            elif isinstance(v, PRODUCT):
                n, new_term = v.split_term()
                if n:
                    add_or_ins(terms, new_term, n)
            else:
                add_or_ins(terms, v)
        return terms

class ADDITIVE(Commutative_set):
    def __repr__(self):
        return "⟨%s⟩" % (' + '.join(map(str, self.terms)))
    def unparse(self):
        dat = Peekable(self.unparse_terms())
        new_dat = []
        for i in dat.nexts():
            new_dat.append(i)
            if q := dat.peek():
                if isinstance(m := get_first_non_pseudo(q), Holder):
                    if m.name == "OPERATOR" and m.data[0] in {'-', '+'}:
                        continue
                new_dat.append(
                    Holder("OPERATOR", ['+']))
        
        return Holder("CLOSURE_PARENTHESIS", data=new_dat)

class PRODUCT(Commutative_set):
    def __repr__(self):
        return f"<{('*'.join(map(str, self.terms)))}>"
    def split_term(self): # 🠒 (num, product|number)
        n, new_term = 1, []
        for k in self.terms:
            if isinstance(k, NUMBER):
                n *= k.number
            else:
                new_term.append(k)
        
        if new_term:
            return n, PRODUCT(new_term)
        return n, NUMBER(1)
    def unparse(self):
        num, A = 1, []
        for i in self.terms:
            if isinstance(i, NUMBER):
                num *= i.number
            else:
                A.append(i.unparse())
        
        r = Holder()
        if num < 0:
            r += Holder("OPERATOR", ['-'])
            num *= -1
        if num != 1 or not len(A):
            r += Holder("NUMBER", [str(num)])
        r += A
        
        return r

class NUMBER(Term):
    def __init__(self, number=1):
        if isinstance(number, str):
            if abs(
                (fN:=float(number)) - (iN:=int(number))
                    ) < 10 ** -15:
                number = iN
            else:
                number = fN
        self.number = number
    def __repr__(self):
        return str(self.number)
    def __hash__(self):
        return hash(self.number)
    def __eq__(self, other):
        return type(self) == type(other) and self.number == other.number
    def unparse(self):
        k = self.number
        res = Holder()
        if k < 0:
            res += Holder("OPERATOR", ['-'])
            k *= -1
        res += Holder("NUMBER", [str(k)])
        return res

class VARIABLE(Term):
    def __init__(self, structure):
        self.variable = VARIABLE.make_var_name(structure)
        self.internal_structure = structure
    def __repr__(self):
        return str(self.variable)
    def __hash__(self):
        return hash(self.variable)
    def __eq__(self, other):
        return type(self) == type(other) and \
            self.variable == other.variable and \
            self.internal_structure == other.internal_structure
    def make_var_name(dat):
        if dat.name == "FUNCTION":
            dat = Holder(data=[dat])
        
        s = ""
        for i in dat.data:
            if i.name == "VAR":
                s += i.data[0]
                continue
            if i.name == "SYMBOL":
                if i.data[0] in SYMBOL_MAP['SYMBOL'][1]:
                    s += '\\'
                s += i.data[0]
                continue
            if i.name == "NUMBER":
                s += i.data[0]
                continue
            if i.name == "FUNCTION":
                if len(i.data) == 1:
                    s += i.data[0]
                    continue
                if len(i.data) == 2:
                    s += i.data[1]
                    continue
                assert 0
            if i.name == "subscript":
                s += f"_<{VARIABLE.make_var_name(i)}>"
                continue
            if i.name == "CLOSURE_SQUARE":
                s += f"[{str(i)}]"
                continue
            assert 0
        return s
    def unparse(self):
        return self.internal_structure

class FUNCTION(Closure):
    def __init__(self, name, args=None):
        self.name = name
        self.terms = args or []
    def __repr__(self):
        return f"{self.name}({', '.join(map(str, self.terms))})"
    def unparse(self):
        if self.name == "factorial":
            return Holder("RIGHT_UNARY_COUPLE", [
                Holder(data=[i.unparse() for i in self.terms]),
                Holder("OPERATOR", ['!'])])
        
        new_args = Holder("CLOSURE_PARENTHESIS")
        
        dat = Peekable(self.terms)
        for i in dat.nexts():
            new_args += Holder("FUNC_ARGUMENT", [i.unparse()])
            if dat.peek():
                new_args += Holder("RELATION", [','])
        
        return Holder("FUNC_CALL", [
            self.name.unparse(),
            new_args])

class FRACTION(Closure):
    def __init__(self, top=None, bottom=None):
        self.terms = [top or NUMBER(), bottom or NUMBER()]
    def top(self):
        return self.terms[0]
    def bottom(self):
        return self.terms[1]
    def __iter__(self):
        return iter((self.top(), self.bottom()))
    def __repr__(self):
        return f"frac({self.top()}, {self.bottom()})"
    def unparse(self):
        return Holder("frac", [
            Holder(data=[self.top().unparse()]),
            Holder(data=[self.bottom().unparse()])])

class EXPONENT(Closure):
    def __init__(self, base=None, exp=None):
        self.terms = [base or NUMBER(), exp or NUMBER(1)]
    def base(self):
        return self.terms[0]
    def exp(self):
        return self.terms[1]
    def __iter__(self):
        return iter((self.base(), self.exp()))
    def __repr__(self):
        return f"pow({self.base()}, {self.exp()})"
    def unparse(self):
        if self.exp() == FRACTION(NUMBER(1), NUMBER(2)):
            return Holder("sqrt", [
                Holder(data=[self.base()])])
        return Holder(
            "EXPONENTIAL", [
                Holder(
                    data=[self.base().unparse()]),
                Holder(
                    "superscript",
                    [self.exp().unparse()])])

class Comp_Parser:
    def __new__(cls, comp):
        if isinstance(comp, str):
            comp = Parser(comp)
        return cls.parse(comp)
    
    @classmethod
    def clean_name(cls, dat):
        if isinstance(dat, Holder):
            assert dat.name in {"VARIABLE", "FUNCTION"}
            return VARIABLE(dat)
        if isinstance(dat, list):
            return VARIABLE(Holder(data=dat))
        assert 0
    
    @classmethod
    def group_by_type(cls, comp, t):
        return [i for i in comp.data if i.name == t]
    
    @classmethod
    def parse_function_call(cls, func, close):
        args = cls.parse_list(
            cls.group_by_type(
                close,
                "FUNC_ARGUMENT"))
        
        if func.name == "VARIABLE":
            return FUNCTION(
                cls.clean_name(func),
                args)
        if func.name == "FUNCEXP":
            if len(func.data) == 1:
                return FUNCTION(
                    cls.clean_name(func.data[0]),
                    args)
            if len(func.data) == 2:
                arg_name = func.data[1].name
                if arg_name == "subscript":
                    return FUNCTION(
                        cls.clean_name(func.data),
                        args)
                if arg_name == "superscript":
                    return EXPONENT(
                        FUNCTION(
                            cls.clean_name(func.data[0]),
                            args),
                        cls.parse(func.data[1])) # exponent
                assert 0
            if len(func.data) == 3:
                return EXPONENT(
                    FUNCTION(
                        cls.clean_name(func.data[:2]),
                        args),
                    cls.parse(func.data[2])) # exponent
            assert 0
        assert 0
    
    @classmethod
    def parse_list(cls, l):
        return list(map(cls.parse, l))
    
    @classmethod
    def parse_product(cls, l): # 🠒 PRODUCT
        if not isinstance(l, Peekable):
            l = Peekable(l)
        
        mul = 1
        for name, data in l.peeks():
            if name == "OPERATOR" and data[0] in {'-', '+'}:
                if data[0] == '-':
                    mul *= -1
                l.next()
            else:
                break
        
        r = []
        for c in l.peeks():
            name, data = c
            if name == "OPERATOR":
                if data[0] in {'-', '+'}:
                    break
            else:
                r.append(
                    cls.parse(
                        l.next()))
        
        if mul < 0:
            r.append(
                NUMBER(-1))
        
        if len(r) > 1:
            return PRODUCT(r)
        return r[0]
    
    @classmethod
    def parse_sqrt(cls, comp):
        assert 2 >= len(comp.data) >= 1
        if len(comp.data) == 1:
            return EXPONENT(
                cls.parse(comp.data[0]),
                FRACTION(
                    NUMBER(1),
                    NUMBER(2)))
        return EXPONENT(
            cls.parse(
                comp.data[1]),
            FRACTION(
                NUMBER(1),
                cls.parse(
                    comp.data[0])))
    
    @classmethod
    def parse_right_unary_couple(cls, comp):
        assert len(comp) == 2
        
        if comp.data[1].name == "OPERATOR" and comp.data[1].data[0] == '!':
            return FUNCTION(
                "factorial",
                [cls.parse(
                    comp.data[0])])
        assert 0
    
    @classmethod
    def parse_sequence(cls, l):
        if not isinstance(l, Peekable):
            l = Peekable(l)
        
        terms = []
        while l:
            terms.append(
                cls.parse_product(l))
        return terms
    
    @classmethod
    def parse(cls, comp):
        name, data = comp
        match name:
            case ''|"superscript"|"FUNC_ARGUMENT"|"CLOSURE_PARENTHESIS":
                s = cls.parse_sequence(data)
                
                if len(s) == 1:
                    return s[0]
                
                if not isinstance(s, Term):
                    s = ADDITIVE(s)
                return s
            case "FUNC_CALL":
                return cls.parse_function_call(*data)
            case "NUMBER":
                return NUMBER(data[0])
            case "VARIABLE":
                return VARIABLE(comp)
            case "EXPONENTIAL":
                assert len(data) == 2
                return EXPONENT(
                    cls.parse(data[0]),
                    cls.parse(data[1]))
            case "sqrt":
                return cls.parse_sqrt(comp)
            case "frac":
                return FRACTION(
                    cls.parse(data[0]),
                    cls.parse(data[1]))
            case "RIGHT_UNARY_COUPLE":
                return cls.parse_right_unary_couple(comp)
            case "ITERABLE"|"RELATION":
                raise NotImplementedError()
            case "OPERATOR":
                raise ValueError("why is an opERATOR here")
            case _:
                print(name)
                assert 0

if __name__ == "__main__":
    # t = r"""\left(f\left(x,y\right)+2\right)^{2}"""
    # t = r"""f\left(a,b\right)+1"""
    # t = r"""\left(\sqrt{x}+\frac{\sqrt[3]{x}}{2}\right)^{2}-2\left(2!\right)\left(x^{y^{z}}\right)!"""
    # t = r"""\left(\sqrt{x}+\frac{\sqrt[3]{x}}{2}\right)^{2}-2\left(2!\right)\left(x^{y^{z}}\right)!\lambda^{2x\phi}"""
    # t = r"""\frac{\sqrt[3]{x}}{2}"""
    # t = r"""x^{2}"""
    # t = r"""\left(x^{2}+y^{2}\right)\left(z+25+2-x+1\ 1\right)"""
    # t = r"""2+\frac{\sqrt[\left(\frac{2}{2}\right)^{2}]{\frac{2}{2}}}{2}"""
    # t = r"""\operatorname{mod}\left(x,2\right)^{2}+\sin^{2}\left(x\right)"""
    # t =  r"""\frac{f\left(X\right)+\sin\left(x\right)+\cos^{2}\left(x\right)+\operatorname{mod}_{2}^{2}\left(x,2\right)^{2}}{8x}"""
    # t = r"""\left(x\right)\left(y\right)+x^{2}y^{2}\left(x-y\right)"""
    t = r"""x^{2}+\frac{\left(x^{2y}-2\right)^{2}}{10x-y\sin\left(\operatorname{mod}\left(x,2\right),y\right)}"""
    print(t)
    print()
    print(k := Comp_Parser(t))
    print()
    print(m := k.unparse())
    print()
    print(compile_latex(m))