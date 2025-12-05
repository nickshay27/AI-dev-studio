// import React, { useEffect, useState } from "react";
// import axios from "axios";
// import Editor from "@monaco-editor/react";

// const API_BASE = "http://127.0.0.1:8000";

// function detectLanguage(path) {
//   if (!path) return "plaintext";
//   const lower = path.toLowerCase();
//   if (lower.endsWith(".js") || lower.endsWith(".jsx")) return "javascript";
//   if (lower.endsWith(".ts") || lower.endsWith(".tsx")) return "typescript";
//   if (lower.endsWith(".py")) return "python";
//   if (lower.endsWith(".json")) return "json";
//   if (lower.endsWith(".md")) return "markdown";
//   if (lower.endsWith(".html")) return "html";
//   if (lower.endsWith(".css")) return "css";
//   return "plaintext";
// }

// function FileTreeNode({ node, onSelectFile, activePath }) {
//   const [open, setOpen] = useState(node.type === "dir");

//   if (node.type === "file") {
//     const isActive = activePath === node.path;
//     return (
//       <div
//         style={{
//           paddingLeft: "0.75rem",
//           paddingBlock: "0.1rem",
//           fontSize: "0.8rem",
//           cursor: "pointer",
//           backgroundColor: isActive ? "#1e293b" : "transparent",
//           borderRadius: "0.25rem",
//         }}
//         onClick={() => onSelectFile(node)}
//       >
//         📄 {node.name}
//       </div>
//     );
//   }

//   return (
//     <div>
//       <div
//         style={{
//           paddingBlock: "0.1rem",
//           fontSize: "0.8rem",
//           cursor: "pointer",
//         }}
//         onClick={() => setOpen((o) => !o)}
//       >
//         {open ? "📂" : "📁"} {node.name}
//       </div>
//       {open &&
//         node.children?.map((child) => (
//           <div key={child.path} style={{ paddingLeft: "0.75rem" }}>
//             <FileTreeNode
//               node={child}
//               onSelectFile={onSelectFile}
//               activePath={activePath}
//             />
//           </div>
//         ))}
//     </div>
//   );
// }

// export default function App() {
//   const [projects, setProjects] = useState([]);
//   const [selectedProject, setSelectedProject] = useState(null);
//   const [projectTree, setProjectTree] = useState(null);

//   const [selectedFile, setSelectedFile] = useState(null);
//   const [fileContent, setFileContent] = useState("");
//   const [editInstruction, setEditInstruction] = useState("");
//   const [isEditing, setIsEditing] = useState(false);
//   const [isGenerating, setIsGenerating] = useState(false);

//   const [newProjectName, setNewProjectName] = useState("");
//   const [newProjectIdea, setNewProjectIdea] = useState("");

//   useEffect(() => {
//     loadProjects();
//   }, []);

//   // const loadProjects = async () => {
//   //   try {
//   //     const res = await axios.get(`${API_BASE}/projects`);
//   //     setProjects(res.data);
//   //     if (!selectedProject && res.data.length > 0) {
//   //       setSelectedProject(res.data[0]);
//   //     }
//   //   } catch (err) {
//   //     console.error("Failed to load projects", err);
//   //   }
//   // };


//   const loadProjects = async () => {
//   try {
//     const res = await axios.get(`${API_BASE}/projects`);

//     console.log("Projects API:", res.data);

//     setProjects(Array.isArray(res.data) ? res.data : []);
    
//     if (!selectedProject && Array.isArray(res.data) && res.data.length > 0) {
//       setSelectedProject(res.data[0]);
//     }
//   } catch (err) {
//     console.error("Failed to load projects", err);
//     setProjects([]); // fallback
//   }
// };

//   useEffect(() => {
//     if (!selectedProject) return;
//     (async () => {
//       try {
//         const res = await axios.get(
//           `${API_BASE}/projects/${selectedProject}/tree`
//         );
//         setProjectTree(res.data.tree);
//       } catch (err) {
//         console.error("Failed to load tree", err);
//       }
//     })();
//   }, [selectedProject]);

//   const handleSelectFile = async (node) => {
//     if (node.type !== "file") return;
//     setSelectedFile(node);
//     try {
//       const res = await axios.get(`${API_BASE}/file`, {
//         params: { path: node.path },
//       });
//       setFileContent(res.data.content ?? "");
//     } catch (err) {
//       console.error("Failed to load file", err);
//       setFileContent("");
//     }
//   };

//   const handleAiEdit = async () => {
//     if (!selectedFile || !editInstruction.trim()) return;
//     setIsEditing(true);
//     try {
//       const res = await axios.post(`${API_BASE}/edit_file`, {
//         path: selectedFile.path,
//         instruction: editInstruction,
//       });
//       setFileContent(res.data.content ?? "");
//       setEditInstruction("");
//     } catch (err) {
//       console.error("AI edit failed", err);
//     } finally {
//       setIsEditing(false);
//     }
//   };

//   const handleGenerateProject = async (e) => {
//     e.preventDefault();
//     if (!newProjectName.trim() || !newProjectIdea.trim()) return;
//     setIsGenerating(true);
//     try {
//       await axios.post(`${API_BASE}/generate_project`, {
//         project_name: newProjectName.trim(),
//         idea: newProjectIdea.trim(),
//       });
//       const createdName = newProjectName.trim();
//       setNewProjectName("");
//       setNewProjectIdea("");
//       await loadProjects();
//       setSelectedProject(createdName);
//     } catch (err) {
//       console.error("Generate project failed", err);
//     } finally {
//       setIsGenerating(false);
//     }
//   };

//   const handleStopProject = async () => {
//   if (!selectedProject) return;

//   try {
//     await axios.post(`${API_BASE}/stop_project`, {
//       project_name: selectedProject,
//     });
//   } catch (err) {
//     console.error("Stop project failed", err);
//   }
// };

// const handleRunProject = async () => {
//   if (!selectedProject) return;

//   try {
//     const res = await axios.post(`${API_BASE}/run_project`, {
//       project_name: selectedProject,
//     });

//     if (res.data.url) {
//       window.open(res.data.url, "_blank"); // open preview in new tab
//     }
//   } catch (err) {
//     console.error("Run project failed", err);
//   }
// };


//   const language = detectLanguage(selectedFile?.path);

//   return (
//     <div className="app-shell">
//       <div className="sidebar">
//         <h2>Projects</h2>
// <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
//   <button onClick={handleRunProject}>▶ Run</button>
//   <button onClick={handleStopProject}>⏹ Stop</button>
// </div>

//         <div
//           style={{
//             border: "1px solid #1e293b",
//             borderRadius: "0.5rem",
//             padding: "0.5rem",
//             display: "flex",
//             flexDirection: "column",
//             gap: "0.35rem",
//             marginBottom: "0.75rem",
//           }}
//         >
//           <input
//             className="input"
//             placeholder="Project name (e.g. todo-app)"
//             value={newProjectName}
//             onChange={(e) => setNewProjectName(e.target.value)}
//           />
//           <textarea
//             className="textarea"
//             placeholder="Project idea / description..."
//             value={newProjectIdea}
//             onChange={(e) => setNewProjectIdea(e.target.value)}
//           />
//           <button onClick={handleGenerateProject} disabled={isGenerating}>
//             {isGenerating ? "Generating..." : "Generate Project"}
//           </button>
//         </div>

//         <div
//           style={{
//             border: "1px solid #1e293b",
//             borderRadius: "0.5rem",
//             padding: "0.5rem",
//             flex: 1,
//             overflowY: "auto",
//           }}
//         >
//           {projects.map((p) => (
//             <div
//               key={p}
//               className={
//                 "project-item" + (p === selectedProject ? " active" : "")
//               }
//               onClick={() => setSelectedProject(p)}
//             >
//               {p}
//             </div>
//           ))}
//           {projects.length === 0 && (
//             <div style={{ fontSize: "0.8rem", color: "#6b7280" }}>
//               No projects yet. Create one above.
//             </div>
//           )}
//         </div>
//       </div>

//       <div className="main-pane">
//         <div className="tree-pane">
//           <h2>Explorer</h2>
//           {projectTree ? (
//             projectTree.map((node) => (
//               <FileTreeNode
//                 key={node.path}
//                 node={node}
//                 onSelectFile={handleSelectFile}
//                 activePath={selectedFile?.path}
//               />
//             ))
//           ) : selectedProject ? (
//             <div style={{ fontSize: "0.8rem", color: "#6b7280" }}>
//               Loading tree...
//             </div>
//           ) : (
//             <div style={{ fontSize: "0.8rem", color: "#6b7280" }}>
//               Select or create a project.
//             </div>
//           )}
//         </div>

//         <div className="editor-pane">
//           <div className="editor-header">
//             <div>
//               {selectedFile ? (
//                 <>
//                   <span style={{ color: "#9ca3af" }}>Editing: </span>
//                   <span>{selectedFile.path}</span>
//                 </>
//               ) : (
//                 <span style={{ color: "#6b7280" }}>
//                   Select a file from the explorer.
//                 </span>
//               )}
//             </div>
//             <div style={{ fontSize: "0.75rem", color: "#9ca3af" }}>
//               Model: local ({language})
//             </div>
//           </div>

//           <div style={{ flex: 1, minHeight: 0 }}>
//             <Editor
//               height="100%"
//               theme="vs-dark"
//               language={language}
//               value={fileContent}
//               onChange={(value) => setFileContent(value ?? "")}
//               options={{
//                 fontSize: 13,
//                 minimap: { enabled: false },
//                 scrollBeyondLastLine: false,
//               }}
//             />
//           </div>

//           <div className="editor-bottom">
//             <textarea
//               placeholder="Describe how AI should edit this file... (e.g. 'Add Tailwind navbar and fix layout for mobile')"
//               value={editInstruction}
//               onChange={(e) => setEditInstruction(e.target.value)}
//             />
//             <button onClick={handleAiEdit} disabled={isEditing || !selectedFile}>
//               {isEditing ? "Thinking..." : "AI Edit"}
//             </button>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }


import { useEffect, useRef, useState } from "react";
import Sidebar from "./components/Sidebar";
import FileTree from "./components/FileTree";
import EditorPane from "./components/EditorPane";
import { api } from "./api";
import detectLanguage from "./detectLanguage";
import Terminal from "./components/Terminal";

export default function App() {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectTree, setProjectTree] = useState(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState("");

  const [isGenerating, setIsGenerating] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  const [runLogsProject, setRunLogsProject] = useState(null);

  const wsGenerateRef = useRef(null);
const [generationProgress, setGenerationProgress] = useState(0);
const [eta, setEta] = useState(0);


  // -----------------------------
  // Load all projects
  // -----------------------------
  const loadProjects = async () => {
    const res = await api.getProjects();

    const list = Array.isArray(res.data)
      ? res.data
      : res.data.projects;

    setProjects(list || []);

    if (!selectedProject && list.length > 0) {
      setSelectedProject(list[0]);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  // -----------------------------
  // Load file tree
  // -----------------------------
  useEffect(() => {
    if (!selectedProject) return;

    api.getProjectTree(selectedProject)
      .then((res) => setProjectTree(res.data.tree))
      .catch(() => setProjectTree(null));
  }, [selectedProject]);

  // -----------------------------
  // Load file contents
  // -----------------------------
  const loadFile = async (node) => {
    if (node.type !== "file") return;

    setSelectedFile(node);

    const res = await api.getFile(node.path);
    setFileContent(res.data.content ?? "");
  };

  // -----------------------------
  // AI Code Editing
  // -----------------------------
  const aiEditFile = async (instruction) => {
    if (!selectedFile) return;

    setIsEditing(true);

    const res = await api.editFile({
      path: selectedFile.path,
      instruction,
    });

    setFileContent(res.data.content ?? "");
    setIsEditing(false);
  };

  // -----------------------------
  // Create new project
  // -----------------------------
const createProject = async (name, idea) => {
  setIsGenerating(true);
  setGenerationProgress(0);
  setEta(0);

  // 1️⃣ Open WebSocket to backend
  wsGenerateRef.current = new WebSocket(
    `ws://127.0.0.1:8000/ws/generate/${name}`
  );

  wsGenerateRef.current.onopen = () => {
    console.log("WS Generate Connected");
  };

  wsGenerateRef.current.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);

      if (msg.event === "file_create") {
        setSelectedFile({ path: msg.file });
        setFileContent("");
      }

      if (msg.event === "editor_update") {
        setSelectedFile({ path: msg.file });
        setFileContent(msg.content);
      }

      if (msg.event === "progress") {
        setGenerationProgress(msg.progress);
      }

      if (msg.event === "eta") {
        setEta(msg.seconds);
      }

      if (msg.event === "finish") {
        setGenerationProgress(100);
        setIsGenerating(false);
        loadProjects();
        setSelectedProject(name);
      }
    } catch (e) {
      console.error("WS parse error", e);
    }
  };

  wsGenerateRef.current.onclose = () => {
    console.log("WS closed");
  };
};

  // -----------------------------
  // Run Project (WebSocket + Terminal)
  // -----------------------------
  const handleRunProject = async () => {
    if (!selectedProject) return;

    // hit backend simple status endpoint
    await api.runProject(selectedProject);

    // show terminal UI
    setRunLogsProject(selectedProject);
  };

  // -----------------------------
  // Stop Project
  // -----------------------------
  const stopProject = async () => {
    if (!selectedProject) return;
    await api.stopProject(selectedProject);
  };

  return (
    <div className="app-shell">

      {/* LEFT SIDEBAR */}
      <Sidebar
        projects={projects}
        selectedProject={selectedProject}
        setSelectedProject={setSelectedProject}
        onRun={handleRunProject}   // ← FIXED
        onStop={stopProject}
        onCreateProject={createProject}
        isGenerating={isGenerating}
      />

      {/* FILE TREE */}
      <FileTree
        tree={projectTree}
        selectedFile={selectedFile}
        onSelectFile={loadFile}
      />

      {/* EDITOR */}
      <EditorPane
  selectedFile={selectedFile}
  setSelectedFile={setSelectedFile}
  fileContent={fileContent}
  setFileContent={setFileContent}

  isGenerating={isGenerating}
  setIsGenerating={setIsGenerating}

  generationProgress={generationProgress}
  setGenerationProgress={setGenerationProgress}

  eta={eta}
  setEta={setEta}

  onAiEdit={aiEditFile}
  isEditing={isEditing}
  language={detectLanguage(selectedFile?.path)}

  wsGenerateRef={wsGenerateRef}
/>


      {/* TERMINAL LOGS */}
     {runLogsProject ? (
  <Terminal projectName={runLogsProject} />
) : null}

    </div>
  );
}
