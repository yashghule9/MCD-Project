# Design of a Dual-Band Wilkinson Power Divider with Wide Frequency Ratio

**Team members:** Ghule Yash Mahesh (S20240020288), Himanshu Chandrakant Sinha (S20240020290)

**Reference paper:** N. Gao, G. Wu, Q. Tang, "Design of a Novel Compact Dual-Band Wilkinson Power
Divider With Wide Frequency Ratio," *IEEE Microwave and Wireless Components Letters*, vol. 24,
no. 2, pp. 81-83, Feb. 2014, DOI: 10.1109/LMWC.2013.2290226.

## 1. Problem Statement

Design a dual-band equal-split Wilkinson power divider operating at f1 = 500 MHz and
f2 = 2 GHz (frequency ratio k = 4), matched and isolated at both bands simultaneously,
using the compact single-line + coupled-line + lumped-element topology of the reference
paper. Target: input/output return loss and isolation better than 20 dB at both bands,
verified first through closed-form circuit analysis and MATLAB lossless modeling, then
validated against a full-wave EM simulation (HFSS/CST).

*(Replace f1/k above with your own assigned operating frequencies if your problem
statement specifies different ones -- the derivation and code do not change, only the
numbers that come out of `wilkinson_model.m`.)*

## 2. Mathematical Analysis

The divider (Fig. 1 of the reference paper) consists of a single transmission line
(impedance Z1) from the input port to a junction, which splits into two identical
coupled-line sections (even/odd-mode impedances Ze, Zo) feeding the two output ports.
An isolation network (R, L, C) connects the coupled lines' secondary conductors between
the two output ports.

### 2.1 Even-mode analysis (input matching)
With port 1 excited symmetrically, no current flows in the isolation network, and the
divider reduces to a single branch with the trunk line's impedance doubled and the input
port's impedance doubled (standard bisection for a 2-way equal-split junction):

Zin = 2 Z1 (1 + j Z1 tanθ) / (Z1 + j tanθ)
Z' = Ze (Zin + j Ze tanθ) / (Ze + j Zin tanθ)

Setting Z' = 1 (normalized) and separating real/imaginary parts gives:

Z1 · Ze = 1
Z1² + 2 Z1⁴ tan²θ − tan²θ = 0

### 2.2 Odd-mode analysis (isolation / output matching)
Driving the two output ports differentially, the symmetry plane becomes a virtual
ground, reducing the circuit to a shorted coupled-line stub (impedance Zo) in parallel
with the bisected isolation network (R/2 in parallel with C in series with L/2):

Za = j Zo tanθ
Zb = [(R/2)(1/jωC + jωL/2)] / [(R/2) + (1/jωC + jωL/2)]

Setting Z'' = Za·Zb/(Za+Zb) = 1 gives:

R = 2 (normalized, i.e. 100 Ω absolute for Z0 = 50 Ω)
2 Zo ωC tanθ + ω²LC = 2

### 2.3 Dual-band design equations
Requiring input match at both f1 and f2 = k·f1 fixes the electrical length of every
line at f1:

θ_f1 = π/(1+k),  θ_f2 = kπ/(1+k)

and solving the quadratic above for Z1 (with Ze = 1/Z1) gives the unique matched pair.
Requiring output match at both frequencies gives L and C in closed form:

L = 2 Zo tanθ_f1 / (ω2 − ω1)
C = (ω2 − ω1) / (Zo ω1 ω2 tanθ_f1)

Zo itself is a free design variable (subject to Zo ≤ Ze) that sets the coupling
coefficient of the coupled lines:

C(dB) = −20 log10[(Ze+Zo)/(Ze−Zo)]

— this is the parameter that lets this topology reach band ratios up to 10, unlike
earlier dual-band Wilkinson designs limited to k < 3.

**Full derivation with every intermediate step is in the reference paper (attached PDF,
`Design_of_a_Novel_Compact_Dual-Band_Wilkinson_Power_Divider_With_Wide_Frequency_Ratio.pdf`),
equations (1)-(13).**

### 2.4 Extension: S-parameters vs. frequency
The paper only solves the equations above *at* f1 and f2 (the matched point). To plot
S-parameters across the band (Section 3), the even/odd-mode reflection coefficients
above are evaluated at every frequency (not only f1, f2) to get S22, S33, S23, S32 via
the standard decomposition:

S22 = S33 = (Γ_even + Γ_odd)/2,  S23 = S32 = (Γ_even − Γ_odd)/2

S11 and S21 = S31 are obtained separately from the real (undoubled) network, since the
even-mode half-circuit above uses a fictitious doubled port-1 impedance and is not
itself S11. With port 1 driven and ports 2/3 real-terminated, symmetry still guarantees
zero current in the isolation network, giving a direct closed form for S11 and, via an
ABCD cascade of the trunk and branch lines, for S21. Full derivation and the verification
against the paper's own worked numerical example (confirming S11 ≈ 0 and
|S21| ≈ 1/√2 at f1) is in `wilkinson_model.m`.

## 3. MATLAB Lossless Modeling

Implemented in `wilkinson_model.m` (the math, reusable as a function) and
`wilkinson_dualband_design.m` (design point, self-check, plots).

For f1 = 500 MHz, k = 4, Zo chosen at 56 Ω (moderate coupling, C(dB) ≈ −14.7 dB):

| Parameter | Value |
|---|---|
| Z1 | 30.72 Ω |
| Ze | 81.38 Ω |
| Zo | 56.00 Ω |
| L | 8.634 nH |
| C | 5.868 pF |
| R | 100.0 Ω |

These match the reference paper's own worked example (Z1 ≈ 31 Ω, Ze ≈ 81 Ω, L ≈ 9 nH,
C ≈ 6 pF) to within rounding, confirming the implementation is correct.

Self-check (asserted in code, passes): S11, S22, S23 all below −20 dB at both 500 MHz
and 2 GHz.

**[Insert the four generated plots here: S11, S22/S33, S23, S21/S31 vs. frequency
(0.1-2.6 GHz), from running `wilkinson_dualband_design.m`.]** Both plots show the
expected dual-null pattern at 0.5 GHz and 2 GHz, matching the shape of the reference
paper's Fig. 5 (simulated/measured input return loss).

## 4. EM Simulation

**Substrate:** εr = 2.2, h = 0.8 mm (matches the reference paper's fabricated
substrate, chosen so the EM layout can also be sanity-checked against the paper's own
measured results as an extra reference point).

**Starting physical dimensions** (computed in `em_layout.m` via Hammerstad microstrip
synthesis, θ evaluated at f1):

| Line | Z0 | Width | εeff | Length (at f1) |
|---|---|---|---|---|
| Z1 (single line) | 30.72 Ω | 4.831 mm | 1.947 | 42.998 mm |
| Ze guess (isolated-line) | 81.38 Ω | 1.094 mm | 1.792 | 44.823 mm |
| Zo guess (isolated-line) | 56.00 Ω | 2.073 mm | 1.853 | 44.079 mm |

The Ze/Zo widths are **isolated-line approximations only** — closed-form coupled-microstrip
synthesis (Akhtarzad et al.) requires iterating W and the gap S simultaneously against
both Ze and Zo, which is better done with the EM tool's own optimizer than by hand.
Starting guess for the coupled-line pair: W ≈ 1.6 mm, gap S ≈ h = 0.8 mm.

**HFSS/CST setup steps:**
1. Draw the substrate (εr = 2.2, h = 0.8 mm, copper cladding) and the three microstrip
   segments (Z1 trunk, two coupled-line branches) using the dimensions above as the
   starting layout.
2. Add the isolation network: two coupling capacitors C to the coupled lines' secondary
   conductors, inductor L between them to a center node, resistor R across the two ends
   (lumped RLC components, or realize R with a thin-film/surface-mount resistor and
   L/C with lumped-element models in the EM tool, per L, C, R values above).
3. Define 3 wave ports (or lumped ports) at Port 1, Port 2, Port 3, reference
   impedance 50 Ω.
4. Set up a frequency sweep covering ~0.1-2.6 GHz (same range as the MATLAB sweep).
5. Run an optimization (HFSS Optimetrics / CST Optimizer) on the coupled line's W and
   gap S, targeting Ze = 81.38 Ω and Zo = 56.00 Ω (or directly targeting S11/S22 minima
   at 500 MHz and 2 GHz — equivalent, and closer to what you can actually measure from
   the simulation).
6. Export the 3-port S-parameters as Touchstone (`.s3p`) over the full swept band.

**[TODO: insert EM-simulated S-parameter plots and final tuned dimensions here once the
HFSS/CST run is complete.]**

## 5. Validation

`validate_em.m` overlays the MATLAB lossless-model curves against the EM-simulated
Touchstone file (`em_results.s3p`) automatically once it is exported from HFSS/CST —
run it after Section 4 to produce the comparison plots.

**[TODO: insert overlay plots (S11, S21, S22, S23 — MATLAB vs. EM) and discuss where/why
they diverge. Expected sources of difference: conductor and dielectric loss (the
MATLAB model is lossless), radiation/parasitic coupling at the T-junction and
coupled-line discontinuities, and the lumped R/L/C components' non-ideal parasitics —
none of which are in the closed-form model.]**

## 6. Conclusion

**[TODO: summarize after Section 5 — did the design meet the >20 dB return
loss/isolation target at both bands in simulation? How closely did EM match the
lossless model? What would you change for a second iteration?]**

## References

1. N. Gao, G. Wu, Q. Tang, "Design of a Novel Compact Dual-Band Wilkinson Power
   Divider With Wide Frequency Ratio," *IEEE MWCL*, vol. 24, no. 2, pp. 81-83, 2014.
2. (Add any textbook/EM-tool documentation references used for the layout synthesis.)

## Contribution Statement

*(Fill in honestly based on who actually did what — required by the course
instructions.)*

| Task | Contributor(s) |
|---|---|
| Paper selection and problem statement | |
| Mathematical derivation (Section 2) | |
| MATLAB modeling and plots (Section 3) | |
| EM layout and simulation (Section 4) | |
| Validation and writeup (Sections 5-6) | |
