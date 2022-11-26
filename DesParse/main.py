class Njective_static_map:
    def __init__(self, types, data):
        self.mappings = {i: {} for i in types}
        for entry in data:
            entry = dict(zip(types, entry))
            for k, v in entry.items():
                self.mappings[k][v] = entry
    
    def __getitem__(self, i):
        return self.mappings[i]

class Peekable_str:
    def __init__(self, s):
        self.s = s
    def __str__(self):
        return self.s
    def next(self):
        if not len(self.s): return
        r, self.s = self.s[0], self.s[1:]
        return r
    def peek(self):
        if not len(self.s): return
        return self.s[0]

class Holder:
    def __init__(self, name="", data=None):
        self.name = name
        self.data = data or []
    def __iadd__(self, other):
        if isinstance(other, list):
            self.data += other
        else:
            self.data.append(other)
        return self
    def __iter__(self):
        return iter((self.name, self.data))
    def __repr__(self):
        return f"{self.name}[{', '.join(map(str, self.data))}]"
    def __str__(self):
        return repr(self)

LETTERS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
NUMBERS = set("0123456789")
ONE_CHAR_OPERATOR = set("+-")
ONE_CHAR_RELATION = set("=<>")
ONE_CHAR_SYMBOLS = set(",':;|@&#!\"")
OPERATORS = {'pm', 'cdot', 'mp', 'times', 'div', 'ast', 'star', 'oplus', 'ominus', 'otimes', 'oslash', 'odot'}
RELATIONS = {'ge', 'le', 'equiv', 'cong', 'gg', 'll', 'doteq', 'sim', 'simeq', 'approx', 'ne'}
SYMBOLS = {'int', 'sum', 'prod', 'Gamma', 'implies', 'Delta', 'Lambda', 'Phi', 'Pi', 'Psi', 'Sigma', 'Theta', 'Upsilon', 'Xi', 'Omega', 'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega', 'digamma', 'varepsilon', 'varkappa', 'varphi', 'varpi', 'varrho', 'varsigma', 'vartheta', 'aleph', 'beth', 'daleth', 'gimel', 'complement', 'ell', 'eth', 'hbar', 'hslash', 'mho', 'partial', 'wp', 'circledS', 'Bbbk', 'Finv', 'Game', 'Im', 'Re', 'aleph', 'beth', 'daleth', 'gimel', 'complement', 'ell', 'eth', 'hbar', 'hslash', 'mho', 'partial', 'wp', 'circledS', 'Bbbk', 'Finv', 'Game', 'Im', 'Re', 'aleph', 'beth', 'daleth', 'gimel', 'complement', 'ell', 'eth', 'hbar', 'hslash', 'mho', 'partial', 'wp', 'circledS', 'Bbbk', 'Finv', 'Game', 'Im', 'Re', 'aleph', 'beth', 'daleth', 'gimel', 'complement', 'ell', 'eth', 'hbar', 'hslash', 'mho', 'partial', 'wp', 'circledS', 'Bbbk', 'Finv', 'Game', 'Im', 'Re', 'triangle', 'triangledown', 'sharp', 'infty', 'diamondsuit', 'bigstar', 'blacksquare', 'blacktriangle', 'blacktriangledown', 'varnothing', 'backslash', '#', '$', '&'}
ONE_ARG_FUNCS = {'overline', 'underline', 'operatorname', 'sqrt'} # add more
TWO_ARG_FUNCS = {'frac', 'binom', 'sqrt'} # add more
BRACKET_PAIRS = Njective_static_map(
    ("name", "left", "right"),
    (('CLOSURE_CURLY'      , '{'     , '}'),
     ('CLOSURE_SQUARE'     , '['     , ']'),
     ('CLOSURE_PARENTHESIS', '('     , ')'),
     ('CLOSURE_VERT'       , '|'     , '|'),
     ('CLOSURE_ANGLE'      , 'langle', 'rangle'),
     ('CLOSURE_DBL_VERT'   , 'lVert' , 'rVert')))

def SCAN_WORD(content):
    buf = ""
    while c := content.peek():
        if c not in LETTERS:
            while s := content.peek(): # loop to remove spaces
                if s != ' ':
                    break
                content.next()
            break
        buf += content.next()
    return buf

def SCAN_NUMBER(content):
    buf, has_decimal = "", False
    while c := content.peek():
        if c in NUMBERS:
            buf += content.next()
        elif c == '.':
            assert not has_decimal # implies badly formatted number, ex. .1. or 1.2.
            buf += content.next()
            has_decimal = True
        else:
            break
    return Holder("NUMBER", [buf])

def SCAN_VARIABLE(content):
    # technically two implmentations can be done here, ill use the one latex wants me to use but multi-letter variable names could be implemented here
    assert content.peek() in LETTERS
    return Holder("VARIABLE", [content.next()])

# creates a scope that automatically collects N latex args
def N_ARG_GENERATOR(name, N, content, func):
    return Holder(name, [func(content, Holder()) for _ in range(N)])

# we assume curly wrapping, unless alternate_exit is specified, which it will search for a special exit word
# also, operators like nthroot are formated like "\sqrt[]{}", for some reason
def TOP(content, contain_scope, alternate_exit=None, scanpair='{}'):
    if alternate_exit is None:
        assert content.next() == scanpair[0] # throws out opening
    
    while c := content.peek():
        if c in NUMBERS or c == '.':
            contain_scope += SCAN_NUMBER(content)
            continue
        if c in LETTERS:
            contain_scope += SCAN_VARIABLE(content)
            continue
        if c == '_':
            content.next() # throw away delimiter
            contain_scope += TOP(content, Holder("subscript"))
            continue
        if c == '^':
            content.next() # throw away delimiter
            contain_scope += TOP(content, Holder("superscript"))
            continue
        if c == '\\':
            content.next() # throws out backslash (delimiter)
            word = SCAN_WORD(content).lstrip()
            
            if not word: # literally just space
                continue
            
            if word in {'left', 'right'}:
                if content.peek() == '\\':
                    follow = SCAN_WORD(content)
                else:
                    follow = content.next()
                
                if word == 'left':
                    closure = BRACKET_PAIRS['left'][follow]
                    contain_scope += TOP(content, 
                        Holder(closure['name']),
                        alternate_exit=closure['right'])
                    continue
                if word == 'right':
                    assert alternate_exit and (follow == alternate_exit)
                    break
            if word in OPERATORS:
                contain_scope += Holder("OPERATOR", [word])
                continue
            if word in SYMBOLS:
                contain_scope += Holder("SYMBOL", [word])
                continue
            if word in RELATIONS:
                contain_scope += Holder("RELATION", [word])
                continue
            if word in ONE_ARG_FUNCS and word in TWO_ARG_FUNCS and content.peek() == '[':
                contain_scope += Holder(word, [
                    TOP(content, Holder(), scanpair='[]'),
                    TOP(content, Holder())])
                continue
            if word in ONE_ARG_FUNCS:
                contain_scope += N_ARG_GENERATOR(word, 1, content, TOP)
                continue
            if word in TWO_ARG_FUNCS:
                contain_scope += N_ARG_GENERATOR(word, 2, content, TOP)
                continue
            
            contain_scope += Holder("FUNCTION", [word])
            continue
        if c in ONE_CHAR_OPERATOR:
            contain_scope += Holder("OPERATOR", [content.next()])
            continue
        if c in ONE_CHAR_SYMBOLS:
            contain_scope += Holder("SYMBOL", [content.next()])
            continue
        if c in ONE_CHAR_RELATION:
            contain_scope += Holder("RELATION", [content.next()])
            continue
        if c == ' ':
            content.next() # throw away space
            continue
        if c == scanpair[1]:
            assert not alternate_exit # we found a closing when not looking for one
            content.next() # throws out closing
            break
        
        raise NotImplementedError(f'Unable to parse symbol "{c}"')
    
    return contain_scope

def parse_latex(s):
    return TOP(Peekable_str(s), Holder(), '')

def compile_latex(s):
    if isinstance(s, Holder):
        name, args = s
    else:
        name, args = '', s
    
    args = [compile_latex(i) if isinstance(i, Holder) else i for i in args]
    if not name:
        r = ""
        for a in args:
            if r and r[-1] in LETTERS and a and a[0] in LETTERS:
                r += ' '
            r += a
        return r
    
    if name == "NUMBER" or name == "VARIABLE":
        return args[0]
    if name == "FUNCTION":
        return f"\\{args[0]}"
    if name == "superscript":
        return "^{%s}" % compile_latex(args)
    if name == "subscript":
        return "_{%s}" % compile_latex(args)
    if name == "OPERATOR":
        if args[0] in ONE_CHAR_OPERATOR:
            return args[0]
        else:
            return f"\\{args[0]}"
    if name == "RELATION":
        if args[0] in ONE_CHAR_RELATION:
            return args[0]
        else:
            return f"\\{args[0]}"
    if name == "SYMBOL":
        if args[0] in ONE_CHAR_SYMBOLS:
            return args[0]
        else:
            return f"\\{args[0]}"
    
    if name in BRACKET_PAIRS['name']:
        pair = BRACKET_PAIRS['name'][name]
        sp = ' ' if len(pair['left']) > 1 else ''
        return f"\\left{pair['left']}{sp}{compile_latex(args)}\\right{pair['right']}{sp}"
    
    A = name in ONE_ARG_FUNCS
    B = name in TWO_ARG_FUNCS
    if A or B:
        if len(args) == 2:
            if A and B:
                return "\\%s[%s]{%s}" % (name, *args)
            if B:
                return "\\%s{%s}{%s}" % (name, *args)
        else:
            return "\\%s{%s}" % (name, *args)
    
    raise NotImplementedError(f'Unable to parse type "{name}"')

# t = r"""r"2\cdot2+2-x_{2}\ast2^{2}")"""
# t = r"""-\int_{ }^{ }\frac{1}{x\sqrt{1-x^{2}}}d_{x}\circ\cos\left(x\right)"""
# t = r"""\overline{dasdasd}"""
# t = r"""\int_{ }^{ }-\frac{x}{\sqrt{1-x^{2}}}\frac{1}{\sqrt{1-x^{2}}\sqrt{1-\left(\sqrt{1-x^{2}}\right)^{2}}}d_{x}"""
# t = r"""x=-1:\ A=-\frac{1}{2}"""
# t = r"""\frac{1}{2}\left(x-\frac{1}{4}\ln\left(\frac{\left|-1+\sin\left(2x\right)\right|}{\left|1+\sin\left(2x\right)\right|}\right)\right)"""
# t = r"""f\left(x,y\right)=-\max\left(-\left(\left(0.4\left(x+2.5\right)\right)^{2}+10\left(2\left(y-0.6\right)+\frac{\sin\left(4\left(2x+2\right)\cdot0.4\right)}{4}\right)^{2}-1\right),-\left(\left(x-1.7\right)^{2}+\left(y-2.2-\frac{\sin\left(\left|x-2.3\right|\right)}{2}\right)^{2}-1\right),-\min\left(\min\left(\left(\left|2\left(y+3.5\right)+\left|\left(x-2.5\right)\right|\right|+\left|\left(x-2.5\right)\right|-1\right),\max\left(0.8\left|\left(x-2.5\right)\right|,0.15\left|\left(y+3.5\right)-2\right|\right)-0.3\right),\min\left(\left(\left|2\left(y+4\right)+\left|\left(x-\frac{2.9}{3}\right)\right|\right|+\left|\left(x-\frac{2.9}{3}\right)\right|-1\right),\max\left(0.8\left|\left(x-\frac{2.9}{3}\right)\right|,0.15\left|\left(y+4\right)-2\right|\right)-0.3\right),\min\left(\left(\left|2\left(y+4\right)+\left|\left(x+2.5\right)\right|\right|+\left|\left(x+2.5\right)\right|-1\right),\max\left(0.8\left|\left(x+2.5\right)\right|,0.15\left|\left(y+4\right)-2\right|\right)-0.3\right),\min\left(\left(\left|2\left(y+3.5\right)+\left|\left(x+\frac{2.9}{3}\right)\right|\right|+\left|\left(x+\frac{2.9}{3}\right)\right|-1\right),\max\left(0.8\left|\left(x+\frac{2.9}{3}\right)\right|,0.15\left|\left(y+3.5\right)-2\right|\right)-0.3\right)\right),-\left(0.3x^{2}+0.25y^{4}-2^{2}\right),-\left(\left(x-3\right)^{2}+\left(y-0.5-\frac{x}{3}\right)^{2}-3\right)\left(\left(x-3.6\right)^{2}+\left(y-2.75\right)^{2}-0.3^{2}\right),-\left(0.2\left(x-5.8\right)^{2}+\left(3\left(y-\frac{x}{3}-1\right)+\sin\left(2x\right)\right)^{2}-0.75\right)\right)-0.08"""
# t = r"""\sqrt[5]{x}"""
# t = r"""!das\backslash d\cdot\&"""
# t = r"""\int_{0^{-1}}^{x^{x^{x^{x^{x\sum_{n=0}^{10}n}}}}}x_{d}"""
# t = r"""\sqrt[\sqrt{2}]{2^{e^{\ln\left(2\right)}}}"""
# t = r"""\max\left(\left|x-p.x\right|,\left|y-p.y\right|\right)\le1"""
# t = r"""\left(-1\right)^{k}\int_{ }^{\lambda}d_{\gamma}f_{k}\left(\gamma\right)\left(\frac{d^{k}}{d\gamma^{k}}\left(\lambda-\gamma\right)^{n}\right)"""
# t = r"""\frac{1}{n!}\int_{ }^{t}d_{\gamma}\left(t-\gamma\right)^{n}f\left(\gamma\right)"""
t = r"""t\left(x,y,a,a_{x},a_{y},s_{x},s_{y}\right)=\left(\frac{\cos\left(a\right)\left(x-a_{x}\right)+\sin\left(a\right)\left(y-a_{y}\right)}{s_{x}},\frac{\cos\left(a\right)\left(y-a_{y}\right)-\sin\left(a\right)\left(x-a_{x}\right)}{s_{y}}\right)"""

r = parse_latex(t)
print(r)
print(compile_latex(r))