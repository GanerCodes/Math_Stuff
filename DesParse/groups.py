from util import instance_intersection, add_or_ins, find_fixed_point
from abc import ABC, abstractmethod
from copy import deepcopy
from itertools import product

class Var:
    def __init__(self, name):
        self.name = name
    
    def __eq__(self, other):
        return (type(self) == type(other) \
                and self.name == other.name) or \
            self.name == other
    
    def __hash__(self):
        return hash(self.name)
    
    def __repr__(self):
        return f"V[{self.name}]"
    
    def __deepcopy__(self, _=None):
        return type(self)(self.name)

class Number(Var):
    pass

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
    
    def add_content(self, t, n=1):
        pass # TODO xd
    
    def __repr__(self):
        return f'[G{self.__class__.__name__[0].upper()}]({" ".join(f"<{k}:{v}>" for k, v in self.terms.items())})'
    
    def __deepcopy__(self, _=None):
        return type(self)(deepcopy(self.terms))
    
    @abstractmethod
    def operate(n1, n2):
        pass

class Additive(Group):
    IDENTITY = Number(0)
    def operate(n1, n2):
        return n1 + n2

class Product(Group):
    IDENTITY = Number(1)
    def operate(n1, n2):
        return n1 * n2