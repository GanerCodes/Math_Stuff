from util import instance_intersection, add_or_ins
from abc import ABC, abstractmethod

class Var:
    def __init__(self, name):
        self.name = name
    
    @classmethod
    def __eq__(cls, self, other):
        return instance_intersection(cls, self, other) and \
            self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __str__(self):
        return f"V[{self.name}]"

class Function:
    def __init__(self, name, terms=None):
        self.name = name
        self.terms = terms or None
    
    def __iter__(self):
        return iter(self.terms)
    
    def __eq__(self, other):
        return self.name == other.name and self.terms == other.terms
    
    def __hash__(self):
        return hash(self.name)
    
    def __repr__(self):
        return f"F[{self.name}]({', '.join(map(str, self))})"

class Group(ABC):
    def __init__(self, content=None):
        self.content = content or {}
    
    def __iter__(self):
        return iter(self.content.items())
    
    @classmethod
    def __eq__(cls, self, other):
        return instance_intersection(cls, self, other) and \
            self.content == other.content
    
    def __hash__(self):
        return 0
    
    @classmethod
    def add_content(cls, self, t, n=1):
        if t == self.identity() or n == 0:
            return
        
        if isinstance(t, cls):
            for k, v in t:
                self.add_content(k, v)
            return
        
        add_or_ins(self.content, t, n)
    
    @abstractmethod
    def identity(self):
        pass
    
    def __repr__(self):
        return f'[G-{self.__class__.__name__[0].upper()}]({", ".join(f"<{k}: {v}>" for k, v in self.content.items())})'

class Additive(Group):
    def identity(self):
        return 0

class Product(Group):
    def identity(self):
        return 1

print(Product({2: 1, 3: -1}))