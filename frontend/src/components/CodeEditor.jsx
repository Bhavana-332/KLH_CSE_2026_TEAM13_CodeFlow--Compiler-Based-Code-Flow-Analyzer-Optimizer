import { useRef } from "react";
import { SAMPLES } from "../samples.js";

export default function CodeEditor({ code, setCode, onCompile, loading, onSelectSample }) {
  const gutterRef = useRef(null);
  const textareaRef = useRef(null);
  const lines = code.split("\n").length;

  const handleScroll = () => {
    if (gutterRef.current && textareaRef.current) {
      gutterRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  };

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      onCompile();
    }
    if (e.key === "Tab") {
      e.preventDefault();
      const { selectionStart, selectionEnd, value } = e.target;
      const newValue = value.slice(0, selectionStart) + "    " + value.slice(selectionEnd);
      setCode(newValue);
      requestAnimationFrame(() => {
        e.target.selectionStart = e.target.selectionEnd = selectionStart + 4;
      });
    }
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <div className="panel-title"><span className="dot" /> Source Code Editor</div>
          <div className="panel-sub">Write CodeFlow source, or load a sample, then compile.</div>
        </div>
        <div className="editor-toolbar">
          <select
            className="select"
            onChange={(e) => onSelectSample(e.target.value)}
            defaultValue=""
          >
            <option value="" disabled>Load sample program…</option>
            {SAMPLES.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
          <button className="btn btn-ghost" onClick={() => setCode("")}>Clear</button>
        </div>
      </div>

      <div className="editor-frame">
        <div className="editor-body">
          <div className="gutter" ref={gutterRef}>
            {Array.from({ length: lines }, (_, i) => (
              <div key={i}>{i + 1}</div>
            ))}
          </div>
          <textarea
            ref={textareaRef}
            className="code-input"
            spellCheck={false}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            onScroll={handleScroll}
            onKeyDown={handleKeyDown}
            placeholder="int x = 10;"
          />
        </div>
      </div>

      <div className="editor-footer">
        <button className="btn btn-primary" onClick={onCompile} disabled={loading}>
          {loading ? "Compiling…" : "⚡ COMPILE & OPTIMIZE"}
        </button>
      </div>
    </div>
  );
}
