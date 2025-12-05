from pathlib import Path


def create_frontend_boilerplate(frontend: Path, port: int) -> None:
    """
    Creates an advanced Vite + React folder structure with basic boilerplate.
    """
    frontend.mkdir(parents=True, exist_ok=True)
    src = frontend / "src"
    src.mkdir(exist_ok=True)

    # Create standard subfolders
    for folder in [
        "assets",
        "components",
        "pages",
        "layout",
        "hooks",
        "context",
        "utils",
        "services",
        "styles",
    ]:
        (src / folder).mkdir(exist_ok=True)

    # index.html
    (frontend / "index.html").write_text(
        f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>AI Generated App</title>
    <link rel="stylesheet" href="/src/styles/global.css" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""
    )

    # main.jsx
    (src / "main.jsx").write_text(
        """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
    )

    # App.jsx
    (src / "App.jsx").write_text(
        """export default function App() {
  return (
    <div style={{ padding: 20 }}>
      <h1>🚀 AI Generated React App</h1>
      <p>Everything is ready. Start building your UI.</p>
    </div>
  );
}
"""
    )

    # global.css
    (src / "styles" / "global.css").write_text(
        "body { font-family: system-ui, sans-serif; background: #f5f6fa; }"
    )

    # api.js
    (src / "services" / "api.js").write_text(
        """import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
});

export default api;
"""
    )

    # vite.config.mjs
    (frontend / "vite.config.mjs").write_text(
        f"""import {{ defineConfig }} from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({{
  plugins: [react()],
  server: {{
    port: {port},
    host: true,
  }},
}})
"""
    )


def setup_tailwind(frontend: Path) -> None:
    """
    Configure Tailwind + PostCSS + update global.css with @tailwind directives.
    """
    # tailwind.config.js
    (frontend / "tailwind.config.js").write_text(
        """
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
}
"""
    )

    # postcss.config.js
    (frontend / "postcss.config.js").write_text(
        """
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""
    )

    # overwrite global.css with Tailwind imports
    (frontend / "src" / "styles" / "global.css").write_text(
        """
@tailwind base;
@tailwind components;
@tailwind utilities;
"""
    )
