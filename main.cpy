⮌ itertools ⨡ groupby as Gb
spl = ⑵[⚇⨯g ∀k,g∈Gb(x,⑴x≡y)¿¬k]

⊢ a_cy(d, c):
    e = d.copy()
    ∀i∈0…(j≔🃌(c)):
        e[c[(i+1)%j]]=d[c[i]]
    ↪ e
⊢ decomp(⠤𝔸):
    𝔸,i,c = ⚇⨯𝔸,0,[]
    ➰𝕋:
        ¿i∉c:
            c,i = c+[i], 𝔸[i]
            ↺
        c+=∣❟
        ∀n,e∈↨⨯𝔸:
            ¿e∈c: ↺
            i=n ; ⇥
        ¡: ⇥ ; ↺
    ↪ spl(c, ∣❟)

cls P:
    __init__ = 𝕊↦σ❟|🜌(𝕊)|[𝔸]
    __mul__ = 𝕊,o↦P(⠤🢖σ+o.σ)
    __neg__ = 𝕊↦P(⠤(c˲˲₋₁∀c∈🢖σ))
    ⊢ __call__(𝕊, ⠤d):
        e = ⚇(d)
        ∀c∈🢖σ:
            e = a_cy(e, c)
        ↪ e

σ = P(0⋄1⋄2)
τ = P(0⋄1⋄3⋄2)

☾⨯Σ('abcd'[i]∀i∈(↕⨯4⨯⚇))
☾⨯Σ('abcd'[i]∀i∈(τ)(⠤↕⨯4⨯⚇))
☾⨯Σ('abcd'[i]∀i∈(τ⨯σ)(⠤↕⨯4⨯⚇))
☾⨯Σ('abcd'[i]∀i∈(τ⨯σ⨯-τ)(⠤↕⨯4⨯⚇))