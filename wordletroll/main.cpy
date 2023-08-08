⮌ random ⨡ choice
⮌ string ⨡ ascii_lowercase as L
W = open('words.txt').read().split('\n')
U = [w∀w∈W¿w∧🃌(set(w))≡🃌(w)]

freq = ⑴{l:Σ(x.count(l)∀x∈x)∀l∈L}
word_diff=⥌w,f↦Σ(f[l]∀l∈w)

➰𝕋:
    WORDS = []
    t = U.copy()
    ∀x∈↕⨯5:
        F = freq(t)
        wrds = {w:word_diff(w,F)∀w∈t}
        wrds_by_diff = sorted(wrds.items(),key=⑴x₁)
        ¿¬🃌(wrds_by_diff): ⇥
        WORDS+=[W≔choice(wrds_by_diff[:(x+2)⌃2])₀]
        # N = choice(↕⨯2)
        t = [w∀w∈t¿⋀(l∉W∀l∈w)]
    
    ☾(⠤((k≔Σ(sorted(⚇⨯set(Σ(WORDS)))))⋄🃌(k))˲˲₋₁, WORDS)
    ¿🃌(k)≠25: ↺
    
    ⇥