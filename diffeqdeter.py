from math import *
import random

eqs="""
x**-0.5 x**-1
-0.5*x**-1.5 -x**-2
"""

class Eq:
    def __init__(self, s):
        self.s = s
    def __len__(self):
        return len(self.s)
    def __mul__(self, v):
        return Eq(f'(({v})*({self.s}))')
    def __add__(self, v):
        return Eq(f'(({v})+({self.s}))')
    def __repr__(self):
        return self.s

eqs = (λt((λt(x.strip()) | λf(x) | λt(Eq(x)))(x.split(' '))) | λf(x))(eqs.split('\n'))

sum = λ(λ(reduce(λ(x+y),x) if len(x) else 0)(list(x)))

def det(a):
    return a[0][0] if len(a) == 1 else sum(det([[v for c,v in enumerate(r) if c!=i] for r in a[1:]])*(m * [1,-1][i%2]) for i,m in enumerate(a[0]))

d = det(eqs)
print(d)
print("Is unique/linearly independent:", all(λt(abs((x⟨random.random()⟩, eval(str(d)))[1])<0.0001)(Δ[1:25])))




# print(eval(det(eqs), globals={'x': 5}))

# print(det([
#     [1,3,1,4],
#     [3,9,5,15],
#     [0,2,1,1],
#     [0,4,2,3]
# ]))

# mulsym = λ(λ('*'.join(x))(λt(f'({x})')(x)))
# det2 = λ(f"({g⟨λt(mulsym(x))(x)⟩[0]})-({g[1]})")

# # WRONG
# det3 = λ(f"(({x[0][0]})*({det2([[x[1][1],x[1][2]],[x[2][1],x[2][2]]])}))-\
# (({x[1][0]})*({det2([[x[1][0],x[1][2]],[x[2][0],x[2][2]]])}))-\
# (({x[2][0]})*({det2([[x[1][0],x[1][1]],[x[2][0],x[2][1]]])}))")

# # print(det2(eqs))

# print(det3(eqs))