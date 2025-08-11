# Image Analyzer (FastAPI + React + YOLO/Contour)

Image Analyzer is a small, production-shaped demo that lets you upload an image, run detection (YOLO or OpenCV Contour, with an Auto fallback), and get an annotated result plus per-box stats. The FastAPI backend handles inference, analytics, and a JSONL-based history (list/detail/delete), while the React UI lets you switch detectors and tweak confidence/max-detections.

---

## Why this project?

- Practical full‑stack demo: end‑to‑end flow (upload → process → output → history) with FastAPI + React.
- Real‑world shape: file I/O, YOLO/Contour detection, annotated results, history & cleanup.
- Clean architecture: clear layers (api / services / models / utils) — easy to extend.
- Safe defaults: CORS, .env, static serving, and diagnostics endpoints for quick debugging.
---

## ⚙️ Installation

> You can run with **Docker** or **locally**. Pick one.

### Option A — Docker (recommended)

```bash
docker compose up --build
# Backend:  http://localhost:8000/docs
# Frontend: http://localhost:3000
```

> ⚠️ Don’t commit model weights. Use `.env` → `MODEL_WEIGHTS=yolov8n.pt` (or point to your own file).

### Option B — Local setup

**Backend**
```bash
cd Backend
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # or: cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**
```bash
cd Frontend
npm install
npm run dev
# open http://localhost:3000
```

---

## 🚀 Usage (UI)

1. **Upload** an image (drag & drop or file picker).  
2. Choose **Detector** (Auto / YOLO / Contour), tweak **Confidence** / **Max detections** if needed.  
3. Click **Analyze** → annotated image appears on the right, **detections** listed below.  
4. Open **History** to view recent uploads, **Preview** or **Delete** items.

---

## 🔌 API Endpoints (Backend)

Swagger UI: **http://localhost:8000/docs**

- `POST /api/v1/analyze`
  - Query: `detector=auto|yolo|contour`, `conf`, `max_dets`
  - Body: `multipart/form-data` with `file` (image)
  - Returns: detections + `annotated_url` + `history_id`

- History
  - `GET    /api/v1/history`
  - `GET    /api/v1/history/{id}`
  - `DELETE /api/v1/history/{id}`
  - `DELETE /api/v1/history`

- Debug
  - `GET /api/v1/debug/version`
  - `GET /api/v1/debug/config`

- Diagnostics
  - `POST /api/v1/analyze_smoke`  (save only)
  - `POST /api/v1/analyze_min`    (contour‑only)

---

## 🗂️ Project Structure

```plaintext
image-analyzer/
├── Backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints.py
│   │   │       └── schemas.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── models/
│   │   │   └── detection.py
│   │   ├── services/
│   │   │   ├── inference.py
│   │   │   └── analytics.py
│   │   └── utils/
│   │       ├── storage.py
│   │       ├── visualize.py
│   │       └── history.py
│   ├── main.py
│   ├── worker.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── uploads/            # static outputs 
├── Frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   └── styles/
│   │       └── global.css
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
└── README.md
```

---

## 🔧 Configuration

`Backend/.env`

```env
UPLOAD_DIR=uploads
CORS_ORIGINS=["http://localhost:3000"]
DETECTOR=auto             
MODEL_WEIGHTS=yolov8n.pt
SECRET_KEY=change-me
```

- The UI can override `detector` via query parameter.
- History is stored in `uploads/history.jsonl` (JSON Lines).

---

## 🧰 Troubleshooting

- **500 errors?** Try `analyze_smoke` (checks saving) then `analyze_min` (Contour path).
- **CORS issues?** Ensure `.env` → `CORS_ORIGINS=["http://localhost:3000"]`.
- **Endpoints missing in /docs?** Check `include_router` and server reload.
- **YOLO/Torch missing?** Set `DETECTOR=contour` (Auto will fallback anyway).

---

## 🤝 Contributing

Issues and PRs are welcome — improvements, bug fixes, or new detectors.  
---

## 📜 License

MIT
