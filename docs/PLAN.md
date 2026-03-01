# Guardrail: Multi-Domain Symptom-to-Signal Translation for TKOS

## One-Line Pitch

A symptom-to-signal translation layer for Triadin Knockout Syndrome that converts the full lived experience of a TKOS child — cardiac instability, skeletal myopathy, medication burden, sleep disruption, exercise intolerance, psychological load, and school participation — into structured, longitudinal, clinician-usable signals, shifting the paradigm from reactive crisis response to proactive daily enablement.

---

## How This Answers the Hackathon Track

This project addresses **both** sub-challenges of Track 3: Symptom Management.

| Track Requirement | How Guardrail Delivers |
|---|---|
| **3.1 General — Flare-Week Planner** | A TKOS-specific "flare mode" that detects converging risk factors (missed dose + poor sleep + heat + elevated HR), generates daily checklists, and auto-produces clinician-ready summaries of what changed from baseline |
| **3.1 General — Emergency Brief Generator** | A cardiac passport + one-page brief with diagnosis, meds, ICD settings, QT-prolonging drug contraindications, and care team contacts — printable, exportable, and wallet-card-ready |
| **3.2 Narrow — Symptom-to-Signal Translation** | The core product: convert patient-reported symptoms + passive biometrics across **multiple domains** into structured signals (baseline vs. deviation, timelines, triggers, functional impact) that clinicians can interpret in a short visit |

### Specific Judging Criteria Alignment

- **Structured signals, not just summaries** — compound risk model produces a four-state classification (green/yellow/orange/red) with explicit evidence for what drove each state, including uncertainty and data gaps
- **Interpretable for clinical use** — auto-generated visit PDF shows risk distribution over time, event context reconstruction, trigger correlation analysis, and medication adherence patterns
- **Safe by design** — no diagnostic claims; escalation templates ("consider contacting... if..."); QT-prolonging drug safety net; documented scope limits and honest gaps
- **Evaluation plan** — case replays, clinician summary comparison, drug interaction audit, alert calibration testing

---

## Why TKOS, and Why This Framing

### The Disease in 60 Seconds

Triadin Knockout Syndrome is an ultra-rare inherited cardiac arrhythmia syndrome (~340 patients worldwide) caused by complete absence of the triadin protein. Key facts from the [International TKOS Registry](https://www.ahajournals.org/doi/10.1161/CIRCGEN.118.002419):

- **95%** of patients present with cardiac arrest or syncope by age 10 (avg. age 3)
- **74%** have recurrent breakthrough cardiac events despite aggressive treatment (nadolol, flecainide, ICDs)
- **29%** have [congenital skeletal myopathy](https://pmc.ncbi.nlm.nih.gov/articles/PMC5373784/) — proximal muscle weakness from loss of triadin in skeletal muscle
- Electrocardiographic features overlap with LQTS, CPVT, and Brugada — creating diagnostic confusion
- Current care = blunt activity restriction ("don't exercise"), fragmented specialist visits, chronic emergency preparedness

### The Strategic Positioning

**What we are NOT building:** Another cardiac monitor. Apple Watch detects AF in elderly populations — it explicitly doesn't work for rare channelopathies, and it monitors one signal in isolation.

**What we ARE building:** The first multi-domain symptom-to-signal translation layer for an ultra-rare disease. We take the full lived experience of a child with TKOS — cardiac symptoms, muscle weakness, medication side effects, energy levels, psychological burden, school participation — and translate that into structured, domain-specific clinician signals that don't exist anywhere today.

The cardiac piece stays as one important domain, but it stops being the whole product.

### What Doesn't Exist Today

| Gap | Why It Matters |
|---|---|
| **No multi-stream context fusion for rare channelopathies** | Every existing tool monitors the heart *in isolation*. Apple Watch's ECG app is [not recommended for patients with known arrhythmias other than AF](https://pmc.ncbi.nlm.nih.gov/articles/PMC10202692/) — it's not designed for CPVT, LQTS, or TKOS patients at all |
| **No symptom-to-signal translation for ultra-rare cardiac syndromes** | Existing rare disease apps focus on [community connection and education](https://pmc.ncbi.nlm.nih.gov/articles/PMC8357707/) rather than structured symptom tracking or clinician-ready signal generation |
| **No "permission system" framing** | Every existing product is a warning system — it tells you when something is wrong. Nothing tells a TKOS kid "today is safe to play." That's a genuinely novel UX paradigm |
| **No multi-domain bridging** | Nobody unifies cardiac + myopathy + medication burden + psychological impact + functional capacity in one structured longitudinal view |

---

## System Design: Three Layers

### Layer 1 — Clinical Foundation (Onboarding + EHR Context)

Before real-time signals make sense, the system must understand THIS patient's clinical profile. With ~340 patients worldwide, generic thresholds are meaningless.

**Onboarding captures:**
- Diagnosis, genotype/subtype, ICD device settings if implanted
- Personal exercise stress test results (ectopy onset HR = the single most important threshold)
- ICD interrogation history (shock dates, preceding rhythms, clustering patterns)
- Medication schedule (names, doses, timing, QT risk category via CredibleMeds)
- Known personal triggers (exercise, fever, startle, sleep deprivation, specific drugs)
- Skeletal muscle status (myopathy presence/severity for the 29%)

**NLP extraction from clinical notes** (via LLM):
- Pre-event context ("playing tag at a birthday party in July heat")
- Prodromal descriptions ("child said he felt heavy 10 min before")
- Treatment response patterns ("ectopy reduced after adding flecainide but returned in summer")
- Clinician severity language ("I remain concerned despite maximal therapy" vs. "stable")

### Layer 2 — Passive Multi-Domain Context Engine (Zero Burden)

This is the core differentiator. Every stream below is captured **without additional user action** beyond wearing an Apple Watch and carrying a phone.

#### Cardiac Domain

| Signal | Source | TKOS Relevance |
|---|---|---|
| HR (bpm), RR interval, QTc, ectopic beat flag | Apple Watch + custom QTc extraction | Primary cardiac signal; deviation from personal baseline |
| RMSSD (HRV) | Apple Watch native | HRV depression = sympathetic shift = increased arrhythmia substrate |
| SpO2 + nocturnal desaturation flag | Apple Watch native | Nocturnal events, respiratory compromise |

#### Functional / Musculoskeletal Domain

| Signal | Source | TKOS Relevance |
|---|---|---|
| Steps/min, METs, sedentary bout duration | Apple Watch native | Tracks exercise capacity and daily functional output |
| Exercise intensity zone, HR recovery post-exertion | Apple Watch + decay curve | Recovery trajectory reveals autonomic dysfunction |
| Daily training load (TRIMP), acute:chronic ratio | Computed from HR + activity | Detects overexertion patterns before events |

#### Medication & Pharmacological Domain

| Signal | Source | TKOS Relevance |
|---|---|---|
| Time since last dose, pharmacokinetic decay model | One-tap confirmation + nadolol half-life model | Nadolol t½ = 20-24h; risk increases at trough |
| QT-prolonging drug flag | CredibleMeds database | Prevents iatrogenic QT prolongation from ER/dentist/dermatologist |

#### Sleep & Recovery Domain

| Signal | Source | TKOS Relevance |
|---|---|---|
| TST, efficiency, WASO, rolling 14-day debt | Apple Watch + rolling deficit computation | Sleep deprivation depresses HRV, increases sympathetic tone |
| Nocturnal bradycardia flag | Apple Watch | Detects overnight autonomic abnormalities |
| Sleep midpoint timing, social jetlag | Computed | Circadian disruption as risk modifier |

#### Environmental Domain

| Signal | Source | TKOS Relevance |
|---|---|---|
| Ambient temperature + humidity | Weather API via GPS | Heat increases cardiac workload, documented arrhythmia trigger |
| Calendar context (PE class, exams, appointments) | Calendar API (opt-in) | Planned exertion or stress contexts |
| Wrist temp delta from personal baseline, fever flag | Apple Watch Series 8+ | Fever: +~10 bpm/°F, independent arrhythmia trigger |

#### Psychosocial & Subjective Domain

| Signal | Source | TKOS Relevance |
|---|---|---|
| Voice biomarkers: speech rate, pause frequency, F0, jitter, shimmer, HNR | Morning voice prompt + openSMILE | Vocal changes correlate with fatigue, medication side effects, psychological state |
| Voice symptom log ("I feel heavy", "dizzy", "heart is fast") | Siri shortcut — one sentence, no screen | Timestamped against surrounding biometric data |

#### Documented Gaps (Honest Limitations)

- **Electrolytes (K+, Mg2+)** — major arrhythmia trigger, untrackable passively. Periodic lab integration can partially address.
- **Continuous QTc stream** — Apple Watch is on-demand, not beat-to-beat.
- **Actual drug serum levels** — needs lab, not sensor.
- **Posture** — too inaccurate at wrist; dropped.
- **Meal tracking** — requires active logging; not core.

### Layer 3 — Signal Translation & Human Interface

#### The Compound Risk Model

Individual factors feed into a weighted score:

```
RiskState = weighted_sum(
    HR_deviation_from_personal_baseline   × w1,
    activity_context_mismatch_score       × w2,   // high HR + low activity = high signal
    HRV_depression_from_7day_baseline     × w3,
    medication_decay_factor               × w4,   // f(hours_since_dose, drug_half_life)
    temperature_risk_factor               × w5,   // above 85°F begins scaling
    sleep_deficit_factor                  × w6,   // < 6 hours = elevated
    circadian_risk_weight                 × w7,   // morning surge, evening trough
    fever_flag                            × w8,
    days_since_last_event                 × w9,   // event clustering modifier
    stress_context_flag                   × w10,
    myopathy_functional_decline           × w11,  // for the 29% with skeletal involvement
    voice_deviation_score                 × w12
)
```

Weights initialize from clinical literature defaults, then adapt per-patient over time.

#### Output: Four-State Permission System (Not Warning System)

| State | Meaning | User Experience |
|---|---|---|
| Green | All factors within baseline range | **"Good conditions today. Enjoy your day."** Active permission — the emotional core of the product |
| Yellow | 1-2 factors mildly elevated | "Take it easier — [plain-language reason]." Gentle nudge |
| Orange | Multiple converging factors or single severe factor | "Stick to calm activities. Here's why: [factors]." Clear guidance |
| Red | Acute concern — sustained anomalous HR without activity context, or manual trigger | Emergency cascade activates |

For a child who lives under constant restriction, being told "today is a good day to ride your bike" is a fundamentally different life than one who only hears "don't."

#### For the Patient/Family (Daily)

- **Morning briefing**: "You slept well, meds are on board, it'll be 72°F — good day ahead."
- **Watch face companion**: Ambient color border (green → yellow → orange) — no numbers, no alarms, intuitive self-regulation
- **Activity pre-check**: "I want to play basketball" → system evaluates current state → "Looks good for 20-30 min" or "Maybe pick something lighter — your HR has been elevated and it's hot"
- **Voice symptom logger**: One sentence via Siri shortcut, timestamped with surrounding biometric context
- **One-tap medication log**: Single notification, single tap, drives the pharmacokinetic model

#### For the Caregiver (Ambient)

- **Parent mirror app**: Real-time risk state on parent's phone. Green = peace of mind. Configurable thresholds (teen may want parent notified only at orange).
- **Emergency cascade**: Red state → auto-send cardiac passport to emergency contacts → display simplified instructions on child's watch → capture all sensor data for clinical review

#### For the Clinician (Periodic) — The Symptom-to-Signal Translation Output

This is where the hackathon track's core ask is delivered. Auto-generated visit-ready summary:

1. **Risk state distribution**: % time in green/yellow/orange over reporting period — a single metric that captures disease burden longitudinally
2. **Event timeline with full context reconstruction**: what was happening across ALL data streams before, during, and after each event
3. **Baseline vs. deviation signals**: structured format showing which domains shifted, when, by how much, and with what confidence
4. **Trigger correlation analysis**: "Events cluster when: temp > 85°F + sleep < 6h" — hypothesis for clinician, not diagnosis
5. **Medication adherence + pharmacokinetic correlation**: missed doses mapped against elevated risk periods
6. **Multi-domain functional trajectory**: activity capacity trend, myopathy progression (if applicable), sleep quality, voice biomarker trends
7. **Side effect burden tracking**: beta-blocker fatigue, exercise intolerance severity
8. **Patient-reported symptoms mapped against biometrics**: "felt heavy" correlated with HR/HRV at that timestamp
9. **Data quality & missingness report**: what the system doesn't know, so the clinician can ask

#### Emergency Brief / Cardiac Passport

One-page printable + wallet card + QR code:
- Diagnosis (TKOS), genotype, baseline status, typical flare signs
- All meds/allergies, ICD settings, QT-prolonging drug contraindications
- Care team contacts + preferred hospital
- "Must know" section for ER: what NOT to administer, communication needs

---

## Flare Mode (Track 3.1 Alignment)

When the system detects converging risk factors or the caregiver manually activates "flare mode":

**Inputs during flare:**
- Increased check-in frequency (severity sliders + yes/no red flags)
- Baseline function profile comparison (sleep, mobility, pain, energy, behavior)

**Outputs during flare:**
- Daily plan/checklist: hydration reminders, rest targets, symptom log prompts, appointment prep
- **Auto-generated clinician message**: what changed from baseline, timeline, key metrics across all domains, suggested questions to ask — saves hours of manual email writing
- Escalation guidance templates: "Consider contacting your electrophysiologist if: [specific thresholds reached]"
- School/activity accommodation letter template with current functional status

---

## Technical Stack (Hackathon MVP)

| Component | Technology | Demo Scope |
|---|---|---|
| Mobile app | React Native or Swift (iOS-first) | Core UI: risk state, morning briefing, activity pre-check, med log, flare mode |
| Wearable integration | Apple HealthKit API | HR, HRV, SpO2, sleep, activity, temperature |
| Environmental context | CoreMotion + OpenWeatherMap API | Activity state + weather |
| Voice biomarkers | openSMILE + morning prompt | Speech rate, jitter, shimmer extraction |
| Risk model | Weighted scoring engine (Python/JS) | Literature-based defaults, simulated personalization |
| EHR simulation | FHIR-formatted sample data | Pre-loaded synthetic TKOS patient with stress test, ICD history, clinical notes |
| NLP on clinical notes | Claude API | Extract triggers, prodromal patterns, treatment response from sample notes |
| Clinician report | Auto-generated PDF | Visit summary with multi-domain signal translation |
| Drug interaction check | CredibleMeds QT drug list (static DB) | Cross-reference prescriptions against QT-prolonging drugs |
| Emergency passport | Structured data → PDF/QR | One-page brief + wallet card |

**Live demo vs. design mockup:**
- **Live:** Risk model on simulated patient data showing compound factor shifts. Clinician PDF generation. Drug interaction check. Emergency passport. Flare mode workflow.
- **Designed:** Watch face companion, parent mirror app, voice logger, full HealthKit integration.

---

## Evaluation Plan

| Method | What It Proves | Track Alignment |
|---|---|---|
| **Case replay** (3 published TKOS scenarios) | Risk model flags elevated risk before documented events; emergency passport contains all critical safety info | 3.2 — structured signals detect deterioration |
| **Clinician summary comparison** | Visit PDF vs. typical parent email: measures completeness, structure, time saved | 3.1 — actionable outputs, time saved |
| **Drug interaction audit** (20 common ER meds) | System correctly flags QT-prolonging contraindications (ondansetron, azithromycin, etc.) | 3.1 — safety, emergency brief |
| **Alert calibration** (1 week simulated data) | Appropriate risk states — no false reds, greens align with genuinely safe conditions | 3.2 — structured signals with evidence |
| **Multi-domain signal completeness** | Output covers cardiac + musculoskeletal + medication + sleep + psychological + functional — not just heart | 3.2 — multi-domain, not single-stream |
| **Flare scenario walkthrough** (3 scripted flares) | Summaries capture key changes, avoid unsafe advice, produce usable clinician messages | 3.1 — flare week planner validation |

---

## Why This Wins

1. **It answers the exact prompt** — symptom-to-signal translation is the 3.2 challenge title, and we deliver it across multiple domains, not just cardiac.
2. **Nobody is doing this** — no existing tool bridges cardiac + myopathy + medication burden + psychological impact + functional capacity for rare channelopathies.
3. **It's a permission system, not a warning system** — telling a TKOS child "today is safe to play" is a genuinely novel UX paradigm that no competitor offers.
4. **It doesn't compete with Apple Watch** — it builds ON wearable data but adds the multi-stream context fusion and TKOS-specific clinical interpretation that consumer devices cannot provide.
5. **It addresses a real, documented need** — 74% breakthrough event rate means current care infrastructure is failing these 340 children.
6. **It's honest about scope** — documented gaps (electrolytes, continuous QTc, serum drug levels), clear escalation guidance, no diagnostic claims.
7. **It scales beyond TKOS** — the architecture (personalized baseline → passive multi-stream sensing → compound risk model → permission UX → clinician signal extraction) transfers to CPVT, LQTS, Brugada, and any episodic rare disease.
8. **It centers humanity** — a child who hears "good day to ride your bike" is living a fundamentally different life than one who only hears "don't."

---

## Sources

- [International Triadin Knockout Syndrome Registry](https://www.ahajournals.org/doi/10.1161/CIRCGEN.118.002419) — Circulation: Genomic and Precision Medicine
- [Congenital myopathy associated with triadin knockout syndrome](https://pmc.ncbi.nlm.nih.gov/articles/PMC5373784/) — PMC
- [Cellular and electrophysiological characterization of TKOS](https://pmc.ncbi.nlm.nih.gov/articles/PMC10202692/) — PMC
- [Patient reported outcome measures in rare diseases](https://pmc.ncbi.nlm.nih.gov/articles/PMC8357707/) — PMC
- [Triadin mutations — ventricular arrhythmias in children](https://jcongenitalcardiology.biomedcentral.com/articles/10.1186/s40949-017-0011-9) — Journal of Congenital Cardiology
- [Characterization and Treatment of TKOS](https://grantome.com/grant/NIH/F31-HL149131-01A1) — NIH Grant
