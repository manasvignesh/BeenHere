# BeenHere — Commercial Product & SaaS Discovery Protocol

This document defines the provider-independent research procedure for discovering, verifying, and classifying commercial products, SaaS platforms, and software services using the host AI agent's available web-search capabilities.

---

## 1. Core Principles & Guardrails

1. **No Fragile Scraping:** Never attempt to scrape arbitrary HTML or bypass login/bot gates. Rely on official documentation, public pricing pages, and verified product registries accessed via the host agent's standard search tools.
2. **Zero Fabrication:** Never invent startup names, mock pricing tiers, or hypothetical products. If a search yields zero commercial products, report the search limitation explicitly.
3. **Marketing vs. Reality:** Marketing landing pages frequently claim "AI-driven autonomous workflows" when the actual implementation is a static template or simple wrapper. Verify feature claims against public documentation, API references, or release changelogs.
4. **Saturation Fallacy:** Never equate the number of search results with market saturation. A hundred blog posts mentioning a keyword does not equal one hundred viable software products.

---

## 2. The 5-Step Product Discovery Workflow

```
┌────────────────────────────────────────────────────────┐
│ Step 1: Formulate Commercial & Persona Search Queries  │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ Step 2: Screen & Filter for Operating Products         │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ Step 3: Classify Competitor Archetypes (Direct/Partial)│
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ Step 4: Verify Feature Claims Against Documentation    │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ Step 5: Document Availability, Vitality & Pricing Model│
└────────────────────────────────────────────────────────┘
```

---

### Step 1: Formulate Commercial & Persona Search Queries
Commercial products are rarely described with academic or algorithmic terms. Convert technical primitives into market terminology:

| Technical Mechanism | Commercial Search Formulations |
| :--- | :--- |
| **"Conversational turn-taking state machine"** | `"AI voice agent platform"`, `"realtime voice AI SaaS"`, `"conversational AI builder"` |
| **"Multi-agent debate consensus"** | `"AI meeting assistant debate"`, `"AI decision support tool"`, `"virtual focus group software"` |
| **"CRDT collaborative state synchronization"** | `"realtime collaborative canvas app"`, `"multiplayer workspace tool"` |
| **"AST code analysis and refactoring"** | `"automated code review SaaS"`, `"AI linter for pull requests"` |

**Query Modifiers:**
- Combine with market operators: `"[problem] software"`, `"[problem] alternative"`, `"best [problem] tools 2025 OR 2026"`, `"[company] competitors"`.
- Check established product directories: Product Hunt, Y Combinator directory, G2, Capterra.

---

### Step 2: Screen & Filter for Operating Products
Distinguish actual operating products from noise:
- **Operating Products:** Possess an official domain, live registration/onboarding flow, public documentation, or accessible demo.
- **Noise to Filter Out:**
  - Generic SEO listicles ("Top 10 AI Tools in 2026") that regurgitate press releases.
  - Abandoned domain squatters or inactive landing pages.
  - Research prototypes labeled as commercial products without public access.

---

### Step 3: Competitor Classification Taxonomy

Categorize every discovered commercial entity into one of three distinct tiers:

#### A. Direct Competitors
- **Definition:** Targets the same primary end-user persona and attempts to solve the identical functional problem through the same delivery medium.
- **Strategic Impact:** High. Requires clear value proposition differentiation or cost/latency advantage.
- **Example:** For an AI voice social platform $\rightarrow$ *Character.ai Call Mode*, *Airchat*.

#### B. Partial Competitors
- **Definition:** Solves a significant subsystem or component of the target problem, or addresses the full problem for a narrow vertical.
- **Strategic Impact:** Moderate. Excellent candidates for integration (consuming via API) or partner ecosystems.
- **Example:** For an AI voice social platform $\rightarrow$ *Vapi.ai*, *Retell AI*, *LiveKit Cloud* (voice transport/agent hosting only).

#### C. Adjacent Products
- **Definition:** Solves an identical underlying mechanism in a completely different commercial category or industry.
- **Strategic Impact:** High architectural inspiration; low direct commercial rivalry.
- **Example:** For an AI voice social platform $\rightarrow$ *Civai* (synthetic citizen panel simulation for municipal surveys).

---

### Step 4: Verify Feature Claims Against Documentation
Apply the **Documentation Verification Rule**:
- **Marketing Claim:** *"Our platform features real-time dynamic group debates with zero hallucinations."*
- **Verification Check:** Inspect the product's official docs or API reference:
  - Does the API support multi-participant WebSockets?
  - Does the documentation explain the turn-taking arbitration mechanism?
  - Are there documented API endpoints for debate scoring or argument graphs?
- **Classification:**
  - If verified in API/docs: `[VERIFIED-METADATA]`
  - If present only in marketing copy: Tag explicitly as `[UNVERIFIED-MARKETING-CLAIM]`.

---

### Step 5: Document Availability, Vitality & Pricing Model
Record the commercial posture of each product:
- **Availability State:** Public GA (General Availability), Public Beta, Waitlist Only, Deprecated / Shut Down.
- **Pricing & Access Model:** Open-source self-hosted, Free tier / Freemium, Usage-based (per-minute or per-token), Enterprise quote only.
- **Ecosystem Moat:** Proprietary fine-tuned model weights, network effects, enterprise compliance (SOC2/HIPAA), or specialized hardware integrations.

---

## 3. Reporting When Web Search Access Is Constrained

If the host agent executes in an offline or search-restricted environment:
1. **Explicit Limitation Disclosure:**
   > *"Notice: Outbound web search was unavailable during this session. Commercial product discovery could not be performed against live directories. Product coverage reflects the host agent's internalized knowledge base and is tagged as `[INFERRED]`."*
2. **Never Invent Competitors:** Disclose unverified coverage rather than generating plausible-sounding product names.
