import { useState } from "react";

export default function FileTreeNode({ node, onSelectFile, activePath }) {
  const [open, setOpen] = useState(node.type === "dir");

  if (node.type === "file") {
    const isActive = activePath === node.path;
    return (
      <div
        className={"file-node" + (isActive ? " active" : "")}
        onClick={() => onSelectFile(node)}
      >
        📄 {node.name}
      </div>
    );
  }

  return (
    <div>
      <div className="folder-node" onClick={() => setOpen((o) => !o)}>
        {open ? "📂" : "📁"} {node.name}
      </div>

      {open &&
        node.children?.map((child) => (
          <div key={child.path} className="tree-indent">
            <FileTreeNode
              node={child}
              onSelectFile={onSelectFile}
              activePath={activePath}
            />
          </div>
        ))}
    </div>
  );
}
