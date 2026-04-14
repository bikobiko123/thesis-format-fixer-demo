import { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

function App() {
  const [file, setFile] = useState(null);
  const [degree, setDegree] = useState("undergraduate");
  const [status, setStatus] = useState("idle");
  const [message, setMessage] = useState("上传 .docx，系统会返回一个 zip 结果包。");

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setMessage("请先选择一个 .docx 文件。");
      return;
    }

    setStatus("processing");
    setMessage("正在解析、修复并生成报告...");
    const form = new FormData();
    form.append("file", file);
    form.append("degree", degree);

    try {
      const response = await fetch(`${API_BASE}/api/process`, {
        method: "POST",
        body: form,
      });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({ detail: "处理失败" }));
        throw new Error(payload.detail);
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "thesis_format_fix_result.zip";
      link.click();
      URL.revokeObjectURL(url);
      setStatus("done");
      setMessage("处理完成：已下载修复文档、校验报告和人工清单。");
    } catch (error) {
      setStatus("error");
      setMessage(error.message);
    }
  }

  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">Demo University Thesis Desk</p>
        <h1>论文格式智能修复工作台</h1>
        <p className="lead">
          规则引擎负责确定性修复，校验器逐条出结论，大模型接口保留给结构解释与错误说明。
        </p>
      </section>

      <form className="upload-card" onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="degree">培养层次</label>
          <select id="degree" value={degree} onChange={(event) => setDegree(event.target.value)}>
            <option value="undergraduate">本科</option>
            <option value="master">硕士</option>
          </select>
        </div>

        <label className="drop-zone">
          <span>{file ? file.name : "选择或拖入 .docx 论文"}</span>
          <small>仅支持 Word Open XML 文档，不处理 PDF 或论文内容生成。</small>
          <input
            type="file"
            accept=".docx"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
        </label>

        <button disabled={status === "processing"} type="submit">
          {status === "processing" ? "处理中..." : "开始格式修复"}
        </button>

        <p className={`status status-${status}`}>{message}</p>
      </form>

      <section className="pipeline" aria-label="system pipeline">
        {["DOCX 解析", "IR 结构识别", "规则修复", "逐条校验", "报告输出"].map((item) => (
          <article key={item}>
            <span />
            <p>{item}</p>
          </article>
        ))}
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
