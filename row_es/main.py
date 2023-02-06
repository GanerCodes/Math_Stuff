from itertools import product
from more_itertools import grouper
from fractions import Fraction

mat = [ [3, 2, 4, 3],
        [5, 6, 1, 5],
        [1, 4, 9, 2] ]
l = len(mat)

mat = [[Fraction(o) for o in i] for i in mat]
ident = [*grouper([Fraction(i==o) for i,o in product(range(l), repeat=2)], l)]
def mul_sca(a, s):
    return [i*s for i in a]
def add_arr(a, o, m=1):
    return [i+m*o for i,o in zip(a,o)]

def p(a=mat):
    for i in a:
        for o in i:
            print("%s/%s" % o.as_integer_ratio(), end='\t')
        print()

def op1(mat, ident, c, r):
    j = -mat[c][r]/mat[r][r]
    mat[c] = add_arr(mat[c], mat[r], j)
    ident[c] = add_arr(ident[c], ident[r], j)
def op2(mat, ident, r):
    j = 1/mat[r][r]
    mat[r] = mul_sca(mat[r], j)
    ident[r] = mul_sca(ident[r], j)

for r in range(l):
    row = mat[r]
    m = row[r]
    for c in range(l):
        if c == r:
            continue
        op1(mat, ident, c, r)
    op2(mat, ident, r)

print("Row Echelon form:")
p(mat)
print("Matrix inverse:")
p(ident)