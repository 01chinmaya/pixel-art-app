# Pixel / Voxel Art Converter — Deploy to Render

## What's in this repo
- `backend/` — FastAPI + Pillow image processing service
- `frontend/` — React + Tailwind + Vite UI
- `render.yaml` — Render Blueprint that deploys both services together

AI enhancement (Stability AI) is wired in but **off by default**. It activates
automatically once you add a `STABILITY_API_KEY` env var on the backend service —
no code changes needed.

---

## Step 1 — Push this to GitHub

```bash
cd pixel-art-app
git init
git add .
git commit -m "Initial commit: pixel art converter"
```

Create a new repo on GitHub (github.com/new), then:

```bash
git remote add origin https://github.com/<your-username>/pixel-art-app.git
git branch -M main
git push -u origin main
```

---

## Step 2 — Deploy via Render Blueprint (one click for both services)

1. Go to https://dashboard.render.com/blueprints
2. Click **New Blueprint Instance**
3. Connect your GitHub account and select the `pixel-art-app` repo
4. Render will detect `render.yaml` and show both services (`pixelart-backend`, `pixelart-frontend`)
5. Click **Apply** — Render builds and deploys both

This takes 2-5 minutes the first time. You'll get two URLs, e.g.:
- Backend: `https://pixelart-backend.onrender.com`
- Frontend: `https://pixelart-frontend.onrender.com`

> Free tier note: Render's free web services spin down after ~15 min of inactivity
> and take ~30-50 seconds to "wake up" on the next request. That's fine for a demo;
> upgrade to a paid instance later if you want it always-on.

---

## Step 3 — Connect frontend to backend URL

`render.yaml` already points `VITE_API_BASE` at `https://pixelart-backend.onrender.com`.
If Render assigns your backend a different subdomain:

1. Go to the `pixelart-frontend` service in the Render dashboard
2. Settings → Environment → edit `VITE_API_BASE` to match your actual backend URL
3. Trigger a manual redeploy (Manual Deploy → Deploy latest commit)

---

## Step 4 — Add AI enhancement later (optional)

When you have a Stability AI key (https://platform.stability.ai/):

1. Go to the `pixelart-backend` service in Render dashboard
2. Settings → Environment → Add Environment Variable
   - Key: `STABILITY_API_KEY`
   - Value: your key
3. Save → Render redeploys the backend automatically
4. The "Enhance with AI" checkbox in the app will now actually call Stability AI.
   Until then, checking that box silently falls back to the plain pixelated result
   (no errors, no broken UX).

---

## Local development (test before deploying)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:5173`. It talks to `http://localhost:8000` by default.

---

## Tuning the pixel art look

Edit `backend/pixelate.py`:
- `block_size` — chunkiness (also adjustable live via the slider in the UI)
- `MINECRAFT_PALETTE` — swap in your own color set for a different game's look
- `contrast_boost` / `saturation_boost` — punchiness of colors
- `add_block_shading` variance range — how strong the per-block lighting effect is
