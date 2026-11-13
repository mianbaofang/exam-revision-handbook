# OxfordAQA International AS Physics 2027 — Historical Superseded Audit

> **Status update (2026-09-09):** This 001–047 audit is retained for traceability
> but is **superseded** by the repaired 94-topic review. Its earlier issue list
> does not describe the current approved HTML/PDF. Use the current review
> ledger and delivery pointers in `artifacts/as-physics-2027-review/`.

## Accuracy review: topics 001-047

Date: 2026-09-09  
Review mode: read-only content audit  
Draft reviewed:
`LOCAL_PATH  
Primary concept file:
`concepts\concept_explanations.json`  
Outline file: `syllabus-outline.json`

## Scope and method

This report reviews the current raster-routing draft, not the earlier authored
JSON files and not the retired Chinese bypass output. Topics 001-047 were checked
against the current outline and the OxfordAQA International AS Physics 9630
specification evidence used by the draft.

For every topic the review checked:

- title and source-point alignment;
- whether the stated explanation covers the mapped exam action and remains within
  the International AS boundary;
- formula, definition, sign convention and unit use;
- worked-example arithmetic and the logic of each solution step;
- presence of a topic-specific visual decision and visual guidance.

## Overall result

- **47/47 topic titles match the current outline.**
- **70/70 source references for topics 001-047 resolve to known outline source
  IDs; no missing source reference was found.**
- **47/47 entries contain four worked-solution steps and the required visual
  fields.**
- **45 topics pass the content audit as written.**
- **At the time of review, 2 topics required content revision:** Topic 010 and
  Topic 041. Those repairs are included in the current 94-topic artifact.
- **2 topics require source-treatment clarification:** Topic 027 and Topic 029.
  Their source statements are official combined statements, while the current
  teaching split assigns the clauses to separate topics. This is a traceability
  issue rather than an arithmetic error.

At the time of review, the draft remained `delivery_eligible: false` and had no
generated visual assets; this historical state is superseded by the current
94-topic artifact.
that is a separate production gate and is not treated as a content pass.

## Topic findings

| # | Topic | Source IDs | Result | Review note |
|---:|---|---|---|---|
| 001 | SI base units and prefixes | SC001, SC002, SC004 | **PASS** | Base units, prefix powers, squared/cubed conversion and the candela/dimensional-analysis boundary are correct. Example: `3.6 mg mm^-3 = 3.6 × 10^3 kg m^-3`. |
| 002 | Energy-unit conversion | SC003 | **PASS** | `1 eV = 1.60 × 10^-19 J` and `1 kW h = 3.60 × 10^6 J` are used in the correct directions. `0.75 kW h = 2.70 × 10^6 J = 1.69 × 10^25 eV`. |
| 003 | Measurement errors and quality | SC005, SC006 | **PASS** | Zero offset is correctly identified as systematic; averaging is correctly limited to random scatter and does not remove the bias. |
| 004 | Absolute and percentage uncertainty | SC007 | **PASS** | Absolute, fractional and percentage uncertainty definitions and the `25.0 ± 0.2 cm` example are correct. |
| 005 | Combining uncertainties | SC008 | **PASS** | Absolute uncertainties are added for sums/differences and fractional uncertainties for products/quotients; the area example gives about `2.7%`. |
| 006 | Graph uncertainty and error bars | SC009 | **PASS** | Limiting gradients and half-range uncertainty are applied correctly: `(2.40 ± 0.33) N m^-1`. |
| 007 | Significant figures and uncertainty reporting | SC010 | **PASS** | The uncertainty/value decimal-place matching in `12.347 ± 0.26 m` is correct. |
| 008 | Order-of-magnitude estimation | SC011, SC012 | **PASS** | The classroom-air estimate and the nearest-power-of-ten test using `√10` are correct. |
| 009 | Scalar and vector quantities | SC013, SC014 | **PASS** | Classification and the `3-4-5` perpendicular-displacement example are correct; path distance is correctly distinguished from displacement. |
| 010 | Equilibrium and resultant force | SC015, SC016 | **REVISE** | The calculation `T sin 35° = 50 N` is valid only if the cable angle is **35° above the horizontal**. The example currently says only “at 35°”, so the angle reference must be added (or the component changed if the intended angle is from the vertical). |
| 011 | Moments, couples and the principle of moments | SC017, SC018, SC019 | **PASS** | Perpendicular-distance definition, couple moment and clockwise/anticlockwise balance are correct. The hinge example gives `100 N`. |
| 012 | Centre of mass | SC020 | **PASS** | The geometric-centre condition and `(1.0, 0.50, 0.25) m` coordinates for the uniform block are correct. |
| 013 | Kinematic quantities and average values | SC021, SC022 | **PASS** | Average speed `5.0 m s^-1` and average velocity `0 m s^-1` for a completed lap are correct. |
| 014 | Motion graphs | SC023 | **PASS** | The velocity-time gradient gives `2.0 m s^-2`; trapezium area gives `15 m` displacement. Signed-area guidance is correct. |
| 015 | Uniform acceleration equations | SC024 | **PASS** | Sign convention and use of `v² = u² + 2as` give the correct braking distance `50 m`. |
| 016 | Free-fall measurement of g | SC025 | **PASS** | For an `s` against `t²` graph, gradient `= g/2`; `4.82` gives `g = 9.64 m s^-2`. |
| 017 | Projectile components and calculation | SC026, SC027 | **PASS** | Components, shared time and maximum-height calculation are correct; horizontal distance in the example is about `17.7 m`. |
| 018 | Drag, lift and terminal speed | SC028, SC029 | **PASS** | Force balance at terminal speed, parachute opening and lower new terminal speed are described correctly. |
| 019 | Newton's laws and F = ma | SC030, SC031 | **PASS** | Resultant force `2100 N`, acceleration `1.75 m s^-2` and the correct third-law partner on the road are all correct. |
| 020 | Momentum conservation and collisions | SC032, SC033 | **PASS** | One-dimensional momentum signs, sticking collision speed `1.2 m s^-1` and perfectly inelastic classification are correct. |
| 021 | Impulse and force-time graphs | SC034 | **PASS** | The two-piece triangular force-time region has area `1.8 N s`; the unit equivalence is correct. |
| 022 | Impact time and force reduction | SC035 | **PASS** | For the same `3.0 kg m s^-1` momentum change, forces `300 N` and `60 N` at the two stopping times are correct. |
| 023 | Work and force-displacement graphs | SC036 | **PASS** | `W = Fs cos θ` is applied with the horizontal component; `40 × 5 × cos 60° = 100 J`. |
| 024 | Power and efficiency | SC037, SC038 | **PASS** | Useful output `8820 W` and efficiency `73.5%` (about `74%` to two significant figures) are correct. |
| 025 | Energy conservation and stores | SC039, SC040 | **PASS** | The reference-height qualification and `mgh = 1/2 mv²` calculation give `15.3 m s^-1`. |
| 026 | Resistive and elastic energy transfers | SC041 | **PASS** | `58.8 J - 36.0 J = 22.8 J` work against resistance is correct, with the correct energy-accounting interpretation. |
| 027 | Density | SC042 | **CLARIFY TRACEABILITY** | The mapped official source text combines density with Hooke's law and the elastic limit. The current topic correctly calculates density, but its source-point field does not describe a density-only statement. Keep the teaching split if desired, but record the Hooke/elastic-limit clause as cross-covered by Topic 028 rather than implying SC042 is fully taught here. |
| 028 | Hooke's law and spring constant | SC043 | **PASS** | The `4.0 cm` extension conversion and `k = 150 N m^-1` result are correct; the explanation properly distinguishes proportionality limit from elastic limit. |
| 029 | Stress, strain and breaking stress | SC044 | **CLARIFY TRACEABILITY** | `σ = 6.0 × 10^7 Pa` and `ε = 7.5 × 10^-4` are correct. The official SC044 wording also names elastic strain energy, which is taught in Topic 030; the outline should make that cross-topic treatment explicit. |
| 030 | Elastic strain energy | SC045 | **PASS** | For a linear force-extension graph, `1/2 F ΔL = 9.0 × 10^-2 J` is correct and the non-linear limitation is stated. |
| 031 | Material behaviour graphs | SC046 | **PASS** | Elastic versus plastic response, fracture, brittle behaviour and the initial stress-strain gradient are accurately described. |
| 032 | Young modulus calculation and graph | SC047, SC048 | **PASS** | `E = FL/(AΔL)` gives `1.5 × 10^11 Pa`; the graph interpretation is correct. |
| 033 | Young modulus practical | SC049 | **PASS** | Diameter sampling, micrometer use, fiducial marker, parallax control, elastic-range selection and best-fit analysis are appropriate. |
| 034 | Atomic model and scattering evidence | SC050, SC051 | **PASS** | Large-angle alpha scattering is correctly linked to a small, dense, positive nucleus. |
| 035 | Nuclear notation and specific charge | SC052, SC053 | **PASS** | The `^23_11Na+` proton/neutron/electron counts and electron specific-charge magnitude `1.76 × 10^11 C kg^-1` are correct. |
| 036 | Particle families and antiparticles | SC054, SC055 | **PASS** | Required antiparticle pairs, equal mass and opposite charge for charged partners are correctly stated. |
| 037 | Annihilation, pair production and rest energy | SC056, SC057 | **PASS** | Charge/momentum accounting for two-photon annihilation is correct, and the International AS `E = mc^2` calculation boundary is respected. |
| 038 | Alpha and beta decay equations | SC058 | **PASS** | The carbon-14 beta-minus equation correctly preserves `A`, raises `Z` by one, and includes the antineutrino. |
| 039 | Half-life from graphs and calculations | SC059 | **PASS** | Three half-lives reduce `960 Bq` to `120 Bq`; the exponential interpretation is correct. |
| 040 | Nuclear excited states and gamma emission | SC060 | **PASS** | Gamma emission from technetium-99m changes nuclear energy state without changing `A`, `Z` or element identity. |
| 041 | Alpha, beta and gamma properties and applications | SC061 | **REVISE** | The paper-thickness example selects beta and says alpha is stopped too easily. For the standard thickness-gauge mapping required here, state **alpha for very thin paper, beta for aluminium foil, and gamma for thicker steel/denser material**. The current example can mis-teach the radiation choice even though the general penetration/ionisation ordering is correct. |
| 042 | Inverse-square law and background radiation | SC062 | **PASS** | Background is subtracted before applying the inverse-square law and added back afterward; predicted measured rate `140 counts min^-1` is correct. |
| 043 | Current, potential difference and resistance | SC063, SC064, SC065 | **PASS** | `Q = 30 C`, `I = 1.0 A` and `R = 12 Ω` follow correctly from the three definitions. |
| 044 | I-V characteristics and Ohm's law | SC066, SC067 | **PASS** | Ohmic, filament-lamp and diode behaviour are correctly distinguished; the reciprocal-gradient reasoning for the lamp is correct. |
| 045 | Ideal ammeters and voltmeters | SC068 | **PASS** | Series ammeter, parallel voltmeter, zero/infinite ideal resistances and the short-circuit warning are correct. |
| 046 | Characteristic graph conventions | SC069 | **PASS** | An `I`-against-`V` gradient of `0.25 A V^-1` gives `R = 4.0 Ω`; the reversed gradient is correctly identified. |
| 047 | Resistivity | SC070 | **PASS** | Diameter conversion, circular area and `ρ = 1.9 × 10^-7 Ω m` are correct. |

## Required revisions before content approval

1. **Topic 010:** specify that the `35°` cable angle is measured above the
   horizontal, or rewrite the component equation to match the intended angle.
2. **Topic 041:** replace the paper-thickness example with the standard
   alpha/paper, beta/aluminium, gamma/steel mapping and retain the explanation
   that the selected radiation must produce a measurable count change.
3. **Topics 027 and 029:** make the cross-topic treatment of the official
   combined source statements explicit in the outline and provenance records.
   This preserves the practical teaching split without claiming that one
   topic alone covers every clause of SC042 or SC044.

No source JSON, HTML, script or image asset was modified during this audit.
