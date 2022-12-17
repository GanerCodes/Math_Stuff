from util import instance_intersection, add_or_ins
from abc import ABC, abstractmethod
from copy import deepcopy

class Var:
    def __init__(self, name):
        self.name = name
    
    def __eq__(self, other):
        return type(self) == type(other) and \
            self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __repr__(self):
        return f"V[{self.name}]"
    
    def __deepcopy__(self, _=None):
        return type(self)(self.name)

class Function:
    def __init__(self, name, terms=None):
        self.name = name
        self.terms = terms or None
    
    def __iter__(self):
        return iter(self.terms)
    
    def __eq__(self, other):
        return type(self) == type(other) and \
            self.name == other.name and self.terms == other.terms
    
    def __hash__(self):
        return hash(self.name)
    
    def __repr__(self):
        return f"F[{self.name}]({', '.join(map(str, self))})"
    
    def __deepcopy__(self, _=None):
        return type(self)(self.name, deepcopy(self.terms))

class Group(ABC):
    def __init__(self, terms=None):
        self.terms = {}
        if terms:
            self.add_content(terms)
    
    def __iter__(self):
        return iter(self.terms.items())
    
    def __len__(self):
        return len(self.terms)
    
    def __eq__(self, other):
        return type(self) == type(other) and \
            self.terms == other.terms
    
    def __hash__(self):
        return 0
    
    def add_content(self, t, n=1): # dfuyasdhisad
        cls = type(self)
        if t == cls.IDENTITY or n == 0:
            return
        
        if isinstance(t, cls):
            if len(t) == 1:
                i, n2 = (*t.terms.items(), )[0]
                self.add_content(i, self.operate(n, n2))
                return
            add_or_ins(self.terms, t, n)
            return
        
        if isinstance(t, dict):
            for i, n2 in t.items():
                self.add_content(i, v * n)
            return
        
        add_or_ins(self.terms, t, n)
    
    def __repr__(self):
        return f'[G-{self.__class__.__name__[0].upper()}]({", ".join(f"<{k}: {v}>" for k, v in self.terms.items())})'
    
    def __deepcopy__(self, _=None):
        return type(self)(deepcopy(self.terms))
    
    @abstractmethod
    def operate(n1, n2):
        pass

class Additive(Group):
    IDENTITY = 0
    def operate(n1, n2):
        return n1 + n2

class Product(Group):
    IDENTITY = 1
    def operate(n1, n2):
        return n1 * n2

# 1/(x+5)^2
j = Product({
    Var("1"): 1,
    Product({
        Additive({
            Var("x"): 1,
            Var("1"): 5
        }): 2
    }): -12
})
print(j)