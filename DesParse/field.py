from util import instance_intersection
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

class Group(ABC):
    def __init__(self, content=None):
        self.content = content or {}
    
    @classmethod
    def add_content(cls, self, t, n=1):
        if t == self.identity() or n == 0:
            return
        
        if isinstance(t, cls):
            for k, v in t:
                self.add_content(k, v)
        
        if t in self.content:
            self.content[t] += n
        else:
            self.content[t] = n
    
    def __iter__(self):
        return iter(self.content.items())
    
    @abstractmethod
    def identity(self):
        pass
    
    @classmethod
    def __eq__(cls, self, other):
        return instance_intersection(cls, self, other) and \
            self.content == other.content
    
    def __hash__(self):
        return 0

class Additive(Group):
    def identity(self):
        return 0

class Product(Group):
    def identity(self):
        return 1