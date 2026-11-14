# Benchmark Evaluation Scenario B: AI Recruitment & Candidate Matching Platform

## 1. Standardized Research Brief

> **Instruction to Agent (Verbatim):**
> 
> *"I want to build an AI-powered recruitment and candidate matching platform. It should extract structured information from unstructured resume PDFs, perform semantic matching against job descriptions, enable candidate rediscovery across legacy applicant pools, and provide recruiter review workflows. It needs to integrate with or sit on top of existing Applicant Tracking Systems (ATS).*
> 
> *Before writing any code, research what already exists:*
> *1. What existing open-source ATS platforms or commercial recruitment products solve this or parts of this?*
> *2. What specific open-source libraries or components can be reused for document extraction, semantic matching, and bias auditing?*
> *3. What license restrictions, dual-licensing hazards, or copyleft obligations apply to the candidate repositories?*
> *4. What are the biggest technical gaps and legal compliance hurdles we must build ourselves?*
> *5. What is your concrete build-versus-reuse recommendation?"*

---

## 2. Target Concept & Architectural Primitives

- **Domain:** Enterprise SaaS / HR Tech / NLP / Information Extraction
- **Core Computational Primitives:**
  - Multimodal layout-aware PDF document conversion and tabular parsing
  - Dense embedding retrieval and cross-encoder semantic re-ranking
  - Algorithmic fairness and demographic parity auditing (EEOC / NYC Local Law 144 compliance)
  - Bi-directional ATS integration synchronization (candidate stages, notes, webhooks)
  - Vector similarity search with relational metadata filtering

---

## 3. Known Failure Modes in Standard AI Research

1. **The PyMuPDF Transitive License Hazard (Horilla HR):**
   - Open-source ATS projects such as `horilla/horilla-hr` are declared as LGPL-2.1.
   - Standard agents recommend adopting Horilla as a turnkey base. However, deep manifest inspection of Horilla's `requirements.txt` reveals a mandatory dependency on `pymupdf` (alias `fitz`).
   - PyMuPDF is dual-licensed under **AGPL-3.0** and Artifex commercial terms. Incorporating it into a commercial SaaS product exposes the entire backend to network copyleft source disclosure obligations unless an expensive commercial license is procured.
2. **Conflating Parser Wrappers with True Layout Models:**
   - Standard agents recommend legacy regex/keyword PDF extractors (`pdfminer.six`, `pypdf`, `PyPDF2`), which fail completely on multi-column resumes, visual skill badges, and complex tables.
   - Modern layout-aware open-source engines like `docling-project/docling` or `unstructured-io/unstructured` are frequently omitted by agents relying on older training distributions.
3. **Ignoring Algorithmic Bias & Regulatory Liability:**
   - Standard agents propose cosine similarity over LLM embeddings without addressing legal algorithmic bias mandates (such as New York City Local Law 144 for Automated Employment Decision Tools).
   - Specialized bias auditing toolkits like `fairlearn/fairlearn` (demographic parity, equalized odds metrics) are rarely recommended.
4. **License Ambiguity in `pgvector` and `OpenCATS`:**
   - GitHub API returns `NOASSERTION` for `pgvector/pgvector` (due to PostgreSQL license format) and `OpenCATS` (due to mixed MPL/CATS headers). Standard agents frequently guess or provide inaccurate licensing advice.

---

## 4. Ground-Truth Solution Space & Evidence Baseline

### Canonical Open-Source Repositories
- **`docling-project/docling`** (Python, MIT): Modern layout-aware document conversion library supporting rich OCR, multi-column reading orders, and table extraction.
- **`huggingface/sentence-transformers`** (Python, Apache-2.0): Standard framework for dense vector embeddings and `CrossEncoder.predict`/`rank` for two-stage candidate retrieval.
- **`fairlearn/fairlearn`** (Python, MIT): Specialized fairness toolkit for computing demographic parity, disparate impact ratios, and metric frames across protected attributes.
- **`pgvector/pgvector`** (C, PostgreSQL License): Open-source vector similarity search extension for PostgreSQL; verified permissive license.
- **`horilla/horilla-hr`** (Python, LGPL-2.1 with transitive AGPL hazard): Full-featured HR/ATS suite, but carries transitive AGPL copyleft liability via `pymupdf`.
- **`opencats/OpenCATS`** (PHP, Mixed MPL-2.0 / CATS License): Legacy ATS system; useful for workflow reference, but outdated architecture.

### Commercial & SaaS Landscape
- **Ashby:** Modern API-first ATS with structured interviewing and built-in candidate sourcing workflows.
- **hireEZ (formerly Hiretual):** Outbound AI sourcing engine across web candidate footprints.
- **Eightfold AI:** Enterprise talent intelligence platform utilizing deep matching models.
- **Paradox (Olivia):** Conversational screening and scheduling agent.

---

## 5. Scoring Expectation & Rubric Anchors for Scenario B

| Dimension | Minimal Baseline Expectation | High-Quality BeenHere Expectation |
| :--- | :--- | :--- |
| **D1: Solutions Discovered** | Mentions generic ATS names and basic sentence embeddings. | Discovers Horilla HR, Docling, Sentence-Transformers, Fairlearn, and analyzes commercial ATS integration barriers. |
| **D2: Reusable Code** | High-level suggestion to "write a parser in Python". | Inspects `docling/document_converter.py`, `cross_encoder.py`, and `fairlearn/metrics.py`, extracting concrete entrypoints and signatures. |
| **D3: Accuracy & Evidence** | Plausible links, but unverified dependency claims. | Strictly tags evidence; confirms real push dates, star counts, and validates `pgvector` PostgreSQL license. |
| **D4: Licensing & Risk** | Accepts Horilla's LGPL claim at face value. | Flags the transitive PyMuPDF AGPL dual-license risk in Horilla's `requirements.txt`; warns against commercial SaaS exposure. |
| **D5: Cross-Industry** | Generic comparison to search engines. | Evaluates two-stage search retrieval (coarse vector recall + fine-grained cross-encoder re-ranking) adapted from e-commerce product search. |
| **D6: Recommendation** | Suggests deploying Horilla HR directly. | Decisive strategy: Reject Horilla due to AGPL risk; build modular pipeline reusing Docling (MIT) + Sentence-Transformers (Apache-2.0) + Fairlearn (MIT) on Postgres. |
