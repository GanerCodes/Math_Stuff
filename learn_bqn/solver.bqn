S←•Show

Det←{1≥≠𝕩?0‿0⊑𝕩;M←𝕊{(𝕩≠l)/⌾⍉1↓x}⋄-´{0‿𝕩⊑x×M𝕩}¨l←↕≠x←𝕩}
CoF←{N←{(l≠1⊑𝕨)/⌾⍉(𝕨⊑⊸≠l←↕≠𝕩)/𝕩}⋄{(¯1⋆𝕨+𝕩)×Det(𝕨⋈𝕩) N x}⌜˜↕≠x←𝕩}
Inv←·⍉CoF÷Det
SwC←{n‿v←𝕨⋄{n-⊸⌽v⌾⊏⊢n⌽𝕩}⌾⍉𝕩}
Sol←{v←𝕩⋄(𝕨⊸{Det 𝕩‿v SwC 𝕨}¨↕≠v)÷Det 𝕨}

m←3‿3⥊∾⟨1‿1‿1
        0‿1‿1
        0‿0‿1⟩
v←2‿3‿1

S "Det: " ⋈ Det m
S "CoF: " ⋈ CoF m
S "Inv: " ⋈ Inv m
S "Sol: " ⋈ m Sol v