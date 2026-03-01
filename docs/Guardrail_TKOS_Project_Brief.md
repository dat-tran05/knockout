# Guardrail: Intelligent Rare Disease Life Management for TKOS

## One-Line Pitch

A context-aware life management platform for Triadin Knockout Syndrome that fuses wearable biometrics, passive environmental sensing, EHR-extracted clinical baselines, and low-burden patient reporting into a unified system that enables safe activity, detects compound risk escalation, and generates clinician-ready longitudinal signals — shifting rare disease care from reactive crisis response to proactive daily living.

---

## The Problem

Triadin Knockout Syndrome (TKOS) is an ultra-rare inherited cardiac arrhythmia syndrome (~340 patients worldwide) caused by complete absence of the triadin protein in the cardiac calcium release unit. 95% of patients present with cardiac arrest or syncope by age 10, 74% have recurrent life-threatening breakthrough cardiac events despite aggressive treatment, and current care is defined by blunt activity restriction ("don't exercise"), fragmented specialist visits, and chronic emergency preparedness with no systematic daily management infrastructure.

The result: children and families live in a permanent state of anxious restriction, clinicians make decisions based on sparse visit snapshots rather than longitudinal patterns, and the gap between "surviving" and "living well" remains unaddressed.

---

## The Core Insight

Heart rate data without context is noise. A heart rate of 110 bpm means something completely different depending on whether the patient is running, sitting still, in 95°F heat, 18 hours past their last nadolol dose, sleep-deprived, or emotionally stressed. Current approaches monitor one variable in isolation. We fuse multiple streams passively to make the signal interpretable — and flip the paradigm from "warning when things go wrong" to "enabling activity when conditions are safe."

---

## System Architecture: Three Layers

### Layer 1 — The Clinical Foundation (EHR Integration + Onboarding)

Before any real-time monitoring makes sense, the system needs to understand THIS specific patient's clinical profile. With ~340 patients worldwide, generic thresholds are useless. Every parameter must be personalized.

**EHR Data Extraction (via FHIR API / manual clinician input at onboarding):**

| Data Source | What We Extract | How It's Used |
|---|---|---|
| Exercise stress test reports | Personal ectopy onset heart rate, max safe HR, type of ectopy observed (PVCs, couplets, bigeminy), onset conditions | Sets personalized HR safety thresholds — the single most important parameter |
| ICD interrogation logs | Shock history (dates, times, preceding rhythm, duration), anti-tachycardia pacing events, ventricular ectopy burden trends | Feeds event history timeline, detects clustering patterns, calibrates risk model |
| ECG reports (serial) | QTc measurements over time, T-wave inversion pattern, any transient QT prolongation episodes | Tracks disease trajectory, identifies periods of increased electrical instability |
| Medication records | Current drugs, dosages, changes over time, documented reasons for changes | Models pharmacokinetic decay curves, correlates med changes with symptom changes |
| Clinical notes (NLP extraction) | Event descriptions (what was patient doing, environmental conditions, preceding symptoms), clinician assessments of severity trajectory, documented triggers | Builds personalized trigger profile, extracts prodromal patterns from past events |
| Echocardiogram reports | Structural normality confirmation, any functional changes over time | Baseline confirmation, long-term structural monitoring |
| Skeletal muscle assessments | Myopathy presence/severity, functional capacity notes | Tracks the 29% with skeletal involvement, often under-monitored |

**Why this matters:** A patient whose stress test showed ectopy onset at 95 bpm needs a very different alert threshold than one whose onset was at 125 bpm. A patient with 3 ICD shocks in the past month is in a different risk stratum than one with zero events in 2 years. A patient whose clinical notes consistently mention events occurring "after waking from naps" has a different trigger profile than one whose events cluster during competitive swimming. This granularity currently lives in scattered paper records and clinician memory — systematizing it is foundational.

**NLP on Clinical Notes — Specific Value for TKOS:**

Clinical notes contain unstructured gold that no structured EHR field captures:

- **Pre-event context:** "Patient was playing tag at a birthday party in July heat when he collapsed" — this gives us activity type (high-intensity intermittent), social context (may resist stopping), environmental factor (heat), and event type (collapse vs. syncope vs. ICD shock).
- **Prodromal descriptions:** "Mother reports the child said he 'felt heavy' and sat down 10 minutes before the event" — this identifies a patient-specific prodromal signal that can be added to the voice logger's tag library.
- **Treatment response patterns:** "Ectopy reduced after adding flecainide but returned during summer months" — seasonal/temperature sensitivity pattern.
- **Clinician risk assessment language:** "I remain concerned about this patient's event frequency despite maximal therapy" vs. "stable and well-controlled" — sentiment extraction from specialist notes provides a clinical severity signal.

The NLP layer doesn't need to be perfect — even partial extraction creates dramatically more structure than what exists today (nothing).

---

### Layer 2 — The Passive Context Engine (Real-Time, Zero Effort)

This is the core technical differentiator. Every data stream here is captured without ANY additional user action beyond wearing their Apple Watch and carrying their phone.

**Data streams and clinical rationale:**

| Stream | Source | Why It Matters for TKOS | Technical Implementation |
|---|---|---|---|
| Heart rate (continuous) | Apple Watch / HealthKit | Primary cardiac signal; deviation from personal baseline (established via EHR + 4-week calibration) indicates potential instability | HealthKit background delivery, sampled every 5-10 sec during activity |
| Heart rate variability | Apple Watch / HealthKit | HRV depression = shift toward sympathetic dominance = increased arrhythmia substrate; documented pre-arrhythmia signal in channelopathy patients | SDNN and RMSSD from HealthKit, compared to 7-day rolling personal baseline |
| Activity state | CoreMotion framework | Distinguishes "HR 110 while running" (expected) from "HR 110 while sitting" (alarming); classifies stationary/walking/running/cycling/driving | CMMotionActivityManager, continuous background |
| Ambient temperature + humidity | Weather API via GPS location | Heat increases cardiac workload, accelerates dehydration, shifts electrolytes; documented arrhythmia risk factor in LQTS/CPVT | OpenWeatherMap API call every 30 min based on device location |
| Medication timing | User one-tap confirmation | Nadolol half-life = 20-24h; system models drug concentration decay curve from last confirmed dose; risk increases at trough | Single daily notification → tap to confirm → pharmacokinetic decay model runs automatically |
| Sleep duration + quality | Apple Watch sleep tracking | Sleep deprivation depresses HRV, increases sympathetic tone, independently increases arrhythmia risk | HealthKit sleep analysis data, compared to personal baseline |
| Skin temperature trend | Apple Watch Series 8+ | Fever detection — increases resting HR ~10 bpm/°F, independently increases arrhythmia risk; also detects illness onset | HealthKit wrist temperature data |
| Calendar context | Calendar API (opt-in) | Detects planned high-exertion activities (PE class, swim practice), stress contexts (exams), medical appointments | EventKit framework, read-only |
| Time of day | System clock | Early morning catecholamine surge on waking; medication trough timing for once-daily dosing; circadian arrhythmia risk variation | Automatic |

**The Compound Risk Model:**

Individual factors feed into a weighted risk score:

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
    stress_context_flag                   × w10
)
```

Weights initialize from clinical literature defaults, then adapt per-patient over time using logged events as ground truth. With enough data points per patient (~6+ months), the model learns which factors matter most for EACH individual.

**Output: Four-state risk classification**

| State | Meaning | User Experience |
|---|---|---|
| 🟢 Green | All factors within baseline range | "Good conditions today. Enjoy your day." Active permission. |
| 🟡 Yellow | 1-2 factors mildly elevated | "Take it a bit easier — [plain-language reason]." Gentle nudge. |
| 🟠 Orange | Multiple converging factors or single severe factor | "Stick to calm activities right now. Here's why: [factors]." Clear guidance. |
| 🔴 Red | Acute concern — sustained anomalous HR without activity context, or manual trigger | Emergency cascade activates. |

**Critical UX principle:** Green is not the absence of alerts. Green is an active, affirmative message. For a child who lives under constant restriction, being told "today is a good day" is the product's emotional core.

---

### Layer 3 — The Human Interface (Minimal Burden, Maximum Signal)

**For the patient/family (daily):**

- **Morning briefing** (push notification): Today's risk baseline based on last night's sleep, medication status, weather forecast, and any planned activities. "You slept well, meds are on board, it'll be 72°F — good day ahead."
- **Live activity companion** (watch face): Ambient color border (green → yellow → orange) that shifts as HR approaches personal threshold. No alarms, no numbers — just intuitive color that teaches self-regulation over time.
- **Activity pre-check** (optional tap): "I want to go play basketball" → system evaluates current risk state + activity intensity → "Looks good for 20-30 minutes, I'll keep watch" or "Maybe pick something lighter today — your HR has been a bit elevated and it's hot out."
- **Voice symptom logger** (Siri shortcut): "I feel heavy" / "dizzy" / "heart is fast" → timestamped, tagged against known prodromal signals, saved with surrounding 10 min of HR/HRV data. No screen, no form. One sentence.
- **One-tap medication log**: Single notification, single tap. Drives the pharmacokinetic model.

**For the caregiver (ambient):**

- **Parent mirror app**: Real-time risk state of child on parent's phone. Green = peace of mind. Yellow/orange = awareness without panic. Configurable alert thresholds (teen may want parent notified only at orange).
- **Emergency cascade**: If red state triggered → auto-send cardiac passport (diagnosis, meds, ICD info, contraindicated drugs, care team contacts) to emergency contacts → display simplified instructions on child's watch → capture all sensor data for clinical review.

**For the clinician (periodic):**

- **Visit-ready summary PDF** (auto-generated before scheduled appointments, pulled from calendar): 
  - Risk state distribution over reporting period (% time in green/yellow/orange)
  - Event timeline with full context reconstruction (what was happening across all data streams before, during, and after each event)
  - Medication adherence rate + correlation between missed doses and elevated risk periods
  - HR and HRV trend lines relative to personal baseline
  - Activity capacity trend (max sustained activity duration and intensity over time)
  - Trigger correlation analysis: "Events cluster when: temp > 85°F + sleep < 6h" (hypothesis for clinician, not diagnosis)
  - Patient-reported symptom patterns from voice logs, mapped against biometric data
  - Side effect burden tracking (beta-blocker fatigue, exercise intolerance severity)
  - Skeletal muscle symptom trajectory (for the 29% with myopathy)
  - QoL / anxiety scores if tracked

- **EHR-integrated event report**: When a significant cardiac event occurs, auto-generate a structured report compatible with clinical documentation standards: timestamp, preceding risk factors, biometric data stream, patient-reported symptoms, medication status, environmental conditions, event type and duration, post-event recovery trajectory.

---

## Differentiators Beyond the Hackathon Prompt

### 1. Permission System, Not Warning System
Most health monitoring tools are anxiety machines — they alert when things go wrong. Guardrail actively tells patients when things are RIGHT. This is the philosophical and UX differentiator: enabling life, not just preventing death.

### 2. QT-Prolonging Drug Safety Net
Built-in database (sourced from CredibleMeds) of medications that prolong the QT interval. When any caregiver enters a new prescription from ANY provider (dentist, dermatologist, urgent care), the system cross-checks against known QT-prolonging drugs and flags conflicts. This prevents a concrete, documented category of iatrogenic harm in LQTS/TKOS patients.

### 3. Travel Preparedness Module
Destination-specific emergency preparation: nearest hospital with electrophysiology capability, critical medical phrases in local language, medication supply planning across time zones, ICD documentation for airport security, climate-adjusted risk model parameters for the destination.

### 4. Community Data Layer (with consent)
With ~340 patients worldwide, every individual's longitudinal data is research-grade. Anonymized, aggregated data across users builds a living natural history dataset that complements the Mayo Clinic TKOS registry. This positions the platform as both a care tool and a research infrastructure — attractive to the Ackerman lab and future gene therapy trial designers.

### 5. Transferability to Adjacent Rare Diseases
The architecture (personalized baseline from EHR → passive multi-stream context sensing → compound risk model → permission/warning UX → clinician signal extraction) is disease-agnostic. TKOS is the beachhead, but the same system adapts to CPVT, LQTS, Brugada syndrome, and potentially any condition where:
- Events are episodic and life-threatening
- Triggers are multi-factorial and patient-specific
- Clinical visits are sparse relative to disease burden
- Current management relies on blunt restriction rather than personalized enablement

---

## Technical Stack (Hackathon MVP)

| Component | Technology | Scope for Demo |
|---|---|---|
| Mobile app | React Native or Swift (iOS-first) | Core UI: risk state display, morning briefing, activity pre-check, med log |
| Wearable integration | Apple HealthKit API | HR, HRV, sleep, activity, temperature |
| Environmental context | CoreMotion + OpenWeatherMap API | Activity state + weather |
| Risk model | Weighted scoring engine (Python/JS) | Literature-based defaults, simulated personalization |
| EHR simulation | FHIR-formatted sample patient data | Pre-loaded synthetic TKOS patient with stress test results, ICD history, clinical notes |
| NLP on clinical notes | Claude API (or similar LLM) | Extract triggers, prodromal descriptions, treatment response patterns from sample notes |
| Clinician report | Auto-generated PDF | Visit summary with risk distribution, event timeline, correlations |
| Drug interaction check | CredibleMeds QT drug list (static DB) | Cross-reference new prescriptions against QT-prolonging drugs |
| Emergency passport | Structured data → PDF/QR code | One-page brief with diagnosis, meds, ICD info, contraindications, contacts |

**What we demo live vs. what we show as design:**
- Live: Risk model running on simulated patient data, showing how compound factors shift risk state. Clinician PDF generation. Drug interaction check. Emergency passport.
- Designed: Watch face companion, parent mirror app, voice logger, full HealthKit integration (requires deployed app + real device).

---

## Evaluation Plan

| Validation Method | What It Proves |
|---|---|
| **Case replay**: Simulate 3 published TKOS cases through the system | Risk model would have flagged elevated risk before documented events; emergency passport contains all critical safety information |
| **Clinician summary comparison**: Generate visit summary from simulated data vs. typical parent-written email update | Measures completeness (fields captured), structure (clinician-interpretable format), and time saved |
| **Drug interaction audit**: Run 20 common ER medications against TKOS patient profile | System correctly flags QT-prolonging contraindications (ondansetron, azithromycin, etc.) |
| **Alert calibration**: Run 1 week of simulated biometric data with varying conditions | System produces appropriate risk states — no false reds, green states align with genuinely safe conditions |
| **Clinician usability** (if accessible): Show visit PDF to a cardiologist | Can they extract the key clinical signals within a 5-minute review? |

---

## Why This Wins

1. **It addresses a real, documented, unmet need** — 74% breakthrough event rate on current therapy means the care infrastructure is failing.
2. **It goes beyond the prompt** — it doesn't just track and report (backward-looking); it enables safe living (forward-looking).
3. **It's technically grounded** — every data stream and risk factor is supported by published clinical evidence from the TKOS registry and adjacent channelopathy literature.
4. **It's honest about what it can and can't do** — we don't claim to predict arrhythmias; we estimate risk state from converging contextual factors.
5. **It scales beyond TKOS** — the architecture is a template for episodic rare disease management broadly.
6. **It centers the patient's humanity** — a child who hears "today is a good day to ride your bike" is living a fundamentally different life than one who only hears "don't."
