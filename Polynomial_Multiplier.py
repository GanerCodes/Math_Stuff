s1 = "-2x^5 +-4x^3 -2x 4x^5 8x^3 4x"
s2 = "4x^3 4x"

def fix(e):
    if e[0] == 'x': e = '1' + e
    if 'x' in e:
        if '^' not in e:
            e += "^1"
    else:
        e += "x^0"
    return e

m = {}
r = ""
for i in filter(None, s1.split(' ')):
    for o in filter(None, s2.split(' ')):
        i, o = fix(i), fix(o)
        eq1 = list(map(int, i.split('x^', 1)))
        eq2 = list(map(int, o.split('x^', 1)))
        
        fac = eq1[0] * eq2[0]
        exp = eq1[1] + eq2[1]
        m[exp] = m[exp] + fac if exp in m else fac

r = ' + '.join(f"{v}x^{i}" for i, v in m.items())
r = r.replace("x^0", "").replace("x^1 ", "x").replace('+ -', '- ')

print(r)