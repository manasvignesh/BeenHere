# Integration Blueprint: Voice-First Synthetic Social Platform with Dialectical Idea Evaluation

> **Target Concept / Product:** Voice-First Synthetic Social Platform  
> **Blueprint Author:** BeenHere Architecture & Code-Reusability Intelligence  
> **Status:** ADVISORY BLUEPRINT (Static Interface & License Verified)  
> **Investigation Date:** 2026-11-13  
> **Target Runtimes:** Python 3.11+, Node.js 22+ / Bun, WebRTC (Daily/LiveKit)

---

## 1. Product Requirements & Architectural Objectives

### 1.1 Core Functional Requirements
1. **Full-Duplex Multi-Speaker Voice Transport:** Low-latency bidirectional WebRTC streaming audio supporting instant user barge-in (interruption) and acoustic echo cancellation.
2. **Dynamic Conversational Floor Arbitration:** Pacing controller that schedules speaking turns among multiple autonomous AI personas and the human user based on dramatic tension and argumentative relevance, preventing overlapping audio collision.
3. **Persistent Stateful Persona Memory:** Cognitive memory stores preserving distinct philosophical worldviews, past user assertions, and cross-session relationship states without epistemic drift or sycophancy.
4. **Real-Time Dialectical Argumentation:** Automated identification of unstated warrants, logical fallacies, and empirical claims using Toulmin argument schemas and Socratic challenge loops.

### 1.2 Non-Functional & Operational Constraints
- **Latency Target:** Conversational audio response target <1,200ms perceived delay during multi-agent turn transitions.
- **Runtime Environment:** Heterogeneous service deployment (Python async audio pipeline bridged to stateful agent processes).
- **Extensibility:** Plug-and-play architecture for STT (Deepgram), TTS (Cartesia/ElevenLabs), and LLM reasoning backends.

---

## 2. Recommended Reusable Components & Roles

| Component Role | Recommended Upstream Candidate | Language / Runtime | Declared vs Source License | Integration Posture | Verified Interface / Entry Point | Evidence Tier |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| **Audio Transport & Pipeline** | [pipecat-ai/pipecat](https://github.com/pipecat-ai/pipecat) | Python 3.11+ | `BSD-2-Clause`<br>(Permissive) | **`ADOPT_AS_DEPENDENCY`** | `src/pipecat/pipeline/pipeline.py`<br>`PipelineSource`, `PipelineSink`, `Pipeline` | `[VERIFIED-SOURCE]` |
| **Stateful Memory & Personas** | [letta-ai/letta-code](https://github.com/letta-ai/letta-code) | TypeScript / Bun (Node 22+) | `Apache-2.0`<br>(Permissive) | **`INTEGRATE_THROUGH_API`** | `@letta-ai/letta-client`<br>Local REST App Server (`letta server`) | `[VERIFIED-SOURCE]` |
| **Social State & Conversation Engine** | [a16z-infra/ai-town](https://github.com/a16z-infra/ai-town) | TypeScript | `MIT`<br>(Permissive) | **`EXTRACT_SPECIFIC_COMPONENT`** | `convex/schema.ts`, `agent/conversation.ts`<br>Agent conversation state machine | `[VERIFIED-SOURCE]` |
| **Debate Reasoning Reference** | [thunlp/ChatEval](https://github.com/thunlp/ChatEval) | Python (Legacy) | `Apache-2.0`<br>(Permissive) | **`REJECT_AS_DEPENDENCY`**<br>*(Reference Only)* | `requirements.txt`, evaluation prompt rubrics | `[VERIFIED-SOURCE]` |

### Qualification / Rejection of Poorly Suited Candidates
- **Rejection of `thunlp/ChatEval` as a Dependency:** While ChatEval is frequently cited in multi-agent debate literature, source inspection of its `requirements.txt` reveals an unmaintained dependency on `langchain>=0.0.155` and an unversioned git repository (`git+https://github.com/OpenBMB/BMTools.git`). Attempting to install ChatEval into a modern 2026 Python environment introduces critical dependency conflicts. Furthermore, ChatEval is designed for offline batch evaluation, offering no streaming or voice interfaces. **Decision:** REJECT package installation; extract only its persona debate evaluation prompt rubrics.
- **Qualification of `a16z-infra/ai-town`:** While AI Town provides clean conversation arbitration patterns, the codebase is deeply coupled to Convex's proprietary reactive cloud backend. Adopting AI Town as a whole would force the entire platform onto Convex. **Decision:** Extract only the conversation state transition equations and reimplement them in Python.

---

## 3. Component Responsibilities & Boundary Definitions

### 3.1 Component 1: Pipecat Voice Pipeline Engine ([pipecat-ai/pipecat](https://github.com/pipecat-ai/pipecat))
- **Assigned Responsibility:** Ingesting microphone audio from the user via WebRTC, performing Voice Activity Detection (VAD) via Silero, streaming audio tokens to Deepgram STT, and streaming output audio packets from Cartesia/ElevenLabs TTS back to the user client.
- **Explicit Scope Boundary:** Pipecat MUST NOT manage long-term agent memories or decide which persona speaks next. It acts strictly as an audio transport and frame-processing pipe.
- **Upstream Files & Entry Points:** `src/pipecat/pipeline/pipeline.py#L21-L120`
- **Key Exported Symbols:** `Pipeline`, `PipelineSource`, `PipelineSink`, `FrameProcessor`.

### 3.2 Component 2: Letta Stateful Persona OS ([letta-ai/letta-code](https://github.com/letta-ai/letta-code))
- **Assigned Responsibility:** Maintaining long-term user memory, episodic memory streams, and distinct persona worldviews across sessions. Updates persona beliefs based on debate outcomes.
- **Explicit Scope Boundary:** Letta MUST NOT handle real-time audio frames or millisecond-level turn arbitration. It is invoked asynchronously over HTTP/REST when conversational context needs updating.
- **Upstream Files & Entry Points:** `@letta-ai/letta-client` / REST endpoint `POST /v1/agents/{agent_id}/messages`
- **Key Exported Symbols:** `LettaClient`, `AgentState`, `Memory`.

### 3.3 Component 3: Conversational Floor & Pacing Director (CUSTOM BUILD)
- **Assigned Responsibility:** Central finite state machine orchestrating room dynamics. Listens to user VAD events, determines conversational tension, schedules the next AI speaker, triggers instant barge-in audio cut-through when the user speaks, and speculatively pre-generates responses across personas.
- **Explicit Scope Boundary:** Does not generate speech or transcribe audio; acts purely as the room coordinator.

---

## 4. Proposed Target Architecture

```
                       ┌──────────────────────────────────────────┐
                       │            Human User Client             │
                       └────────────────────┬─────────────────────┘
                                            │ WebRTC Duplex Audio (Opus 48kHz)
                                            ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         Pipecat Audio Pipeline (ADOPT)                           │
│  - WebRTC Transport Layer (Daily / LiveKit)                                      │
│  - Silero VAD (Voice Activity Detection & Interruption Event Bus)                 │
│  - Deepgram STT (Streaming Audio Tokens -> Raw Text)                             │
│  - Cartesia Sonic TTS (Streaming Synthesis -> Audio Frames)                      │
└───────────────────────────────────────────┬──────────────────────────────────────┘
                                            │ Transcript Stream & VAD Events
                                            ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                  Conversational Floor & Pacing Director (BUILD)                  │
│  - Avionics Priority Cut-Through: Instant User Barge-in Mute (<80ms)              │
│  - Beat & Pacing Controller (Façade Pattern): Tension-based turn scheduler       │
│  - Speculative Parallel Dispatcher: Pre-computes opposing personas on pause      │
└────────────────────────┬──────────────────────────────────┬──────────────────────┘
                         │ Active Speaker Token             │ Background Text Chunks
                         ▼                                  ▼
┌───────────────────────────────────────────────┐ ┌────────────────────────────────┐
│      Letta Stateful Personas (INTEGRATE)      │ │   Toulmin Dialectic Linter     │
│  - Persistent Episodic Memory Stream          │ │   (BUILD - Prompt Extracted)   │
│  - Belief Graph & Anti-Sycophancy Vectors     │ │ - Claim & Warrant Verification │
│  - REST Service (`letta server` Bun/TS)       │ │ - Socratic Challenge Loop Gating│
└───────────────────────────────────────────────┘ └────────────────────────────────┘
```

---

## 5. Interface Boundaries & Data Contracts

### 5.1 Pipecat $\leftrightarrow$ Floor Director (In-Process Python Async Queue)
- **Protocol:** `asyncio.Queue` passing typed Pipecat `Frame` objects.
- **Data Payload:**
  ```python
  class UserInterruptionEvent(Frame):
      timestamp_ms: int
      confidence: float

  class TranscriptChunkFrame(Frame):
      text: str
      is_final: bool
      speaker_id: str
  ```
- **Serialization Overhead:** Zero (in-memory object reference, <0.1ms).

### 5.2 Floor Director $\leftrightarrow$ Letta Agent Service (HTTP/REST JSON)
- **Protocol:** HTTP/1.1 or HTTP/2 over local loopback (`http://127.0.0.1:8283`).
- **Data Payload:**
  ```json
  {
    "agent_id": "persona_adversarial_skeptic_01",
    "role": "user",
    "message": "User claims that local-first CRDTs eliminate the need for server infrastructure.",
    "stream": true
  }
  ```
- **Serialization Overhead:** ~2-5ms JSON serialization.

---

## 6. Dependency & Runtime Constraints Matrix

| Upstream Component | Declared Runtime | Key Dependencies | Potential Conflicts & Friction |
| :--- | :--- | :--- | :--- |
| **Pipecat** | Python `>=3.11` | `aiofiles`, `aiohttp`, `loguru`, `numpy` | Requires modern Python 3.11+ event loop; native C++ audio libraries (PortAudio / WebRTC) must be present on host. |
| **Letta Code** | Node `>=22.23.5` or `Bun` | `@letta-ai/letta-client`, `@modelcontextprotocol/sdk` | Node/Bun runtime separate from Python; best deployed as a local sidecar service or Docker container. |
| **AI Town Patterns** | TypeScript | `convex` | Avoid Convex dependency by extracting purely algorithmic state transition math into native Python. |
| **ChatEval Rubrics** | Python (Legacy) | `langchain>=0.0.155` | **Do not install.** Extracted prompt strings have zero runtime dependencies. |

---

## 7. License Compliance & Legal Risk Matrix

| Component | Source License | Copyleft Tier | Permitted Use Cases | Required Compliance Actions |
| :--- | :--- | :--- | :--- | :--- |
| **Pipecat** | `BSD-2-Clause` | None | Commercial SaaS & Binary | Retain copyright notice in source distributions. |
| **Letta Code** | `Apache-2.0` | None | Commercial SaaS & Binary | Include Apache 2.0 license notice; state significant file modifications. |
| **AI Town (Extracted)**| `MIT` | None | Commercial SaaS & Binary | Retain original copyright attribution in extracted module header. |
| **ChatEval (Rubric)**  | `Apache-2.0` | None | Unrestricted | Retain paper/author citation in prompt template docstrings. |

> *DISCLAIMER: This analysis reflects static heuristic code and manifest inspection. It is not formal legal advice. Qualified legal counsel should review license compatibility before commercial distribution.*

---

## 8. Missing Functionality (Custom Build Scope)

The following components do NOT exist in any discovered repository and MUST be built from scratch:

1. **Multi-Speaker Floor Arbiter (`floor_director.py`):**
   - *Why It Must Be Built:* Existing frameworks assume dyadic (1-to-1) voice conversation. A room with 3 synthetic agents requires a priority scheduler that evaluates which agent has the highest argumentative relevance and prevents multi-agent audio cross-talk.
   - *Estimated Complexity:* `Moderate` (~400 lines of Python `asyncio` finite state machine).
2. **Speculative Parallel Dispatcher (`speculative_dispatcher.py`):**
   - *Why It Must Be Built:* Generating LLM tokens in-series across 3 agents produces unplayable 3,000–5,000ms latency silences. Pre-generating potential rebuttals concurrently during human speech pauses and canceling unused branches upon barge-in is required to maintain natural pacing.
   - *Estimated Complexity:* `Moderate` (~300 lines of Python async task cancellation).
3. **Toulmin Dialectical Linter (`dialectical_linter.py`):**
   - *Why It Must Be Built:* Evaluates streaming user statements for unbacked claims or fallacies, injecting Socratic challenge prompts into the conversation stream when warrant confidence drops below threshold.
   - *Estimated Complexity:* `Low-to-Moderate` (~250 lines using prompt templates inspired by ChatEval).

---

## 9. Implementation Sequence & Phased Roadmap

```
Phase 1: Pipeline Scaffolding  ───► Phase 2: Floor Arbiter ───► Phase 3: Letta Sidecar ───► Phase 4: Dialectics
(Pipecat WebRTC + STT/TTS)         (Turn State Machine)        (Memory & Persona OS)        (Toulmin Linter)
```

- **Phase 1: Audio Pipeline Scaffolding (Days 1–5):**
  - Install and configure `pipecat-ai/pipecat` with Daily/LiveKit WebRTC transport, Deepgram STT, and Cartesia TTS.
  - Verify single-agent audio loopback and barge-in interruption timing.
- **Phase 2: Conversational Floor Director (Days 6–12):**
  - Implement the `FloorDirector` class adapting Façade beat tension patterns.
  - Test turn-taking scheduling among mock text agents.
- **Phase 3: Letta Persona Integration (Days 13–18):**
  - Stand up local `letta server` sidecar.
  - Configure 3 distinct persona belief templates via `@letta-ai/letta-client`.
  - Wire async persona prompt dispatching into the Floor Director.
- **Phase 4: Dialectical Evaluation & Pacing Polish (Days 19–25):**
  - Implement the Toulmin dialectical linter as a background stream observer.
  - Benchmark voice turn-around latency under multi-persona load.

---

## 10. Validation & Contract Testing Plan

1. **Priority Barge-in Latency Test:**
   - *Method:* Inject synthetic user speech audio while an AI persona is streaming audio.
   - *Success Threshold:* AI audio packet stream must terminate within <100ms of user VAD trigger.
2. **Turn Arbitration Collision Test:**
   - *Method:* Simulate simultaneous response availability from 3 personas.
   - *Success Threshold:* Exactly 1 persona is assigned the audio floor; remaining 2 personas are buffered or canceled with zero overlapping audio frames.
3. **Memory Persistence Contract Test:**
   - *Method:* Issue a controversial pitch in Session 1; restart client and verify in Session 2 that Persona 1 recalls the pitch and previous objections.
   - *Success Threshold:* Letta archival memory returns accurate premise context.

---

## 11. Alternative Architectural Paths & Unresolved Risks

| Architectural Path | Trade-offs | Maintenance Burden | Feasibility Verdict |
| :--- | :--- | :--- | :--- |
| **Path 1: Composite Integration (Recommended)** | Uses Pipecat for transport + Letta for memory + Custom Floor Arbiter. | Moderate (Python $\leftrightarrow$ Letta HTTP bridge) | **RECOMMENDED** |
| **Path 2: Monolithic Node.js Rewrite** | Translates Pipecat into Node.js to unify stack with Letta and AI Town. | Extreme (6+ months rebuilding WebRTC audio pipeline) | **REJECTED** |
| **Path 3: Proprietary Multimodal API Wrap** | Wraps OpenAI Realtime API directly with custom client routing. | Low dev time, but extreme API costs ($0.30+/min) and zero multi-agent arbitration support. | **REJECTED** |

### Unresolved Technical Risks
- *Concurrent LLM API Costs:* Speculative parallel pre-computation across 3 personas increases LLM token consumption by an estimated 40–60%. `[INFERRED]`
- *TTS Concurrency Spikes:* Rapid back-and-forth multi-persona debates require maintaining active WebSocket streaming sessions with TTS providers, requiring robust connection pooling. `[INFERRED]`

---

## 12. Evidence Ledger & Audit Summary
- `[VERIFIED-SOURCE]`: 4 entries confirmed via direct HTTP inspection of source code files (`pipeline.py`, `package.json`, `schema.ts`, `requirements.txt`).
- `[VERIFIED-METADATA]`: 4 entries confirmed via official repository manifests and GitHub API endpoints.
- `[INFERRED]`: 2 architectural risk estimations deduced from latency and concurrency constraints.
- `[VERIFIED-TEST]`: 0 entries (no compiled local binary was executed).
- `[UNKNOWN]`: 0 entries.
