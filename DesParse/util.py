from types import UnionType
from typing import Union
from copy import deepcopy

class Njective_static_map:
    def __init__(self, types, data):
        self.mappings = {i: {} for i in types}
        for entry in data:
            entry = dict(zip(types, entry))
            for k, v in entry.items():
                self.mappings[k][v] = entry
    
    def __getitem__(self, i):
        return self.mappings[i]

class Holder:
    def __init__(self, name="", data=None, *, hide_data=False):
        self.name = name
        self.data = data or []
        self.hide_data = hide_data
    def __iadd__(self, other):
        if isinstance(other, list):
            self.data += other
        else:
            self.data.append(other)
        return self
    def __iter__(self):
        return iter((self.name, self.data))
    def __len__(self):
        return len(self.data)
    def __getitem__(self, i):
        return self.data[i]
    def __repr__(self):
        return f"{self.name or '*'}[{', '.join(map(str, self.data))}]"
    def __str__(self):
        return repr(self)
    def __bool__(self):
        return True
    def __eq__(self, other):
        if type(self) != type(other): return
        if isinstance(self, str): return self == other
        if (self.name != other.name) or (len(self.data) != len(other.data)): return
        return all(A == B for A, B in zip(self.data, other.data))
    def __hash__(self):
        return hash((self.name, len(self.data))) # meh
    def pretty(self, q=0):
        t, r = ('  '*(q + 1)), f"{self.name or '*'}["
        if self.hide_data:
            r += "..."
        else:
            if self.name == "TEXT":
                r += f'"{self.data[0]}"'
            elif len(self.data) > 1:
                for a in self.data:
                    r += f"\n{t}{a.pretty(q+1) if isinstance(a, Holder) else a}"
            elif len(self.data):
                a = self.data[0]
                r += f"{a.pretty(q+1) if isinstance(a, Holder) else a}"
        return r + ']'

class Peekable:
    def __init__(self, s):
        self.s = s
    def __str__(self):
        return str(self.s)
    def __len__(self):
        return len(self.s)
    def __bool__(self):
        return bool(len(self))
    def next(self):
        if not len(self.s): return
        r, self.s = self.s[0], self.s[1:]
        return r
    def peek(self, n=0):
        if len(self.s) <= n: return
        return self.s[n]
    def peeks(self):
        while len(self):
            yield self.peek()
    def nexts(self):
        while len(self):
            yield self.next()

def add_or_ins(d: dict, v: object, n: int=1):
    if v in d:
        d[v] += n
    else:
        d[v] = n

def instance_intersection(cls, *terms):
    # int, 4, 4.4 🠒 False
    # float|int, 4, 4.4 🠒 False
    # int|str, 4, 5 🠒 int
    # (class Egg(str)) Egg|str|float, egg1, egg2 🠒 Egg|str
    if isinstance(cls, UnionType):
        r = tuple(t for t in cls.__args__ if instance_intersection(t, *terms))
        if not r:
            return False
        if len(r) == 1:
            return r[0]
        return Union(r)
    elif all(isinstance(t, cls) for t in terms):
        return cls
    return False

def find_fixed_point(obj, func):
    while True:
        old_obj = deepcopy(obj)
        obj = func(obj)
        if old_obj == obj:
            return obj