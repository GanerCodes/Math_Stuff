from string import digits, ascii_uppercase
charset = digits + ascii_uppercase

def normal_from_base(n, b):
    r = 0
    Q = ''
    for i, c in enumerate(n[::-1]):
        Q += f'{charset.index(c)}*{b}^{i}+'
        r += charset.index(c) * b**i
    print(end=Q[:-1])
    return r
def base_from_normal(n, b):
    r = ''
    Q = ''
    while n:
        Q += f"{n}/{b}=%sr%s⇒"%divmod(n, b)
        n, c = divmod(n, b)
        r += charset[c]
    print(end=Q[:-1])
    return r[::-1]
def base_convert(n, f, t=10):
    print(end=f'{f}→{t} "{n}": ')
    if f != 10:
        n = normal_from_base(str(n), int(f))
    if t != 10:
        if f != 10:
            print(end=f" = {n} ⭢ ")
        n = base_from_normal(n, t)
    print(f" = {n}")
    return n

for n, b in [("1011", 2), ("1101110", 2), ("0101011", 2), ("FF1", 16), ("1001", 16), ("5AE", 16)]:
    (base_convert(n, b))
print()
for n, b in [(56, 2), (502, 2), (4000, 16), (240, 16)]:
    (base_convert(n, 10, b))
print()
for n in ["10011100", "11110011", "11100011001100011001"]:
    (base_convert(n, 2, 16))
print()
for n in ["AFE2", "4078"]:
    (base_convert(n, 16, 2))