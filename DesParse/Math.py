from latex_comprehension import Parser, Holder, Peekable, BRACKET_PAIRS

class Term:
    pass

class Closure(Term):
    def __init__(self, terms=None):
        self.terms = terms or []
    def __iter__(self):
        return iter(self.terms)
    def __repr__(self):
        return "{%s}" % (', '.join(map(str, self.terms)))

class Commutative_set(Closure):
    pass
class PARENTHESIS(Commutative_set):
    def __repr__(self):
        return "(%s)" % (', '.join(map(str, self.terms)))
class PRODUCT(Commutative_set):
    def __repr__(self):
        return '*'.join(map(str, self.terms))

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
class VARIABLE(Term):
    def __init__(self, variable):
        self.variable = variable
    def __repr__(self):
        return str(self.variable)

class FUNCTION(Term):
    def __init__(self, name, args=None):
        self.name = name
        self.args = args or []
    def __iter__(self):
        return iter(self.args)
    def __repr__(self):
        return f"{self.name}({', '.join(map(str, self.args))})"
class FRACTION(Term):
    def __init__(self, top=None, bottom=None):
        self.top = top or NUMBER()
        self.bottom = bottom or NUMBER()
    def __iter__(self):
        return iter((self.top, self.bottom))
    def __repr__(self):
        return f"({self.top})/({self.bottom})"
class EXPONENT(Term):
    def __init__(self, base=None, exp=None):
        self.base = base or NUMBER()
        self.exp = exp or NUMBER()
    def __iter__(self):
        return iter((self.base, self.exp))
    def __repr__(self):
        return f"{self.base}**({self.exp})"

class Comp_Parser:
    def __new__(cls, comp):
        return cls.parse(comp)
    
    @classmethod
    def parse_function_name(cls, dat):
        assert dat.name == "FUNCTION"
        if len(dat.data) == 1:
            return dat.data[0]
        
        assert len(dat.data) == 2 # case of operatorname
        return dat.data[1]
    
    @classmethod
    def clean_var_name(cls, dat):
        s = ""
        for i in dat.data:
            if i.name == "VAR":
                s += i.data[0]
                continue
            if i.name == "SYMBOL":
                s += i.data[0]
                continue
            if i.name == "NUMBER":
                s += i.data[0]
                continue
            if i.name == "FUNCTION":
                s += cls.parse_function_name(i)
                continue
            if i.name == "subscript":
                s += f"<{cls.clean_var_name(i)}>"
                continue
            assert 0
        return s
    
    @classmethod
    def clean_name(cls, dat):
        if isinstance(dat, Holder):
            if dat.name == "VARIABLE":
                return cls.clean_var_name(dat)
            if dat.name == "FUNCTION":
                return cls.parse_function_name(dat)
        if isinstance(dat, list):
            return cls.clean_var_name(Holder(data=dat))
        assert 0
    
    @classmethod
    def group_by_type(cls, comp, t):
        return [i for i in comp.data if i.name == t]
    
    @classmethod
    def parse_function_call(cls, func, close):
        args = cls.parse_list(cls.group_by_type(close, "FUNC_ARGUMENT"))
        print(close)
        if func.name == "VARIABLE":
            return FUNCTION(cls.clean_name(func), args)
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
        
        negative = None
        for name, data in l.peeks():
            if name == "OPERATOR" and data[0] in {'-', '+'}:
                if data[0] == '-':
                    negative = None if negative else -1
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
        
        if negative:
            r.append(
                NUMBER(-1))
            
        return PRODUCT(r)
    
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
            case ''|"superscript"|"FUNC_ARGUMENT":
                return cls.parse_sequence(data)
            case 'CLOSURE_PARENTHESIS':
                return PARENTHESIS(
                    cls.parse_sequence(data))
            case "FUNC_CALL":
                return cls.parse_function_call(*data)
            case "NUMBER":
                return NUMBER(data[0])
            case "VARIABLE":
                return VARIABLE(cls.clean_var_name(comp))
            case "EXPONENTIAL":
                assert len(data) == 2
                return EXPONENT(
                    cls.parse(data[0]),
                    cls.parse(data[1]))
            case "RIGHT_UNARY_COUPLE"|"ITERABLE"|"RELATION":
                raise NotImplementedError()
            case "OPERATOR":
                raise ValueError("why is an opERATOR here")
            case _:
                assert 0

if __name__ == "__main__":
    t = r"""\left(f\left(x,y\right)+2\right)^{2}"""
    q = Parser(t)
    print(q.pretty())
    print(Comp_Parser(q))
    
