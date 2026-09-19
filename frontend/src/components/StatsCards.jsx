export default function StatsCards({ stats }) {
  if (!stats) return null;
  const cards = [
    ["Statements Before", stats.statementsBefore],
    ["Statements After", stats.statementsAfter],
    ["Optimizations Applied", stats.optimizationsApplied],
    ["Reduction", `${stats.reductionPercent}%`],
  ];
  return (
    <div className="stats-grid">
      {cards.map(([label, value]) => (
        <div className="stat-card" key={label}>
          <div className="stat-value">{value}</div>
          <div className="stat-label">{label}</div>
        </div>
      ))}
    </div>
  );
}
