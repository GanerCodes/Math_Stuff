from latex_parse import (parse_latex, compile_latex, Peekable, Holder, LETTERS, NUMBERS, ONE_ARG_FUNCS, TWO_ARG_FUNCS, PSEUDO_CLOSURES, SYMBOL_MAP, BRACKET_PAIRS)

ITER_TYPES = {'int', 'prod', 'sum'}
SPLIT_OPERATORS = set("+-,")
RIGHT_UNARY_OPERATORS = set("!")

def TAKE_ENSURE(content, name):
    assert content and content.peek().name == name
    return content.next()

def TAKE_N(content, N=1):
    return [content.next() for _ in range(N)]

def CHECK_SEQUENCE(content, *names):
    r = []
    for i, n in enumerate(names):
        if q := content.peek(i):
            if (isinstance(n, str) and (n == '*' or n == q.name)) or q.name in n:
                r.append(q)
                continue
            return
        return
    return r

def match_user_function(symb):
    if symb.name == "VARIABLE":
        if symb.data[0].data[0] in {'f', 'g', 'h'}:
            return True

class Parser:
    CHAIN = []
    
    def __init_subclass__(cls):
        Parser.CHAIN.append(cls)
    
    def __new__(cls, data, print_steps=False):
        if cls == Parser:
            if isinstance(data, str):
                data = parse_latex(data)
            for c in Parser.CHAIN:
                data = c(data)
                if print_steps:
                    print(c.__name__, data)
            return data
        
        if not isinstance(data, Peekable):
            data = Peekable(data)
           
        return cls.TOP(data)
    
    def format_args(content, scope):
        if isinstance(content, list):
            content = Peekable(content)
        if scope is None:
            scope = Holder()
        return content, scope
    
    @classmethod
    def PARSE_INNER(cls, cell, func=None, **kwargs):
        if func is None:
            func = cls.TOP
        return Holder(cell.name, func(cell.data, **kwargs).data)
    
    @classmethod
    def TOP(cls, content, scope=None, CHECKERS=None):
        content, scope = cls.format_args(content, scope)
        CHECKERS = CHECKERS or cls.CHECKERS
        
        for name, data in content.peeks():
            for checker in cls.CHECKERS:
                checker = getattr(cls, checker)
                if check := checker(name, data, content):
                    scope += check
                    break
            else:
                scope += content.next()
        
        return scope

class PassZero(Parser):
    @classmethod
    def ITERABLE_CHECKER(cls, name, data, content):
        if name == "ITERABLE":
            content and content.next()
            return Holder(name, [
                data[0],
                cls.PARSE_INNER(data[1]),
                cls.PARSE_INNER(data[2]),
                cls.PARSE_INNER(data[3])])
        
        if not (CHECK_SEQUENCE(content,
            'SYMBOL', 'subscript', 'superscript') \
                and data[0] in ITER_TYPES):
            return
        
        first, lower, upper = TAKE_N(content, 3)
        body = Holder()
        for name, data in content.peeks():
            if name == "RELATION" or (name == "OPERATOR" and data[0] in SPLIT_OPERATORS):
                break
            body += content.next()
        return cls.ITERABLE_CHECKER("ITERABLE", [first, lower, upper, body], None)

    @classmethod
    def VARIABLE_CHECKER(cls, name, data, content):
        if name not in {"VAR", "SYMBOL"}: return
        VARIABLE = Holder("VARIABLE", [content.next()])
        
        if not (r := content.peek()): return VARIABLE
        if r.name == "subscript":
            VARIABLE += content.next()
            if not (r := content.peek()): return VARIABLE
        if r.name == "CLOSURE_SQUARE": # ~
            VARIABLE += content.next()
            if not (r := content.peek()): return VARIABLE
        if r.name == "SYMBOL" and r.data[0] == '.':
            if not (t := content.peek(1)): return VARIABLE
            if t.name in {"VAR", "SYMBOL"}:
                VARIABLE += content.next() # add dot
                VARIABLE += cls.VARIABLE_CHECKER(t.name, t.data, content).data # add the rest
        return VARIABLE
    
    @classmethod
    def FUNC_CHECKER(cls, name, data, content):
        if not (name in ONE_ARG_FUNCS or name in TWO_ARG_FUNCS): return
        
        r = Holder(name)
        for a in content.next().data:
            r += cls.PARSE_INNER(a)
        return r
    
    @classmethod
    def CLOSURE_CHECKER(cls, name, data, content):
        if not (name == '' or name in BRACKET_PAIRS['name']): return
        
        return cls.PARSE_INNER(content.next())
    
    @classmethod
    def SCRIPT_CHECKER(cls, name, data, content):
        if name not in {'subscript', 'superscript'}: return
        
        return cls.PARSE_INNER(content.next())
    
    CHECKERS = ('ITERABLE_CHECKER', 'SCRIPT_CHECKER', 'VARIABLE_CHECKER', 'CLOSURE_CHECKER', 'FUNC_CHECKER')

class DumbFunctionPass(PassZero):
    @classmethod
    def VARIABLE_FUNCTION_CHECKER(cls, name, data, content):
        if name != "FUNCTION": return
        f = content.next()
        if CHECK_SEQUENCE(content, 'subscript', 'superscript'): # why
            return Holder("FUNCEXP", [f] + TAKE_N(content, 2))
        elif CHECK_SEQUENCE(content, 'superscript'):
            return Holder("FUNCEXP", [f, content.next()])
        else:
            return Holder("FUNCEXP", [f])
        
    CHECKERS = ('VARIABLE_FUNCTION_CHECKER', 'ITERABLE_CHECKER', 'CLOSURE_CHECKER', 'FUNC_CHECKER')

# Not doing this, too much weird behavior to be bothered. 
# class SecondDumbImplicitFunctionPass(DumbFunctionPass):
#     @classmethod
#     def IMPLICIT_FUNCTION_ARG_CHECKER(cls, name, data, content):
#         if name != "FUNCEXP": return
#         'FUNCEXP', 'OPERATOR'['-'], 'NUMBER'
#         'FUNCEXP', 'VARIABLE', 'SUPERSCRIPT'
#         'FUNCEXP', 'VARIABLE', 'SUPERSCRIPT'

class FunctionCallPass(DumbFunctionPass):
    @classmethod
    def FUNCTION_CALL_CHECKER(cls, name, data, content):
        if name == "FUNC_CALL":
            content and content.next()
            args = Holder(data[1].name)
            for i in data[1].data:
                if i.name == "FUNC_ARGUMENT":
                    args += cls.PARSE_INNER(i)
                else:
                    args += i
            
            return Holder(name, [data[0], args])
        
        if not (content.peek(1) and content.peek(1).name == "CLOSURE_PARENTHESIS"): return
        
        if name == "FUNCEXP" or match_user_function(content.peek()):
            func, func_params = TAKE_N(content, 2)
            new_params = Holder(func_params.name)
            
            it = Peekable(func_params.data)
            while it:
                buffer = []
                for name, data in it.peeks():
                    if name == "RELATION" and data[0] == ',':
                        break
                    buffer.append(it.next())
                new_params += [Holder("FUNC_ARGUMENT", buffer)]
                if it.peek():
                    new_params += it.next()
            
            return cls.FUNCTION_CALL_CHECKER("FUNC_CALL", [func, new_params], None)
    
    CHECKERS = ('FUNCTION_CALL_CHECKER', 'ITERABLE_CHECKER', 'CLOSURE_CHECKER', 'FUNC_CHECKER', 'VARIABLE_FUNCTION_CHECKER')

class PassOne(FunctionCallPass):
    @classmethod
    def EXPONENT_CHECKER(cls, name, data, content):
        if name == "EXPONENTIAL":
            content and content.next()
            return Holder(name, [cls.PARSE_INNER(i) for i in data])
        
        if not CHECK_SEQUENCE(content, '*', 'superscript'):
            return
        
        base, exp = TAKE_N(content, 2)
        return cls.EXPONENT_CHECKER("EXPONENTIAL", [Holder(data=[base]), exp], None)
    
    CHECKERS = ('EXPONENT_CHECKER', 'ITERABLE_CHECKER', 'CLOSURE_CHECKER', 'FUNC_CHECKER', 'VARIABLE_FUNCTION_CHECKER', 'FUNCTION_CALL_CHECKER')

class PassTwo(PassOne):
    @classmethod
    def RIGHT_UNARY_OPERATOR_CHECKER(cls, name, data, content):
        if name == "RIGHT_UNARY_COUPLE":
            content and content.next()
            return Holder(name, [cls.PARSE_INNER(data[0]), data[1]])
        
        if not (CHECK_SEQUENCE(content, '*', 'OPERATOR') and \
            content.peek(1).data[0] in RIGHT_UNARY_OPERATORS):
            return
        
        arg, op = TAKE_N(content, 2)
        return cls.RIGHT_UNARY_OPERATOR_CHECKER("RIGHT_UNARY_COUPLE", [Holder(data=[arg]), op], None)
    
    CHECKERS = ('RIGHT_UNARY_OPERATOR_CHECKER', 'ITERABLE_CHECKER', 'CLOSURE_CHECKER', 'FUNC_CHECKER', 'VARIABLE_FUNCTION_CHECKER', 'FUNCTION_CALL_CHECKER', 'EXPONENT_CHECKER')

if __name__ == "__main__":
    # t = r"""\frac{1}{n!}\int_{ }^{t}d_{\gamma}\left(t-\gamma\right)^{n}f\left(\gamma\right)"""
    # t = r"""d.x^{2}"""
    # t = r"""\int_{d.x}^{d.y+\int_{0}^{2}\pi d_{\pi}}\ln\left(\left|\lambda^{3^{3\text{hi}}}\right|\right)d_{\lambda}"""
    # t = r"""1x^{2x^{3x^{4x}}}"""
    # t = r"""x^{\frac{1}{2}}"""
    # t = r"""3!"""
    # t = r"""\sin\left(x\right)^{2}"""
    # t = r"""\cos^{2}\left(x\right)"""
    # t = r"""\min\left(a,b,f\left(x\right)^{2},2+\cos\left(2,bx^{2}\right)\right)^{2}"""
    # t = r"""c=\sqrt{\frac{B}{p_{0}\equiv_{\text{density}}}}\text{(B=bulk modulus:}\frac{P}{ΔV\text{/}V}\ _{\text{(Inverse of compression)}}\text{)}"""
    # t = r"""\operatorname{mod}\left(x,2\right)^{2}"""
    # t = r"""f\left(X\right)+\sin\left(x\right)+\cos^{2}\left(x\right)+\operatorname{mod}_{2}^{2}\left(x,2\right)^{2}"""
    # t = r"""f\left(x\right)+\sin\left(x\right)+\operatorname{mod}\left(x,2\right)+\sin^{-1}\left(x\right)+\tan_{2}\left(x\right)+\tan_{2}^{2}\left(x\right)+\operatorname{mod}^{2}\left(x\right)+\operatorname{mod}_{2}^{2}\left(x\right)"""
    # t = r"""f_{2}\left(x\right)"""
    # t = r"""f.x_{22}.y_{2dasdds2}\left(2\right)"""
    # t = r"""\lambda+2"""
    # t = r"""2+\left(f\left(x,y\right)\right)^{2}-5x^{2y+2^{2}}+f\left(x,y\right)"""
    # t = r"""\sqrt{x}+\sqrt[3]{x}"""
    # t = r"""\sin\left(2!,2\right)+\left(\sqrt{x}+\frac{\sqrt[3]{x}}{2}\right)^{2}-2\left(2!\right)\left(x^{y^{z}}\right)!\lambda^{2x\phi}f_{22}.x\left(2\right)"""\
    t = r"""\zeta\left(s\right)=\frac{1}{\Gamma\left(s\right)}\int_{0}^{\infty}\frac{x^{s-1}}{e^{x}-1}dx\zeta\left(s\right)=\frac{1}{\Gamma\left(s\right)}\int_{0}^{\infty}\frac{x^{s-1}}{e^{x}-1}dx\zeta\left(s\right)=\frac{1}{\Gamma\left(s\right)}\int_{0}^{\infty}\frac{x^{s-1}}{e^{x}-1}dx\zeta\left(s\right)=\frac{1}{\Gamma\left(s\right)}\int_{0}^{\infty}\frac{x^{s-1}}{e^{x}-1}dx\zeta\left(s\right)=\frac{1}{\Gamma\left(s\right)}\int_{0}^{\infty}\frac{x^{s-1}}{e^{x}-1}dx\zeta\left(s\right)=\frac{1}{\Gamma\left(s\right)}\int_{0}^{\infty}\frac{x^{s-1}}{e^{x}-1}dx"""
    q = Parser(t, print_steps=True)
    print(q.pretty())
    print(compile_latex(q))