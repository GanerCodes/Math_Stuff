⮌ random ⨡ choice
⮌ string ⨡ ascii_lowercase as L
W = open('words.txt').read().split('\n')
U = {Σ(sorted(w))∀w∈W¿w∧🃌(set(w))≡🃌(w)}

freq = ⑴{l:Σ(x.count(l)∀x∈x)∀l∈L}
word_diff=⥌w,f↦Σ(f[l]∀l∈w)
rem=⥌s,w↦{x∀x∈s¿⋀(l∉x∀l∈w)}

⊢ part(u,n=4):
    ¿¬u∨n≤0:↪u
    m = {l:∅∀l∈L}
    ∀w∈u: m[w₀]|={w₁˲}
    ↪ {k:part(v,n-1)∀k,v∈m.items()¿v}

p = part(U)
# pprint(freq(U))

⊢ do(U, l=□):
    l=l∨[]
    ¿¬(sml≔sorted(((a,b)∀a,b∈freq(U).items()¿b>0), key=⑴x₁)): ↪
    sml = sml₀ ₀
    ¿🃌(l)≡4: ☾(sml)
    ∀k∈sorted((rem(U,w)∀w∈U¿sml∈w), key=len, reverse=𝕋):
        do(k, l+[k])
do(U)

# pprint(p)


# ☾⨯([(k,🃌(v))∀k,v∈p['a']['s']['t'].items()])

# ll = {l:{w∀w∈U¿l∈w}∀l∈L}
# 
# ☾(ll)

# {x:{i∀i∈U¿⋀(a≠b∀a,b∈i|ζ|x)} ∀x∈U}