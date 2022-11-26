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
    def __init__(self, name, data=None):
        self.name = name
        self.data = data or []
    def __iadd__(self, other):
        if isinstance(other, list):
            self.data += other
        else:
            self.data.append(other)
        return self
    def __str__(self):
        return f"{self.name}[{', '.join(map(str, self.data))}]"

ONE_CHAR_BINARY_OP = set("+-")
SPECIAL_SYMBOLS = {'lambda', 'aleph', 'circ'} # add more
# integrals are weird, not a multi arg function but just a symbol that has a superscript and subscript
BINARY_OPERATORS = {'pm', 'cdot', 'mp', 'times', 'div', 'ast',
    'star', 'oplus', 'ominus', 'otimes', 'oslash', 'odot', 'int'}
ONE_ARG_FUNCS = {'overline', 'underline', 'operatorname', 'sqrt'} # add more
TWO_ARG_FUNCS = {'frac', 'binom'} # add more
NUMBERS = set("0123456789")
LETTERS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
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
            buf = (buf or "0") + content.next()
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
    return Holder(name, [func(content, Holder("PARAM")) for _ in range(N)])
# we assume curly wrapping, unless alternate_exit is specified, which it will search for a special exit word
def TOP(content, contain_scope, alternate_exit=None):
    if alternate_exit is None:
        assert content.next() == '{' # throws out opening curly
    
    while c := content.peek():
        if c in ONE_CHAR_BINARY_OP:
            contain_scope += Holder("BINARY_OP", [content.next()])
            continue
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
            word = SCAN_WORD(content)
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
            if word in BINARY_OPERATORS:
                contain_scope += Holder("BINARY_OP", [word])
                continue
            if word in SPECIAL_SYMBOLS:
                contain_scope += Holder("SYMBOL", [word])
                continue
            if word in ONE_ARG_FUNCS:
                contain_scope += N_ARG_GENERATOR(word, 1, content, TOP)
                continue
            if word in TWO_ARG_FUNCS:
                contain_scope += N_ARG_GENERATOR(word, 2, content, TOP)
                continue
            contain_scope += Holder("FUNCTION", [word])
            continue
        if c == ',':
            contain_scope += Holder("COMMA", [content.next()])
            continue
        if c == ' ':
            content.next() # throw away space
            continue
        if c == '}':
            assert not alternate_exit # we found a closing curly when not looking for one
            content.next() # throws out closing curly
            break
        
        raise NotImplementedError(f'Unable to parse symbol "{c}"')
    
    return contain_scope

# t = r"""r"2\cdot2+2-x_{2}\ast2^{2}")"""
# t = r"""-\int_{ }^{ }\frac{1}{x\sqrt{1-x^{2}}}d_{x}\circ\cos\left(x\right)"""
# t = r"""\overline{dasdasd}"""
t = r"""\int_{ }^{ }-\frac{x}{\sqrt{1-x^{2}}}\frac{1}{\sqrt{1-x^{2}}\sqrt{1-\left(\sqrt{1-x^{2}}\right)^{2}}}d_{x}"""

scope = Holder("MAIN", [])
TOP(Peekable_str(t), scope, '')
print(scope)