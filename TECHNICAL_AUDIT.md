# TECHNICAL AUDIT REPORT: SkillMatch AI
**Date:** November 2026  
**Auditor:** Senior Software Architect, ML Engineer & QA Specialist  
**System Evaluated:** SkillMatch AI – Smart Career Compatibility Analyzer  

---

## 1. Executive Summary

A comprehensive architectural and functional audit of the existing codebase was conducted across all modules, pages, models, and utility scripts. While the foundational natural language processing, taxonomy parsing, and PDF report generation work effectively, the system currently suffers from **severe data persistence vulnerabilities**, **session-state fragility across browser refreshes**, **limited analytical depth (lack of role comparisons and history tracking)**, and **unvalidated machine learning evaluation claims**.

This document details the root causes of all identified issues and establishes the remediation blueprint implemented across Phases 2 through 8.

---

## 2. Comprehensive Audit Findings

### Issue 1: Absolute Loss of State on Browser Refresh (Critical Data Persistence Vulnerability)
- **Files Affected:** `app.py`, `utils/helpers.py`, all `pages/*.py`
- **Root Cause:** All candidate profiles, extracted skills, matched jobs, gaps, and generated roadmaps are stored exclusively in volatile `st.session_state` in memory. Streamlit clears `st.session_state` whenever a user presses F5 / refreshes their browser or when the Python server restarts.
- **Impact:** Candidates must re-upload their resume and re-run all computations every time they navigate back or refresh the page. There is zero historical record of past compatibility evaluations.
- **Remediation Plan:** Implement an embedded SQLite database (`database/skillmatch.db`) with 7 relational tables as the single source of truth, featuring automatic profile persistence, auto-reload on launch, and unique session tracking.

---

### Issue 2: Redundant and Heavy Recalculations on Streamlit Reruns
- **Files Affected:** `pages/2_🎯_Job_Matching.py`, `pages/4_🚀_Career_Recommendations.py`
- **Root Cause:** In Streamlit, any widget interaction (e.g., toggling a slider or radio button) triggers a complete script rerun from top to bottom. `pages/2_🎯_Job_Matching.py` was recalculating TF-IDF vector transformations and cosine similarity on every single widget change even when resume text and job description had not changed.
- **Impact:** Unnecessary CPU overhead, laggy slider interactions, and risk of duplicate database inserts.
- **Remediation Plan:** Introduce computation caching / memoization and conditional checks (only recalculate when target role, JD, weights, or resume hash change), coupled with idempotent database transactions.

---

### Issue 3: Incomplete Button Actions & Missing Interaction Callbacks
- **Files Affected:** `pages/1_📄_Resume_Analyzer.py`, `pages/2_🎯_Job_Matching.py`, `pages/5_🗺️_Learning_Roadmap.py`, `app.py`
- **Root Cause:**
  - On the Home page, there was no secondary "Explore Features" button as required by the specification.
  - On the Resume Analyzer, skill removals and additions triggered full page `st.rerun()`, but did not persist changes to any underlying database.
  - In Job Matching, there was no "Save Analysis to Profile" button.
  - In Learning Roadmap, steps were displayed as static cards without interactive completion checkboxes, meaning users could not track their upskilling progress.
- **Impact:** Decreased user engagement, inability to track learning progress, and lack of explicit saving options.
- **Remediation Plan:** Add explicit "Save Analysis", "Mark Milestone Completed", and "Explore Features" callbacks with database persistence.

---

### Issue 4: Fragile Resume Parsing Error Boundaries
- **Files Affected:** `modules/resume_parser.py`
- **Root Cause:** While PyMuPDF handles standard PDF structures, PDF stream edge cases (e.g. zero-page documents, encrypted PDFs without passwords, or dual-column layout collisions) could fail silently or produce unstructured whitespace artifacts without persistent feedback.
- **Impact:** Potential user confusion when uploading non-standard PDF formats.
- **Remediation Plan:** Harden exception handling, add format validation, clean dual-column flow, and log extraction diagnostics.

---

### Issue 5: Artificial 100% Accuracy Claim in Supervised Classifier Training
- **Files Affected:** `train_models.py`
- **Root Cause:** In `train_models.py`, training accuracy was computed on the entire training set $X$ (`clf.predict(X)`) without a stratified train/test split or k-fold cross-validation. Evaluating on the training set caused an overfitted 100% reported accuracy, which does not reflect true generalization performance.
- **Impact:** Misleading evaluation metric in academic and professional contexts.
- **Remediation Plan:** Refactor `train_models.py` to use Stratified 5-Fold Cross-Validation or stratified train/test split ($80/20$), report out-of-fold precision/recall/F1, and document clearly that the dataset is a curated starter benchmark.

---

### Issue 6: Lack of Multi-Role Job Comparison
- **Files Affected:** `pages/2_🎯_Job_Matching.py`
- **Root Cause:** The matching interface only allowed a 1-to-1 comparison between the candidate and a single job role.
- **Impact:** Candidates cannot benchmark multiple opportunities side-by-side (e.g. comparing readiness for "Data Analyst" vs "Data Scientist" vs "Machine Learning Engineer").
- **Remediation Plan:** Implement a Multi-Role Comparison feature allowing candidates to select 2 to 4 roles simultaneously and compare scores, matched skills, and critical gaps in a comparative Plotly radar and bar view.

---

### Issue 7: Inconsistent and Basic UI Styling
- **Files Affected:** `utils/helpers.py`, all `pages/*.py`
- **Root Cause:** Streamlit default widgets (radio buttons, sliders, file uploader) clashed with custom CSS cards, and there was no dark/light cohesive palette. The compatibility gauge was small and lacked visual prominence.
- **Impact:** Did not meet the standard of a modern, premium AI SaaS application.
- **Remediation Plan:** Implement a complete design overhaul with deep navy backgrounds, electric-blue/purple highlights, rounded dashboard cards, glassmorphic badges, sleek circular score indicators, and cohesive typography.

---

### Issue 8: Absence of Analysis History & Audit Trails
- **Files Affected:** Entire architecture
- **Root Cause:** There was no page or database module dedicated to managing previous candidate analyses, re-opening past sessions, or safely deleting records.
- **Impact:** Inability to audit career progress over time.
- **Remediation Plan:** Build `modules/database.py` and a dedicated `pages/8_📜_Analysis_History.py` providing instant retrieval, detailed inspection, single deletion, and confirmed history clearing.

---

## 3. Action Matrix & Implementation Roadmap

| Phase | Milestone | Priority | Status |
| :---: | :--- | :---: | :---: |
| **Phase 1** | Comprehensive Technical Audit (`TECHNICAL_AUDIT.md`) | Highest | COMPLETED |
| **Phase 2** | SQLite Database Architecture (`database/skillmatch.db`) | Highest | PENDING |
| **Phase 3** | Streamlit State Management & DB Sync | Highest | PENDING |
| **Phase 4** | Interactive Button Repairs & Callbacks | High | PENDING |
| **Phase 5** | Complete UI/UX Redesign (SaaS Theme) | High | PENDING |
| **Phase 6** | Functional Improvements (History, Multi-Role Compare, Roadmap Progress) | High | PENDING |
| **Phase 7** | Machine Learning Validation & Fair Metric Reporting | Medium | PENDING |
| **Phase 8** | Comprehensive Automated & E2E Testing | High | PENDING |
| **Phase 9** | Final Delivery & Documentation Updates | Medium | PENDING |

