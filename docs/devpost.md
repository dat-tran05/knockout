# Knockout

> *The ICD captures emergencies. Knockout captures everything in between.*

---

## Inspiration

Triadin Knockout Syndrome (TKOS) is one of the rarest and most dangerous inherited arrhythmia syndromes in existence. Only **21 patients** appear on the international registry. There are no clinical practice guidelines. Each cardiologist is improvising.

Children present on average at **age 3** — with cardiac arrest or exertional syncope. Even on maximal therapy, **74%** of patients experience breakthrough events. **68%** carry a defibrillator implanted in their chest.

One of our team members *is* that patient. She has survived **6 cardiac arrests**. Her experience made three critical gaps impossible to ignore:

**The ICD Gap** — ICDs only log events above their detection threshold (typically >190 bpm). Subclinical arrhythmias between 70–190 bpm — the ones that signal disease progression and reveal whether medication is working — go completely unrecorded.

**The Visit Gap** — There are **2,160 waking hours** between quarterly cardiology appointments with zero clinical observation. Symptoms get reported from memory weeks after the fact. Timing, context, and surrounding physiology are lost.

**The 'Why' Gap** — No system has ever captured the compound context behind an episode: medication trough + heat + poor sleep. Individual factors are sometimes noted. The combination never is.

---

## What It Does

Knockout is a passive monitoring and pattern-learning platform for TKOS and related channelopathies, built around six continuous data streams anchored to a **personal baseline**:

- Heart rate & HRV (Apple Watch)
- Sleep architecture
- Wrist temperature
- Local weather conditions
- Medication timing

A **pharmacokinetic model** overlays a real-time blood-level curve onto HRV, exposing trough-related vulnerability windows that were previously invisible. Risk in TKOS can be understood conceptually as:

$$\text{Risk} \propto \text{Adrenergic Load} + \text{Ca}^{2+} \text{ Instability} - \text{Medication Effect}$$

**One-tap Apple Watch capture** timestamps the exact moment a symptom occurs and auto-captures 24 hours of surrounding context — creating a labeled event with full physiologic state attached.

A **Bayesian learning loop** uses each labeled event to refine a personal pre-episode model. After ~20–30 labeled events, the system identifies which stream combinations most reliably precede *this patient's* episodes specifically.

Finally, **one-click physician report generation** compresses longitudinal data into a structured PDF optimized for a 5-minute quarterly review.

![Main dashboard with live vitals](https://raw.githubusercontent.com/dat-tran05/knockout/new-main/images/index.png)
---

## How We Built It

### Arrhythmia Detection: HRV Heuristic Engine

Raw Apple Watch BPM readings are converted to RR intervals:

$$RR_{ms} = \frac{60{,}000}{\text{BPM}}$$

We compute six distinct HRV metrics and combine them into a weighted ensemble confidence score:

$$\text{Confidence} = \left(\frac{\sum_i \text{score}_i \times \text{weight}_i}{\sum_i \text{weight}_i}\right) \times \text{sample\_factor}$$

| Metric | Weight | AFib Signature |
|---|---|---|
| CV (Coefficient of Variation) | 2.5 | > 0.065 — irregularly spaced beats |
| RMSSD | 2.0 | > 40 ms — rapid erratic beat changes |
| pNN20 | 1.5 | > 0.40 — most beats differ significantly from the last |
| SD1/SD2 (Poincaré ratio) | 1.5 | > 0.75 — scatter becomes circular instead of elliptical |
| SampEn (Sample Entropy) | 1.5 | > 1.5 — the rhythm has no repeating pattern |
| LF/HF Spectral Ratio | 1.0 | Collapses toward 1.0 — normal low-frequency rhythm disappears |

![Episode timeline view showing cardiac event log](https://raw.githubusercontent.com/AntoDono/knockout/new-main/images/episode.png)

---

### Deep Learning Architecture: CNN + 1D ResNet

![CNN Resnet Architecture](https://raw.githubusercontent.com/AntoDono/knockout/new-main/images/architecture.png)

For higher-confidence event classification, we built a **ResNet-30 1D architecture**:

- **Input**: 100-sample BPM windows (1 channel)
- **Stem**: `Conv1d(k=7, s=2) → BatchNorm → ReLU → MaxPool` → 32 channels
- **Residual Layers**: 3 progressively deeper blocks (32 → 96 → 192 channels) with stride-2 downsampling
- **Each ResBlock**: `Conv1d(k=3) → BN → ReLU → Conv1d(k=3, s=1) → BN` with skip connections
- **Output**: Global Average Pooling → Fully Connected → 2 classes (AFib / Healthy)

Convolutional layers slide over the BPM time axis to detect the local rhythm irregularities that define AFib. Residual skip connections allow 6-block depth without vanishing gradients on a small, human-labeled dataset.

**Result: ~2M parameters / 2.2 MB on disk** — small enough to run inference on an Apple Watch without a server round-trip.

---

### Muon Optimizer: Spectral Descent for Edge Deployment

To hit mobile constraints, we replaced Adam with the **Muon optimizer**, which performs steepest descent in the *dual space* with respect to the spectral norm.

Traditional optimizers treat 2D gradient matrices as flattened 1D vectors, which drowns out small but clinically meaningful gradient signals. We instead apply SVD to the gradient momentum matrix $G$:

$$G = U \Sigma V^\top$$

The closest orthogonal matrix drops $\Sigma$ so every direction updates equally:

$$O = UV^\top$$

Exact SVD is computationally expensive at inference time, so we approximate the polar factor using **Newton-Schulz iteration**, starting at $X_0 = cG$:

$$X_{K+1} = X_K + \frac{1}{2} X_K \left(I - X_K^\top X_K\right)$$

After 5 iterations, $X_5$ converges to $UV^\top$. This rapid convergence is what allowed us to compress the full model to **2.2 MB** — roughly the size of a single high-quality image.

---

### Bayesian Learning Loop

Heuristics alone cannot catch every patient-specific pattern, so the system learns continuously:

1. **Heuristic engine flags** a potential arrhythmia event
2. **Patient confirms or denies** with one tap on Apple Watch
3. **Model priors update** — each response feeds directly back into the Bayesian baseline

After ~20–30 labeled events, the model identifies which stream combinations most reliably precede this patient's episodes specifically. Every new day brings new training data.

---

## Challenges We Ran Into

**Data scarcity at the population level.** With 21 known patients globally, population-level ML is unrealistic. We shifted the entire modeling philosophy to individualized baselines — every threshold, every alert, every detected pattern is relative to *this patient's* history, not a reference population.

**Signal vs. noise in pediatric wearable data.** HRV and temperature fluctuate naturally with activity, emotion, and growth. Normalizing all streams against personal rolling baselines — rather than fixed clinical thresholds — was essential to avoid constant false positives in a pediatric population.

**Balancing safety and psychological burden.** A child with TKOS already lives under blanket restriction. Designing calm, actionable notifications rather than anxiety-inducing alerts required careful calibration, especially for caregivers receiving alerts on behalf of young patients.

**Edge deployment constraints.** Getting a clinically useful deep learning model running on Apple Watch without server latency required all of the architectural choices above — the Muon optimizer, spectral-norm-aware training, and ResNet depth/width tradeoffs optimized for 2.2 MB.

---

## Accomplishments We're Proud Of

- First system to integrate **pharmacokinetic modeling** with wearable biometric data for a cardiac channelopathy
- A **2.2 MB on-device model** that classifies arrhythmias without a server round-trip
- A **Bayesian personalization loop** that improves accuracy continuously over a single patient's lifetime
- A workflow that reduces thousands of hours of passive data into a **5-minute structured physician report**
- Most importantly: reframing TKOS care from reactive emergency response to continuous physiologic awareness

---

## What We Learned

Arrhythmias in TKOS are not random. They are threshold phenomena driven by the convergence of sympathetic load, intracellular calcium instability, and pharmacologic protection:

$$\text{Risk} \propto \text{Adrenergic Load} + [\text{Ca}^{2+}]_i \text{ Instability} - \text{Medication Effect}$$

Individual risk factors are sometimes noted in chart reviews. The combinations that actually precipitate episodes are never captured — because no tool existed to measure them simultaneously and continuously.

We also learned that rare disease is not a data problem waiting for more patients. It is a *per-patient* data problem waiting for better instrumentation.

---

## What's Next for Knockout

The immediate next step is validating individualized trough clustering patterns in collaboration with the Mayo Clinic TKOS registry and pediatric cardiology centers.

Beyond TKOS, the architecture applies directly to any cardiac channelopathy — CPVT, LQTS, Brugada syndrome — where ICD detection has gaps, medication timing drives risk windows, and between-visit monitoring is absent.

Long term: 21 patients with zero systematic longitudinal data today becomes the first structured real-world evidence base for a class of diseases that has never had one. The goal is to move cardiac care for the rarest patients on earth from reactive to predictive.