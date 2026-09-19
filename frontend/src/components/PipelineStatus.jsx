const STEP_LABELS = [
  ["lexical", "Lexical Analysis"],
  ["syntax", "Syntax Analysis"],
  ["semantic", "Semantic Analysis"],
  ["optimization", "Optimization"],
  ["flowchart", "Flowchart Generation"],
];

const ICONS = {
  pending: "○",
  busy: "⟳",
  done: "✓",
  error: "✗",
  skipped: "–",
};

export default function PipelineStatus({ stages }) {
  return (
    <div className="panel">
      <div className="panel-header">
        <div className="panel-title"><span className="dot" /> Compilation Pipeline</div>
      </div>
      <div className="pipeline">
        {STEP_LABELS.map(([key, label]) => {
          const state = stages?.[key] || "pending";
          return (
            <div className={`pipeline-step ${state}`} key={key}>
              <span className="icon">{ICONS[state]}</span>
              <span>{label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
