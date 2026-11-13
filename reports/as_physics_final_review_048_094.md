# OxfordAQA International AS Physics 2027 — Historical Superseded Review

> **Status update (2026-09-09):** This 048–094 review records a pre-repair
> candidate and is **superseded**. The listed issues were resolved in the
> current 94-topic artifact. Do not use this report as the current approval
> decision; use `artifacts/as-physics-2027-review/agent-product-review.json`
> and the current delivery pointers instead.
## Final content review: topics 048–094

**Review date:** 2026-09-09  
**Route:** OxfordAQA International Advanced Subsidiary Physics, code 9631, International market, 2027  
**Scope:** topics 048–094 in `artifacts/as-physics-2027-review/concepts/concept_explanations.json`  
**Review type:** independent source, physics, worked-example, and topic-split review  
**Formal delivery status:** not approved by this report

## Conclusion

All 47 topics in the assigned range were read in the current concept file and
matched to the corresponding outline requirements and official specification
evidence. The split is generally based on atomic examinable points and
teachable procedures rather than simply renaming the official section headings.

The current range is **not accuracy-clean yet**. Most explanations and numerical
examples are sound, but six bounded revisions remain necessary:

1. Topic 049 introduces critical-field/current limits even though critical field
   is explicitly outside the International AS assessment boundary.
2. Topic 052 names cell-series and identical-cell-parallel rules but gives no
   explicit cell-network checkpoint and leaves the internal-resistance behavior
   of parallel identical cells too vague.
3. Topic 059 does not explicitly teach the required energy variation with time
   and the corresponding displacement/time graph interpretation.
4. Topic 071 says that a graphical explanation is required but does not itself
   provide the required frame-by-frame graphical construction.
5. Topic 073 still presents `fundamental` and `overtone` as optional teaching
   synonyms, whereas the specification states that those terms will not be used;
   the exam-facing boundary should be stated more strictly.
6. Topic 093 contains a false statement about mass at fixed momentum: from
   `lambda = h/p`, changing mass at fixed momentum does not change wavelength.

Topic 089 also has a **coverage weakness**: stopping potential is defined but is
not demonstrated in its worked example. Topic 090 does use stopping potential,
so this is a bounded reinforcement rather than a new physics error.

The current visual fields are present for all 47 topics and route to the required
external landscape infographic path. This report does not approve generated
assets, visual semantics, the rendered HTML, or PDF delivery; those remain
separate gates.

## Evidence and method

Reviewed artifacts:

- `artifacts/as-physics-2027-review/concepts/concept_explanations.json`
- `artifacts/as-physics-2027-review/syllabus-outline.json`
- `artifacts/as-physics-2027-review/syllabus-evidence.json`
- `artifacts/as-physics-2027-review/qualification.json`

The official evidence used here is the OxfordAQA International AS and A-level
Physics specification, Version 5.1, especially pages 18–22 of the extracted
source. The source states, among other boundaries, that critical field is not
assessed, a graphical explanation of stationary-wave formation is expected,
`fundamental` and `overtone` will not be used for string harmonics, spectrometer
operation is not tested, and experimental determination of stopping potential is
not required.

Every worked example in this range was independently recalculated or checked by
dimensional/limiting reasoning. Numerical checks include resistance networks,
electrical energy and power, potential dividers, emf/internal resistance,
oscillator periods, echo depth, phase conversion, first-harmonic frequency,
Young's slits, grating angles, refraction, critical angle, eV/J conversion,
line-spectrum frequency, photon energy, photoelectric stopping potential, and
de Broglie wavelength.

## Topic coverage and verdicts

`PASS` means no factual or numerical correction is required in the current
entry. `ISSUE` means the entry needs the bounded replacement recorded below.

| No. | Topic ID | Topic | Verdict | Review note |
|---:|---|---|---|---|
| 048 | `requirement-d64c880b36585809` | Temperature effects and thermistors | PASS | Metal and NTC trends, sensor use, and divider direction are correct. |
| 049 | `requirement-60ba2192b9710614` | Superconductivity | ISSUE | Remove or explicitly exclude non-assessed critical-field/current limits. |
| 050 | `requirement-1d2b60218e456009` | Series and parallel resistance | PASS | Series sum, reciprocal parallel rule, and 4 Ω/12 Ω result of 3.0 Ω are correct. |
| 051 | `requirement-5395266b51c1a0b6` | Electrical energy and power | PASS | `P = IV = 36 W`; `E = IVt = 1.08 × 10^4 J` for 5.0 min. |
| 052 | `requirement-2f9d938234333c8f` | Series and parallel circuit rules | ISSUE | Add an explicit cell-series/identical-parallel checkpoint and state the parallel-cell resistance behavior. |
| 053 | `requirement-26feb098b153f6ba` | Charge and energy conservation in circuits | PASS | Junction-current example gives 1.6 A and the loop/junction distinction is correct. |
| 054 | `requirement-102899ef35a6f31f` | Potential divider principle | PASS | The unloaded divider equation and 9 V, 2 kΩ/7 kΩ result of 7.0 V are correct. |
| 055 | `requirement-6ea2548a0a4b455c` | Sensor potential dividers | PASS | NTC/LDR direction is correctly conditioned on the output-arm position. |
| 056 | `requirement-fb9403085bde483f` | Emf and internal-resistance equations | PASS | `I = 0.500 A` and terminal pd `1.40 V` are correctly obtained. |
| 057 | `requirement-80b5f5d83c7b977b` | Cell practical | PASS | `V–I` intercept is emf and gradient is `−r`; sign handling is correct. |
| 058 | `requirement-7342f9257a4054c5` | Oscillator periods | PASS | Mass–spring formula and `T = 0.314 s` calculation are correct; small-angle scope is stated. |
| 059 | `requirement-001f66231c4b26fb` | Oscillation energy | ISSUE | Explicit displacement/time variation and graph interpretation are under-taught. |
| 060 | `requirement-6b8ed8d2b1f47c70` | Damping | PASS | Energy loss, amplitude decay, and heavy-damping description are correct. |
| 061 | `requirement-312220a03f5ea194` | Simple-harmonic-systems practical | PASS | Period averaging and `T^2` graph choices are appropriate; `T = 1.58 s`, `T^2 = 2.50 s^2`. |
| 062 | `requirement-227541d0870bccef` | Free and forced vibrations | PASS | Free motion and continuing periodic drive are correctly distinguished. |
| 063 | `requirement-80751126bc87a551` | Resonance and damping | PASS | Greater damping lowers and broadens the resonance peak. |
| 064 | `requirement-5ad77306fa354acb` | Resonance applications | PASS | Resonance is qualified by a driver and natural-mode frequency matching. |
| 065 | `requirement-4a3b7259b37a2e06` | Wave quantities and phase | PASS | Phase and phase difference are now explicitly defined; quarter-cycle example is correct. |
| 066 | `requirement-2d793fb068a24f4f` | Wave speed equation | PASS | `c = fλ`, `f = 1/T`, and the 2.0 m s⁻¹ result are correct. |
| 067 | `requirement-236670283c0299fa` | Phase difference | PASS | `0.25` cycle is correctly converted to `90° = π/2 rad`. |
| 068 | `requirement-deaaa207abb346dc` | Longitudinal, transverse and energy propagation | PASS | Direction-of-displacement and energy-propagation distinctions are correct. |
| 069 | `requirement-0a2f23d1c1030b1c` | Ultrasound in medicine | PASS | Echo depth correctly divides the 0.2002 m round trip by two to give about 0.100 m. |
| 070 | `requirement-4e020ec065242eb1` | Polarisation | PASS | Polarisation evidence and Polaroid/aerial examples are correct; Malus's law is excluded. |
| 071 | `requirement-cd2a2f72f0f8e3b1` | Superposition and stationary-wave formation | ISSUE | The required graphical construction is described but not actually supplied in the entry. |
| 072 | `requirement-d3f52af33fb7c646` | First harmonic on a string | PASS | Formula, node/antinode pattern, and 50 Hz example are correct. |
| 073 | `requirement-502f6d7cd434a9f9` | Stationary-wave applications and harmonics | ISSUE | Tighten the exam terminology boundary for `fundamental` and `overtone`. |
| 074 | `requirement-4f161a349f5f3d08` | Stationary-wave practical | PASS | Controlled-variable plan and `f` against `sqrt(T)` test are correct. |
| 075 | `requirement-ff5736f5271f0067` | Interference, path difference and coherence | PASS | Coherence and integer/half-integer path-difference rules are correctly scoped. |
| 076 | `requirement-3bd2c6bc597845d2` | Fringe spacing | PASS | `w = 4.0 mm` is correct after SI conversion. |
| 077 | `requirement-6b8ec2cf800bee1d` | Interference applications and laser safety | PASS | White-light, sound/EM interference, and laser hazards are accurately described. |
| 078 | `requirement-aba89b989bedebf1` | Young's slits and diffraction practical | PASS | Both required practical components are now represented; `700 nm` and about `600 nm` calculations are correct for the supplied data. |
| 079 | `requirement-f9e9def8bb60abde` | Single-slit diffraction | PASS | Width trend is correct and the earlier unqualified brightness claim has been removed. |
| 080 | `requirement-0147dd7defe0b012` | Transmission gratings | PASS | Line-density inversion and `17.5°` first-order angle are correct. |
| 081 | `requirement-1377c6d63dc9d301` | Refraction and Snell's law | PASS | Normal-angle convention and `19.5°` glass angle are correct. |
| 082 | `requirement-4e09c0dc48c0f258` | Critical angle and total internal reflection | PASS | `41.8°` for glass-to-air and the high-to-low-index condition are correct. |
| 083 | `requirement-2d91757d9d2c4b7c` | Optical fibres | PASS | Step-index guidance, modal/material dispersion, broadening, and absorption are correct. |
| 084 | `requirement-89d7e30470722ea0` | Excitation and ionisation | PASS | Bound-state excitation is correctly separated from electron removal. |
| 085 | `requirement-593f8a7d9d3bba27` | Electron volt conversion in atomic collisions | PASS | `4.2 eV = 6.72 × 10^-19 J` is correct. |
| 086 | `requirement-a9b42a320e877000` | Line spectra and energy-level transitions | PASS | `2.50 eV` gives `6.03 × 10^14 Hz` after conversion to joules. |
| 087 | `requirement-67eef347d190b81a` | Characteristic X-rays | PASS | Continuous bremsstrahlung and target-specific characteristic lines are correctly separated. |
| 088 | `requirement-532f95f57aa983d2` | Photon energy | PASS | `600 nm` photon energy is correctly `3.32 × 10^-19 J`. |
| 089 | `requirement-9980755dbdef70a8` | Threshold frequency and work function | PASS* | Threshold reasoning is correct; add a stopping-potential checkpoint for complete coverage. |
| 090 | `requirement-73f270bfa33c6681` | Photoelectric equation | PASS | `4.0 − 2.5 = 1.5 eV` gives `V_s = 1.5 V`; the energy balance is correct. |
| 091 | `requirement-0915fd3c31e1d2df` | Electron diffraction | PASS | Diffraction is correctly interpreted as evidence of matter-wave behaviour. |
| 092 | `requirement-43007c179dd5afef` | Photoelectric evidence for photon behaviour | PASS | At fixed frequency, intensity changes photocurrent but not `E_k(max)` or `V_s`. |
| 093 | `requirement-3a895b896f27ea98` | de Broglie wavelength | ISSUE | The fixed-momentum mass statement is physically false. |
| 094 | `requirement-26cb5e667302c665` | Evidence and changing models of matter | PASS | Model revision is accurately tied to spectra, photoelectric, and diffraction evidence. |

## Required revisions

### Topic 049 — Superconductivity

**Topic ID:** `requirement-60ba2192b9710614`

**Current text:** “Below the critical temperature, current flows with very little
energy dissipation; exceeding the relevant temperature, field or current limit
removes the state.”

**Problem:** The specification defines superconductivity using zero resistivity at
and below a material-dependent critical temperature and explicitly says that
critical field will not be assessed. Mentioning a field/current limit without a
clear boundary can make a non-assessed variable appear to be required content.

**Replacement text:** “For a particular material, resistivity is zero (or treated
as negligible in practical discussion) at and below its material-dependent
critical temperature. For International AS, focus on the critical-temperature
condition; critical field is not assessed. Applications include producing strong
magnetic fields and reducing energy loss in electric-power transmission.”

### Topic 052 — Series and parallel circuit rules

**Topic ID:** `requirement-2f9d938234333c8f`

**Current text:** “For cells in series, emfs and internal resistances combine in the
circuit direction; identical cells in parallel retain the same emf while sharing
current.”

**Problem:** The source point explicitly includes cells in series and identical
cells in parallel. The prose names the cases but does not make the resistance
consequence explicit, and the worked example tests only two series resistors.
Students could therefore miss the exam distinction between adding identical-cell
emfs in series and retaining one-cell emf in parallel.

**Replacement text:** “Cells in series have a total emf equal to the algebraic
sum of their emfs and a total internal resistance equal to the sum of their
internal resistances. Identical cells in parallel have the emf of one cell,
share the current, and—when their internal resistances are included—have a lower
effective internal resistance (for N identical cells, r/N in the ideal symmetric
case). Add a short worked checkpoint comparing two identical cells in series with
two identical cells in parallel.”

### Topic 059 — Oscillation energy

**Topic ID:** `requirement-001f66231c4b26fb`

**Current text:** “Energy values vary with both displacement and time, so a graph
must identify the oscillator position.”

**Problem:** The source requires students to relate kinetic, potential, and total
energy to **both displacement and time**. The current entry correctly describes
the turning points and equilibrium but does not state the time dependence or what
the required graphs should show.

**Replacement text:** “For an ideal oscillator, at equilibrium (`x = 0`) kinetic
energy is maximum and potential energy is minimum; at `x = ±A`, the mass is
momentarily at rest, kinetic energy is zero and potential energy is maximum. As
time progresses through a cycle, kinetic and potential energies vary periodically
in opposite phase while total mechanical energy remains constant (in the absence
of damping). Be able to read or sketch the corresponding energy-versus-
displacement and energy-versus-time graphs.”

### Topic 071 — Superposition and stationary-wave formation

**Topic ID:** `requirement-cd2a2f72f0f8e3b1`

**Current text:** “A graphical explanation should plot successive snapshots of the
two travelling waves and their resultant ... The required visual must show at
least two travelling-wave traces, their sum, fixed node positions and oscillating
antinode positions; it is not a text-only poster.”

**Problem:** This is a specification of what a future visual should contain, not
the graphical explanation itself. The official source explicitly says that a
graphical explanation will be expected. The current concept entry therefore
cannot yet demonstrate that the learner has been shown the required construction.

**Replacement text:** Add an actual four-frame or equivalent graphical sequence:
two equal-frequency waves travelling in opposite directions, their pointwise
resultant at successive phases, and the fixed node/antinode positions labelled.
The accompanying caption should state that cancellation is permanent at nodes,
reinforcement is maximal at antinodes, and an ideal stationary wave has no net
energy transfer along the medium. The imported visual must be semantically
reviewed after rendering; a text-only prompt is not sufficient evidence.

### Topic 073 — Stationary-wave applications and harmonics

**Topic ID:** `requirement-502f6d7cd434a9f9`

**Current text:** “The exam uses first harmonic and does not require the terms
fundamental or overtone as examination terminology; those words may be mentioned
only as optional teaching synonyms.”

**Problem:** The specification says that the terms `fundamental` (for first
harmonic) and `overtone` will not be used. Calling them optional teaching
synonyms weakens the exam-facing boundary and may reintroduce terminology the
student is meant to avoid in this route.

**Replacement text:** “Use the specification's terminology: first harmonic,
second harmonic, third harmonic, and so on. The terms `fundamental` and
`overtone` are not used in this qualification and should not be used as required
answer labels. For strings fixed at both ends, the nth harmonic contains n
half-wavelengths and n antinodes.”

### Topic 093 — de Broglie wavelength

**Topic ID:** `requirement-3a895b896f27ea98`

**Current text:** “For fixed mass, increasing momentum decreases wavelength; for
fixed momentum, a more massive particle has a shorter wavelength.”

**Problem:** The second clause contradicts `lambda = h/p`. At fixed momentum,
wavelength is independent of mass. A greater mass gives a shorter wavelength only
when the comparison holds speed constant, because then `p = mv` is greater.

**Replacement text:** “From `lambda = h/p`, increasing momentum always decreases
the de Broglie wavelength. If speed is held fixed, increasing mass increases
momentum and therefore decreases wavelength. If momentum is held fixed, changing
mass does not change wavelength. Diffraction becomes less pronounced when the
wavelength is small compared with the aperture or crystal spacing.”

## Coverage reinforcement

### Topic 089 — Threshold frequency and work function

**Topic ID:** `requirement-9980755dbdef70a8`

The current explanation correctly defines threshold frequency, work function, and
stopping potential, and Topic 090 correctly calculates a stopping potential from
the photoelectric equation. To make this topic independently complete, add one
short checkpoint such as:

> A metal has `phi = 2.0 eV`. Photons of `1.5 eV` cannot eject electrons, however
> intense the beam. If photons above threshold produce `E_k(max) = 0.80 eV`, the
> stopping potential is `V_s = 0.80 V` because `E_k(max) = eV_s`.

This is a coverage reinforcement, not an arithmetic correction.

## Numerical and limiting checks

The following checks were recomputed independently from the current examples:

| Topic | Check | Result |
|---:|---|---:|
| 050 | `1/R = 1/4.0 + 1/12` | `R = 3.0 ohm` |
| 051 | `P = 12 × 3.0`, `E = 12 × 3.0 × 300` | `36 W`, `1.08 × 10^4 J` |
| 054 | `9.0 × 7.0/(2.0 + 7.0)` | `7.0 V` |
| 056 | `I = 1.50/(2.80 + 0.20)`; `V = 1.50 − Ir` | `0.500 A`, `1.40 V` |
| 058 | `2pi sqrt(0.50/200)` | `0.314 s` |
| 061 | `31.6/20`; square | `1.58 s`, `2.50 s^2` |
| 066 | `2.5 × 0.80` | `2.0 m s^-1` |
| 067 | `0.25 × 360`, `0.25 × 2pi` | `90 deg`, `pi/2 rad` |
| 069 | `1540 × 130e-6 / 2` | `0.1001 m` (about `10.0 cm`) |
| 072 | `(1/(2 × 0.80)) sqrt(64/0.010)` | `50 Hz` |
| 076 | `600e-9 × 2.0 / 0.30e-3` | `4.0 mm` |
| 078 | Young: `4.20e-3 × 0.25e-3 / 1.50`; grating: `d sin 21.1 deg` | `7.0e-7 m`; about `6.0e-7 m` |
| 080 | `d = 1/(600e3)`; `sin theta = 500e-9/d` | `theta = 17.5 deg` |
| 081 | `sin theta2 = sin 30/1.50` | `theta2 = 19.5 deg` |
| 082 | `asin(1.00/1.50)` | `41.8 deg` |
| 085 | `4.2 × 1.60e-19` | `6.72e-19 J` |
| 086 | `2.50 × 1.60e-19 / 6.63e-34` | `6.03e14 Hz` |
| 088 | `6.63e-34 × 3.00e8 / 600e-9` | `3.32e-19 J` |
| 090 | `E_k(max) = 4.0 − 2.5` eV | `V_s = 1.5 V` |
| 093 | `6.63e-34 / 3.0e-24` | `2.21e-10 m` |

Conceptual entries without numerical examples were checked using limiting cases:
series/parallel current and pd rules, conservation at junctions and loops,
damping, resonance, wave classification, polarisation, stationary-wave nodes,
coherence, optical-fibre dispersion, excitation/ionisation, X-ray spectra,
photoelectric evidence, and model revision.

## Final review state

After the six revisions above and the Topic 089 reinforcement, rerun this
47-topic content review against the repaired concepts file. The current report
does not approve HTML, visuals, or PDF. The external visual route is available,
but every imported visual still requires individual semantic review and the whole
rendered HTML must be visibly reviewed before delivery.
