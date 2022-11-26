from latex_parse import *

class Peekable_holding_sequence(Peekable_str):
    pass

def abstract_parse(s: Holder):
    content = Peekable_holding_sequence(s.data)

if __name__ == "__main__":
    t = r"""\frac{1}{n!}\int_{ }^{t}d_{\gamma}\left(t-\gamma\right)^{n}f\left(\gamma\right)"""
    print(abstract_parse(parse_latex(t)))