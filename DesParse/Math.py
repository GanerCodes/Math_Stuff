from latex_comprehension import Parser, compile_latex, Holder, Peekable, SYMBOL_MAP, PSEUDO_CLOSURES

class Term:
    def __eq__(self, other):
        return type(self) == type(other)
    
class Closure(Term):
    def __init__(self, terms=None):
        self.terms = terms or []
    def __iter__(self):
        return iter(self.terms)
    def __repr__(self):
        return "{%s}" % (' + '.join(map(str, self.terms)))
    def __len__(self):
        return len(self.terms)
    def __getitem__(self, i):
        return self.terms[i]
    def __eq__(self, other):
        if not super() == other:
            return False
        return list(self) == list(other)
        
    def unparse_terms(self):
        return [c.unparse() for c in self]

class Commutative_set(Closure):
    def unparse(self):
        dat = Peekable(self.unparse_terms())
        new_dat = []
        for i in dat.nexts():
            new_dat.append(i)
            if q := dat.peek():
                
                m = q
                while isinstance(m, Holder) and len(m) and m.name in PSEUDO_CLOSURES:
                    if m.name == "OPERATOR":
                        if q.data[0] in {'-', '+'}:
                            break
                    m = m.data[0]
                else:
                    new_dat.append(
                        Holder("OPERATOR", ['+']))
                
            
        return Holder(data=new_dat)
    # TODO: add communtative __eq__
        
class PARENTHESIS(Commutative_set):
    def __repr__(self):
        return "(%s)" % (', '.join(map(str, self.terms)))
    def unparse(self):
        p = super().unparse()
        p.name = "CLOSURE_PARENTHESIS"
        return p
class PRODUCT(Commutative_set):
    def __repr__(self):
        return '*'.join(map(str, self.terms))
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
        
        print("THE:", r)
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
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.number == other.number
    def unparse(self):
        k = self.number
        res = Holder()
        if k < 0:
            res += Holder("OPERATOR", ['-'])
            k *= -1
        res += Holder("NUMBER", str(k))
        return res
class VARIABLE(Term):
    def __init__(self, structure):
        self.variable = VARIABLE.make_var_name(structure)
        self.internal_structure = structure
    def __repr__(self):
        return str(self.variable)
    def __eq__(self, other):
        if not super() == other:
            return False
        return self.variable == other.variable and self.internal_structure == other.internal_structure
    def make_var_name(dat):
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
                s += f"<{VARIABLE.make_var_name(i)}>"
                continue
            assert 0
        return s
    def unparse(self):
        return self.internal_structure

class FUNCTION(Term):
    def __init__(self, name, args=None):
        self.name = name
        self.args = args or []
    def __iter__(self):
        return iter(self.args)
    def __repr__(self):
        return f"{self.name}({', '.join(map(str, self.args))})"
    def __eq__(self, other):
        if not super() == other:
            return False
        if self.name != other.name:
            return False
        return list(self) == list(other)
    def unparse(self):
        if self.name == "factorial":
            return Holder("RIGHT_UNARY_COUPLE", [
                Holder(data=[i.unparse() for i in self.args]),
                Holder("OPERATOR", ['!'])])
        
        new_args = Holder("CLOSURE_PARENTHESIS")
        
        dat = Peekable(self.args)
        for i in dat.nexts():
            new_args += Holder("FUNC_ARGUMENT", [i.unparse()])
            if dat.peek():
                new_args += Holder("RELATION", [','])
        
        return Holder("FUNC_CALL", [
            self.name.unparse(),
            new_args])
class FRACTION(Term):
    def __init__(self, top=None, bottom=None):
        self.top = top or NUMBER()
        self.bottom = bottom or NUMBER()
    def __iter__(self):
        return iter((self.top, self.bottom))
    def __repr__(self):
        return f"({self.top})/({self.bottom})"
    def __eq__(self, other):
        if not super() == other:
            return False
        return (self.top == other.top and self.bottom == other.bottom)
    def unparse(self):
        return Holder("frac", [
            Holder(data=[self.top.unparse()]),
            Holder(data=[self.bottom.unparse()])])
class EXPONENT(Term):
    def __init__(self, base=None, exp=None):
        self.base = base or NUMBER()
        self.exp = exp or NUMBER()
    def __iter__(self):
        return iter((self.base, self.exp))
    def __repr__(self):
        return f"{self.base}**({self.exp})"
    def __eq__(self, other):
        if not super() == other:
            return False
        return (self.base == other.base and self.exp == other.exp)
    def unparse(self):
        if self.exp == FRACTION(NUMBER(1), NUMBER(2)):
            return Holder("sqrt", [
                Holder(data=[self.base])])
        return Holder(
            "EXPONENTIAL", [
                Holder(
                    data=[self.base.unparse()]),
                Holder(
                    "superscript",
                    [self.exp.unparse()])])

class Comp_Parser:
    def __new__(cls, comp):
        return cls.parse(comp)
    
    @classmethod
    def clean_name(cls, dat):
        if isinstance(dat, Holder):
            assert dat.name in {"VARIABLE", "FUNCTION"}
            return VARIABLE(dat)
        if isinstance(dat, list):
            return VARIABLE(Holder(data=[dat]))
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
            
        return PRODUCT(r)
    
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
        if len(terms) == 1:
            terms = terms[0]
        return terms
    
    @classmethod
    def parse(cls, comp):
        name, data = comp
        match name:
            case ''|"superscript"|"FUNC_ARGUMENT"|"CLOSURE_PARENTHESIS":
                s = cls.parse_sequence(data)
                
                if len(s) == 1:
                    return s[0]
                
                if name == "CLOSURE_PARENTHESIS":
                    return PARENTHESIS(s)
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

def deparse_math():
    pass

if __name__ == "__main__":
    # t = r"""\left(f\left(x,y\right)+2\right)^{2}"""
    # t = r"""f\left(a,b\right)+1"""
    # t = r"""\left(\sqrt{x}+\frac{\sqrt[3]{x}}{2}\right)^{2}-2\left(2!\right)\left(x^{y^{z}}\right)!"""
    # t = r"""\left(\sqrt{x}+\frac{\sqrt[3]{x}}{2}\right)^{2}-2\left(2!\right)\left(x^{y^{z}}\right)!\lambda^{2x\phi}"""
    # t = r"""\frac{\sqrt[3]{x}}{2}"""
    # t = r"""x^{2}"""
    t = r"""\left(x^{2}+y^{2}\right)\left(z+25+2-x+1\ 1\right)"""
    q = Parser(t)
    print()
    print(q.pretty())
    print()
    k = Comp_Parser(q)
    print(k)
    m = k.unparse()
    print()
    print(m.pretty())
    print()
    print(compile_latex(m))
