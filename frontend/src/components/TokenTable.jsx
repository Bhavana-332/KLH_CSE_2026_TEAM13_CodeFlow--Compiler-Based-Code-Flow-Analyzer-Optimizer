export default function TokenTable({ tokens }) {
  if (!tokens || tokens.length === 0) {
    return <div className="empty-state">No tokens yet — compile some source code to see the lexer output.</div>;
  }
  return (
    <div className="scroll-box">
      <table className="token-table">
        <thead>
          <tr>
            <th style={{ width: "10%" }}>#</th>
            <th style={{ width: "35%" }}>Lexeme</th>
            <th style={{ width: "35%" }}>Token Type</th>
            <th style={{ width: "20%" }}>Line</th>
          </tr>
        </thead>
        <tbody>
          {tokens.map((t, i) => (
            <tr key={i}>
              <td style={{ color: "var(--text-faint)" }}>{i + 1}</td>
              <td>{t.value || <span style={{ opacity: 0.4 }}>—</span>}</td>
              <td><span className="token-type">{t.type}</span></td>
              <td>{t.line}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
