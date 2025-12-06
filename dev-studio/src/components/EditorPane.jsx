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

  wsGenerateRef, // WebSocket from parent
}) {
  const [instruction, setInstruction] = useState("");
  const [typing, setTyping] = useState(false);

  // ============================================================
  // 🔥 HANDLE STREAMING EVENTS FROM BACKEND LLM
  // ============================================================
  useEffect(() => {
    if (!wsGenerateRef?.current) return;

    const ws = wsGenerateRef.current;

    ws.onmessage = (event) => {
      let msg;
      try {
        msg = JSON.parse(event.data);
      } catch {
        return;
      }

      // -------------------------
      // FILE CREATED
      // -------------------------
      if (msg.event === "file_create") {
        setSelectedFile({ path: msg.file });
        setFileContent("");
        setIsGenerating(true);
        return;
      }

      // -------------------------
      // LIVE CONTENT (TYPING)
      // -------------------------
      if (msg.event === "editor_update") {
        setSelectedFile({ path: msg.file });
        setFileContent(msg.content);

        setTyping(true);
        setTimeout(() => setTyping(false), 250);

        return;
      }

      // -------------------------
      // PROGRESS UPDATE
      // -------------------------
      if (msg.event === "progress") {
        setGenerationProgress(msg.progress);
        return;
      }

      // -------------------------
      // ETA UPDATE
      // -------------------------
      if (msg.event === "eta") {
        setEta(msg.seconds);
        return;
      }

      // -------------------------
      // FINISHED
      // -------------------------
      if (msg.event === "finish") {
        setGenerationProgress(100);
        setIsGenerating(false);
        return;
      }
    };
  }, [wsGenerateRef]);

  // ============================================================
  // UI
  // ============================================================
  return (
    <div className="editor-pane">

      {/* ================= HEADER ================= */}
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

      {/* ================= GENERATION STATUS ================= */}
      {isGenerating && (
        <div className="generation-status">

          <div className="gen-row">
            <span>⚡ Generating project…</span>
            {typing && <span className="typing-dot">●</span>}
          </div>

          {/* Progress Bar */}
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

      {/* ================= MONACO EDITOR ================= */}
      <Editor
        height="100%"
        theme="vs-dark"
        language={language}
        value={fileContent}
        onChange={(v) => setFileContent(v ?? "")}
        options={{
          fontSize: 13,
          minimap: { enabled: false },
          smoothScrolling: true,
          scrollBeyondLastLine: false,
        }}
      />

      {/* ================= AI EDIT AREA ================= */}
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
