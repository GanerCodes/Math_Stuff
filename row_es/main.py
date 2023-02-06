from fractions import Fraction

mat = [ [3, 2, 4],
        [5, 6, 1],
        [1, 4, 9] ]

mat = [[Fraction(o) for o in i] for i in mat]

def mul_sca(a, s):
    return [i*s for i in a]
def add_arr(a, o, m=1):
    return [i+m*o for i,o in zip(a,o)]

def p(a=mat):
    for i in a:
        for o in i:
            print("%s/%s" % o.as_integer_ratio(), end=' ')
        print()

mat[-1] = add_arr(mat[-1], mat[-2], -(mat[-1][0] / mat[-2][0]))
mat[-2] = add_arr(mat[-2], mat[-1], -(mat[-2][1] / mat[-1][1]))
p()