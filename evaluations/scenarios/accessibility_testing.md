# Benchmark Evaluation Scenario C: Automated Accessibility Testing Platform

## 1. Standardized Research Brief

> **Instruction to Agent (Verbatim):**
> 
> *"I want to build an automated accessibility (a11y) testing platform for web applications. It needs to evaluate web pages and single-page apps against WCAG 2.1 and 2.2 Level AA/AAA standards, test interactive keyboard navigation and focus traps, measure visual color contrast, and provide automated code remediations in CI/CD.*
> 
> *Before writing any code, research what already exists:*
> *1. What existing open-source accessibility engines, testing tools, or browser extensions exist?*
> *2. What specific components, rules engines, or AST parsers can be reused directly?*
> *3. What license obligations (MPL, LGPL, MIT) apply to the leading candidate tools?*
> *4. What are the known empirical limitations of automated accessibility testing tools?*
> *5. What is your concrete build-versus-reuse recommendation?"*

---

## 2. Target Concept & Architectural Primitives

- **Domain:** Developer Tools / Quality Assurance / Web Standards & Accessibility
- **Core Computational Primitives:**
  - Accessibility Object Model (AOM) and DOM tree traversal
  - WCAG rule evaluation engine and rule parameterization
  - Graph cycle detection for keyboard focus traps and tab order traversal
  - Perceptual color contrast calculation (WCAG 2.1 formula vs WCAG 2.2 APCA)
  - AST parsing and JSX codemod synthesis for shift-left automated remediation

---

## 3. Known Failure Modes in Standard AI Research

1. **Overestimating Automated Detection Coverage:**
   - Standard agents routinely claim that automated tools catch *"80% to 90% of accessibility issues"*.
   - Rigorous empirical evidence (e.g. UK Government Digital Service audits, Veduis 2026 corpus) proves that automated engines detect only **30% to 57%** of WCAG criteria. Semantic issues (logical tab flow, meaningful image alt-text, screen-reader announcements) cannot be evaluated by DOM inspection alone.
2. **Copyleft & Architecture Confusion between Axe-core and Pa11y:**
   - Standard agents treat `pa11y` and `axe-core` as interchangeable competitors.
   - In reality, `axe-core` is the underlying evaluation engine (licensed under **MPL-2.0** file-level weak copyleft), while `pa11y` is a CLI runner wrapping Puppeteer and axe-core (licensed under **LGPL-3.0**).
   - Embedding Pa11y as an internal library in proprietary SaaS products introduces LGPL-3.0 obligations, whereas importing `@axe-core/puppeteer` or `axe-core` npm package falls under MPL-2.0 library permissions.
3. **Conflating Static AST Linting with Rendered DOM Inspection:**
   - Standard agents frequently suggest using static linters like `eslint-plugin-jsx-a11y` to check color contrast, ignoring that contrast depends on computed CSS styles, background images, and runtime DOM layout that do not exist in static source files.
4. **Superficial Analogies:**
   - Standard agents cite physical accessibility metaphors (ADA wheelchair ramps, tactile paving) without identifying transferable computational primitives (such as directed graph traversal for keyboard tab loops).

---

## 4. Ground-Truth Solution Space & Evidence Baseline

### Canonical Open-Source Repositories
- **`dequelabs/axe-core`** (JavaScript, MPL-2.0): The gold-standard automated rules engine for WCAG 2.0, 2.1, and 2.2 Level A/AA/AAA. Weak copyleft allows importing as an npm library without infecting host application code.
- **`pa11y/pa11y`** (JavaScript, LGPL-3.0): Node.js CLI tool running accessibility tests against web pages via Puppeteer.
- **`jsx-eslint/eslint-plugin-jsx-a11y`** (JavaScript, MIT): Static AST linter for React JSX elements, catching markup violations before build.
- **`microsoft/accessibility-insights-web`** (TypeScript, MIT): Web extension and scanner offering automated checks, tab-stop visualization, and assisted manual audit workflows.
- **`GoogleChrome/lighthouse`** (JavaScript, Apache-2.0): Full-page audit suite containing an accessibility category powered by axe-core.

### Academic & Empirical Research Foundations
- **Veduis LLC (2026):** *What Automated Accessibility Testing Actually Detects: A Browser-Verified Corpus of 64 WCAG 2.2 Fail and Pass Pairs Evaluated Against axe-core 4.14.0* (Zenodo/CERN, DOI: 10.5281/zenodo.23829967). Rigorously documents the exact empirical coverage limits across WCAG rules.
- **Vaughan & Suarez (2026):** *Colour Contrast on the Web: A WCAG 2.1 Level AA Compliance Audit of Common Crawl's Top 500 Domains* (arXiv:2602.24067). Analyzes automated static CSS parsing versus live computed DOM contrast.
- **Aljedaani & Mollik (2026):** *Large Language Models for Web Accessibility: A Systematic Literature Review* (arXiv:2605.13873).

---

## 5. Scoring Expectation & Rubric Anchors for Scenario C

| Dimension | Minimal Baseline Expectation | High-Quality BeenHere Expectation |
| :--- | :--- | :--- |
| **D1: Solutions Discovered** | Mentions axe-core and Lighthouse generically. | Discovers Axe-core, Pa11y, Accessibility Insights, and ESLint JSX A11y, distinguishing static AST from live DOM. |
| **D2: Reusable Code** | High-level suggestion to "run accessibility scans". | Inspects `axe-core/lib/core/index.js` and `eslint-plugin-jsx-a11y/src/index.js`, extracting exact audit APIs and runner configs. |
| **D3: Accuracy & Evidence** | Claims automated tools catch "90% of bugs". | Accurately cites empirical research (Veduis 2026) demonstrating that automated engines cover 30–50% of WCAG criteria. |
| **D4: Licensing & Risk** | Claims all tools are standard permissive open-source. | Differentiates MPL-2.0 (Axe-core) from LGPL-3.0 (Pa11y); advises on clean architectural separation for commercial CI/CD. |
| **D5: Cross-Industry** | Superficial analogy to building ramps. | Maps keyboard navigation auditing to directed graph cycle detection from compiler control-flow analysis. |
| **D6: Recommendation** | Vague advice to build a custom browser extension. | Decisive strategy: Adopt `axe-core` as core engine; integrate Playwright for multi-step browser flows; use `eslint-plugin-jsx-a11y` for IDE linting; build custom keyboard focus graph detector. |
