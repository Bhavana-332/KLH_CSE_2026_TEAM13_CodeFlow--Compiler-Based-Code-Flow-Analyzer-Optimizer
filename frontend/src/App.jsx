import { useState } from "react";
import { compileSource } from "./api.js";
import { SAMPLES, DEFAULT_SAMPLE } from "./samples.js";

import CodeEditor from "./components/CodeEditor.jsx";
import PipelineStatus from "./components/PipelineStatus.jsx";
import TokenTable from "./components/TokenTable.jsx";
import AstTree from "./components/AstTree.jsx";
import OptimizationPanel from "./components/OptimizationPanel.jsx";
import FlowchartPanel from "./components/FlowchartPanel.jsx";
import CodeComparison from "./components/CodeComparison.jsx";
import StatsCards from "./components/StatsCards.jsx";
import ErrorPanel from "./components/ErrorPanel.jsx";

const TABS = [
  { id: "tokens", label: "Token Explorer" },
  { id: "ast", label: "AST Viewer" },
  { id: "optimizations", label: "Optimization Report" },
  { id: "flowcharts", label: "Before / After Flowcharts" },
  { id: "compare", label: "Code Comparison" },
];

export default function App() {
  const [code, setCode] = useState(DEFAULT_SAMPLE.code);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [netError, setNetError] = useState(null);
  const [activeTab, setActiveTab] = useState("flowcharts");

  const handleCompile = async () => {
    setLoading(true);
    setNetError(null);
    try {
      const data = await compileSource(code);
      setResult(data);
    } catch (err) {
      setNetError(
        "Could not reach the CodeFlow backend. Make sure the FastAPI server is running on http://localhost:8000 (see the README)."
      );
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSample = (id) => {
    const sample = SAMPLES.find((s) => s.id === id);
    if (sample) setCode(sample.code);
  };

  const status = loading ? "busy" : result ? (result.success ? "ready" : "error") : "ready";
  const statusText = loading
    ? "Compiling…"
    : result
    ? (result.success ? "Ready" : "Compilation failed")
    : "Ready";

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <div className="brand-mark">⚡</div>
          <div>
            <div className="brand-title">CodeFlow Compiler</div>
            <div className="brand-subtitle">Compiler Design • Code Optimization &amp; Flowchart Visualizer</div>
          </div>
        </div>
        <div className="status-pill">
          <span className={`status-dot ${status}`} />
          {statusText}
        </div>
      </header>

      <CodeEditor
        code={code}
        setCode={setCode}
        onCompile={handleCompile}
        loading={loading}
        onSelectSample={handleSelectSample}
      />

      {netError && (
        <div className="panel" style={{ borderColor: "#5a2323" }}>
          <ErrorPanel error={{ stage: "Network", message: netError }} />
        </div>
      )}

      {result && <PipelineStatus stages={result.stages} />}

      {result && !result.success && (
        <div className="panel">
          <ErrorPanel error={result.error} />
        </div>
      )}

      {result && result.success && (
        <>
          <div className="panel">
            <div className="panel-header">
              <div className="panel-title"><span className="dot" /> Statistics</div>
            </div>
            <StatsCards stats={result.stats} />
          </div>

          <div className="panel">
            <div className="tabs">
              {TABS.map((tab) => (
                <button
                  key={tab.id}
                  className={`tab ${activeTab === tab.id ? "active" : ""}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {activeTab === "tokens" && <TokenTable tokens={result.tokens} />}
            {activeTab === "ast" && <AstTree ast={result.ast} />}
            {activeTab === "optimizations" && (
              <OptimizationPanel optimizations={result.optimizations} stats={result.stats} />
            )}
            {activeTab === "flowcharts" && (
              <FlowchartPanel before={result.flowchartBefore} after={result.flowchartAfter} />
            )}
            {activeTab === "compare" && (
              <CodeComparison original={result.originalCode} optimized={result.optimizedCode} />
            )}
          </div>
        </>
      )}

      <div className="footer-note">
        CodeFlow Compiler — a Compiler Design mini-project: Lexer → Parser → Semantic Analyzer → Optimizer → CFG
      </div>
    </div>
  );
}
