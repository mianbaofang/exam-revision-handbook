# OxfordAQA International AS Physics 2027 — Historical Superseded Audit

> **Status update (2026-09-09):** This 048–094 audit is retained for traceability
> but is **superseded** by the repaired 94-topic review. Its earlier issue list
> does not describe the current approved HTML/PDF. Use the current review
> ledger and delivery pointers in `artifacts/as-physics-2027-review/`.
## Accuracy Audit: Topics 048–094

**Audit date:** 2026-09-09  
**Audit type:** Read-only content and source-coverage review  
**Historical result at time of review:** 41 `PASS`, 6 `ISSUE`  
**Formal delivery status at time of review:** Not approved. This historical
report does not replace the current HTML review, visual review, or delivery
gate.

## Scope and evidence

This audit covers topics 048–094 in:

`LOCAL_PATH

The comparison sources were:

- `LOCAL_PATH
- `LOCAL_PATH
- `LOCAL_PATH

The selected route is OxfordAQA International Advanced Subsidiary Physics, code 9631, International market, selected exam year 2027. The underlying source is the OxfordAQA International AS and A-level Physics specification, Version 5.1. The AS scope is Units 1–2 / sections 3.1–3.5; A2-only content was not used as an AS requirement.

The review checked:

- whether each topic maps to the stated atomic exam point(s), rather than merely repeating an official section heading;
- definitions, scope boundaries, equations, units, qualitative claims, and worked-example reasoning;
- whether practical topics cover the practical action named by the source;
- whether terminology is aligned with the International AS wording;
- whether each entry has the required explanation, example, solution steps, pitfall, source points, and visual-decision fields.

All 47 numerical worked examples in this range were recalculated. No general arithmetic or unit-conversion error was found. The `topic-split-status.json` still records the draft as `draft-review-required`, with no generated assets and no final LLM HTML review; therefore the accuracy result below is not a delivery approval.

## Topic-by-topic verdict

| No. | Topic | Verdict | Audit note |
|---:|---|---|---|
| 048 | Temperature effects and thermistors | `PASS` | Correct metal/NTC trends, sensor use, and divider example. |
| 049 | Superconductivity | `PASS` | Correct critical-temperature boundary and application limits. |
| 050 | Series and parallel resistance | `PASS` | Series/parallel equations and numerical check are correct. |
| 051 | Electrical energy and power | `PASS` | `E = IVt` and power forms are used with correct units. |
| 052 | Series and parallel circuit rules | `PASS` | Current, pd, and cell-network rules are correctly distinguished. |
| 053 | Charge and energy conservation in circuits | `PASS` | Junction-current and loop-energy reasoning is correct. |
| 054 | Potential divider principle | `PASS` | Output-resistor condition and calculation are correct. |
| 055 | Sensor potential dividers | `PASS` | Thermistor/LDR direction depends correctly on output position; potentiometer boundary is stated. |
| 056 | Emf and internal-resistance equations | `PASS` | `ε = E/Q`, `ε = I(R+r)`, and terminal-pd calculation are correct. |
| 057 | Cell practical | `PASS` | `V–I` intercept/gradient interpretation and practical advice are correct. |
| 058 | Oscillator periods | `PASS` | Mass–spring and small-angle pendulum equations are correctly scoped. |
| 059 | Oscillation energy | `PASS` | Turning-point and equilibrium energy exchange is correct. |
| 060 | Damping | `PASS` | Energy loss, amplitude reduction, and heavy-damping description are correct. |
| 061 | Simple-harmonic-systems practical | `PASS` | Period averaging and `T²` graph treatment are appropriate. |
| 062 | Free and forced vibrations | `PASS` | Continuing periodic drive is correctly required for forced vibration. |
| 063 | Resonance and damping | `PASS` | Peak height and width changes with damping are correctly described. |
| 064 | Resonance applications | `ISSUE` | See Issue 1. The stationary-wave statement is too absolute. |
| 065 | Wave quantities and phase | `ISSUE` | See Issue 2. Phase and phase difference are under-taught in this entry. |
| 066 | Wave speed equation | `PASS` | `c = fλ` and `f = 1/T` are correctly applied. |
| 067 | Phase difference | `PASS` | Cycle, degree, and radian conversions are correct. |
| 068 | Longitudinal, transverse and energy propagation | `PASS` | Sound, string, electromagnetic-wave examples and propagation direction are correct. |
| 069 | Ultrasound in medicine | `PASS` | Echo-depth calculation correctly divides the round-trip distance by two. |
| 070 | Polarisation | `PASS` | Correctly uses polarisation as evidence for transverse motion and excludes Malus’s law. |
| 071 | Superposition and stationary-wave formation | `ISSUE` | See Issue 3. The required graphical explanation is not actually supplied. |
| 072 | First harmonic on a string | `PASS` | Formula, variables, node/antinode pattern, and numerical result are correct. |
| 073 | Stationary-wave applications and harmonics | `ISSUE` | See Issue 4. Application coverage and terminology boundary need repair. |
| 074 | Stationary-wave practical | `PASS` | Independent-variable control and `f` against `√T` test are correct. |
| 075 | Interference, path difference and coherence | `PASS` | Coherence, path-difference conditions, and Young arrangement are correct. |
| 076 | Fringe spacing | `PASS` | `w = λD/s`, assumptions, conversions, and result are correct. |
| 077 | Interference applications and laser safety | `PASS` | White-light, sound, EM-wave interference, and laser hazard points are correct. |
| 078 | Young’s slits and diffraction practical | `ISSUE` | See Issue 5. The worked example covers Young’s slits but not the diffraction-grating practical. |
| 079 | Single-slit diffraction | `ISSUE` | See Issue 6. The central-brightness claim is unqualified and not required by the source. |
| 080 | Transmission gratings | `PASS` | Line-density conversion, grating equation, application, and spectrometer boundary are correct. |
| 081 | Refraction and Snell’s law | `PASS` | Normal-angle convention, speed/index relation, and calculation are correct. |
| 082 | Critical angle and total internal reflection | `PASS` | Direction condition, critical-angle equation, and example are correct. |
| 083 | Optical fibres | `PASS` | Core/cladding, modal/material dispersion, broadening, and absorption are correctly explained. |
| 084 | Excitation and ionisation | `PASS` | Bound-state excitation is correctly distinguished from electron removal. |
| 085 | Electron volt conversion in atomic collisions | `PASS` | eV/J conversion direction and example are correct. |
| 086 | Line spectra and energy-level transitions | `PASS` | Discrete levels and `hf = ΔE` calculation are correct. |
| 087 | Characteristic X-rays | `PASS` | Continuous background and characteristic lines are correctly separated. |
| 088 | Photon energy | `PASS` | `E = hf = hc/λ` and SI conversion are correct. |
| 089 | Threshold frequency and work function | `PASS` | Threshold, photon number, work function, and stopping-potential roles are correct. |
| 090 | Photoelectric equation | `PASS` | `hf = φ + E_k(max)` and eV-to-stopping-potential reasoning are correct. |
| 091 | Electron diffraction | `PASS` | Diffraction evidence is correctly interpreted as particle wave behaviour. |
| 092 | Photoelectric evidence for photon behaviour | `PASS` | Frequency/intensity consequences and photon interpretation are correct. |
| 093 | de Broglie wavelength | `PASS` | `λ = h/p` calculation and momentum trend are correct. |
| 094 | Evidence and changing models of matter | `PASS` | Model revision is accurately tied to line spectra, photoelectric effect, and diffraction evidence. |

## Issues requiring Writer revision

### Issue 1 — Topic 064: Resonance applications

The explanation says that stationary waves “are also a resonance phenomenon.” The source point in the forced-vibration/resonance section asks for examples involving stationary waves; it does not make every stationary-wave description identical to resonance. A stationary pattern can be described through superposition and boundary conditions, while resonance additionally concerns efficient energy transfer from a periodic driver near a natural frequency.

**Required revision:** change the statement to a qualified form such as “stationary-wave situations may involve resonance when a periodic driver excites a natural mode,” and retain the existing frequency-matching explanation in the worked example.

### Issue 2 — Topic 065: Wave quantities and phase

The source requires definitions of amplitude, frequency, wavelength, wave speed, phase, and phase difference. The current entry gives clear definitions for the first four, but phase is only described as “position within a cycle,” and phase difference is deferred to Topic 067. The only worked example tests wavelength. This leaves the source requirement only partially demonstrated in the named topic.

**Required revision:** add an explicit definition of phase for a point in a cycle and an explicit definition of phase difference between two oscillations, then add a short identification example (for example, in-phase, antiphase, or quarter-cycle separation). Topic 067 may retain the numerical conversion treatment.

### Issue 3 — Topic 071: Superposition and stationary-wave formation

The source explicitly states that a graphical explanation of stationary-wave formation is expected. The current prose says that snapshots “should show” destructive interference at nodes and constructive interference at antinodes, but the entry itself contains no actual graphical sequence, coordinate sketch, or frame-by-frame construction. A node-only verbal example is not equivalent to the required graphical explanation.

**Required revision:** include a genuine graphical explanation showing two equal-frequency, opposite-travelling waves at successive phases, their resultant, fixed nodes, and oscillating antinodes. The visual must be checked for physical correctness after rendering; a generic text-heavy infographic is not a substitute.

### Issue 4 — Topic 073: Stationary-wave applications and harmonics

The source requires applications to strings, microwaves, and sound waves, plus interpretation of harmonics. The explanation names strings, air columns, and microwaves, but the worked example only asks for a string mode. There is no explicit sound or microwave application checkpoint. In addition, the sentence saying the terms “fundamental” and “overtone” should not be used is stronger than the specification wording. The specification says those terms will not be used as examination terms; it does not state that the words are forbidden in all teaching contexts.

**Required revision:** add at least one sound or microwave application example/checkpoint, and change the scope note to “the exam uses first harmonic and does not require the terms fundamental/overtone as examination terminology.” Keep “first harmonic” as the assessed term.

### Issue 5 — Topic 078: Young’s slits and diffraction practical

The source practical requirement covers both Young’s-slit interference and interference by a diffraction grating. The current example calculates wavelength from Young’s-slit fringe spacing only. The prose mentions the grating, but does not demonstrate how to evaluate its data, geometry, uncertainty, or comparison with an expected wavelength.

**Required revision:** add a separate diffraction-grating practical checkpoint or second worked example, such as using line density and measured angle/order to calculate wavelength, discussing repeat readings and uncertainty, or evaluating a discrepancy. Keep the Young’s-slit example as the complementary half of the topic.

### Issue 6 — Topic 079: Single-slit diffraction

The source requires the qualitative change in central-maximum width with wavelength and slit width. The current final step adds: “Its central brightness may decrease as the transmitted light is distributed more broadly.” This is not needed for the source point and is presented without the illumination, aperture, and normalisation conditions that determine how intensity is being compared. It can therefore distract from the assessed width relationship or be read as an unconditional rule.

**Required revision:** remove that sentence, or qualify it explicitly as a conditional observation under a stated experimental comparison. The core conclusion should remain: increasing wavelength or reducing slit width increases the central-maximum width.

## Overall conclusion

The current 048–094 draft is substantially source-aligned and its numerical examples are generally sound. It is **not yet accuracy-clean** because six entries have identifiable content or coverage defects. The six repairs above are bounded Writer revisions; after they are made, the full topic range must be rechecked, the actual visual assets must be reviewed, and the rendered HTML must receive the required complete LLM review before any formal PDF delivery claim.

This report does not approve the current HTML, does not approve the current visual manifest, and does not promote the draft to final-ready status.
