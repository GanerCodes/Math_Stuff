from string import digits, ascii_uppercase
charset = digits + ascii_uppercase

def normal_from_base(n, b):
    return sum(charset.index(c) * b**i for i, c in enumerate(n[::-1]))
def base_from_normal(n, b):
    r = ''
    while n:
        n, c = divmod(n, b)
        r += charset[c]
    return r[::-1]
def base_convert(n, f, t=10):
    return base_from_normal(normal_from_base(str(n), int(f)), t)

for n, b in [("1011", 2), ("1101110", 2), ("0101011", 2), ("FF1", 16), ("1001", 16), ("5AE", 16)]:
    print(base_convert(n, b))
print()
for n, b in [(56, 2), (502, 2), (4000, 16), (240, 16)]:
    print(base_convert(n, 10, b))
print()
for n in ["10011100", "11110011", "11100011001100011001"]:
    print(base_convert(n, 2, 16))
print()
for n in ["AFE2", "4078"]:
    print(base_convert(n, 16, 2))