import Editor from "@monaco-editor/react";
import { useState, useEffect } from "react";

export default function EditorPane({
  selectedFile,
  setSelectedFile,
  fileContent,
  setFileContent,
  isGenerating,
  setIsGenerating,
  generationProgress,
  setGenerationProgress,
  eta,
  setEta,
  onAiEdit,
  isEditing,
  language,
}) {
  const [instruction, setInstruction] = useState("");
  const [typing, setTyping] = useState(false);

  // ★ Live typing indicator
  useEffect(() => {
    if (!isGenerating) return;
    setTyping(true);

    const timeout = setTimeout(() => setTyping(false), 400);
    return () => clearTimeout(timeout);
  }, [fileContent]);

  return (
    <div className="editor-pane">
      {/* =================== HEADER =================== */}
      <div className="editor-header">
        <div>
          {selectedFile ? (
            <>
              <span className="gray">Editing:</span> {selectedFile.path}
            </>
          ) : (
            <span className="gray">Select a file</span>
          )}
        </div>

        <span className="gray small">Model: local ({language})</span>
      </div>

      {/* =================== PROJECT GENERATION UI =================== */}
      {isGenerating && (
        <div className="generation-status">
          <div className="gen-row">
            <span>⚡ Generating project…</span>
            {typing && <span className="typing-dot">●</span>}
          </div>

          {/* Progress bar */}
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${generationProgress}%` }}
            ></div>
          </div>

          <div className="eta">
            ETA: {eta}s • {generationProgress}%
          </div>
        </div>
      )}

      {/* =================== MONACO EDITOR =================== */}
      <Editor
        height="100%"
        theme="vs-dark"
        language={language}
        value={fileContent}
        onChange={(v) => setFileContent(v ?? "")}
        options={{
          fontSize: 13,
          minimap: { enabled: false },
        }}
      />

      {/* =================== AI EDIT BAR =================== */}
      <div className="editor-bottom">
        <textarea
          placeholder="AI instruction..."
          value={instruction}
          onChange={(e) => setInstruction(e.target.value)}
        />

        <button
          onClick={() => {
            onAiEdit(instruction);
            setInstruction("");
          }}
          disabled={!selectedFile || isEditing || isGenerating}
        >
          {isEditing ? "Thinking..." : "AI Edit"}
        </button>
      </div>
    </div>
  );
}
