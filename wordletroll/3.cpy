⮌ string ⨡ ascii_lowercase as L
⮌ random ⨡ choice as ch
fs = frozenset
W = open('words.txt').read().split('\n')
U = fs({Σ(sorted(w))∀w∈W¿w∧🃌(fs(w))≡🃌(w)})

cls MAN:
    ⊢ __init__(𝕊, U):
        🢖U,🢖C = U,{}
        ∀w∈U:
            ∀l∈w:
                ¿l∈🢖C: 🢖C[l]|={w}
                ¡: 🢖C[l]={w}
        🢖O = sorted(🢖U, key=🢖cac)
    __call__ = 𝕊,w↦🢖U-set.union(⠤(🢖C[l]∀l∈w))
    cac = 𝕊,st↦Σ(🃌(🢖C[l])∀l∈st)
    first = 𝕊↦{🢖O₀}¿🢖O¡□

⊢ K_N(g, n, I):
    ¿n≡1:↪g.first()
    ¿🃌(g.O)<n֎-1֎:↪
    ∀v∈g.O:
        ¿(G≔K_N(MAN(g(v)),n-1,I))∧(((s≔{v}.union(G))-I)∨🃌(s)≠5): ↪s
mp = {Σ(sorted(w)):w∀w∈W}

S,I = U,∅
➰𝕋:
    ☾⨯🃌(set(Σ(☾⨯{mp[Σ(sorted(w))]∀w∈(m≔K_N(MAN(S),5,I))})))
    I = I.union(m)