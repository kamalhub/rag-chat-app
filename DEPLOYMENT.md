# Deployment Guide

Deploy the backend on **Railway** and the frontend on **Vercel**.

---

## 1. Push to GitHub (prerequisite)

Make sure the repo is on GitHub first. From your terminal:

```bash
cd ~/rag
gh repo create rag-chat-app --public --source=. --remote=origin --push
```

Or create the repo at [github.com/new](https://github.com/new), then:

```bash
git remote add origin https://github.com/YOUR_USERNAME/rag-chat-app.git
git push -u origin main
```

---

## 2. Deploy the Backend on Railway

### Step-by-step

1. Go to [railway.com](https://railway.app) and sign in with GitHub.

2. Click **"New Project"** → **"Deploy from GitHub Repo"**.

3. Select your `rag-chat-app` repository.

4. Railway will detect the repo. You need to tell it to only build the backend:
   - Go to **Settings** → **Root Directory** → set it to `backend`
   - Railway will auto-detect the `Dockerfile` and use it.

5. Add your environment variable:
   - Go to the **Variables** tab
   - Click **"New Variable"**
   - Add: `OPENAI_API_KEY` = `your-actual-key`

6. Railway will auto-deploy. Once it's live, go to **Settings** → **Networking** → **Generate Domain**.
   You'll get a URL like `https://rag-chat-app-production-xxxx.up.railway.app`.

7. Test it by visiting `https://your-railway-url.up.railway.app/docs` — you should see the FastAPI Swagger UI.

### Notes
- Railway's free tier gives you $5/month of usage, which is enough for light testing.
- The FAISS vector store is in-memory, so it resets when the service restarts. For production, you'd want to persist the index to a volume.

---

## 3. Deploy the Frontend on Vercel

### Step-by-step

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub.

2. Click **"Add New..."** → **"Project"**.

3. Import your `rag-chat-app` repository.

4. Configure the project settings:
   - **Framework Preset:** Next.js (should be auto-detected)
   - **Root Directory:** Click "Edit" and set it to `frontend`

5. Add the environment variable so the frontend knows where the backend is:
   - Expand **"Environment Variables"**
   - Add: `NEXT_PUBLIC_API_URL` = `https://your-railway-url.up.railway.app`
     (use the Railway URL from step 2.6 above)

6. Click **"Deploy"**. Vercel will build and deploy automatically.

7. You'll get a URL like `https://rag-chat-app.vercel.app`. Open it and you're live!

### Notes
- Every push to `main` will auto-deploy both Vercel and Railway.
- If you change the Railway URL later, update the `NEXT_PUBLIC_API_URL` in Vercel's project settings and redeploy.

---

## 4. CORS Update (important)

Once both are deployed, update the backend CORS settings to restrict access to your Vercel domain only. In `backend/main.py`, change:

```python
allow_origins=["*"],
```

to:

```python
allow_origins=["https://rag-chat-app.vercel.app"],
```

Then push the change — Railway will auto-redeploy.

---

## Quick Reference

| Service  | Platform | Root Directory | Key Environment Variable           |
|----------|----------|----------------|------------------------------------|
| Backend  | Railway  | `backend`      | `OPENAI_API_KEY`                   |
| Frontend | Vercel   | `frontend`     | `NEXT_PUBLIC_API_URL` (Railway URL)|

---

## Troubleshooting

**Backend won't start on Railway:**
- Check the deploy logs in Railway for errors.
- Make sure `OPENAI_API_KEY` is set in the Variables tab.
- Verify the Root Directory is set to `backend`.

**Frontend can't reach the backend:**
- Check that `NEXT_PUBLIC_API_URL` is set correctly in Vercel (no trailing slash).
- Make sure the Railway service has a public domain generated.
- Check browser console for CORS errors — update `allow_origins` in `main.py`.

**"No documents ingested" error:**
- The FAISS store is in-memory and starts empty after each deploy.
- Upload a document via the UI first before chatting.
