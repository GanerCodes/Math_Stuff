def convertNoParentheses(s):
    s = s.replace(' ', '').replace('||', '|').replace('&&', '&')
    buf = ""
    final = "#"
    for i, c in enumerate(s):
        if c in "&|^":
            final = final.replace('#', buf)
            if c == '&':
                final = f"max({final}, #)"
            elif c == '|':
                final = f"min({final}, #)"
            elif c == '^':
                final = f"(({final}) * (#))"
            buf = ''
        else:
            buf += c
    final = final.replace('#', buf).replace('!', '-')
    return final

def convert(s):
    s = s.replace(' ', '')
    n = 0
    buf = ''
    final = ''
    l = []
    
    if not ('(' in s or ')' in s):
        return convertNoParentheses(s)
    
    for i, c in enumerate(s):
        if c == '(':
            n += 1
        elif c == ')':
            n -= 1
            if n == 0:
                final += f"[[{len(l)}]]"
                l.append(convert(buf))
                buf = ''
        elif n > 0:
            buf += c
        elif n == 0:
            final += c
    
    final = convertNoParentheses(final)
    
    for i, v in enumerate(l):
        final = final.replace(f"[[{i}]]", v)
    return final

if __name__ == '__main__':
    equation = "!a && b || !(c ^ d)"
    print(convert(equation))