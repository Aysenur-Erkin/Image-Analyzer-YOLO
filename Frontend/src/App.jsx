import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  analyzeImage,
  fetchHistory,
  deleteHistoryItem,
  clearHistory,
} from "./services/api";

export default function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  const [imgUrl, setImgUrl] = useState(null);
  const [objects, setObjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [info, setInfo] = useState("");

  const [conf, setConf] = useState(0.25);
  const [maxDets, setMaxDets] = useState(200);
  const [detector, setDetector] = useState("auto");

  const [history, setHistory] = useState([]);
  const [busyId, setBusyId] = useState(null);
  const [clearing, setClearing] = useState(false);

  const dropRef = useRef(null);
  const backendBase = useMemo(() => "http://localhost:8000", []);

  useEffect(() => {
    (async () => {
      try {
        const h = await fetchHistory(20);
        setHistory(h.items || []);
      } catch {}
    })();
  }, []);

  const onFile = (f) => {
    setFile(f || null);
    setImgUrl(null);
    setObjects([]);
    setErr("");
    setInfo("");

    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(f ? URL.createObjectURL(f) : null);
  };

  const onDragOver = (e) => {
    e.preventDefault();
    dropRef.current?.classList.add("dropzone--active");
  };
  const onDragLeave = () => {
    dropRef.current?.classList.remove("dropzone--active");
  };
  const onDrop = (e) => {
    e.preventDefault();
    dropRef.current?.classList.remove("dropzone--active");
    const f = e.dataTransfer.files?.[0];
    if (f) onFile(f);
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setErr("");
    setInfo("");
    try {
      const data = await analyzeImage(file, conf, maxDets, detector);
      const full = data.annotated_url ? backendBase + data.annotated_url : null;
      setImgUrl(full);
      setObjects(data.objects || []);

      try {
        const h = await fetchHistory(20);
        setHistory(h.items || []);
      } catch {}
    } catch (e) {
      setErr(e.message || "Analyze failed");
      setImgUrl(null);
      setObjects([]);
    } finally {
      setLoading(false);
    }
  };

  const onRefreshHistory = async () => {
    try {
      const h = await fetchHistory(20);
      setHistory(h.items || []);
      setInfo("History refreshed.");
      setTimeout(() => setInfo(""), 1500);
    } catch (e) {
      setErr(String(e));
    }
  };

  const onDeleteOne = async (id) => {
    if (!id) return;
    const ok = window.confirm("Delete this record and its files?");
    if (!ok) return;

    setBusyId(id);
    setErr("");
    setInfo("");
    try {
      await deleteHistoryItem(id);
      setHistory((prev) => prev.filter((x) => x.id !== id));
      setInfo("Record deleted.");
      setTimeout(() => setInfo(""), 1500);
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusyId(null);
    }
  };

  const onClearAll = async () => {
    const ok = window.confirm("All history and related files will be deleted. Are you sure?");
    if (!ok) return;

    setClearing(true);
    setErr("");
    setInfo("");
    try {
      const res = await clearHistory();
      setHistory([]);
      setInfo(`Cleared. Deleted records: ${res.deleted}`);
      setTimeout(() => setInfo(""), 2000);
    } catch (e) {
      setErr(String(e));
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="app">
      <header className="app__header">
        <div className="container">
          <h1 className="brand">Image Analyzer</h1>
          <p className="muted">YOLO & OpenCV based image analysis</p>
        </div>
      </header>

      <main className="container">
        <section className="card">
          <h2 className="card__title">1) Upload & configure</h2>

          <form onSubmit={onSubmit} className="controls">
            <div className="controls__row">
              <label className="btn">
                Choose File
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => onFile(e.target.files?.[0] ?? null)}
                  hidden
                />
              </label>

              <div
                ref={dropRef}
                className="dropzone"
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
                onDrop={onDrop}
              >
                <span className="muted">Drag & drop</span>
              </div>

              <button className="btn btn--primary" type="submit" disabled={loading || !file}>
                {loading ? "Analyzing..." : "Analyze"}
              </button>
            </div>

            <div className="controls__row">
              <label className="field">
                <span>Conf: {conf.toFixed(2)}</span>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={conf}
                  onChange={(e) => setConf(parseFloat(e.target.value))}
                />
              </label>

              <label className="field">
                <span>Max dets</span>
                <input
                  type="number"
                  min="1"
                  max="3000"
                  step="1"
                  value={maxDets}
                  onChange={(e) => setMaxDets(parseInt(e.target.value || "1", 10))}
                  style={{ width: 100 }}
                />
              </label>

              <label className="field">
                <span>Detector</span>
                <select
                  value={detector}
                  onChange={(e) => setDetector(e.target.value)}
                  style={{
                    background: "black",
                    color: "white",
                    border: "none",
                    outline: "none",
                  }}
                >
                  <option value="auto">Auto</option>
                  <option value="yolo">YOLO</option>
                  <option value="contour">Contour</option>
                </select>
              </label>

              {file && <span className="muted">Selected: {file.name}</span>}
            </div>
          </form>

          {err && <div className="alert alert--error">{err}</div>}
          {info && !err && <div className="alert" style={{ color: "#c7f9cc" }}>{info}</div>}
        </section>

        <section className="grid">
          <div className="card">
            <h2 className="card__title">2) Preview</h2>
            {!previewUrl ? (
              <p className="muted">No image selected yet.</p>
            ) : (
              <img src={previewUrl} alt="preview" className="image" />
            )}
          </div>

          <div className="card">
            <h2 className="card__title">3) Annotated output</h2>
            {!imgUrl ? (
              <p className="muted">No analysis result yet.</p>
            ) : (
              <>
                <img src={imgUrl} alt="annotated" className="image" />
              </>
            )}
          </div>
        </section>

        <section className="card">
          <h2 className="card__title">4) Detections</h2>
          <p className="muted">Total: {objects.length}</p>

          {objects.length === 0 ? (
            <p>No objects found.</p>
          ) : (
            <div className="table">
              <div className="table__head">
                <div>Label</div>
                <div>Conf</div>
                <div>Area</div>
                <div>BBox [x1, y1, x2, y2]</div>
              </div>
              <div className="table__body">
                {objects.map((o, i) => (
                  <div className="table__row" key={i}>
                    <div>{o.label}</div>
                    <div>{o.confidence.toFixed(2)}</div>
                    <div>{o.area}</div>
                    <div>{o.bbox?.join(", ") ?? "-"}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        <section className="card">
          <div
            className="card__title"
            style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}
          >
            <span>5) Recent uploads</span>
            <div className="actions">
              <button className="btn" onClick={onRefreshHistory}>
                Refresh
              </button>
              <button
                className="btn btn--danger"
                onClick={onClearAll}
                disabled={clearing || history.length === 0}
              >
                {clearing ? "Clearing..." : "Clear all"}
              </button>
            </div>
          </div>

          {!history.length ? (
            <p className="muted">No records yet.</p>
          ) : (
            <div className="history">
              {history.map((it) => {
                const hrefPath = it.annotated_url || it.original_url || null;
                const fullHref = hrefPath ? backendBase + hrefPath : "#";
                const isBusy = busyId === it.id;

                return (
                  <div key={it.id} className="history__item">
                    <a className="history__thumb" href={fullHref} target="_blank" rel="noreferrer">
                      {hrefPath ? (
                        <img src={backendBase + hrefPath} alt={it.filename} />
                      ) : (
                        <div className="history__placeholder">no image</div>
                      )}
                    </a>
                    <div className="history__meta">
                      <div className="history__name" title={it.filename}>
                        {it.filename}
                      </div>
                      <div className="history__sub muted">
                        {new Date(it.uploaded_at).toLocaleString()} · {it.objects_count} objects
                      </div>
                      <div className="history__labels">
                        {(it.labels || []).map((l) => (
                          <span key={l} className="tag">
                            {l}
                          </span>
                        ))}
                      </div>
                      <div className="actions" style={{ marginTop: 8 }}>
                        <button
                          className="btn btn--danger"
                          onClick={() => onDeleteOne(it.id)}
                          disabled={isBusy}
                          title="Delete record and files"
                        >
                          {isBusy ? "Deleting..." : "Delete"}
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </main>

      <footer className="footer">
        <div className="container muted">© {new Date().getFullYear()} Image Analyzer</div>
      </footer>
    </div>
  );
}
