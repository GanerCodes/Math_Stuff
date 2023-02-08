from itertools import product
from more_itertools import grouper
from fractions import Fraction

mat = [ [-1,-3,-3],
        [ 2, 6, 1],
        [ 3, 8, 3] ]
l = len(mat)

mat = [[Fraction(o) for o in i] for i in mat]
ident = [*grouper([Fraction(i==o) for i,o in product(range(l), repeat=2)], l)]

mat[1],mat[2]=mat[2],mat[1]
ident[1],ident[2]=ident[2],ident[1]

def dot(A, B):
    return sum(a*b for a,b in zip(A,B))

def mat_mul(a, b):
    return [[dot(a[y], (v[x] for v in b)) for x in range(len(b[0]))] for y in range(len(a))]

# print(mat_mul([[2,6,-2],[1,3,4]],[[2,1],[4,6]]))
print(mat_mul([[1,1],[0,0]],[[-1,-1],[1,1]]))

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
        p(mat)
        print()
    op2(mat, ident, r)

print("Row Echelon form:")
p(mat)
print("Matrix inverse:")
p(ident)