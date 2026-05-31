/* ============================================================
   LetterLens — Backend integration seam
   ------------------------------------------------------------
   THIS IS THE ONE FILE YOUR TEAM EDITS TO GO LIVE.

   The UI never builds analysis itself — it calls runTriage(letterText)
   and renders whatever view-model comes back.

   • Leave apiUrl = null  -> built-in local mock (works offline, any letter)
   • Set apiUrl = "<url>"  -> POSTs the letter to your backend and renders
                              the real agent output via adaptTriageState().

   Your backend should expose run_triage() (src/graph.py) over HTTP and
   return the TriageState dict (src/schemas.py) as JSON. See README.md in
   design_handoff_letterlens/ for the full contract.
   ============================================================ */

window.LetterLensConfig = {
  // ── set this to your endpoint to switch from mock to live agents ──
  apiUrl: null,                 // e.g. "https://your-host/api/triage"
  // optional: extra headers (auth tokens, etc.)
  headers: {},
};

/* ---- letter-type → presentation (icon + accent tones) ----
   Keys match Classification.letter_type from src/agents/orchestrator.py. */
const LETTER_TYPE_META = {
  'debt collection':    { label: 'Debt collection',    tone: '#b06a4f', toneBg: '#f6ece4', icon: I.cash },
  'housing / eviction': { label: 'Housing / eviction', tone: '#c2564a', toneBg: '#f9e7e3', icon: I.home },
  'employment':         { label: 'Employment',         tone: '#a07d34', toneBg: '#f4eedb', icon: I.briefcase },
  'general legal letter': { label: 'General legal letter', tone: '#4a6aa8', toneBg: '#e9eef8', icon: I.search },
};
const typeMeta = (lt) => LETTER_TYPE_META[(lt || '').toLowerCase()] || LETTER_TYPE_META['general legal letter'];
const cap = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s);

/* ============================================================
   adaptTriageState — REAL backend TriageState (src/schemas.py)
   ─────────────────────────────────────────────────────────────
   Maps the dict returned by run_triage() into the UI view-model.
   This is the contract. If you change a field name in the backend,
   change it here too (and only here).
   ============================================================ */
function adaptTriageState(state, letterText) {
  const c = state.classification || {};
  const meta = typeMeta(c.letter_type);

  // specialist_findings is a LIST keyed by agent_name -> index by name
  const byName = {};
  (state.specialist_findings || []).forEach((f) => { byName[f.agent_name] = f; });
  const finding = (name) => {
    const f = byName[name] || {};
    return {
      summary: f.summary || '',
      confidence: f.confidence || 'medium',
      needsLawyer: !!f.needs_lawyer,
      points: f.key_points || [],
      deadlines: f.deadlines || [],
    };
  };

  const v = state.verdict || {};
  const d = state.draft_response || {};
  const law = state.lawyer_recommendation;

  // Live synthesis returns { verdict, reason, next_steps, urgent_deadlines }.
  // Mock / legacy shape uses { value, summary, next_steps }.
  const verdictValue = v.verdict || v.value || 'consult_lawyer';
  const verdictSummary = v.reason || v.summary || '';
  const urgentDeadlines = v.urgent_deadlines || [];

  // Live lawyer_finder returns { lawyer_type, reason, questions_to_ask,
  //   estimated_cost_range, legal_help_categories, documents_to_prepare,
  //   urgency_guidance, jurisdiction_note }.
  // Mock shape adds should_show; live agents only run when verdict warrants it,
  // so presence of the object is sufficient to show the card.
  const showLawyer = law && (law.should_show !== false);

  return {
    id: 'live',
    label: meta.label,
    sub: c.summary || '',
    icon: meta.icon, tone: meta.tone, toneBg: meta.toneBg,
    text: letterText,
    classification: {
      letter_type: cap(c.letter_type) || 'General legal letter',
      jurisdiction: c.jurisdiction && c.jurisdiction !== 'unknown' ? c.jurisdiction : 'Unknown',
      urgency: c.urgency || 'medium',
      summary: c.summary || '',
    },
    findings: { risk: finding('risk'), rights: finding('rights'), obligations: finding('obligations') },
    verdict: {
      value: verdictValue,
      summary: verdictSummary,
      next_steps: v.next_steps || [],
      urgent_deadlines: urgentDeadlines,
    },
    draft: { subject: d.subject || '', body: d.body || '', tone: d.tone || 'calm and documented' },
    lawyer: showLawyer ? {
      type: cap(law.lawyer_type) || 'Civil legal aid',
      blurb: law.reason || 'Recommended by the referral agent',
      questions: law.questions_to_ask || [],
      cost: law.estimated_cost_range || law.cost_notes || '',
      documents: law.documents_to_prepare || [],
      urgencyGuidance: law.urgency_guidance || '',
      jurisdictionNote: law.jurisdiction_note || '',
    } : null,
    latencies: state.latencies || {},
  };
}

/* ============================================================
   LOCAL MOCK — no backend required.
   Mirrors the logic in src/agents/* so teammates can paste ANY
   letter and see a faithful result offline. Replaced wholesale
   the moment apiUrl is set.
   ============================================================ */
function classifyLocal(text) {
  const t = (text || '').toLowerCase();
  let letter_type = 'general legal letter';
  if (/debt|collection|amount due/.test(t)) letter_type = 'debt collection';
  else if (/eviction|notice to quit|rent/.test(t)) letter_type = 'housing / eviction';
  else if (/employment|termination|severance|warning/.test(t)) letter_type = 'employment';

  let urgency = 'medium';
  if (/\b(24 hours|48 hours|immediately|urgent|lawsuit|eviction)\b/.test(t)) urgency = 'high';

  let jurisdiction = 'Unknown';
  const m = (text || '').match(/\b(CA|NY|TX|FL|IL|MA|WA|DC)\b/);
  if (m) jurisdiction = m[1];
  return { letter_type, urgency, jurisdiction };
}

function extractDeadlines(text) {
  const out = [];
  const patterns = [
    /\bwithin \d+ days\b/gi,
    /\bby [A-Z][a-z]+ \d{1,2},? \d{4}\b/g,
    /\brespond by [^.,\n]+/gi,
    /\bdue by [^.,\n]+/gi,
  ];
  patterns.forEach((p) => { const f = (text || '').match(p); if (f) out.push(...f); });
  return [...new Set(out.map((s) => s.trim()))];
}

function buildGenericTriage(text) {
  const c = classifyLocal(text);
  const meta = typeMeta(c.letter_type);
  const needsLawyer = c.urgency === 'high';
  const deadlines = extractDeadlines(text);

  const baseRisk = [
    'Don’t ignore it until you know the deadline and whether the sender has authority.',
    'Keep the envelope, attachments, dates, and every message in one place.',
  ];
  const baseRights = [
    'You can ask for clarification in writing before admitting any facts or liability.',
    'Keep copies of all letters you receive and send.',
  ];
  const riskExtra = {
    'debt collection': ['Ignoring a collection demand can lead to ongoing collection activity or a lawsuit.', 'You may have the right to dispute the debt or request validation, depending on timing.'],
    'housing / eviction': ['Housing notices can have short response windows and court consequences.'],
    'employment': ['Employment letters may affect pay, benefits, references, or claims deadlines.'],
    'general legal letter': [],
  }[c.letter_type];
  const rightsExtra = {
    'debt collection': ['You may be able to dispute the debt or request formal validation.', 'Collectors can be limited in how and when they contact you.'],
    'housing / eviction': ['You may have notice, habitability, payment, or court-process rights.', 'Local tenant protections can matter a lot — check them quickly.'],
    'employment': ['You may have rights related to wages, discrimination, retaliation, or final pay.', 'Signing a release can affect future claims — read carefully before signing.'],
    'general legal letter': [],
  }[c.letter_type];

  const hasDeadlines = deadlines.length > 0;
  let value = 'handle_yourself';
  let vSummary = 'This appears suitable for careful self-handling with documentation.';
  if (c.urgency === 'high') { value = 'urgent'; vSummary = 'This looks time-sensitive and should be reviewed quickly.'; }
  else if (needsLawyer) { value = 'consult_lawyer'; vSummary = 'This may be manageable, but the risk level suggests getting legal guidance.'; }
  else if (hasDeadlines) { value = 'consult_lawyer'; vSummary = 'There are possible deadlines, so verify before acting.'; }

  const next_steps = [
    'Save the letter, envelope, attachments, and any related messages.',
    'Calendar any stated deadlines.',
    'Respond in writing without admitting liability or waiving rights.',
  ];
  if (value !== 'handle_yourself') next_steps.push('Contact a relevant legal-aid group or lawyer before the deadline.');

  const lawyerType = {
    'debt collection': 'Consumer debt defense',
    'housing / eviction': 'Tenant rights or eviction defense',
    'employment': 'Employment law',
    'general legal letter': 'Consumer protection or general civil legal aid',
  }[c.letter_type];

  // deterministic, plausible latencies (stable per letter length)
  const n = (text || '').length;
  const j = (base, span) => base + (n % span);
  const latencies = {
    orchestrator: j(720, 120), risk: j(1260, 200), rights: j(1140, 160),
    obligations: j(620, 120), synthesis: j(370, 80), response_drafter: j(1460, 160),
    lawyer_finder: j(660, 120),
  };

  return {
    id: 'generic', label: meta.label, sub: `Detected a ${c.letter_type} with ${c.urgency} urgency.`,
    icon: meta.icon, tone: meta.tone, toneBg: meta.toneBg, text,
    classification: { letter_type: meta.label, jurisdiction: c.jurisdiction, urgency: c.urgency, summary: `This reads as a ${c.letter_type} with ${c.urgency} urgency.` },
    findings: {
      risk: { summary: `The main risk is that this ${c.letter_type} may escalate if deadlines are missed.`, confidence: 'medium', needsLawyer, points: [...baseRisk, ...riskExtra], deadlines: c.urgency === 'high' ? ['Treat this as time-sensitive — verify any stated deadline today.'] : [] },
      rights: { summary: 'You likely have process and documentation rights worth preserving.', confidence: 'medium', needsLawyer, points: [...baseRights, ...rightsExtra], deadlines: [] },
      obligations: { summary: 'Verify deadlines, preserve records, and respond carefully — no admissions.', confidence: 'medium', needsLawyer, points: [
        'Confirm who sent it and whether they have authority to demand action.',
        'Calendar every stated deadline before you draft a response.',
        'Avoid admissions, payment promises, or signatures until the facts check out.',
      ], deadlines: deadlines.length ? deadlines : ['No explicit deadline detected — still verify dates in the full document.'] },
    },
    verdict: { value, summary: vSummary, next_steps },
    draft: { subject: `Response regarding ${c.letter_type}`, tone: 'calm and documented', body:
`To whom it may concern,

I received your letter and am reviewing it. Please provide any supporting documents, account records, dates, and the legal basis for the requested action. I do not admit liability or waive any rights by asking for this information.

Please communicate with me in writing so I can keep accurate records.

Sincerely,
[Your name]${value === 'urgent' ? '\n\nNote: Because your letter appears time-sensitive, I am also seeking appropriate guidance.' : ''}` },
    lawyer: value !== 'handle_yourself' ? {
      type: lawyerType, blurb: 'Often available through free legal aid',
      questions: ['What deadline matters most right now?', 'Should I respond before you review the full letter?', 'What documents should I gather?', 'Do you offer a limited-scope consult or legal-aid referral?'],
      cost: 'Ask about free legal aid, nonprofit clinics, limited-scope consults, and flat-fee options before agreeing to anything.',
    } : null,
    latencies,
  };
}

function mockTriage(text) {
  // Re-use the lovingly hand-written sample results when the canned text is used…
  const known = (window.SAMPLES || []).find((s) => s.text.trim() === (text || '').trim());
  if (known) return known;
  // …otherwise classify the pasted letter locally.
  return buildGenericTriage(text);
}

/* ============================================================
   runTriage — the single entry point the UI calls.
   ============================================================ */
async function runTriage(letterText) {
  const cfg = window.LetterLensConfig || {};
  if (cfg.apiUrl) {
    const res = await fetch(cfg.apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(cfg.headers || {}) },
      body: JSON.stringify({ letter_text: letterText }),
    });
    if (!res.ok) throw new Error(`Triage API ${res.status}: ${res.statusText}`);
    const state = await res.json();
    return adaptTriageState(state, letterText);
  }
  // local mock — resolve on next tick so callers can show a pending state
  return new Promise((resolve) => setTimeout(() => resolve(mockTriage(letterText)), 120));
}

window.LetterLens = { runTriage, adaptTriageState, mockTriage, buildGenericTriage };
