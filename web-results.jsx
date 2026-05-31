/* ============================================================
   LetterLens Web — Results dashboard
   ============================================================ */

function FindingCard({ id, data }) {
  const [expanded, setExpanded] = React.useState(false);
  const m = AGENTS[id];
  const points = data.points || [];
  const deadlines = data.deadlines || [];
  const toggle = () => setExpanded((value) => !value);
  const onKeyDown = (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggle();
    }
  };

  return (
    <div
      className={`finding-card ${expanded ? 'expanded' : ''}`}
      style={{ '--ag-ink': m.ink, '--ag-bg': m.bg }}
      role="button"
      tabIndex="0"
      aria-expanded={expanded}
      onClick={toggle}
      onKeyDown={onKeyDown}
    >
      <div className="fhead">
        <div className="fico" style={{ background: m.bg, color: m.ink }}>{m.icon}</div>
        <span className="fname">{m.name}</span>
        <span className="conf">{data.confidence}</span>
        <span className="fchev">{I.chev}</span>
      </div>
      <p className="fsummary">{data.summary}</p>
      <div className="fmore"><span>{expanded ? 'Hide details' : 'Show details'}</span></div>
      {expanded && (
        <div className="finding-details">
          <ul className="kp">
            {points.map((p, i) => (
              <li key={i}><span className="tick">{I.tick}</span><span>{p}</span></li>
            ))}
          </ul>
          {deadlines.length > 0 && (
            <div className="dl-tags">
              {deadlines.map((d, i) => <span className="dl-tag" key={i}>{I.activity} {d}</span>)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function WebResults({ sample, showTrace }) {
  const [copied, setCopied] = React.useState(false);
  const [steps, setSteps] = React.useState(() => sample.verdict.next_steps.map(() => false));
  const msFor = (key) => {
    const value = sample.latencies && sample.latencies[key];
    return Number.isFinite(value) ? Math.max(value, 0) : 0;
  };

  const v = VERDICTS[sample.verdict.value];
  const c = sample.classification;
  const allDeadlines = ['risk', 'rights', 'obligations']
    .flatMap((k) => sample.findings[k].deadlines)
    .filter((d) => !/time-sensitive/i.test(d));
  // Prefer urgent_deadlines from the live synthesis agent when present.
  const urgentDeadlines = (sample.verdict.urgent_deadlines || []).filter(Boolean);
  const primaryDeadline = urgentDeadlines[0] || allDeadlines[0];

  const traceOrder = ['orchestrator', 'risk', 'rights', 'obligations', 'synthesis', 'response_drafter',
    ...(sample.lawyer ? ['lawyer_finder'] : [])];
  const totalMs = traceOrder.reduce((a, k) => a + msFor(k), 0);
  const maxLat = Math.max(1, ...traceOrder.map(msFor));

  const copyDraft = () => {
    const text = `Subject: ${sample.draft.subject}\n\n${sample.draft.body}`;
    if (navigator.clipboard) navigator.clipboard.writeText(text).catch(() => {});
    setCopied(true); setTimeout(() => setCopied(false), 1800);
  };
  const toggleStep = (i) => setSteps((s) => s.map((val, j) => (j === i ? !val : val)));

  return (
    <div className="dash">
      {/* verdict + key dates */}
      <div className="verdict-band">
        <div className="verdict">
          <div className="verdict-top">
            <div className="verdict-badge">{v.icon}</div>
            <div>
              <div className="verdict-label">Our read</div>
              <div className="verdict-title">{v.label}</div>
            </div>
          </div>
          <p className="verdict-summary">{sample.verdict.summary}</p>
          <div className="verdict-chips">
            <span className="vchip">{c.letter_type}</span>
            <span className="vchip">{c.urgency} urgency</span>
            <span className="vchip ghost">{c.jurisdiction === 'Unknown' ? 'No state detected' : c.jurisdiction}</span>
          </div>
        </div>
        {primaryDeadline ? (
          <div className="dates">
            <div className="cal">{I.calendar}</div>
            <div className="eyebrow">Don’t miss this</div>
            <p>{primaryDeadline}</p>
            <small>{urgentDeadlines.length > 0 ? 'flagged by the synthesis agent' : 'flagged by the obligations agent'}</small>
          </div>
        ) : (
          <div className="dates">
            <div className="cal">{I.calendar}</div>
            <div className="eyebrow">Deadlines</div>
            <p>No explicit deadline detected — still verify dates in the full document.</p>
            <small>flagged by the obligations agent</small>
          </div>
        )}
      </div>

      {/* findings */}
      <div>
        <div className="sec-head"><h3>How we read it</h3><span className="count">3 specialists in parallel</span></div>
        <div className="findings-grid">
          {['risk', 'rights', 'obligations'].map((k) => (
            <FindingCard key={k} id={k} data={sample.findings[k]} />
          ))}
        </div>
      </div>

      {/* next steps + draft */}
      <div className="cols-2">
        <div>
          <div className="sec-head"><h3>Your next steps</h3></div>
          <div className="steps">
            {sample.verdict.next_steps.map((stp, i) => (
              <button key={i} className={`step ${steps[i] ? 'done' : ''}`} onClick={() => toggleStep(i)}>
                <span className="box">{I.tick}</span>
                <p><span className="num">{String(i + 1).padStart(2, '0')}</span> {stp}</p>
              </button>
            ))}
          </div>
        </div>
        <div>
          <div className="sec-head"><h3>A reply you can send</h3><span className="count">draft</span></div>
          <div className="draft">
            <div className="draft-top">
              <div className="s">
                <span className="eyebrow">Subject</span>
                <b>{sample.draft.subject}</b>
              </div>
              <button className="draft-copy" onClick={copyDraft}>{copied ? I.check : I.copy} {copied ? 'Copied' : 'Copy'}</button>
            </div>
            <div className="draft-body">{sample.draft.body}</div>
          </div>
        </div>
      </div>

      {/* lawyer */}
      {sample.lawyer && (
        <div className="lawyer">
          <div className="lawyer-grid">
            <div>
              <div className="lawyer-head">
                <span className="ic">{I.hand}</span>
                <div><b>If you want a hand</b><small>{sample.lawyer.blurb}</small></div>
              </div>
              <div className="lawyer-type"><span>Look for</span>{sample.lawyer.type}</div>
              <p className="cost">{sample.lawyer.cost}</p>
              {sample.lawyer.urgencyGuidance && (
                <div className="lawyer-urgency">{I.alert}{sample.lawyer.urgencyGuidance}</div>
              )}
              {sample.lawyer.documents && sample.lawyer.documents.length > 0 && (
                <div className="lawyer-docs">
                  <span className="eyebrow">Gather before your consult</span>
                  <ul>
                    {sample.lawyer.documents.map((doc, i) => (
                      <li key={i}><span className="tick">{I.tick}</span><span>{doc}</span></li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            <ul className="qlist">
              <span className="eyebrow">Questions to ask</span>
              {sample.lawyer.questions.map((q, i) => (
                <li key={i}><span className="q">Q{i + 1}</span><span>{q}</span></li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* trace */}
      {showTrace && (
        <div className="trace">
          <div className="trace-head">
            <b><span className="weave"></span> Agent trace</b>
            <small>W&B Weave · {traceOrder.length} ops</small>
          </div>
          {traceOrder.map((k) => (
            <div className="trace-row" key={k} style={{ '--tr': AGENTS[k].ink }}>
              <span className="nm">{AGENTS[k].name.toLowerCase()}</span>
              <span className="bar"><i style={{ width: `${(msFor(k) / maxLat) * 100}%` }}></i></span>
              <span className="ms">{Math.round(msFor(k))}ms</span>
            </div>
          ))}
          <div className="trace-total"><span>orchestrator → specialists → synthesis → draft{sample.lawyer ? ' → referral' : ''}</span><b>{(totalMs / 1000).toFixed(2)}s total</b></div>
        </div>
      )}

      <div className="disclaimer">
        {I.info}
        <span>LetterLens gives legal information and orientation, not legal advice. For decisions about your situation, talk to a qualified lawyer.</span>
      </div>
    </div>
  );
}

window.WebResults = WebResults;
