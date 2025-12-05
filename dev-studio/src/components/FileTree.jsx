import FileTreeNode from "./FileTreeNode";

export default function FileTree({ tree, selectedFile, onSelectFile }) {
  return (
    <div className="tree-pane">
      <h2>Explorer</h2>
      {tree ? (
        tree.map((node) => (
          <FileTreeNode
            key={node.path}
            node={node}
            activePath={selectedFile?.path}
            onSelectFile={onSelectFile}
          />
        ))
      ) : (
        <div className="empty-text">Select or create a project.</div>
      )}
    </div>
  );
}
