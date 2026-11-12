# BeenHere — Feature Gap & Enhancement Intelligence Protocol

This reference guide establishes the formal protocol for conducting systematic gap analyses between a proposed software concept and existing solutions, identifying genuine opportunities, and cross-pollinating mechanisms from adjacent fields.

---

## 1. The Core Distinctions

### A. Missing Feature vs. Deliberate Engineering Trade-off
Not every capability missing in existing products is an opportunity waiting to be seized. Often, a feature is missing because:
1. **Deliberate Scope Discipline:** The creators intentionally kept the product focused on a single primitive (e.g., LiveKit focusing on WebRTC transport rather than cognitive agent memory).
2. **Fundamental Technical Barrier:** The feature requires unfeasible bandwidth, compute, or latency (e.g., running 100 concurrent local 70B LLMs on consumer mobile hardware).
3. **Negative User Experience Trade-off:** The feature introduces friction that degrades user retention (e.g., forcing rigid academic citations during casual social voice chat).
4. **Genuine Technical Whitespace:** An unserved problem that current architectures can now solve due to recent breakthroughs (e.g., sub-second voice-to-voice streaming APIs enabling real-time multi-agent floor arbitration).

BeenHere requires agents to evaluate whether a gap represents a **real engineering opportunity** or an **intentional trade-off**.

---

## 2. The 7-Step Gap Extraction Process

```
┌────────────────────────────────────────────────────────┐
│ Step 1: Decompose Idea into Core Functional Primitives │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ Step 2: Map Existing Solutions Against Primitives      │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ Step 3: Classify Coverage (Supported / Partial / None) │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ Step 4: Diagnose Failure Modes & Current Limitations   │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ Step 5: Screen Adjacent Fields for Novel Enhancements  │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ Step 6: Prioritize Enhancements (Feasibility vs Impact)│
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ Step 7: Document Comprehensive Enhancement Dossier     │
└────────────────────────────────────────────────────────┘
```

---

## 3. The Feature Coverage Matrix

Structure the comparative audit across discovered competitors, libraries, and the proposed concept:

| Target Capability / Subsystem | Current State in Prior Art | Nature of the Gap | Trade-off or Opportunity? | Priority |
| :--- | :--- | :--- | :--- | :---: |
| **Real-time multi-agent floor control** | Handled linearly or via single-agent endpoints (Pipecat, Vapi). | Architectural omission: concurrent speaker arbitration is absent in voice. | **Genuine Opportunity**: Pacing algorithms from game AI can bridge this. | High |
| **Dialectical assumption testing** | Handled in asynchronous text (ChatEval). | Latency gap: multi-round debate is too slow for voice. | **Technical Barrier to Solve**: Requires speculative background branching. | High |
| **Persistent episodic agent memory** | Handled via vector stores (Letta / MemGPT). | Solved: existing open-source libraries provide robust APIs. | **Solved Prior Art**: Do not rebuild; adopt existing library. | Low |

---

## 4. The 8-Point Enhancement Dossier

For every proposed enhancement borrowed from an adjacent domain, the research report must provide:

1. **Source of Inspiration:** What specific industry, product, or academic paper pioneered this mechanism?
2. **Evidence of Technical Feasibility:** What working code, benchmark, or paper proves the mechanism functions in practice?
3. **Target User Problem Addressed:** Exactly what user frustration, bottleneck, or latency does this resolve?
4. **Expected Concrete Benefit:** Measurable advantage (e.g. "Reduces perceived debate latency from 4,000ms to 800ms").
5. **Integration Complexity:** Qualitative rating: `Low` (wrapper/config), `Moderate` (custom state machine), `Heavy` (core protocol rebuild).
6. **Relevant Reusable Code:** Specific GitHub repositories or libraries that can be adopted or extracted.
7. **Inherent Limitations & Failure Modes:** When does this enhancement break down (e.g. edge cases, resource cost, failure under packet loss)?
8. **Implementation Priority:** `Essential (MVP Critical)` vs. `Optional (Post-MVP Differentiator)`.

---

## 5. Anti-Patterns in Feature Analysis

| Flawed Analytical Habit | Why It Fails | Correct Analytical Standard |
| :--- | :--- | :--- |
| *"Competitor X doesn't have feature Y, so we will win by adding it."* | Ignores whether users actually want feature Y, or if Competitor X discarded it intentionally. | Verify whether customer demand or technical friction explains feature absence. |
| *"Let's combine 10 features from 10 different apps."* | Feature bloat; results in an incoherent product with severe architectural coupling. | Focus on the single unifying mechanism that creates disproportionate value. |
| *"This enhancement is zero-cost to add."* | Every new mechanism introduces state management, testing burden, and failure surface. | Explicitly document integration complexity and operational overhead. |
