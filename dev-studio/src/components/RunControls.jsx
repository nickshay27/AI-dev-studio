export default function RunControls({ selectedProject, onRun, onStop }) {
  return (
    <div className="run-controls">
      <button onClick={() => onRun(selectedProject)}>▶ Run</button>
      <button onClick={() => onStop(selectedProject)}>⏹ Stop</button>
    </div>
  );
}
