# TutorTrace

> **An explainable adaptive learning engine that models what a student knows, understands why they struggle, and decides what they should learn next.**

TutorTrace is an adaptive tutoring platform built around **Bayesian Knowledge Tracing (BKT)**. Instead of reducing learning to right/wrong answers or a single score, it maintains a live probabilistic model of each learner and uses misconceptions, response time, prerequisites, uncertainty, and forgetting to decide what should happen next.

## The Problem

Most learning platforms treat two students with the same score as equally skilled, even when their underlying problems are completely different.

A wrong answer could mean the student does not know the concept, has a specific misconception, is missing a prerequisite, rushed through the question, or simply does not know the answer.

**TutorTrace was built to understand that difference.**

## What Makes TutorTrace Different?

### 1. Probabilistic Mastery Instead of Static Scores

TutorTrace maintains a separate mastery probability for every skill using **Bayesian Knowledge Tracing**.

```text
Integer Operations       84%
One-Step Equations       67%
Two-Step Equations       31%
Inequalities             52%
```

This creates a much richer learner profile than a single percentage.

### 2. A Correct Answer Can Still Show Struggle

TutorTrace considers response time as evidence. A normal correct response and an unusually slow correct response both increase mastery, but the latter can be interpreted as more effortful learning.

### 3. Fast Mistakes Can Be Careless Slips

A very fast incorrect response may indicate rushing rather than true non-mastery, so TutorTrace can treat it differently from a normal incorrect response.

### 4. “I Don't Know” Is Its Own Signal

Students can explicitly choose **I don't know**. TutorTrace records this as uncertainty rather than treating it exactly like a confidently selected wrong answer.

### 5. Misconception Fingerprinting

Wrong options can be tagged with the misconception they represent. If a learner repeatedly makes an `inverse_operation_error`, TutorTrace records the pattern and can deliberately investigate it with another targeted question.

### 6. Prerequisite Diagnosis

If a learner struggles with Two-Step Equations, the real problem may be One-Step Equations.

```text
Two-Step Equations
        ↓
One-Step Equations
        ↓
Integer Operations
```

TutorTrace can temporarily pivot to the weaker foundational skill and return to the original topic once that prerequisite improves.

### 7. Memory Decay

TutorTrace distinguishes between **stored mastery** and **effective mastery**, allowing the system to model forgetting without destroying the learner's historical mastery state.

### 8. Explainable Adaptation

Every question has a `selection_reason`, such as:

```text
Building your starting skill profile.
Practicing your current weakest skill.
Checking whether this error pattern repeats.
A weaker prerequisite may be blocking progress.
```

The adaptive logic is therefore transparent instead of being hidden inside a black box.

## How It Works

TutorTrace uses **Bayesian Knowledge Tracing** to estimate the probability (P(L)) that a learner has mastered a skill.

BKT models four probabilities: initial mastery (P(L_0)), learning (P(T)), guessing (P(G)), and slipping (P(S)).

For a correct response:

[
P(L|Correct)=\frac{P(L)(1-P(S))}{P(L)(1-P(S))+(1-P(L))P(G)}
]

After observing a response, TutorTrace updates mastery and then combines that learner state with diagnostic signals.

```text
Question
   ↓
Student Response
   ├── Correctness
   ├── Response Time
   ├── Selected Distractor
   └── "I Don't Know"
          ↓
Bayesian Mastery Update
          ↓
Misconception + Prerequisite Analysis
          ↓
Memory-Aware Learner State
          ↓
Adaptive Question Selection
          ↓
Explainable Next Question
```

## Data-Informed Model

BKT parameters were fitted offline using the **ASSISTments 2009–2010 Skill Builder dataset**.

* **82,550 training interactions**
* **19,725 test interactions**
* **8 fitted source skills**
* **Test AUC: 0.7013**
* **Test RMSE: 0.4425**

The fitted values initialize TutorTrace's learner model rather than starting every student at zero.

## Skills & Question Bank

TutorTrace currently models **8 skills**: Integer Operations, Fraction Operations, Order of Operations, Distributive Property, One-Step Equations, Two-Step Equations, Inequalities, and Exponents.

The prototype contains **48 curated questions — 6 per skill**, with metadata for difficulty, expected response time, misconceptions, and prerequisite targets.

## Teacher Analytics

TutorTrace also converts individual learner models into classroom insights through a simulated teacher dashboard.

It can highlight class-wide weaknesses and produce recommendations such as:

```text
Two-Step Equations
7 / 10 learners below mastery threshold
Severity: HIGH
Recommendation: Revisit One-Step Equations
```

This turns learner analytics into **actionable teaching decisions**.

## Tech Stack

**Frontend:** React, JavaScript, HTML, CSS, Tailwind CSS
**Backend:** Python 3.11, FastAPI, Pydantic, Uvicorn
**ML / Adaptive Logic:** Bayesian Knowledge Tracing, pyBKT, NumPy, Bayesian inference, epsilon-greedy selection, prerequisite graphs, misconception fingerprinting, memory decay
**Testing:** pytest, httpx, FastAPI TestClient
**Tools:** Git, GitHub, VS Code, Swagger/OpenAPI
**Deployment:** Vercel frontend + Render backend
**Data:** ASSISTments Skill Builder dataset, JSON model/configuration files, in-memory learner state

## Architecture

```text
React + Tailwind Frontend
          ↓ REST / JSON
       FastAPI
          ↓
 ┌────────┼───────────┐
 BKT   Diagnostics   Adaptive Selector
          ↓
      Learner State
       ↙        ↘
Student UI   Teacher Analytics
```

The frontend never reimplements BKT or adaptive logic; the backend remains the single source of truth.

## Live Deployment

**TutorTrace:**
https://tutor-trace-93050tgck-shells-projects-19c05890.vercel.app

**Frontend:** Vercel
**Backend:** Render
**Communication:** HTTPS REST API

## Screenshots / Demo

### 1. Adaptive Student Experience

<!-- Add screenshot here -->

*Main question interface with skill, difficulty, confidence input, and “I don't know”.*

### 2. Response-Aware Learning

<!-- Add screenshot here -->

*Correct answer requiring extra time, demonstrating `slow_correct` evidence.*

### 3. Misconception Detection

<!-- Add screenshot here -->

*Wrong distractor revealing a specific misconception.*

### 4. Prerequisite Pivot

<!-- Add screenshot here -->

*TutorTrace detects a weaker prerequisite blocking progress.*

### 5. Explainable Adaptation

<!-- Add screenshot here -->

*“Why this question?” panel showing the selector's reasoning.*

### 6. Mastery Dashboard

<!-- Add screenshot here -->

*Per-skill probabilistic mastery instead of one overall score.*

### 7. Teacher Heatmap

<!-- Add screenshot here -->

*Simulated classroom mastery heatmap highlighting common weaknesses.*

### 8. Teacher Intervention Alert

<!-- Add screenshot here -->

*Class-wide weakness paired with a prerequisite-based recommendation.*

## Future Scope

Future versions can add PostgreSQL/Redis persistence, real classroom accounts, curriculum-scale prerequisite graphs, larger diagnostic question banks, learner-specific forgetting models, question-specific response-time calibration, spaced repetition, long-term learning histories, and educator-validated misconception taxonomies.

## The Vision

TutorTrace is built around one principle:

> **Personalized education requires understanding the learner, not simply generating more content.**

Instead of asking only **“Was the answer correct?”**, TutorTrace asks **what the response reveals, why the learner may be struggling, and what learning action should happen next.**

**TutorTrace doesn't just react to answers — it traces learning.**
