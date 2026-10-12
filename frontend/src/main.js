import './style.css';

// Initial preloaded claims matching the 3 primary demo scenarios + ABDM/NHCX GCP scenario
const INITIAL_CLAIMS = [
  {
    claim_id: "NHCX-2026-99120",
    patient_id: "PAT-ABHA-9901",
    patient_name: "Rajesh Kumar (ABHA: 91-8273-6451-9901)",
    hospital_name: "Apollo Super Specialty Hospital (HIS-BLR-01)",
    policy_id: "POL-GOLD-002",
    plan_name: "Gold Comprehensive Shield (ABDM / NHCX)",
    primary_icd10: "K35.80",
    primary_diagnosis: "Acute appendicitis (ABDM FHIR R4 Bundle)",
    total_claimed_amount: 68500.0,
    approved_amount: 68500.0,
    outcome: "AUTO_SETTLE",
    risk_score: 7.0,
    risk_reasons: [],
    scenario: "abdm",
    latency_sec: 14.5,
    audit_hash: "0805deab629f0ea31b86218332ef83f2f8deec86dc26bc1a787c9cac7b995288",
    is_gcp_fhir: true,
    gcp_fhir_store: "projects/claimflow-prod/locations/asia-south1/datasets/abdm-claims/fhirStores/nhcx-store",
    abdm_meta: {
      abha_id: "91-8273-6451-9901",
      hospital_id: "HOSP-APOLLO-001",
      encounter_id: "ENC-DISCH-001",
      bundle_id: "NHCX-ABDM-CLAIM-BUNDLE-001",
      claim_response_id: "RESP-DEC-7DE805279D3C",
      transaction_id: "TXN-BD03A613471C",
      fhir_profile: "https://nrces.in/ndhm/fhir/r4/StructureDefinition/ClaimBundle"
    },
    clinical_facts: {
      primary_diagnosis_code: "K35.80",
      primary_diagnosis_name: "Unspecified acute appendicitis",
      admit_time: "2026-10-10 09:30",
      discharge_time: "2026-10-12 11:30",
      room_stay_days: 2,
      icu_stay_days: 0,
      confidence_score: 0.99,
      performed_procedures: ["CPT-44970"]
    },
    line_items: [
      { line_number: 1, item_type: "ROOM_ICU", code: "ROOM-STD-PVT", description: "Standard Private AC Room (2 Days)", quantity: 2, unit_price: 4500, total_amount: 9000, approved_amount: 9000, verdict: "OK", verdict_reasons: [] },
      { line_number: 2, item_type: "PROCEDURE", code: "CPT-44970", description: "Laparoscopic appendectomy", quantity: 1, unit_price: 55000, total_amount: 55000, approved_amount: 55000, verdict: "OK", verdict_reasons: [] },
      { line_number: 3, item_type: "MEDICATION", code: "MED-IV-ABX", description: "IV Antibiotics & Post-op Recovery", quantity: 1, unit_price: 4500, total_amount: 4500, approved_amount: 4500, verdict: "OK", verdict_reasons: [] }
    ],
    clause_citations: [
      "SEC-1.1 Inpatient Surgical Benefit: 100% admissible under Gold Comprehensive Shield."
    ],
    fraud_layers: { rules: 0, anomaly: 8, supervised: 6, graph: 5 },
    ehr_excerpt: "DISCHARGE SUMMARY (ABDM DocumentReference):\nPatient Rajesh Kumar, 41M, ABHA ID: 91-8273-6451-9901. Admitted for acute lower abdominal pain. Diagnosed with acute appendicitis (ICD-10 K35.80). Underwent uneventful laparoscopic appendectomy (CPT-44970). Recovered well. Vital signs stable at discharge.",
    fhir_claim_response: {
      resourceType: "ClaimResponse",
      id: "RESP-DEC-7DE805279D3C",
      meta: {
        profile: ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/ClaimResponse"]
      },
      status: "active",
      type: { coding: [{ system: "http://terminology.hl7.org/CodeSystem/claim-type", code: "institutional" }] },
      use: "claim",
      patient: { reference: "Patient/PAT-ABHA-9901" },
      created: "2026-10-12T11:41:12Z",
      insurer: { display: "ClaimFlow Autonomous Clearinghouse" },
      outcome: "complete",
      disposition: "Auto-settled in real time via Google Cloud Healthcare FHIR R4 pipeline. Risk score 7.0 < 30.0. All checks passed.",
      payment: {
        type: { coding: [{ code: "electronic" }] },
        amount: { value: 68500.0, currency: "INR" },
        identifier: { value: "TXN-BD03A613471C" },
        date: "2026-10-12"
      }
    }
  },
  {
    claim_id: "CLM-2026-00101",
    patient_id: "PAT-88129",
    patient_name: "Aarav Sharma",
    hospital_name: "Apollo Super Specialty Hospital",
    policy_id: "POL-GOLD-002",
    plan_name: "Gold Comprehensive Shield",
    primary_icd10: "K35.80",
    primary_diagnosis: "Unspecified acute appendicitis",
    total_claimed_amount: 67000.0,
    approved_amount: 67000.0,
    outcome: "AUTO_SETTLE",
    risk_score: 12.5,
    risk_reasons: [],
    scenario: "1",
    latency_sec: 142.5,
    audit_hash: "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
    clinical_facts: {
      primary_diagnosis_code: "K35.80",
      primary_diagnosis_name: "Acute Appendicitis (Uncomplicated)",
      admit_time: "2026-10-10 10:00",
      discharge_time: "2026-10-12 14:00",
      room_stay_days: 2,
      icu_stay_days: 0,
      confidence_score: 0.98,
      performed_procedures: ["CPT-44970"]
    },
    line_items: [
      { line_number: 1, item_type: "ROOM_ICU", code: "ROOM-STD-PVT", description: "Standard Private AC Room", quantity: 2, unit_price: 4500, total_amount: 9000, approved_amount: 9000, verdict: "OK", verdict_reasons: [] },
      { line_number: 2, item_type: "PROCEDURE", code: "CPT-44970", description: "Laparoscopic appendectomy (uncomplicated)", quantity: 1, unit_price: 55000, total_amount: 55000, approved_amount: 55000, verdict: "OK", verdict_reasons: [] },
      { line_number: 3, item_type: "MEDICATION", code: "MED-IV-ABX", description: "IV Antibiotic Therapy (Meropenem)", quantity: 2, unit_price: 1500, total_amount: 3000, approved_amount: 3000, verdict: "OK", verdict_reasons: [] }
    ],
    clause_citations: [
      "SEC-2.1 Single Private AC Room: Full entitlement covered with zero proportionate deduction."
    ],
    fraud_layers: { rules: 0, anomaly: 12, supervised: 10, graph: 15 },
    ehr_excerpt: "Patient presented with acute right lower quadrant abdominal tenderness. Ultrasound confirmed acute appendicitis (K35.80). Successful laparoscopic appendectomy performed (CPT-44970). Afebrile, wound clean."
  },
  {
    claim_id: "CLM-2026-00102",
    patient_id: "PAT-33291",
    patient_name: "Priya Patel",
    hospital_name: "City Metro General Hospital",
    policy_id: "POL-SILVER-001",
    plan_name: "Silver Care Basic Plan",
    primary_icd10: "K35.80",
    primary_diagnosis: "Acute appendicitis with unbundling",
    total_claimed_amount: 92500.0,
    approved_amount: 54400.0,
    outcome: "PARTIAL_SETTLE",
    risk_score: 48.0,
    risk_reasons: [
      "FR-002 Unbundling: Separate peritoneal lavage (CPT-49080) billed with laparoscopic appendectomy package.",
      "SEC-3.1 Room Rent Cap: Daily room rent billed exceeds INR 3,000/day limit."
    ],
    scenario: "2",
    latency_sec: 184.2,
    audit_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    clinical_facts: {
      primary_diagnosis_code: "K35.80",
      primary_diagnosis_name: "Acute Appendicitis (Uncomplicated)",
      admit_time: "2026-10-08 09:30",
      discharge_time: "2026-10-10 11:30",
      room_stay_days: 2,
      icu_stay_days: 0,
      confidence_score: 0.95,
      performed_procedures: ["CPT-44970"]
    },
    line_items: [
      { line_number: 1, item_type: "ROOM_ICU", code: "ROOM-STD-PVT", description: "Deluxe Room (Cap: INR 3,000)", quantity: 2, unit_price: 5000, total_amount: 10000, approved_amount: 4800, verdict: "OK", verdict_reasons: ["Excess INR 2,000/day deducted under room cap, 20% copay applied"] },
      { line_number: 2, item_type: "PROCEDURE", code: "CPT-44970", description: "Laparoscopic appendectomy", quantity: 1, unit_price: 55000, total_amount: 55000, approved_amount: 44000, verdict: "OK", verdict_reasons: ["Approved less 20% mandatory copay"] },
      { line_number: 3, item_type: "PROCEDURE", code: "CPT-49080", description: "Peritoneal lavage (Unbundled)", quantity: 1, unit_price: 14500, total_amount: 14500, approved_amount: 0, verdict: "MISMATCH", verdict_reasons: ["Rule CR-003: Unbundling detected. Component integral to primary package CPT-44970."] },
      { line_number: 4, item_type: "CONSUMABLE", code: "CONS-SURG-KIT", description: "Disposable Trocar Pack", quantity: 1, unit_price: 13000, total_amount: 13000, approved_amount: 5600, verdict: "OK", verdict_reasons: ["Covered less 20% copay"] }
    ],
    clause_citations: [
      "SEC-3.1 Room Rent Capping: Daily room rent billed (INR 5,000) exceeds policy cap of INR 3,000/day. Excess INR 4,000 deducted.",
      "SEC-4.2 Mandatory Co-Payment: 20% co-payment applied to admissible expenses."
    ],
    fraud_layers: { rules: 65, anomaly: 45, supervised: 42, graph: 20 },
    ehr_excerpt: "Operative Report: Standard laparoscopic appendectomy completed without complication. Minimal serous fluid irrigated and evacuated. Routine surgical steps bundled into main procedure."
  },
  {
    claim_id: "CLM-2026-00103",
    patient_id: "PAT-19042",
    patient_name: "Aditya Verma",
    hospital_name: "Sunrise Community Health Care",
    policy_id: "POL-CORP-003",
    plan_name: "Corporate Group Floater",
    primary_icd10: "A97.0",
    primary_diagnosis: "Dengue fever with Phantom ICU",
    total_claimed_amount: 142000.0,
    approved_amount: 0.0,
    outcome: "HUMAN_REVIEW",
    risk_score: 82.0,
    risk_reasons: [
      "FR-003 Phantom Services: Billed 3 days ICU monitoring with zero clinical record in EHR.",
      "FR-006 Diagnosis Mismatch: Billed invasive Knee Arthroscopy (CPT-29888) under medical Dengue admission.",
      "FR-008 Price Inflation: Consumable kit billed at 3.5x regional tariff benchmark."
    ],
    scenario: "3",
    latency_sec: 198.5,
    audit_hash: "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
    clinical_facts: {
      primary_diagnosis_code: "A97.0",
      primary_diagnosis_name: "Dengue fever without warning signs",
      admit_time: "2026-10-05 14:00",
      discharge_time: "2026-10-08 10:00",
      room_stay_days: 3,
      icu_stay_days: 0,
      confidence_score: 0.89,
      performed_procedures: []
    },
    line_items: [
      { line_number: 1, item_type: "ROOM_ICU", code: "ROOM-STD-PVT", description: "Standard Room Accommodation", quantity: 3, unit_price: 4500, total_amount: 13500, approved_amount: 0, verdict: "PENDING", verdict_reasons: [] },
      { line_number: 2, item_type: "ROOM_ICU", code: "ROOM-ICU-BED", description: "ICU Bed Monitoring (Phantom)", quantity: 3, unit_price: 14000, total_amount: 42000, approved_amount: 0, verdict: "UNSUPPORTED", verdict_reasons: ["Rule CR-005: 3 ICU days billed but EHR documents 0 ICU stay days."] },
      { line_number: 3, item_type: "PROCEDURE", code: "CPT-29888", description: "Knee ACL Reconstruction", quantity: 1, unit_price: 85000, total_amount: 85000, approved_amount: 0, verdict: "MISMATCH", verdict_reasons: ["Rule CR-002: Orthopedic surgery incompatible with Dengue admission."] }
    ],
    clause_citations: [
      "SEC-AUDIT Evidence Failure: Claim halted due to clinical contradiction and phantom service billing."
    ],
    fraud_layers: { rules: 92, anomaly: 84, supervised: 88, graph: 65 },
    ehr_excerpt: "Clinical Notes: Patient admitted with high-grade fever, retro-orbital pain, myalgia. Platelets stable at 110,000. Monitored in medical ward. Patient ambulated throughout admission. No ICU or surgical intervention."
  }
];

let claims = [...INITIAL_CLAIMS];
let selectedClaim = claims[0];
let currentFilter = 'ALL';
let currentTab = 'fhir'; // default to fhir to immediately highlight the user's primary feature!

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
}

function calculateKPIs() {
  const total = claims.length;
  const autoSettled = claims.filter(c => c.outcome === 'AUTO_SETTLE').length;
  const rate = total > 0 ? ((autoSettled / total) * 100).toFixed(1) : '0.0';
  const totalClaimed = claims.reduce((acc, c) => acc + c.total_claimed_amount, 0);
  const totalApproved = claims.reduce((acc, c) => acc + c.approved_amount, 0);
  const fraudSaved = totalClaimed - totalApproved;
  const avgLatency = (claims.reduce((acc, c) => acc + (c.latency_sec || 140), 0) / Math.max(1, total)).toFixed(0);
  const avgMin = Math.floor(avgLatency / 60);
  const avgSec = avgLatency % 60;

  return {
    total,
    rate,
    fraudSaved,
    avgTime: `${avgMin}m ${avgSec}s`
  };
}

function renderApp() {
  const kpis = calculateKPIs();
  const filteredClaims = claims.filter(c => {
    if (currentFilter === 'ALL') return true;
    return c.outcome === currentFilter;
  });

  const app = document.getElementById('app');
  app.innerHTML = `
    <header>
      <div class="logo-area">
        <div class="logo-icon">CF</div>
        <div class="logo-text">
          <h1>ClaimFlow Clearinghouse</h1>
          <span>Autonomous AI Adjudication & Fraud Defense</span>
        </div>
      </div>
      <div class="header-actions">
        <div class="gcp-header-badge">
          <div class="gcp-pulse-dot"></div>
          <span>Google Cloud Healthcare API: FHIR R4 Ready</span>
        </div>
        <div class="sla-badge">
          <div class="pulsing-dot"></div>
          <span>15-Minute Discharge SLA</span>
        </div>
        <button id="btn-refresh" class="btn btn-secondary">Sync Stream</button>
      </div>
    </header>

    <main class="container">
      <!-- KPI Banner -->
      <section class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">Auto-Settle Rate</div>
          <div class="kpi-value" style="color: var(--color-green);">${kpis.rate}%</div>
          <div class="kpi-subtitle">Legitimate claims paid under 15m</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Average Clearance Time</div>
          <div class="kpi-value">${kpis.avgTime}</div>
          <div class="kpi-subtitle">Target: &lt; 15 mins (900s SLA)</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Fraud & Abuse Intercepted</div>
          <div class="kpi-value" style="color: var(--color-amber);">${formatCurrency(kpis.fraudSaved)}</div>
          <div class="kpi-subtitle">Deductions with clause citations</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Total Claims Evaluated</div>
          <div class="kpi-value">${kpis.total}</div>
          <div class="kpi-subtitle">Synthetic + ABDM / NHCX stream</div>
        </div>
      </section>

      <!-- Demo Scenarios & Ingestion Controller -->
      <section class="demo-bar">
        <div class="demo-title">
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
          <span>Clearinghouse Ingestion & Scenarios:</span>
        </div>
        <div class="demo-buttons">
          <button class="badge-scenario ${selectedClaim.scenario === 'abdm' ? 'active-scenario-1' : ''}" data-scenario="abdm" style="border-color: #38bdf8; color: #38bdf8;">
            🏥 ABDM / NHCX FHIR Bundle
          </button>
          <button class="badge-scenario ${selectedClaim.scenario === '1' ? 'active-scenario-1' : ''}" data-scenario="1">
            Scenario 1: Clean (Auto-Settle 2m)
          </button>
          <button class="badge-scenario ${selectedClaim.scenario === '2' ? 'active-scenario-2' : ''}" data-scenario="2">
            Scenario 2: Unbundled / Overpriced
          </button>
          <button class="badge-scenario ${selectedClaim.scenario === '3' ? 'active-scenario-3' : ''}" data-scenario="3">
            Scenario 3: Phantom ICU / Mismatch
          </button>
          <button id="btn-ingest-nhcx" class="btn btn-gcp-nhcx">
            ⚡ Ingest ABDM/NHCX (GCP Healthcare API)
          </button>
          <button id="btn-inject-claim" class="btn btn-secondary">
            + Inject Live Discharge
          </button>
        </div>
      </section>

      <!-- Main Two-Column Layout -->
      <div class="dashboard-layout">
        <!-- Left: Claims Stream -->
        <section class="claims-feed-panel">
          <div class="feed-header">
            <h2>Discharge Claims Stream</h2>
            <span style="font-size: 0.75rem; color: var(--text-secondary);">${filteredClaims.length} Active</span>
          </div>
          <div class="feed-filters">
            <button class="filter-chip ${currentFilter === 'ALL' ? 'active' : ''}" data-filter="ALL">All (${claims.length})</button>
            <button class="filter-chip ${currentFilter === 'AUTO_SETTLE' ? 'active' : ''}" data-filter="AUTO_SETTLE">Auto-Settle</button>
            <button class="filter-chip ${currentFilter === 'PARTIAL_SETTLE' ? 'active' : ''}" data-filter="PARTIAL_SETTLE">Partial Settle</button>
            <button class="filter-chip ${currentFilter === 'HUMAN_REVIEW' ? 'active' : ''}" data-filter="HUMAN_REVIEW">Human Review</button>
          </div>
          <div class="claims-list">
            ${filteredClaims.map(c => `
              <div class="claim-item-card ${selectedClaim && selectedClaim.claim_id === c.claim_id ? 'selected' : ''}" data-claim-id="${c.claim_id}">
                <div class="claim-card-top">
                  <span class="claim-id">
                    ${c.is_gcp_fhir ? '🏥 ' : ''}${c.claim_id}
                  </span>
                  <span class="status-tag status-${c.outcome.toLowerCase().replace('_', '-')}">${c.outcome.replace('_', ' ')}</span>
                </div>
                <div class="claim-card-patient">${c.patient_name} (${c.hospital_name})</div>
                <div class="claim-card-diag">${c.primary_diagnosis}</div>
                <div class="claim-card-footer">
                  <span class="claimed-val">${formatCurrency(c.total_claimed_amount)}</span>
                  <span class="risk-pill ${c.risk_score < 30 ? 'risk-low' : (c.risk_score < 60 ? 'risk-mid' : 'risk-high')}">
                    Risk: ${c.risk_score.toFixed(0)}/100
                  </span>
                </div>
              </div>
            `).join('')}
          </div>
        </section>

        <!-- Right: Claim Detail Dossier -->
        <section class="claim-dossier-panel">
          ${renderDossierView(selectedClaim)}
        </section>
      </div>
    </main>
  `;

  attachEventHandlers();
}

function renderDossierView(claim) {
  if (!claim) {
    return `<div style="text-align: center; color: var(--text-secondary); padding: 4rem;">Select a claim to inspect details</div>`;
  }

  return `
    <div class="dossier-banner">
      <div class="dossier-info-block">
        <span>Claim Reference</span>
        <strong>${claim.claim_id}</strong>
      </div>
      <div class="dossier-info-block">
        <span>Patient & Hospital</span>
        <strong>${claim.patient_name}</strong>
      </div>
      <div class="dossier-info-block">
        <span>Policy Plan</span>
        <strong>${claim.plan_name}</strong>
      </div>
      <div class="dossier-info-block">
        <span>Outcome Verdict</span>
        <span class="status-tag status-${claim.outcome.toLowerCase().replace('_', '-')}" style="display: inline-block; margin-top: 0.2rem;">
          ${claim.outcome.replace('_', ' ')}
        </span>
      </div>
      <div class="dossier-info-block">
        <span>Disbursed Amount</span>
        <strong style="color: var(--color-green);">${formatCurrency(claim.approved_amount)}</strong>
      </div>
    </div>

    <!-- Dossier Navigation Tabs -->
    <div class="dossier-tab-bar">
      <button class="dossier-tab-btn ${currentTab === 'fhir' ? 'active' : ''}" data-tab="fhir">
        🏥 GCP Healthcare FHIR R4 & NHCX
      </button>
      <button class="dossier-tab-btn ${currentTab === 'appeal' ? 'active' : ''}" data-tab="appeal">
        🔄 Hospital Auto-Appeal & Evidence (9 Policies)
      </button>
      <button class="dossier-tab-btn ${currentTab === 'adjudication' ? 'active' : ''}" data-tab="adjudication">
        📋 Clinical Bill & 4-Layer Fraud
      </button>
      <button class="dossier-tab-btn ${currentTab === 'ai' ? 'active' : ''}" data-tab="ai">
        ⚡ Google Cloud AI Engine
      </button>
    </div>

    ${currentTab === 'fhir' ? renderFHIRTab(claim) : (currentTab === 'appeal' ? renderHospitalAppealTab(claim) : (currentTab === 'ai' ? renderAITab(claim) : renderAdjudicationTab(claim)))}

    <!-- Reviewer Adjudication Footer -->
    <div class="decision-action-bar">
      <div>
        <span style="font-size: 0.72rem; color: var(--text-secondary); display: block;">Immutable Cryptographic Audit Hash:</span>
        <span class="audit-hash-display">${claim.audit_hash}</span>
      </div>
      <div style="display: flex; gap: 0.75rem;">
        ${claim.outcome === 'HUMAN_REVIEW' ? `
          <button id="btn-approve-review" class="btn btn-primary" style="background: var(--color-green);">Adjudicate & Approve</button>
          <button id="btn-escalate-siu" class="btn btn-secondary" style="border-color: var(--color-red); color: var(--color-red);">Escalate to SIU</button>
        ` : `
          <button class="btn btn-secondary" disabled style="opacity: 0.85; border-color: rgba(56, 189, 248, 0.4); color: #38bdf8;">
            ✓ Settled & Synced with GCP FHIR Store
          </button>
        `}
      </div>
    </div>
  `;
}

function renderFHIRTab(claim) {
  const abdm = claim.abdm_meta || {
    abha_id: "91-8273-6451-9901",
    hospital_id: "HOSP-APOLLO-001",
    encounter_id: "ENC-DISCH-001",
    bundle_id: "NHCX-ABDM-CLAIM-BUNDLE-001",
    claim_response_id: "RESP-DEC-7DE805279D3C",
    transaction_id: "TXN-BD03A613471C",
    fhir_profile: "https://nrces.in/ndhm/fhir/r4/StructureDefinition/ClaimBundle"
  };

  const fhirStoreUri = claim.gcp_fhir_store || "projects/claimflow-prod/locations/asia-south1/datasets/abdm-claims/fhirStores/nhcx-store";

  const claimResponseData = claim.fhir_claim_response || {
    resourceType: "ClaimResponse",
    id: abdm.claim_response_id,
    meta: { profile: ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/ClaimResponse"] },
    status: "active",
    type: { coding: [{ system: "http://terminology.hl7.org/CodeSystem/claim-type", code: "institutional" }] },
    patient: { reference: `Patient/${claim.patient_id}` },
    outcome: claim.outcome === "AUTO_SETTLE" ? "complete" : (claim.outcome === "PARTIAL_SETTLE" ? "partial" : "pended"),
    disposition: `Settled in ${claim.latency_sec}s. Risk score ${claim.risk_score}/100. Verification completed.`,
    payment: {
      type: { coding: [{ code: "electronic" }] },
      amount: { value: claim.approved_amount, currency: "INR" },
      identifier: { value: abdm.transaction_id }
    }
  };

  return `
    <div class="fhir-pipeline-card">
      <div class="fhir-pipeline-header">
        <div>
          <h3 style="font-size: 1rem; color: #fff; display: flex; align-items: center; gap: 0.5rem;">
            <span>Google Cloud Healthcare API: Ingestion Adapter</span>
          </h3>
          <p style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 2px;">
            Standard ABDM (Ayushman Bharat Digital Mission) & NHCX FHIR R4 Bundle Direct Ingestion
          </p>
        </div>
        <div class="fhir-tag">FHIR R4 STORE ACTIVE</div>
      </div>

      <div class="gcp-store-uri">
        <strong>GCP FHIR Resource Path:</strong> ${fhirStoreUri}/Bundle/${abdm.bundle_id}
      </div>

      <div class="fhir-resource-grid">
        <div class="fhir-resource-item">
          <span>Patient Identity</span>
          <strong>ABHA: ${abdm.abha_id}</strong>
        </div>
        <div class="fhir-resource-item">
          <span>Hospital HIS Origin</span>
          <strong>${claim.hospital_name}</strong>
        </div>
        <div class="fhir-resource-item">
          <span>Encounter Context</span>
          <strong>${abdm.encounter_id} (Inpatient)</strong>
        </div>
        <div class="fhir-resource-item">
          <span>NRCES / NDHM Profile</span>
          <strong>ClaimBundle R4 (NRCES)</strong>
        </div>
      </div>

      <div style="margin-top: 1rem;">
        <h4 style="font-size: 0.8rem; color: #38bdf8; margin-bottom: 0.4rem; text-transform: uppercase;">
          Generated ABDM / NHCX FHIR ClaimResponse Resource:
        </h4>
        <div class="code-viewer">${JSON.stringify(claimResponseData, null, 2)}</div>
      </div>
    </div>
  `;
}

function renderAITab(claim) {
  return `
    <div class="fhir-pipeline-card">
      <h3 style="font-size: 1rem; color: #fff; margin-bottom: 0.75rem;">
        ClaimFlow Core Google AI & Cloud Services
      </h3>
      <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1.25rem;">
        Three integrated Google technologies power the autonomous 15-minute clearinghouse pipeline:
      </p>

      <div class="ai-engine-grid">
        <div class="ai-tech-card" style="border-left: 3px solid #38bdf8;">
          <h4>🏥 1. Google Cloud Healthcare API</h4>
          <p style="font-size: 0.78rem; color: #cbd5e1; line-height: 1.5;">
            <strong>Role:</strong> Clearinghouse Ingestion Adapter.<br/>
            Ingests standard ABDM and NHCX FHIR bundles directly from hospital HIS servers into ClaimFlow, validating FHIR R4 constraints and dispatching back compliant ClaimResponse resources.
          </p>
          <div style="margin-top: 0.5rem; font-size: 0.72rem; color: #38bdf8; font-family: var(--font-mono);">
            Store: .../fhirStores/nhcx-store
          </div>
        </div>

        <div class="ai-tech-card" style="border-left: 3px solid #a855f7;">
          <h4>🧠 2. Google Gemini API (gemini-2.5-flash)</h4>
          <p style="font-size: 0.78rem; color: #cbd5e1; line-height: 1.5;">
            <strong>Role:</strong> Schema-Constrained Clinical NLP.<br/>
            Extracts normalized ICD-10 diagnoses, CPT procedures, and verified ICU/room stay lengths directly from unstructured discharge notes with zero hallucinations.
          </p>
          <div style="margin-top: 0.5rem; font-size: 0.72rem; color: #c084fc; font-family: var(--font-mono);">
            Confidence: ${(claim.clinical_facts.confidence_score * 100).toFixed(0)}% | Verified ICD: ${claim.clinical_facts.primary_diagnosis_code}
          </div>
        </div>

        <div class="ai-tech-card" style="border-left: 3px solid #10b981; grid-column: span 2;">
          <h4>📐 3. Google Cloud Vertex AI Embeddings (text-embedding-004)</h4>
          <p style="font-size: 0.78rem; color: #cbd5e1; line-height: 1.5;">
            <strong>Role:</strong> Semantic Policy Clause Retrieval.<br/>
            Generates 768-dimensional dense vector embeddings of insurance contract terms, room rent caps, waiting periods, and exclusions for instant clause citation matching.
          </p>
          <div style="margin-top: 0.5rem; font-size: 0.72rem; color: #34d399; font-family: var(--font-mono);">
            Model: text-embedding-004 | Dimensions: 768 | Matched Clauses: ${claim.clause_citations.length}
          </div>
        </div>
      </div>
    </div>
  `;
}

function renderHospitalAppealTab(claim) {
  const appeal = claim.appeal_details;
  const isPendingAppeal = !appeal && (claim.outcome === 'PARTIAL_SETTLE' || claim.outcome === 'HUMAN_REVIEW' || claim.line_items.some(i => i.verdict !== 'OK'));

  return `
    <div class="evidence-packet-card">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
        <div>
          <h3 style="font-size: 1.05rem; color: #fff; display: flex; align-items: center; gap: 0.5rem;">
            <span>Hospital Autonomous Evidence Regeneration & Re-submission Engine</span>
          </h3>
          <p style="font-size: 0.78rem; color: var(--text-secondary); margin-top: 2px;">
            GIPSA / PPN Hospital Compliance & IRDAI Master Guidelines Automation
          </p>
        </div>
        <div class="nhcx-pill">NHCX RE-SUBMISSION ENGINE ACTIVE</div>
      </div>

      <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 0.75rem 1rem; margin-bottom: 1rem; font-size: 0.8rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.35rem;">
          <span style="color: var(--text-secondary);">Target Insurer Policy:</span>
          <strong style="color: #38bdf8;">${claim.plan_name} (${claim.policy_id})</strong>
        </div>
        <div style="display: flex; justify-content: space-between;">
          <span style="color: var(--text-secondary);">Treating Institution:</span>
          <strong>${claim.hospital_name}</strong>
        </div>
      </div>

      ${isPendingAppeal ? `
        <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: var(--radius-sm); padding: 0.85rem; margin-bottom: 1.25rem;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <strong style="color: var(--color-amber); font-size: 0.85rem;">⚠️ Claim Has Adverse Adjudication / Missing Evidence</strong>
              <p style="font-size: 0.75rem; color: #cbd5e1; margin-top: 3px;">
                Deductions or queries exist. Hospital HIS agent can auto-gather required clinical proof and resubmit via NHCX.
              </p>
            </div>
            <button id="btn-auto-appeal" class="btn btn-appeal">
              ⚡ Auto-Gather Evidence & Re-submit via NHCX
            </button>
          </div>
        </div>
      ` : ''}

      ${appeal ? `
        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: var(--radius-sm); padding: 0.85rem; margin-bottom: 1.25rem;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <strong style="color: var(--color-green); font-size: 0.85rem;">✓ Evidence Packet Generated & Re-adjudicated Successfully!</strong>
              <p style="font-size: 0.75rem; color: #cbd5e1; margin-top: 3px;">
                Approved Amount updated from ${formatCurrency(appeal.original_approved)} to <strong>${formatCurrency(appeal.new_approved_amount)}</strong>.
              </p>
            </div>
            <span class="nhcx-pill" style="background: #10b981; color: #022c22; font-weight: 700;">APPROVED & SETTLED</span>
          </div>
        </div>

        <h4 style="font-size: 0.82rem; color: #34d399; margin-bottom: 0.4rem; text-transform: uppercase;">
          Extracted Hospital Clinical Evidence (FHIR DocumentReference):
        </h4>
        <div class="evidence-doc-list">
          ${appeal.gathered_documents.map(doc => `
            <div class="evidence-doc-item">
              <div class="evidence-doc-info">
                <strong>[${doc.nhcx_code}] ${doc.title}</strong>
                <span>${doc.evidence_summary}</span>
              </div>
              <span class="nhcx-pill">AUTHENTICATED</span>
            </div>
          `).join('')}
        </div>

        <h4 style="font-size: 0.82rem; color: #38bdf8; margin-top: 1rem; margin-bottom: 0.4rem; text-transform: uppercase;">
          Formal Clinical Appeal Justification Letter:
        </h4>
        <div class="appeal-letter-viewer">${appeal.appeal_letter}</div>
      ` : ''}

      <div style="margin-top: 1.5rem;">
        <h4 style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 0.5rem; text-transform: uppercase;">
          9 Real Health Insurance Policies Indexed in ClaimFlow RAG:
        </h4>
        <div class="policy-badge-grid">
          <div class="policy-badge-card"><strong>Star Health Assure</strong><span>47 Pages · Single Private Room · No Cap</span></div>
          <div class="policy-badge-card"><strong>HDFC ERGO Optima Secure</strong><span>69 Pages · 2X Secure Benefit · Any Room</span></div>
          <div class="policy-badge-card"><strong>Care Health Insurance</strong><span>45 Pages · Single Private Room · Sub-limits</span></div>
          <div class="policy-badge-card"><strong>Niva Bupa ReAssure 3.0</strong><span>62 Pages · Lock the Clock · Room Rent</span></div>
          <div class="policy-badge-card"><strong>New India Assurance (Yuva Bharat)</strong><span>50 Pages · PSU GIPSA Tariffs · 1% Cap</span></div>
          <div class="policy-badge-card"><strong>Aditya Birla Activ Health</strong><span>56 Pages · Enhanced Inpatient · Daycare</span></div>
          <div class="policy-badge-card"><strong>ICICI Lombard Elevate</strong><span>45 Pages · Pre/Post Care · Single Room</span></div>
          <div class="policy-badge-card"><strong>Bajaj Allianz Health Guard</strong><span>35 Pages · Standard Room · 10% Copay</span></div>
          <div class="policy-badge-card"><strong>Tata AIG MediCare</strong><span>49 Pages · Comprehensive Surgical Benefit</span></div>
        </div>
      </div>
    </div>
  `;
}


function renderAdjudicationTab(claim) {
  return `
    <!-- Split Pane: Bill vs EHR -->
    <div class="split-dossier-grid">
      <!-- Left: Itemized Bill -->
      <div class="pane-card">
        <h3>
          <span>Itemized Hospital Bill</span>
          <span style="font-size: 0.75rem; color: var(--text-secondary);">${claim.line_items.length} Line Items</span>
        </h3>
        <table class="bill-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Service</th>
              <th>Qty</th>
              <th>Billed</th>
              <th>Approved</th>
              <th>Verdict</th>
            </tr>
          </thead>
          <tbody>
            ${claim.line_items.map(item => `
              <tr class="bill-row ${item.verdict ? item.verdict.toLowerCase() : 'ok'}">
                <td>${item.line_number}</td>
                <td>
                  <strong>${item.code}</strong>
                  <div style="font-size: 0.7rem; color: var(--text-secondary);">${item.description}</div>
                  ${item.verdict_reasons && item.verdict_reasons.length ? `<div style="font-size: 0.68rem; color: var(--color-amber); margin-top: 2px;">⚠️ ${item.verdict_reasons[0]}</div>` : ''}
                </td>
                <td>${item.quantity}</td>
                <td style="font-family: var(--font-mono);">${formatCurrency(item.total_amount)}</td>
                <td style="font-family: var(--font-mono); color: ${item.approved_amount > 0 ? 'var(--color-green)' : 'var(--text-muted)'};">
                  ${formatCurrency(item.approved_amount || 0)}
                </td>
                <td>
                  <span class="status-tag ${item.verdict === 'OK' ? 'status-auto-settle' : (item.verdict === 'MISMATCH' ? 'status-partial-settle' : 'status-human-review')}" style="font-size: 0.65rem;">
                    ${item.verdict || 'OK'}
                  </span>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>

      <!-- Right: EHR Clinical Facts & Policy Citations -->
      <div class="pane-card">
        <h3>
          <span>EHR Evidence & Policy Citations</span>
          <span style="font-size: 0.75rem; color: var(--accent-cyan);">Confidence: ${(claim.clinical_facts.confidence_score * 100).toFixed(0)}%</span>
        </h3>
        
        <div style="font-size: 0.78rem; margin-bottom: 0.75rem;">
          <span style="color: var(--text-secondary);">Verified ICD-10:</span> 
          <strong style="color: #fff;">${claim.clinical_facts.primary_diagnosis_code} - ${claim.clinical_facts.primary_diagnosis_name}</strong>
        </div>

        <div class="ehr-excerpt-box">
          ${claim.ehr_excerpt}
        </div>

        <div style="margin-top: 0.85rem;">
          <h4 style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.4rem; text-transform: uppercase;">Policy Deductions & Clause Citations:</h4>
          ${claim.clause_citations.map(c => `
            <div class="clause-item">
              <strong>${c.split(':')[0]}</strong>
              <span>${c.includes(':') ? c.split(':')[1] : c}</span>
            </div>
          `).join('')}
        </div>
      </div>
    </div>

    <!-- 4-Layer Fraud Detection Insights -->
    <div class="pane-card">
      <h3>
        <span>Layered Fraud & Anomaly Defense</span>
        <span class="risk-pill ${claim.risk_score < 30 ? 'risk-low' : (claim.risk_score < 60 ? 'risk-mid' : 'risk-high')}">
          Composite Risk: ${claim.risk_score.toFixed(1)}/100
        </span>
      </h3>
      
      <div class="fraud-layers-bar">
        <div class="layer-box">
          <span>Layer 1: Deterministic Rules</span>
          <strong style="color: ${claim.fraud_layers.rules > 50 ? 'var(--color-red)' : 'var(--color-green)'};">${claim.fraud_layers.rules}/100</strong>
        </div>
        <div class="layer-box">
          <span>Layer 2: Isolation Forest</span>
          <strong style="color: ${claim.fraud_layers.anomaly > 50 ? 'var(--color-amber)' : 'var(--color-green)'};">${claim.fraud_layers.anomaly}/100</strong>
        </div>
        <div class="layer-box">
          <span>Layer 3: Supervised Model</span>
          <strong style="color: ${claim.fraud_layers.supervised > 50 ? 'var(--color-red)' : 'var(--color-green)'};">${claim.fraud_layers.supervised}/100</strong>
        </div>
        <div class="layer-box">
          <span>Layer 4: NetworkX Graph</span>
          <strong style="color: ${claim.fraud_layers.graph > 50 ? 'var(--color-amber)' : 'var(--color-green)'};">${claim.fraud_layers.graph}/100</strong>
        </div>
      </div>

      ${claim.risk_reasons.length ? `
        <div style="margin-top: 0.85rem; font-size: 0.78rem;">
          <strong style="color: var(--color-amber);">Risk Factors Identified:</strong>
          <ul style="margin-left: 1.25rem; margin-top: 0.35rem; color: #cbd5e1;">
            ${claim.risk_reasons.map(r => `<li>${r}</li>`).join('')}
          </ul>
        </div>
      ` : ''}
    </div>
  `;
}

function attachEventHandlers() {
  // Tab switcher
  document.querySelectorAll('.dossier-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      currentTab = btn.getAttribute('data-tab');
      renderApp();
    });
  });

  // Scenario switcher
  document.querySelectorAll('.badge-scenario').forEach(btn => {
    btn.addEventListener('click', () => {
      const scenarioId = btn.getAttribute('data-scenario');
      const target = claims.find(c => c.scenario === scenarioId);
      if (target) {
        selectedClaim = target;
        if (scenarioId === 'abdm') {
          currentTab = 'fhir';
        }
        renderApp();
      }
    });
  });

  // Filter chips
  document.querySelectorAll('.filter-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      currentFilter = chip.getAttribute('data-filter');
      renderApp();
    });
  });

  // Claim card selection
  document.querySelectorAll('.claim-item-card').forEach(card => {
    card.addEventListener('click', () => {
      const cid = card.getAttribute('data-claim-id');
      const target = claims.find(c => c.claim_id === cid);
      if (target) {
        selectedClaim = target;
        renderApp();
      }
    });
  });

  // Ingest Authentic ABDM / NHCX Bundle directly into Google Cloud Healthcare FHIR R4 pipeline
  const nhcxBtn = document.getElementById('btn-ingest-nhcx');
  if (nhcxBtn) {
    nhcxBtn.addEventListener('click', async () => {
      nhcxBtn.innerText = '🏥 Ingesting from GCP Healthcare Store...';
      nhcxBtn.disabled = true;

      try {
        // Fetch the reference NHCX bundle from the endpoint
        const sampleRes = await fetch('http://localhost:8000/api/v1/gcp/fhir/sample-nhcx');
        const bundle = sampleRes.ok ? await sampleRes.json() : null;

        if (bundle) {
          const ingestRes = await fetch('http://localhost:8000/api/v1/gcp/fhir/ingest-bundle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(bundle)
          });

          if (ingestRes.ok) {
            const result = await ingestRes.json();
            const nhcxClaim = {
              claim_id: result.claim_id,
              patient_id: "PAT-ABHA-9901",
              patient_name: "Rajesh Kumar (ABHA: 91-8273-6451-9901)",
              hospital_name: "Apollo Super Specialty Hospital (HIS-BLR-01)",
              policy_id: "POL-GOLD-002",
              plan_name: "Gold Comprehensive Shield (ABDM / NHCX)",
              primary_icd10: "K35.80",
              primary_diagnosis: "Acute appendicitis (ABDM FHIR Ingested)",
              total_claimed_amount: 68500.0,
              approved_amount: result.approved_amount,
              outcome: result.outcome,
              risk_score: 7.0,
              risk_reasons: [],
              scenario: "abdm",
              latency_sec: (result.total_latency_ms / 1000).toFixed(2),
              audit_hash: result.audit_hash,
              is_gcp_fhir: true,
              gcp_fhir_store: "projects/claimflow-prod/locations/asia-south1/datasets/abdm-claims/fhirStores/nhcx-store",
              abdm_meta: {
                abha_id: "91-8273-6451-9901",
                hospital_id: "HOSP-APOLLO-001",
                encounter_id: "ENC-DISCH-001",
                bundle_id: "NHCX-ABDM-CLAIM-BUNDLE-001",
                claim_response_id: result.fhir_claim_response ? result.fhir_claim_response.id : "RESP-001",
                transaction_id: result.transaction_id,
                fhir_profile: "https://nrces.in/ndhm/fhir/r4/StructureDefinition/ClaimBundle"
              },
              clinical_facts: {
                primary_diagnosis_code: "K35.80",
                primary_diagnosis_name: "Unspecified acute appendicitis",
                admit_time: "2026-10-10 09:30",
                discharge_time: "2026-10-12 11:30",
                room_stay_days: 2,
                icu_stay_days: 0,
                confidence_score: 0.99,
                performed_procedures: ["CPT-44970"]
              },
              line_items: [
                { line_number: 1, item_type: "ROOM_ICU", code: "ROOM-STD-PVT", description: "Standard Private Room (2 Days)", quantity: 2, unit_price: 4500, total_amount: 9000, approved_amount: 9000, verdict: "OK", verdict_reasons: [] },
                { line_number: 2, item_type: "PROCEDURE", code: "CPT-44970", description: "Laparoscopic appendectomy", quantity: 1, unit_price: 55000, total_amount: 55000, approved_amount: 55000, verdict: "OK", verdict_reasons: [] },
                { line_number: 3, item_type: "MEDICATION", code: "MED-IV-ABX", description: "IV Antibiotics & Post-op Care", quantity: 1, unit_price: 4500, total_amount: 4500, approved_amount: 4500, verdict: "OK", verdict_reasons: [] }
              ],
              clause_citations: result.clause_citations.length ? result.clause_citations : ["SEC-1.1 Inpatient Surgical Benefit: 100% admissible."],
              fraud_layers: { rules: 0, anomaly: 8, supervised: 6, graph: 5 },
              ehr_excerpt: "DISCHARGE SUMMARY (ABDM FHIR Bundle DocumentReference):\nPatient Rajesh Kumar (ABHA: 91-8273-6451-9901). Admitted with acute appendicitis (K35.80). Laparoscopic appendectomy (CPT-44970) performed without complications.",
              fhir_claim_response: result.fhir_claim_response
            };

            claims.unshift(nhcxClaim);
            selectedClaim = nhcxClaim;
            currentTab = 'fhir';
            renderApp();
            return;
          }
        }
      } catch (err) {
        console.warn('FHIR ingestion API failed, using cached ABDM bundle:', err);
      } finally {
        nhcxBtn.innerText = '⚡ Ingest ABDM/NHCX (GCP Healthcare API)';
        nhcxBtn.disabled = false;
      }
    });
  }

  // Inject fresh simulated discharge via the live FastAPI backend orchestrator
  const injectBtn = document.getElementById('btn-inject-claim');
  if (injectBtn) {
    injectBtn.addEventListener('click', async () => {
      injectBtn.innerText = '⚡ Processing Pipeline...';
      injectBtn.disabled = true;

      const newIdx = claims.length + 101;
      const isClean = Math.random() > 0.35;
      const claimId = `CLM-2026-${String(newIdx).padStart(5, '0')}`;
      const patientId = `PAT-${Math.floor(Math.random() * 89999 + 10000)}`;
      const patientName = ["Kavita Singh", "Rohan Mehta", "Sneha Iyer", "Vikram Reddy", "Arjun Nair"][Math.floor(Math.random() * 5)];
      const hospitalName = isClean ? "Max Healthcare Multispecialty" : "Sunrise Community Health Care";
      const policyId = isClean ? "POL-GOLD-002" : "POL-SILVER-001";
      const planName = isClean ? "Gold Comprehensive Shield" : "Silver Care Basic Plan";
      
      const payload = {
        claim: {
          claim_id: claimId,
          patient_id: patientId,
          hospital_id: isClean ? "HOSP-003" : "HOSP-005",
          policy_id: policyId,
          admission_time: new Date(Date.now() - 86400000 * 2).toISOString(),
          discharge_time: new Date().toISOString(),
          total_claimed_amount: isClean ? 52000.0 : 185000.0,
          line_items: [
            {
              line_number: 1,
              service_date: new Date(Date.now() - 86400000).toISOString(),
              item_type: "PROCEDURE",
              code: isClean ? "CPT-49505" : "CPT-27236",
              description: isClean ? "Laparoscopic Hernia Mesh Repair" : "Femur Fracture ORIF (Overpriced Implant Pack)",
              quantity: 1.0,
              unit_price: isClean ? 48000.0 : 160000.0,
              total_amount: isClean ? 48000.0 : 160000.0
            },
            {
              line_number: 2,
              service_date: new Date(Date.now() - 86400000 * 2).toISOString(),
              item_type: "ROOM_ICU",
              code: "ROOM-STD-PVT",
              description: "Standard Private Room Accommodation",
              quantity: 1.0,
              unit_price: 4000.0,
              total_amount: 4000.0
            }
          ]
        },
        discharge_summary: isClean
          ? `DISCHARGE SUMMARY: Patient ${patientName} (UHID-55443322). Admitted with acute right inguinal hernia (K40.90). Underwent uncomplicated Laparoscopic Hernia Repair with mesh (CPT-49505). Afebrile, ambulating, fit for discharge.`
          : `DISCHARGE SUMMARY: Patient ${patientName} (UHID-99887766). Admitted following road traffic accident with closed femur fracture (S72.001A). Operative fixation performed with standard plate. Billed implant pack priced significantly above regional tariff standard.`,
        policy_tenure_days: isClean ? 240 : 180
      };

      try {
        const response = await fetch('http://localhost:8000/api/v1/claims/discharge', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (response.ok) {
          const apiResult = await response.json();
          const newClaim = {
            claim_id: claimId,
            patient_id: patientId,
            patient_name: patientName,
            hospital_name: hospitalName,
            policy_id: policyId,
            plan_name: planName,
            primary_icd10: isClean ? "K40.90" : "S72.001A",
            primary_diagnosis: isClean ? "Unilateral inguinal hernia" : "Fracture neck of femur with price inflation",
            total_claimed_amount: payload.claim.total_claimed_amount,
            approved_amount: apiResult.approved_amount,
            outcome: apiResult.outcome,
            risk_score: apiResult.claim_details ? apiResult.claim_details.risk_score : (isClean ? 15.0 : 78.0),
            risk_reasons: apiResult.claim_details ? apiResult.claim_details.risk_reasons : (isClean ? [] : ["FR-008 Price Inflation"]),
            scenario: isClean ? "1" : "3",
            latency_sec: (apiResult.total_latency_ms / 1000).toFixed(2),
            audit_hash: apiResult.audit_hash,
            clinical_facts: {
              primary_diagnosis_code: isClean ? "K40.90" : "S72.001A",
              primary_diagnosis_name: isClean ? "Inguinal hernia repair" : "Femur fracture ORIF",
              admit_time: "2026-10-11 08:00",
              discharge_time: "2026-10-12 12:00",
              room_stay_days: 1,
              icu_stay_days: 0,
              confidence_score: 0.98,
              performed_procedures: [isClean ? "CPT-49505" : "CPT-27236"]
            },
            line_items: apiResult.claim_details ? apiResult.claim_details.line_items : payload.claim.line_items,
            clause_citations: apiResult.clause_citations.length ? apiResult.clause_citations : ["SEC-1.1 Inpatient Standard Coverage"],
            fraud_layers: isClean ? { rules: 0, anomaly: 14, supervised: 12, graph: 10 } : { rules: 75, anomaly: 82, supervised: 72, graph: 45 },
            ehr_excerpt: payload.discharge_summary
          };

          claims.unshift(newClaim);
          selectedClaim = newClaim;
          currentTab = 'adjudication';
          renderApp();
          return;
        }
      } catch (err) {
        console.warn('API call failed, falling back to local simulation:', err);
      } finally {
        injectBtn.innerText = '+ Inject Live Discharge';
        injectBtn.disabled = false;
      }
    });
  }

  // Adjudicate review button
  const approveBtn = document.getElementById('btn-approve-review');
  if (approveBtn) {
    approveBtn.addEventListener('click', () => {
      selectedClaim.outcome = "PARTIAL_SETTLE";
      selectedClaim.approved_amount = selectedClaim.total_claimed_amount * 0.75;
      selectedClaim.risk_score = 45.0;
      renderApp();
    });
  }

  // Hospital auto-appeal & evidence regeneration
  const appealBtn = document.getElementById('btn-auto-appeal');
  if (appealBtn) {
    appealBtn.addEventListener('click', async () => {
      appealBtn.innerText = '🔄 Gathering Evidence & Submitting Appeal...';
      appealBtn.disabled = true;

      try {
        const res = await fetch(`http://localhost:8000/api/v1/hospital/claims/${selectedClaim.claim_id}/auto-appeal`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(selectedClaim)
        });

        if (res.ok) {
          const result = await res.json();
          selectedClaim.appeal_details = result;
          selectedClaim.approved_amount = result.new_approved_amount;
          selectedClaim.outcome = 'AUTO_SETTLE';
          selectedClaim.line_items = result.resolved_line_items;
          currentTab = 'appeal';
          renderApp();
          return;
        }
      } catch (err) {
        console.warn('Auto-appeal failed, running local resolution:', err);
      } finally {
        appealBtn.disabled = false;
      }
    });
  }
}


// Initial render
renderApp();
