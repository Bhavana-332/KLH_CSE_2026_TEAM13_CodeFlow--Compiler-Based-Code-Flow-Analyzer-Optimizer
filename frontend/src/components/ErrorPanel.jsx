export default function ErrorPanel({ error }) {
  if (!error) return null;
  return (
    <div className="error-panel">
      <div className="error-title">❌ Compilation Failed</div>
      <span className="error-stage">{error.stage}</span>
      <div className="error-message">{error.message}</div>
      {error.sourceLine ? (
        <div className="error-source">
          <span className="line-no">{error.line}</span>{error.sourceLine}
        </div>
      ) : null}
    </div>
  );
}
