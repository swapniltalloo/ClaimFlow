import './style.css';

// Initial preloaded claims matching the 3 primary demo scenarios + diverse cases
const INITIAL_CLAIMS = [
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
  const avgLatency = (claims.reduce((acc, c) => acc + (c.latency_sec || 160), 0) / Math.max(1, total)).toFixed(0);
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
        <div class="sla-badge">
          <div class="pulsing-dot"></div>
          <span>15-Minute Discharge SLA: 100% On-Target</span>
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
          <div class="kpi-subtitle">Synthetic clearinghouse stream</div>
        </div>
      </section>

      <!-- Demo Scenarios Controller -->
      <section class="demo-bar">
        <div class="demo-title">
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
          <span>Live Demo Scenarios:</span>
        </div>
        <div class="demo-buttons">
          <button class="badge-scenario ${selectedClaim.scenario === '1' ? 'active-scenario-1' : ''}" data-scenario="1">
            Scenario 1: Clean Claim (Auto-Settle 2m)
          </button>
          <button class="badge-scenario ${selectedClaim.scenario === '2' ? 'active-scenario-2' : ''}" data-scenario="2">
            Scenario 2: Unbundled / Overpriced (Partial Settle)
          </button>
          <button class="badge-scenario ${selectedClaim.scenario === '3' ? 'active-scenario-3' : ''}" data-scenario="3">
            Scenario 3: Phantom ICU / Mismatch (Human Review)
          </button>
          <button id="btn-inject-claim" class="btn btn-primary" style="margin-left: 0.5rem;">
            + Inject Live Discharge
          </button>
        </div>
      </section>

      <!-- Main Two-Column Layout -->
      <div class="dashboard-layout">
        <!-- Left: Claims Stream -->
        <section class="claims-feed-panel">
          <div class="feed-header">
            <h2>Live Discharge Claims</h2>
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
                  <span class="claim-id">${c.claim_id}</span>
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
              <tr class="bill-row ${item.verdict.toLowerCase()}">
                <td>${item.line_number}</td>
                <td>
                  <strong>${item.code}</strong>
                  <div style="font-size: 0.7rem; color: var(--text-secondary);">${item.description}</div>
                  ${item.verdict_reasons.length ? `<div style="font-size: 0.68rem; color: var(--color-amber); margin-top: 2px;">⚠️ ${item.verdict_reasons[0]}</div>` : ''}
                </td>
                <td>${item.quantity}</td>
                <td style="font-family: var(--font-mono);">${formatCurrency(item.total_amount)}</td>
                <td style="font-family: var(--font-mono); color: ${item.approved_amount > 0 ? 'var(--color-green)' : 'var(--text-muted)'};">
                  ${formatCurrency(item.approved_amount)}
                </td>
                <td>
                  <span class="status-tag ${item.verdict === 'OK' ? 'status-auto-settle' : (item.verdict === 'MISMATCH' ? 'status-partial-settle' : 'status-human-review')}" style="font-size: 0.65rem;">
                    ${item.verdict}
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
          <span>Layer 3: Supervised Model (SHAP)</span>
          <strong style="color: ${claim.fraud_layers.supervised > 50 ? 'var(--color-red)' : 'var(--color-green)'};">${claim.fraud_layers.supervised}/100</strong>
        </div>
        <div class="layer-box">
          <span>Layer 4: NetworkX Graph Signals</span>
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
          <button class="btn btn-secondary" disabled style="opacity: 0.7;">Disbursed via Simulated UPI/NEFT</button>
        `}
      </div>
    </div>
  `;
}

function attachEventHandlers() {
  // Scenario switcher
  document.querySelectorAll('.badge-scenario').forEach(btn => {
    btn.addEventListener('click', () => {
      const scenarioId = btn.getAttribute('data-scenario');
      const target = claims.find(c => c.scenario === scenarioId);
      if (target) {
        selectedClaim = target;
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

  // Inject fresh simulated claim
  const injectBtn = document.getElementById('btn-inject-claim');
  if (injectBtn) {
    injectBtn.addEventListener('click', () => {
      const newIdx = claims.length + 101;
      const isClean = Math.random() > 0.35;
      const newClaim = {
        claim_id: `CLM-2026-${String(newIdx).padStart(5, '0')}`,
        patient_id: `PAT-${Math.floor(Math.random() * 89999 + 10000)}`,
        patient_name: ["Kavita Singh", "Rohan Mehta", "Sneha Iyer", "Vikram Reddy"][Math.floor(Math.random() * 4)],
        hospital_name: "Max Healthcare Multispecialty",
        policy_id: "POL-GOLD-002",
        plan_name: "Gold Comprehensive Shield",
        primary_icd10: isClean ? "K40.90" : "S72.001A",
        primary_diagnosis: isClean ? "Unilateral inguinal hernia" : "Fracture neck of femur with price inflation",
        total_claimed_amount: isClean ? 52000.0 : 185000.0,
        approved_amount: isClean ? 52000.0 : 0.0,
        outcome: isClean ? "AUTO_SETTLE" : "HUMAN_REVIEW",
        risk_score: isClean ? 18.0 : 76.5,
        risk_reasons: isClean ? [] : ["FR-008 Price Inflation: Surgical pack priced at 3.2x tariff median."],
        scenario: isClean ? "1" : "3",
        latency_sec: Math.floor(Math.random() * 60 + 120),
        audit_hash: "a" + Math.random().toString(16).substring(2, 10) + "b" + Math.random().toString(16).substring(2, 10),
        clinical_facts: {
          primary_diagnosis_code: isClean ? "K40.90" : "S72.001A",
          primary_diagnosis_name: isClean ? "Inguinal hernia repair" : "Femur fracture ORIF",
          admit_time: "2026-10-11 08:00",
          discharge_time: "2026-10-12 12:00",
          room_stay_days: 1,
          icu_stay_days: 0,
          confidence_score: 0.96,
          performed_procedures: [isClean ? "CPT-49505" : "CPT-27236"]
        },
        line_items: [
          { line_number: 1, item_type: "PROCEDURE", code: isClean ? "CPT-49505" : "CPT-27236", description: isClean ? "Hernia Mesh Repair" : "Femur Fracture ORIF", quantity: 1, unit_price: isClean ? 48000 : 160000, total_amount: isClean ? 48000 : 160000, approved_amount: isClean ? 48000 : 0, verdict: isClean ? "OK" : "MISMATCH", verdict_reasons: [] }
        ],
        clause_citations: isClean ? ["SEC-1.1 Inpatient Surgical Benefit: 100% admissible."] : ["SEC-3.1 Price Cap Deduction"],
        fraud_layers: isClean ? { rules: 10, anomaly: 15, supervised: 12, graph: 10 } : { rules: 75, anomaly: 82, supervised: 70, graph: 40 },
        ehr_excerpt: isClean ? "Clinical Summary: Elective hernia mesh repair completed. Patient ambulating, wound clean. Fit for discharge." : "Clinical Summary: Closed fracture femur. Surgical fixation performed with standard implants."
      };

      claims.unshift(newClaim);
      selectedClaim = newClaim;
      renderApp();
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
}

// Initial render
renderApp();
