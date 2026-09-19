export default function OptimizationPanel({ optimizations, stats }) {
  if (!optimizations || optimizations.length === 0) {
    return <div className="empty-state">No optimizations were applicable to this program — it was already minimal.</div>;
  }
  return (
    <div>
      <div className="opt-list">
        {optimizations.map((opt, i) => (
          <div className="opt-item" key={i}>
            <div className="opt-item-head">
              <span className="opt-badge">{opt.type}</span>
              <span className="opt-line">line {opt.line}</span>
            </div>
            <div className="opt-transform">
              <span className="opt-before">{opt.before}</span>
              <span className="opt-arrow">→</span>
              <span className="opt-after">{opt.after}</span>
            </div>
          </div>
        ))}
      </div>
      {stats && (
        <div className="opt-summary">
          {stats.optimizationsApplied} optimization{stats.optimizationsApplied === 1 ? "" : "s"} applied
          &nbsp;·&nbsp; statement count reduced from {stats.statementsBefore} to {stats.statementsAfter}
          &nbsp;({stats.reductionPercent}% reduction)
        </div>
      )}
    </div>
  );
}
