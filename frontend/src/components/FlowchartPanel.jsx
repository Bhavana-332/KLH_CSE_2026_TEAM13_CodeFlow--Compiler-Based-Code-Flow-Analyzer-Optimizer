export default function FlowchartPanel({ before, after }) {
  if (!before || !after) {
    return <div className="empty-state">Compile a program to generate the before/after control-flow graphs.</div>;
  }
  return (
    <div className="flow-grid">
      <div className="flow-before">
        <div className="flow-col-title"><span className="swatch" /> BEFORE OPTIMIZATION</div>
        <div className="flow-canvas" dangerouslySetInnerHTML={{ __html: before }} />
      </div>
      <div className="flow-after">
        <div className="flow-col-title"><span className="swatch" /> AFTER OPTIMIZATION</div>
        <div className="flow-canvas" dangerouslySetInnerHTML={{ __html: after }} />
      </div>
    </div>
  );
}
