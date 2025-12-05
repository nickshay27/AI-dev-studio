import { useEffect, useRef, useState } from "react";

// Helper: remove Vite ANSI color escape codes
const stripAnsi = (str) =>
  str.replace(
    /[\u001b\u009b][[()#;?]*(?:[0-9]{1,4}(?:;[0-9]{0,4})*)?[0-9A-ORZcf-nq-uy=><]/g,
    ""
  );

export default function Terminal({ projectName }) {
  if (!projectName) return null;

  const [logs, setLogs] = useState("");
  const [viteUrl, setViteUrl] = useState(null);
  const terminalRef = useRef(null);
  const openedRef = useRef(false); // prevents multiple new tabs

  useEffect(() => {
    const ws = new WebSocket(`ws://127.0.0.1:8000/ws/logs/${projectName}`);

    ws.onmessage = (event) => {
      const rawText = event.data;
      const cleanText = stripAnsi(rawText);

      // Append logs
      setLogs((prev) => prev + cleanText);

      // Auto-scroll terminal
      if (terminalRef.current) {
        terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
      }

      // ⭐ SUPER-RELIABLE PORT DETECTION
      // matches: localhost:3000/ or localhost:5173/
      const match = cleanText.match(/localhost:(\d+)\//);

      if (match) {
        const port = match[1];
        const url = `http://localhost:${port}`;

        setViteUrl(url);

        // Auto-open only once
        if (!openedRef.current) {
          openedRef.current = true;
          window.open(url, "_blank");
        }
      }
    };

    ws.onclose = () => console.log("Terminal WebSocket closed");

    return () => ws.close();
  }, [projectName]);

  return (
    <div className="terminal-container">
      <div
        ref={terminalRef}
        className="terminal-box"
        style={{
          background: "#000",
          color: "#0f0",
          padding: "10px",
          height: "250px",
          overflowY: "auto",
          fontSize: "12px",
          borderTop: "2px solid #333",
        }}
      >
        <pre>{logs}</pre>
      </div>

      {viteUrl && (
        <button
          onClick={() => window.open(viteUrl, "_blank")}
          style={{
            width: "100%",
            padding: "8px",
            marginTop: "5px",
            background: "#1e40af",
            color: "white",
            borderRadius: "5px",
          }}
        >
          🌐 Open App → {viteUrl}
        </button>
      )}
    </div>
  );
}
