from latex_comprehension import Parser, Holder

class Term:
    pass

# integrals, parenthesis, functions, etc.; stuff that holds things
class Closure(Term):
    def __init__(self, terms=None):
        self.terms = terms or []
    def __iter__(self):
        return iter(self.terms)
    def __str__(self):
        return "{%s}" % (', '.join(map(str, self.terms)))

class Commutative_set(Closure):
    pass
class PARENTHESIS(Commutative_set):
    def __str__(self):
        return "(%s)" % (', '.join(map(str, self.terms)))
class PRODUCT(Commutative_set):
    def __str__(self):
        return '*'.join(map(str, self.terms))

class NUMBER(Term):
    def __init__(self, number=1):
        self.number = number
    def __str__(self):
        return str(self.number)
class VARIABLE(Term):
    def __init__(self, variable):
        self.variable = variable
    def __str__(self):
        return str(self.variable)

class FUNCTION(Term):
    def __init__(self, name, args=None):
        self.name = name
        self.args = args or []
    def __iter__(self):
        return iter(self.args)
    def __str__(self):
        return f"{self.name}({', '.join(map(str, self.args))})"
class FRACTION(Term):
    def __init__(self, top=None, bottom=None):
        self.top = top or NUMBER()
        self.bottom = bottom or NUMBER()
    def __iter__(self):
        return iter((self.top, self.bottom))
    def __str__(self):
        return f"({self.top})/({self.bottom})"
class EXPONENT(Term):
    def __init__(self, base=None, exp=None):
        self.base = base or NUMBER()
        self.exp = exp or NUMBER()
    def __iter__(self):
        return iter((self.base, self.exp))
    def __str__(self):
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
            if i.name == "SYMBOL" and i.data[0] == ".":
                s += '.'
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
        args = cls.group_by_type(close, "FUNC_ARG")
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
    def parse(cls, comp):
        name, data = comp
        if not name:
            return
            # return Commutative_set(list(map(parse_from_comp, data)))
        if name == "FUNC_CALL":
            return cls.parse_function_call(*data)

if __name__ == "__main__":
    t = r"""f.x_{22}.y_{2dasdds2}\left(2\right)"""
    q = Parser(t)
    print(Comp_Parser(q.data[0]))
    
