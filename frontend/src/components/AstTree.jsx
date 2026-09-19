import { useState } from "react";

function TreeNode({ node, depth }) {
  const [open, setOpen] = useState(depth < 2);
  const hasChildren = node.children && node.children.length > 0;

  return (
    <div className="ast-node">
      <div className="ast-row" onClick={() => hasChildren && setOpen(!open)}>
        <span className={`ast-caret ${open ? "open" : ""}`}>{hasChildren ? "▸" : "·"}</span>
        <span className="ast-type">{node.type}</span>
        {node.label && <span className="ast-label">{node.label}</span>}
        {node.line ? <span className="ast-line">line {node.line}</span> : null}
      </div>
      {hasChildren && open && (
        <div>
          {node.children.map((child) => (
            <TreeNode node={child} depth={depth + 1} key={child.id} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function AstTree({ ast }) {
  if (!ast) {
    return <div className="empty-state">No AST yet — compile some source code first.</div>;
  }
  return (
    <div className="ast-tree scroll-box" style={{ maxHeight: 380, padding: "10px 12px" }}>
      <TreeNode node={ast} depth={0} />
    </div>
  );
}
