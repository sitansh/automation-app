Frontend (React + Vite)
--------------------------------

This project contains a minimal React SPA scaffold using Vite in `frontend/`.

Setup (from project root):

```bash
cd frontend
npm install
npm run dev
```

The dev server proxies `/api` and `/reports` calls to the backend at `http://127.0.0.1:8080` (see `vite.config.js`).

When ready for production, run `npm run build` and serve the `dist/` assets (optionally configure FastAPI to serve static files).
