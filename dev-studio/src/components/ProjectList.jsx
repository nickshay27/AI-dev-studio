export default function ProjectList({ projects, selected, onSelect }) {
  return (
    <div className="project-list">
      {projects.map((p) => (
        <div
          key={p}
          className={"project-item" + (p === selected ? " active" : "")}
          onClick={() => onSelect(p)}
        >
          {p}
        </div>
      ))}
      {projects.length === 0 && (
        <div className="empty-text">No projects yet.</div>
      )}
    </div>
  );
}
