/* ============================================================
   LetterLens Web — App shell (top bar, composer, dock, flow)
   ============================================================ */
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "accent": "#3f6fb0",
  "verdictColor": true,
  "density": "regular",
  "revealSpeed": "default",
  "letterFont": "mono"
}/*EDITMODE-END*/;

const ACCENTS = {
  "#3f6fb0": { deep: "#305a94", c50: "#eef4fb", c100: "#dde8f6" },
  "#3c7d74": { deep: "#2c6058", c50: "#ecf5f3", c100: "#d3e8e3" },
  "#5b63b4": { deep: "#474e96", c50: "#f0f1fb", c100: "#e0e2f5" },
  "#6b6a78": { deep: "#52515f", c50: "#f2f2f5", c100: "#e4e4ea" },
};
const SPEED = { calm: 0.55, default: 1, fast: 1.9 };

function Composer({ onAnalyze, liveMode }) {
  const [text, setText] = React.useState('');
  const [active, setActive] = React.useState(null);
  const [busy, setBusy] = React.useState(false);
  const pick = (s) => { setText(s.text); setActive(s.id); };
  const go = async () => {
    if (!text.trim() || busy) return;
    setBusy(true);
    try { await onAnalyze(text); }
    catch (e) { setBusy(false); alert('Could not analyze the letter: ' + e.message); }
  };
  return (
    <div className="compose-wrap">
      <div className="compose">
        <div className="eyebrow">Legal letter triage</div>
        <h1>What did you get in the mail?</h1>
        <p className="lead">Paste a letter that’s worrying you. Seven agents read it the way a careful lawyer would, then hand back a plain-English verdict, your next steps, and a reply you can send.</p>

        <div className="composer-box">
          <textarea value={text}
            onChange={(e) => { setText(e.target.value); setActive(null); }}
            placeholder="Paste the full text of the letter here — names, dates, amounts, and all."></textarea>
        </div>
        <div className="compose-actions">
          <div className="reassure"><span>{liveMode ? 'Configured API' : 'Private mock'}</span><i></i><span>Plain-English</span><i></i><span>Not legal advice</span></div>
          <button className="btn-primary" disabled={!text.trim() || busy} onClick={go}>{busy ? I.activity : I.search} {busy ? 'Reading…' : 'Analyze letter'}</button>
        </div>

        <div className="or-line"><span className="l"></span><span>or start with an example</span><span className="l"></span></div>
        <div className="sample-grid">
          {SAMPLES.map((s) => (
            <button key={s.id} className={`sample-card ${active === s.id ? 'active' : ''}`} onClick={() => pick(s)}>
              <span className="sample-ico" style={{ background: s.toneBg, color: s.tone }}>{s.icon}</span>
              <span>
                <b>{s.label}</b>
                <small>{s.sub}</small>
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function LetterDock({ sample, onNew }) {
  const liveMode = sample.mode === 'live';
  return (
    <div className="dock">
      <div className="dock-head">
        <div className="row">
          <span className="eyebrow">The letter</span>
          <button className="new-btn" onClick={onNew}>{I.plus} New letter</button>
        </div>
        <div className="doc-class">
          <span className="ic" style={{ background: sample.toneBg, color: sample.tone }}>{sample.icon}</span>
          <div>
            <b>{sample.classification.letter_type}</b>
            <small>{sample.classification.urgency} urgency · {sample.classification.jurisdiction === 'Unknown' ? 'no state detected' : sample.classification.jurisdiction}</small>
          </div>
        </div>
      </div>
      <div className="doc-paper">{sample.text}</div>
      <div className="doc-foot">{I.lock} {liveMode ? 'Sent to your configured triage API' : 'Local mock mode · nothing is sent anywhere'}</div>
    </div>
  );
}

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [stage, setStage] = React.useState('input'); // input | analyzing | results
  const [sample, setSample] = React.useState(null);
  const [showTrace, setShowTrace] = React.useState(false);
  const liveMode = Boolean(window.LetterLensConfig?.apiUrl);

  const ac = ACCENTS[t.accent] || ACCENTS["#3f6fb0"];
  const verdictCls = sample && t.verdictColor ? VERDICTS[sample.verdict.value].cls : 'mono-verdict';
  const rootStyle = {
    '--accent': t.accent, '--accent-deep': ac.deep, '--accent-50': ac.c50, '--accent-100': ac.c100,
    '--letter-font': t.letterFont === 'serif' ? 'var(--serif)' : 'var(--mono)',
  };

  const start = async (text) => {
    setShowTrace(false);
    const vm = await LetterLens.runTriage(text);
    setSample(vm);
    setStage('analyzing');
  };
  const restart = () => { setStage('input'); setSample(null); };

  const twoPane = stage === 'results';

  return (
    <div className={`app stage-${stage} density-${t.density} ${verdictCls}`} style={rootStyle}>
      <div className="topbar">
        <div className="brand" onClick={restart}>
          <span className="lens"></span>
          <b>Letter<span>Lens</span></b>
          <span className="tag">Legal letter triage</span>
        </div>
        <div className="top-actions">
          {stage === 'results' && (
            <button className={`top-btn ${showTrace ? 'on' : ''}`} onClick={() => setShowTrace(!showTrace)}>
              {I.activity} Agent trace
            </button>
          )}
          <span className="note-pill">{I.info} Information, not legal advice</span>
        </div>
      </div>

      <div className={`workspace ${twoPane ? 'two' : ''}`}>
        {twoPane && <LetterDock sample={sample} onNew={restart} />}
        <div className="main">
          {stage === 'input' && <Composer onAnalyze={start} liveMode={liveMode} />}
          {stage === 'analyzing' && <WebAnalyzing sample={sample} speed={SPEED[t.revealSpeed] || 1} onDone={() => setStage('results')} />}
          {stage === 'results' && <WebResults sample={sample} showTrace={showTrace} />}
        </div>
      </div>

      <TweaksPanel>
        <TweakSection label="Theme" />
        <TweakColor label="Accent" value={t.accent} options={Object.keys(ACCENTS)} onChange={(v) => setTweak('accent', v)} />
        <TweakToggle label="Verdict-driven colour" value={t.verdictColor} onChange={(v) => setTweak('verdictColor', v)} />
        <TweakSection label="Layout" />
        <TweakRadio label="Density" value={t.density} options={['compact', 'regular', 'comfy']} onChange={(v) => setTweak('density', v)} />
        <TweakRadio label="Letter font" value={t.letterFont} options={['mono', 'serif']} onChange={(v) => setTweak('letterFont', v)} />
        <TweakSection label="Agent reveal" />
        <TweakRadio label="Pipeline speed" value={t.revealSpeed} options={['calm', 'default', 'fast']} onChange={(v) => setTweak('revealSpeed', v)} />
        <TweakButton label="Replay analysis" onClick={() => { if (sample) setStage('analyzing'); }} />
      </TweaksPanel>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
