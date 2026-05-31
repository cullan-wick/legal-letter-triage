/* ============================================================
   LetterLens Web — Analyzing view (horizontal agent pipeline)
   ============================================================ */
const { useState, useEffect, useRef } = React;

const FLOW_GAP = 240;

function buildTimelineWeb(sample) {
  const L = sample.latencies;
  const showLawyer = ['consult_lawyer', 'urgent'].includes(sample.verdict.value);
  const seg = {};
  seg.orchestrator = { start: 0, end: L.orchestrator };
  let t = L.orchestrator + FLOW_GAP;
  const s = t;
  seg.risk = { start: s, end: s + L.risk };
  seg.rights = { start: s, end: s + L.rights };
  seg.obligations = { start: s, end: s + L.obligations };
  t = Math.max(seg.risk.end, seg.rights.end, seg.obligations.end) + FLOW_GAP;
  seg.synthesis = { start: t, end: t + L.synthesis };
  t = seg.synthesis.end + FLOW_GAP;
  seg.response_drafter = { start: t, end: t + L.response_drafter };
  t = seg.response_drafter.end + FLOW_GAP;
  if (showLawyer) { seg.lawyer_finder = { start: t, end: t + L.lawyer_finder }; t = seg.lawyer_finder.end; }
  return { seg, total: t, showLawyer };
}

function statusOf(seg, elapsed) {
  if (elapsed >= seg.end) return 'done';
  if (elapsed >= seg.start) return 'run';
  return 'pending';
}
const fmtMs = (ms) => `${Math.round(ms)} ms`;

function PNode({ id, seg, elapsed, sample, sm }) {
  const m = AGENTS[id];
  const st = statusOf(seg, elapsed);
  return (
    <div className={`pnode ${sm ? 'sm' : ''} ${st}`} style={{ '--ag-ink': m.ink, '--ag-bg': m.bg, '--ag-line': m.bg }}>
      <div className="pdot">{st === 'done' ? I.check : m.icon}</div>
      <div className="pbody">
        <div className="pname">{m.name}</div>
        <div className="pstat">{st === 'run' ? 'Working…' : st === 'done' ? 'Done' : 'Waiting'}</div>
        <div className="plat">{fmtMs(sample.latencies[id])}</div>
      </div>
    </div>
  );
}

function WebAnalyzing({ sample, speed, onDone }) {
  const tl = useRef(buildTimelineWeb(sample)).current;
  const [elapsed, setElapsed] = useState(0);
  const doneRef = useRef(false);

  useEffect(() => {
    const t0 = performance.now();
    let stopped = false;
    const iv = setInterval(() => {
      if (stopped) return;
      const e = (performance.now() - t0) * speed;
      setElapsed(e);
      if (e >= tl.total + 600) {
        stopped = true; clearInterval(iv);
        if (!doneRef.current) { doneRef.current = true; onDone(); }
      }
    }, 45);
    return () => { stopped = true; clearInterval(iv); };
  }, []);

  const s = tl.seg;
  const orchDone = elapsed >= s.orchestrator.end;
  const specsDone = elapsed >= Math.max(s.risk.end, s.rights.end, s.obligations.end);
  const synthDone = elapsed >= s.synthesis.end;
  const draftDone = elapsed >= s.response_drafter.end;

  const running = ['orchestrator', 'risk', 'rights', 'obligations', 'synthesis', 'response_drafter', ...(tl.showLawyer ? ['lawyer_finder'] : [])]
    .filter((id) => elapsed >= s[id].start && elapsed < s[id].end);
  let headline = 'Reading your letter…';
  if (running.length > 1) headline = 'Three specialists are reviewing in parallel…';
  else if (running.length === 1) headline = AGENTS[running[0]].status;
  else if (elapsed >= tl.total) headline = 'Wrapping up your verdict…';
  else if (orchDone) headline = 'Piecing the findings together…';

  const pct = Math.min(100, Math.round((elapsed / tl.total) * 100));

  return (
    <div className="analyze-wrap">
      <div className="analyze-head">
        <div className="eyebrow">Analyzing · {pct}%</div>
        <h2>Reading it the way a careful lawyer would</h2>
        <p>{headline}</p>
        <div className="barwrap"><i style={{ width: pct + '%' }}></i></div>
      </div>

      <div className="flow">
        {/* classifier */}
        <div className="flow-col">
          <PNode id="orchestrator" seg={s.orchestrator} elapsed={elapsed} sample={sample} />
          {orchDone && (
            <div className="class-chip">
              <span className="pip"></span>{sample.classification.letter_type}
              <small>· {sample.classification.urgency}</small>
            </div>
          )}
        </div>

        <div className={`conn ${orchDone ? 'fill' : ''}`}><i></i></div>

        {/* specialists, parallel */}
        <div className="fan">
          <span className="fan-tag">Specialists · parallel</span>
          <PNode id="risk" seg={s.risk} elapsed={elapsed} sample={sample} sm />
          <PNode id="rights" seg={s.rights} elapsed={elapsed} sample={sample} sm />
          <PNode id="obligations" seg={s.obligations} elapsed={elapsed} sample={sample} sm />
        </div>

        <div className={`conn ${specsDone ? 'fill' : ''}`}><i></i></div>

        <div className="flow-col">
          <PNode id="synthesis" seg={s.synthesis} elapsed={elapsed} sample={sample} />
        </div>

        <div className={`conn ${synthDone ? 'fill' : ''}`}><i></i></div>

        <div className="flow-col">
          <PNode id="response_drafter" seg={s.response_drafter} elapsed={elapsed} sample={sample} />
        </div>

        {tl.showLawyer && (
          <React.Fragment>
            <div className={`conn ${draftDone ? 'fill' : ''}`}><i></i></div>
            <div className="flow-col">
              <PNode id="lawyer_finder" seg={s.lawyer_finder} elapsed={elapsed} sample={sample} />
            </div>
          </React.Fragment>
        )}
      </div>
    </div>
  );
}

window.WebAnalyzing = WebAnalyzing;
