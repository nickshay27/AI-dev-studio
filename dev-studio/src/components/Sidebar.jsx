import ProjectList from "./ProjectList";
import ProjectCreator from "./ProjectCreator";
import RunControls from "./RunControls";

export default function Sidebar({
  projects,
  selectedProject,
  setSelectedProject,
  onRun,
  onStop,
  onCreateProject,
  isGenerating,
}) {
  return (
    <div className="sidebar">
      <h2>Projects</h2>

      <RunControls
        selectedProject={selectedProject}
        onRun={onRun}
        onStop={onStop}
      />

      <ProjectCreator
        onCreate={onCreateProject}
        isGenerating={isGenerating}
      />

      <ProjectList
        projects={projects}
        selected={selectedProject}
        onSelect={setSelectedProject}
      />
    </div>
  );
}
