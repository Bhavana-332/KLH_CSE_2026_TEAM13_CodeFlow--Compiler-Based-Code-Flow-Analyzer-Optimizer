export default function CodeComparison({ original, optimized }) {
  if (!original || !optimized) {
    return <div className="empty-state">Compile a program to compare original vs optimized source.</div>;
  }
  return (
    <div className="compare-grid">
      <div>
        <div className="flow-col-title">Original Code</div>
        <pre className="code-block">{original}</pre>
      </div>
      <div>
        <div className="flow-col-title">Optimized Code</div>
        <pre className="code-block">{optimized}</pre>
      </div>
    </div>
  );
}
