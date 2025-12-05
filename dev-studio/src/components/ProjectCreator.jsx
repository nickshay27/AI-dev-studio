import { useState } from "react";

export default function ProjectCreator({ onCreate, isGenerating }) {
  const [name, setName] = useState("");
  const [idea, setIdea] = useState("");

  const submit = () => {
    if (!name.trim() || !idea.trim()) return;
    onCreate(name.trim(), idea.trim());
    setName("");
    setIdea("");
  };

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 flex flex-col gap-3">
      <h3 class="text-slate-200 font-semibold text-lg mb-1">Create New Project</h3>

      {/* Project Name */}
      <input
        placeholder="Project name (e.g. todo-app)"
        value={name}
        onChange={(e) => setName(e.target.value)}
        className="px-3 py-2 rounded-md bg-slate-900 border border-slate-700 
                   text-slate-200 text-sm outline-none focus:ring-2 
                   focus:ring-blue-500 focus:border-blue-500"
      />

      {/* Project Idea */}
      <textarea
        placeholder="Describe the project idea..."
        value={idea}
        onChange={(e) => setIdea(e.target.value)}
        rows={3}
        className="px-3 py-2 rounded-md bg-slate-900 border border-slate-700 
                   text-slate-200 text-sm resize-none outline-none 
                   focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      />

      {/* Submit Button */}
      <button
        onClick={submit}
        disabled={isGenerating}
        className={`py-2 px-4 rounded-md text-sm font-medium transition 
          ${
            isGenerating
              ? "bg-blue-900 text-blue-300 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700 text-white"
          }`}
      >
        {isGenerating ? "Generating..." : "Create Project"}
      </button>
    </div>
  );
}
