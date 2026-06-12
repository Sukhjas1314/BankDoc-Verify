import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api",
  withCredentials: true
});

function readCookie(name) {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${name}=`))
    ?.split("=")[1];
}

api.interceptors.request.use(async (config) => {
  if (["post", "put", "patch", "delete"].includes(config.method)) {
    let token = readCookie("csrftoken");
    if (!token) {
      await api.get("/csrf/");
      token = readCookie("csrftoken");
    }
    if (token) {
      config.headers["X-CSRFToken"] = decodeURIComponent(token);
    }
  }
  return config;
});

export function getDashboard() {
  return api.get("/dashboard/");
}

export function uploadReport(file) {
  const form = new FormData();
  form.append("file", file);
  return api.post("/upload/", form, { headers: { "Content-Type": "multipart/form-data" } });
}

export function extractReport(uploadedFileId) {
  return api.post("/extract/", { uploaded_file_id: uploadedFileId });
}

export function validateReport(uploadedFileId) {
  return api.post("/validate/", { uploaded_file_id: uploadedFileId });
}

export function getHistory() {
  return api.get("/history/");
}

export function reportUrl(runId) {
  return `${api.defaults.baseURL}/report/${runId}/`;
}
