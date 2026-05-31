/* ============================================================
   LetterLens — data + icons
   Mocked outputs mirror the real agent logic in src/agents/*
   ============================================================ */

/* ---- inline line icons (simple, stroke-based) ---- */
const I = {
  search: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>,
  alert: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><path d="M12 9v4"/><path d="M12 17h.01"/><path d="M10.3 3.9 2.4 18a2 2 0 0 0 1.7 3h15.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/></svg>,
  shield: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/></svg>,
  calendar: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>,
  scales: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v18M7 21h10M5 7h14M5 7l-2.5 6a3 3 0 0 0 5 0L5 7Zm14 0-2.5 6a3 3 0 0 0 5 0L19 7Z"/></svg>,
  pen: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>,
  hand: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><path d="M11 12V5.5a1.5 1.5 0 0 1 3 0V12"/><path d="M14 11V4.5a1.5 1.5 0 0 1 3 0V12"/><path d="M17 11.5V6.5a1.5 1.5 0 0 1 3 0V15a6 6 0 0 1-6 6h-2a6 6 0 0 1-5.2-3l-2.4-4a1.6 1.6 0 0 1 2.7-1.6L11 16"/><path d="M8 12V6.5a1.5 1.5 0 0 1 3 0V12"/></svg>,
  check: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="m20 6-11 11-5-5"/></svg>,
  tick: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round"><path d="m20 6-11 11-5-5"/></svg>,
  chev: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 6 6 6-6 6"/></svg>,
  copy: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>,
  send: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>,
  expand: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/></svg>,
  activity: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>,
  info: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>,
  lock: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>,
  home: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M9 21v-6h6v6"/></svg>,
  cash: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/><path d="M6 12h.01M18 12h.01"/></svg>,
  briefcase: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>,
  plus: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.1" strokeLinecap="round" strokeLinejoin="round"><path d="M12 5v14M5 12h14"/></svg>,
};

/* ---- agent palette (calm, harmonious oklch family) ---- */
const AGENTS = {
  orchestrator: { name: 'Classifier',  status: 'Spotting the letter type and urgency…', ink: '#4a6aa8', bg: '#e9eef8', icon: I.search },
  risk:         { name: 'Risk',         status: 'Weighing what could go wrong…',          ink: '#b06a4f', bg: '#f6ece4', icon: I.alert },
  rights:       { name: 'Rights',       status: 'Finding what protects you…',             ink: '#4d8a6e', bg: '#e7f1ea', icon: I.shield },
  obligations:  { name: 'Obligations',  status: 'Pulling out deadlines and duties…',      ink: '#a07d34', bg: '#f4eedb', icon: I.calendar },
  synthesis:    { name: 'Verdict',      status: 'Weighing it all into one call…',         ink: '#7a63a8', bg: '#efebf7', icon: I.scales },
  response_drafter: { name: 'Drafter',  status: 'Writing a calm, careful reply…',         ink: '#4f78a3', bg: '#e9f0f6', icon: I.pen },
  lawyer_finder: { name: 'Referral',    status: 'Matching you to the right kind of help…', ink: '#a45f86', bg: '#f5e9f0', icon: I.hand },
};

const VERDICTS = {
  handle_yourself: { cls: 'v-handle',  label: 'You can likely handle this', icon: I.check },
  consult_lawyer:  { cls: 'v-consult', label: 'Worth a second opinion',     icon: I.shield },
  urgent:          { cls: 'v-urgent',  label: 'Time-sensitive — act soon',  icon: I.alert },
};

/* ---- three samples, run through the real pipeline logic ---- */
const SAMPLES = [
  {
    id: 'debt',
    label: 'Debt collection',
    sub: 'Notice of collection · $2,840.17',
    icon: I.cash, tone: '#b06a4f', toneBg: '#f6ece4',
    text:
`NOTICE OF COLLECTION

Date: May 31, 2026

Dear Recipient,

Our office is attempting to collect an alleged balance of $2,840.17 related to an account ending in 0000. Unless you respond within 30 days of receiving this notice, we may assume the debt is valid and continue collection activity.

This communication is from a debt collector. Please contact us in writing if you dispute this debt or request additional information.

Sincerely,
Example Collection Office`,
    classification: { letter_type: 'Debt collection', jurisdiction: 'Unknown', urgency: 'medium', summary: 'This reads as a debt-collection notice with a standard response window — serious, but not an emergency.' },
    findings: {
      risk: { summary: 'The debt could escalate to continued collection or a lawsuit if it is ignored.', confidence: 'medium', needsLawyer: false, points: [
        'Don\u2019t ignore it until you know the deadline and whether the sender has authority.',
        'Keep the envelope, attachments, dates, and every message in one place.',
        'Ignoring a collection demand can lead to ongoing collection activity or a lawsuit.',
        'You may have the right to dispute the debt or request validation, depending on timing.' ], deadlines: [] },
      rights: { summary: 'You likely have dispute and documentation rights worth preserving.', confidence: 'medium', needsLawyer: false, points: [
        'You can ask for clarification in writing before admitting any facts or liability.',
        'Keep copies of all letters you receive and send.',
        'You may be able to dispute the debt or request formal validation.',
        'Collectors can be limited in how and when they contact you.' ], deadlines: [] },
      obligations: { summary: 'Verify the deadline, preserve records, and respond carefully — no admissions.', confidence: 'medium', needsLawyer: false, points: [
        'Confirm who sent it and whether they have authority to demand payment.',
        'Calendar the deadline before you draft any response.',
        'Avoid admissions, payment promises, or signatures until the facts check out.' ], deadlines: ['Respond within 30 days of receiving the notice'] },
    },
    verdict: { value: 'consult_lawyer',
      summary: 'There\u2019s a real deadline here, so verify the debt before you act. A short check-in with consumer help can make sure you don\u2019t waive any rights.',
      next_steps: [
        'Save the letter, envelope, attachments, and any related messages.',
        'Calendar the 30-day response window today.',
        'Respond in writing without admitting liability or waiving rights.',
        'Contact a consumer legal-aid group or lawyer before the deadline.' ] },
    draft: { subject: 'Response regarding the collection notice', tone: 'calm and documented', body:
`To whom it may concern,

I received your letter dated May 31, 2026 and am reviewing it. Please provide the supporting documents, account records, dates, and the legal basis for the balance you are claiming. I do not admit liability or waive any rights by requesting this information.

Please communicate with me in writing so I can keep accurate records.

Sincerely,
[Your name]` },
    lawyer: { type: 'Consumer debt defense', blurb: 'Often available through free legal aid', questions: [
      'What deadline matters most right now?',
      'Should I respond before you review the full letter?',
      'What documents should I gather?',
      'Do you offer a limited-scope consult or legal-aid referral?' ],
      cost: 'Ask about free legal aid, nonprofit clinics, limited-scope consults, and flat-fee options before agreeing to anything.' },
    latencies: { orchestrator: 760, risk: 1340, rights: 1180, obligations: 640, synthesis: 410, response_drafter: 1520, lawyer_finder: 690 },
  },

  {
    id: 'eviction',
    label: 'Eviction notice',
    sub: 'Notice to pay or quit · 3 days',
    icon: I.home, tone: '#c2564a', toneBg: '#f9e7e3',
    text:
`NOTICE TO PAY OR QUIT

Date: May 31, 2026

Dear Tenant,

Our records show unpaid rent for the current rental period. You are instructed to pay the claimed balance or vacate the premises within 3 days. If you do not respond, the landlord may begin eviction proceedings.

This sample is fictional and intentionally redacted.`,
    classification: { letter_type: 'Housing / eviction', jurisdiction: 'Unknown', urgency: 'high', summary: 'This is a pay-or-quit notice with a very short window and possible court consequences — treat it as time-sensitive.' },
    findings: {
      risk: { summary: 'Housing notices can carry short response windows and lead straight to court.', confidence: 'medium', needsLawyer: true, points: [
        'Don\u2019t ignore it until you know the deadline and whether the sender has authority.',
        'Keep the envelope, attachments, dates, and every message in one place.',
        'Housing notices can have short response windows and court consequences.' ], deadlines: ['Treat this as time-sensitive — verify the stated deadline today'] },
      rights: { summary: 'You may have notice, habitability, payment, and court-process protections.', confidence: 'medium', needsLawyer: true, points: [
        'You can ask for clarification in writing before admitting any facts or liability.',
        'Keep copies of all letters you receive and send.',
        'You may have notice, habitability, payment, or court-process rights.',
        'Local tenant protections can matter a lot — check them quickly.' ], deadlines: [] },
      obligations: { summary: 'Verify the 3-day window immediately and preserve everything.', confidence: 'medium', needsLawyer: true, points: [
        'Confirm who sent it and whether they have authority to demand this.',
        'Calendar the deadline before you draft any response.',
        'Avoid admissions, payment promises, or signatures until the facts check out.' ], deadlines: ['Pay the claimed balance or vacate within 3 days'] },
    },
    verdict: { value: 'urgent',
      summary: 'This looks time-sensitive and should be reviewed quickly. The window is short, so reach out for tenant help today while you preserve the notice.',
      next_steps: [
        'Save the notice, envelope, attachments, and any related messages.',
        'Calendar the 3-day window now — count from when you received it.',
        'Respond in writing without admitting liability or waiving rights.',
        'Contact a tenant-rights or eviction-defense resource today.' ] },
    draft: { subject: 'Response regarding the notice to pay or quit', tone: 'calm and documented', body:
`To whom it may concern,

I received your notice dated May 31, 2026 and am reviewing it. Please provide the ledger, payment records, dates, and the legal basis for the amount and deadline stated. I do not admit liability or waive any rights by requesting this information.

Please communicate with me in writing so I can keep accurate records.

Sincerely,
[Your name]

Note: Because your letter appears time-sensitive, I am also seeking appropriate guidance.` },
    lawyer: { type: 'Tenant rights or eviction defense', blurb: 'Many cities have same-day tenant hotlines', questions: [
      'What deadline matters most right now?',
      'Should I respond before you review the full letter?',
      'What documents should I gather?',
      'Do you offer a limited-scope consult or legal-aid referral?' ],
      cost: 'Ask about free legal aid, nonprofit clinics, limited-scope consults, and flat-fee options before agreeing to anything.' },
    latencies: { orchestrator: 720, risk: 1410, rights: 1220, obligations: 680, synthesis: 380, response_drafter: 1480, lawyer_finder: 740 },
  },

  {
    id: 'employment',
    label: 'Employment warning',
    sub: 'Final written warning · sign by Jun 7',
    icon: I.briefcase, tone: '#a07d34', toneBg: '#f4eedb',
    text:
`EMPLOYMENT WARNING LETTER

Date: May 31, 2026

Dear Employee,

This letter documents a final written warning related to alleged policy violations. You are asked to sign and return this document by June 7, 2026. Failure to respond may result in additional disciplinary action up to and including termination.

This sample is fictional and intentionally redacted.`,
    classification: { letter_type: 'Employment', jurisdiction: 'Unknown', urgency: 'medium', summary: 'This is a final-warning letter asking for a signature by a set date — worth a careful, considered response.' },
    findings: {
      risk: { summary: 'It may affect pay, benefits, references, or future claim deadlines.', confidence: 'medium', needsLawyer: false, points: [
        'Don\u2019t ignore it until you know the deadline and whether the sender has authority.',
        'Keep the envelope, attachments, dates, and every message in one place.',
        'Employment letters may affect pay, benefits, references, or claims deadlines.' ], deadlines: [] },
      rights: { summary: 'You may have wage, discrimination, retaliation, or final-pay protections.', confidence: 'medium', needsLawyer: false, points: [
        'You can ask for clarification in writing before admitting any facts or liability.',
        'Keep copies of all letters you receive and send.',
        'You may have rights related to wages, discrimination, retaliation, or final pay.',
        'Signing a release can affect future claims — read carefully before signing.' ], deadlines: [] },
      obligations: { summary: 'Note the sign-by date, but you can acknowledge receipt without agreeing.', confidence: 'medium', needsLawyer: false, points: [
        'Confirm who sent it and whether they have authority to require a signature.',
        'Calendar the deadline before you draft any response.',
        'Avoid admissions or signatures until the facts check out — you can sign "received, not agreed".' ], deadlines: ['Sign and return by June 7, 2026'] },
    },
    verdict: { value: 'consult_lawyer',
      summary: 'There\u2019s a sign-by date, so verify what you\u2019re agreeing to before acting. A brief employment-law check can keep you from waiving anything.',
      next_steps: [
        'Save the letter, attachments, and any related messages or policies.',
        'Calendar the June 7 sign-by date.',
        'Respond in writing without admitting fault — note "received, not agreed" if you must sign.',
        'Contact an employment lawyer or worker resource before signing.' ] },
    draft: { subject: 'Response regarding the written warning', tone: 'calm and documented', body:
`To whom it may concern,

I received the written warning dated May 31, 2026 and am reviewing it. Please share the specific policies referenced, the underlying records, and the dates involved. I acknowledge receipt of this document; I do not admit the alleged violations or waive any rights by responding.

Please communicate with me in writing so I can keep accurate records.

Sincerely,
[Your name]` },
    lawyer: { type: 'Employment law', blurb: 'Many offer free initial consultations', questions: [
      'What deadline matters most right now?',
      'Should I sign before you review the full letter?',
      'What documents should I gather?',
      'Do you offer a limited-scope consult or legal-aid referral?' ],
      cost: 'Ask about free legal aid, nonprofit clinics, limited-scope consults, and flat-fee options before agreeing to anything.' },
    latencies: { orchestrator: 740, risk: 1290, rights: 1240, obligations: 700, synthesis: 400, response_drafter: 1560, lawyer_finder: 660 },
  },
];

Object.assign(window, { I, AGENTS, VERDICTS, SAMPLES });
