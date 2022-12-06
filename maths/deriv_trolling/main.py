from math import *
from numpy import arange
from functools import reduce
from scipy.special import gamma

def op_integ(f, delta=0.000025):
    def g(a, b):
        return sum(delta * f(x) for x in arange(a, b, delta))
    return g

def op_deriv(f, delta=0.000001):
    def g(x):
        return (f(x + delta) - f(x)) / delta
    return g

def op_differgral(f, q):
    """ n = ceil(q)
    
    base_deriv = f
    for _ in range(n):
        base_deriv = op_deriv(f)
    
    def g(a, b):
        def Q(x):
            return base_deriv(x) / pow(b - x, q - n + 1)
        return op_integ(Q)(a, b) / gamma(n - q)
    
    return g """
    
    def g(a, b):
        def Q(x):
            return pow(b - x, q - 1) * f(x)
        return op_integ(Q)(a, b) / gamma(q)
    
    return g

def f(x):
    return sin(x)

import matplotlib.pyplot as plt
x = tuple(arange(0, 2 * pi, 0.02))
y = tuple(map(lambda x: op_differgral(f, x)(0, x), x))
plt.plot(x, y)
plt.show()