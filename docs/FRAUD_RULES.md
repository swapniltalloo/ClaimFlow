# ClaimFlow Fraud Detection Rules Catalog

This document defines the 8 primary fraud patterns detected by ClaimFlow's hybrid engine (Deterministic Rules + Anomaly Models + Supervised Classifier).

| Rule ID | Pattern Name | Category | Logic & Detection Criteria | Severity Score (0-100) |
|---|---|---|---|---|
| **FR-001** | Upcoding | Coding Abuse | Procedure billed requires complex/severe condition, but clinical findings indicate minor/simple severity (e.g., uncomplicated appendectomy billed as open laparotomy with peritonitis). | 75 |
| **FR-002** | Unbundling | Billing Abuse | Individual procedure components billed separately when an all-inclusive comprehensive package code exists in the tariff schedule. | 65 |
| **FR-003** | Phantom Services | Fabrication | Billed procedures, labs, or consumables with zero corresponding clinical documentation or evidence snippets in the EHR discharge summary. | 95 |
| **FR-004** | Length-of-Stay Inflation | Billing Abuse | Total billed room/ward/ICU days exceed the duration between recorded clinical admission and discharge timestamps. | 85 |
| **FR-005** | Duplicate Billing | Error / Fraud | Identical service code, medication, or consumable billed multiple times for the same encounter or cross-submitted across insurers. | 80 |
| **FR-006** | Diagnosis-Procedure Mismatch | Clinical Incoherence | The billed surgical or diagnostic procedure is clinically incompatible with the primary/secondary ICD-10 diagnoses (e.g., orthopedic surgery billed for dengue fever). | 90 |
| **FR-007** | Exclusion / Waiting Period Violation | Policy Violation | Billed service belongs to a restricted pre-existing condition, initial 30-day exclusion, or standard waiting period without elapsed coverage tenure. | 70 |
| **FR-008** | Price Inflation | Overcharging | Billed unit cost of a consumable, implant, or service exceeds 2 standard deviations (>2σ) above regional tariff benchmarks. | 60 |
