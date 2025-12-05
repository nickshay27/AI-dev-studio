import axios from "axios";

export const API_BASE = "http://127.0.0.1:8000";

export const api = {
  getProjects: () => axios.get(`${API_BASE}/projects`),

  getProjectTree: (name) =>
    axios.get(`${API_BASE}/projects/${name}/tree`),

  getFile: (path) =>
    axios.get(`${API_BASE}/file`, { params: { path } }),

  editFile: (payload) =>
    axios.post(`${API_BASE}/edit_file`, payload),

  generateProject: (payload) =>
    axios.post(`${API_BASE}/generate_project`, payload),

  runProject: (name) =>
    axios.post(`${API_BASE}/run_project`, { project_name: name }),

  stopProject: (name) =>
    axios.post(`${API_BASE}/stop_project`, { project_name: name }),
};
