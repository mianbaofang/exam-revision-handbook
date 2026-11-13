# OxfordAQA International AS Physics 2027 — Historical Superseded Review

> **Status update (2026-09-09):** This 001–047 review records a pre-repair
> candidate and is **superseded**. The listed issues were resolved in the
> current 94-topic artifact. Do not use this report as the current approval
> decision; use `artifacts/as-physics-2027-review/agent-product-review.json`
> and the current delivery pointers instead.

## Final content review: topics 001-047

**Review date:** 2026-09-09  
**Route:** OxfordAQA International Advanced Subsidiary Physics, International market, 2027  
**Scope:** topics 001-047 in `artifacts/as-physics-2027-review/concepts/concept_explanations.json`  
**Review type:** independent source, physics, worked-example, and topic-split review  
**Formal delivery status:** not approved by this report

## Conclusion

All 47 topics in the current concept file were read and matched to the current
outline and OxfordAQA specification evidence. The split is generally based on
atomic examinable points and teachable procedures, not a one-to-one rename of
official section headings.

The range is **not content-clean yet**. Five bounded revisions or traceability
clarifications remain:

1. Topic 001 does not explicitly teach derived SI units.
2. Topic 006 does not explain the graph-uncertainty method when no error bars are
   supplied.
3. Topics 027 and 029 split official combined statements across adjacent topics;
   this cross-topic treatment must be recorded explicitly.
4. Topic 035 calculates electron specific charge but does not explicitly cover
   the required proton, nucleus and ion comparisons.

Topic 010 now explicitly says that the cable angle is 35 degrees above the
horizontal, so its component equation is valid. Topic 041 now uses the standard
alpha/paper, beta/aluminium foil and gamma/thicker steel mapping. Both earlier
issues are closed in the current concepts file.

This report does not approve generated visuals, rendered HTML, or PDF delivery.

## Evidence and method

Reviewed:

- `artifacts/as-physics-2027-review/concepts/concept_explanations.json`
- `artifacts/as-physics-2027-review/syllabus-outline.json`
- `artifacts/as-physics-2027-review/syllabus-evidence.json`
- `artifacts/as-physics-2027-review/qualification.json`
- local OxfordAQA International AS Physics specification extraction

Every entry was checked for title/source alignment, scope boundaries, definitions,
equations, signs, units, numerical arithmetic, solution-step logic, and visual
fields. All numerical examples in this range were independently recalculated.

## Topic verdicts

`PASS` means no factual or numerical correction is required in the current entry.
`ISSUE` means a bounded content revision is required. `TRACE` means the teaching
split is acceptable but provenance must record the official combined statement.

| No. | Topic | Verdict | Review note |
|---:|---|---|---|
| 001 | SI base units and prefixes | ISSUE | Add derived SI units, for example `N = kg m s^-2` and `J = kg m^2 s^-2`. |
| 002 | Energy-unit conversion | PASS | J/eV and kW h/J conversions are correct. |
| 003 | Measurement errors and quality | PASS | Random/systematic error and quality terms are correctly distinguished. |
| 004 | Absolute and percentage uncertainty | PASS | Definitions and example are correct. |
| 005 | Combining uncertainties | PASS | Sum, product, quotient and power rules are correct. |
| 006 | Graph uncertainty and error bars | ISSUE | Add guidance for graphs without error bars; retain limiting-line method where error bars exist. |
| 007 | Significant figures and uncertainty reporting | PASS | Value/uncertainty decimal-place rule is correct. |
| 008 | Order-of-magnitude estimation | PASS | Estimation and nearest-power-of-ten reasoning are correct. |
| 009 | Scalar and vector quantities | PASS | Classifications and vector addition are correct. |
| 010 | Equilibrium and resultant force | PASS | Current text states 35 degrees above the horizontal; calculation is valid. |
| 011 | Moments, couples and principle of moments | PASS | Definitions and balance calculation are correct. |
| 012 | Centre of mass | PASS | Geometric-centre treatment is correct. |
| 013 | Kinematic quantities and average values | PASS | Average speed and velocity example are correct. |
| 014 | Motion graphs | PASS | Gradient and signed-area interpretation are correct. |
| 015 | Uniform acceleration equations | PASS | Sign convention and braking example are correct. |
| 016 | Free-fall measurement of g | PASS | `gradient = g/2` treatment is correct. |
| 017 | Projectile components and calculation | PASS | Components and numerical example are correct. |
| 018 | Drag, lift and terminal speed | PASS | Force balance and terminal-speed explanation are correct. |
| 019 | Newton's laws and F = ma | PASS | Laws, resultant force and third-law partner are correct. |
| 020 | Momentum conservation and collisions | PASS | Signs, conservation and collision classification are correct. |
| 021 | Impulse and force-time graphs | PASS | Area/impulse calculation and units are correct. |
| 022 | Impact time and force reduction | PASS | Longer stopping time/lower force relationship is correct. |
| 023 | Work and force-displacement graphs | PASS | `W = Fs cos theta` and area interpretation are correct. |
| 024 | Power and efficiency | PASS | Power and efficiency calculations are correct. |
| 025 | Energy conservation and stores | PASS | Reference height and energy conversion are correct. |
| 026 | Resistive and elastic energy transfers | PASS | Energy accounting is correct. |
| 027 | Density | TRACE | Density is correct; Hooke's law and elastic limit from the combined source are cross-covered by Topic 028. |
| 028 | Hooke's law and spring constant | PASS | Stiffness, extension and elastic-limit distinction are correct. |
| 029 | Stress, strain and breaking stress | TRACE | Calculations are correct; elastic strain energy from the combined source is taught in Topic 030 and needs explicit cross-reference. |
| 030 | Elastic strain energy | PASS | Force-extension area calculation is correct. |
| 031 | Material behaviour graphs | PASS | Elastic, plastic, fracture and brittle behaviour are correct. |
| 032 | Young modulus calculation and graph | PASS | Formula, units and graph interpretation are correct. |
| 033 | Young modulus practical | PASS | Measurement controls and graph choices are appropriate. |
| 034 | Atomic model and scattering evidence | PASS | Rutherford evidence is correctly interpreted. |
| 035 | Nuclear notation and specific charge | ISSUE | Add explicit proton, nucleus and ion specific-charge comparisons. |
| 036 | Particle families and antiparticles | PASS | Antiparticle identities and charge/mass relations are correct. |
| 037 | Annihilation, pair production and rest energy | PASS | Conservation statements and AS boundary are correct. |
| 038 | Alpha and beta decay equations | PASS | Decay bookkeeping and neutrino terms are correct. |
| 039 | Half-life from graphs and calculations | PASS | Half-life calculation and exponential interpretation are correct. |
| 040 | Nuclear excited states and gamma emission | PASS | Gamma emission changes energy state, not `A` or `Z`. |
| 041 | Alpha, beta and gamma properties and applications | PASS | Current mapping is alpha/paper, beta/aluminium foil, gamma/thicker steel. |
| 042 | Inverse-square law and background radiation | PASS | Background subtraction/restoration is correct. |
| 043 | Current, potential difference and resistance | PASS | Definitions and numerical example are correct. |
| 044 | I-V characteristics and Ohm's law | PASS | Ohmic, lamp and diode behaviour are correct. |
| 045 | Ideal ammeters and voltmeters | PASS | Ideal resistance assumptions and connections are correct. |
| 046 | Characteristic graph conventions | PASS | Axis convention and reciprocal-gradient reasoning are correct. |
| 047 | Resistivity | PASS | Area conversion and resistivity result are correct. |

## Required revisions

### Topic 001: derived SI units

Add: “Derived SI units are formed by combining SI base units; for example,
`N = kg m s^-2` and `J = kg m^2 s^-2`.” Keep dimensional analysis outside the
route if that remains the qualification boundary.

### Topic 006: graphs with and without error bars

Add: “If no error bars are provided, use the spread of the measured points and
the stated measurement information to judge acceptable steepest and shallowest
lines. Do not invent error bars or treat the best-fit line alone as an
uncertainty estimate.”

### Topic 035: specific charge comparisons

Add a proton/nucleus/ion comparison: for a proton, `q/m = +e/m_p`; for a fully
ionised nucleus with proton number `Z` and nucleon number `A`,
`q/m = Ze/m_nucleus` approximately; for an ion, use its net charge and ion mass.
State the sign when direction matters and magnitude when requested.

## Source-traceability clarifications

The official source statement mapped to Topic 027 combines density, Hooke's law
and elastic limit. Record it as cross-covered by Topics 027-028. The source
statement mapped to Topic 029 also names elastic strain energy; record it as
cross-covered by Topics 029-030. These are traceability repairs, not numerical
failures.

## Numerical checks

Independent recalculation confirmed the current results, including:

| Topic | Result |
|---:|---:|
| 001 | `3.6 x 10^3 kg m^-3` |
| 002 | `2.70 x 10^6 J = 1.69 x 10^25 eV` |
| 004 | `0.8%` |
| 005 | `2.73%` |
| 006 | `0.325`, reported as `0.33 N m^-1` |
| 008 | about `1.4 x 10^2 kg` |
| 009 | `5.0 m` |
| 010 | `87 N` |
| 013 | `5.0 m s^-1`, average velocity `0` |
| 014 | `2.0 m s^-2`, `15 m` |
| 015 | `50 m` |
| 016 | `9.64 m s^-2` |
| 017 | `1.02 s`, `17.7 m` |
| 019 | `1.75 m s^-2` |
| 020 | `1.2 m s^-1` |
| 021 | `1.8 N s` |
| 023 | `100 J` |
| 024 | `8820 W`, `73.5%` |
| 025 | `15.3 m s^-1` |
| 026 | `22.8 J` |
| 027 | `2.70 x 10^3 kg m^-3` |
| 028 | `150 N m^-1` |
| 029 | `6.0 x 10^7 Pa`, `7.5 x 10^-4`, `1.0 x 10^8 Pa` |
| 030 | `0.090 J` |
| 032 | `1.5 x 10^11 Pa` |
| 035 | `1.76 x 10^11 C kg^-1` for electron magnitude |
| 039 | `120 Bq` |
| 042 | `140 counts min^-1` |
| 043 | `30 C`, `1.0 A`, `12 ohm` |
| 046 | `4.0 ohm` |
| 047 | `1.9 x 10^-7 ohm m` |

## Final review state

After the three content revisions and two traceability updates above, rerun this
47-topic review against the repaired concepts and outline files. The current
report does not approve HTML, visuals, or PDF.

**Current status:** `draft-review-required` / `delivery_eligible: false`
