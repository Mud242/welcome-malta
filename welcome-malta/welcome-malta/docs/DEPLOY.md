# Going live — Welcome Malta (≈15 minutes)

**Chosen platform: Cloudflare Pages** · open access, no geo-restrictions · cost: €0
(static hosting, unmetered bandwidth, automatic HTTPS).

Why this one over GitHub Pages / Netlify / Vercel:

- **EU latency**: Cloudflare's free tier serves from edge nodes across Europe
- **Cookieless Web Analytics**: usage stats for grant/EURES reporting with **no
  consent banner** (no cookies, no personal data collection by the analytics)
- **Room to grow**: Access rules, redirects, and Workers are one click away if ever needed
- **Backup**: GitHub Pages works from the same repo with zero changes — portability is free

---

## Route A — connected to GitHub (recommended, auto-deploy on every push)

> Prerequisite: the monthly content-watch CI already assumes GitHub, so the repo exists for both.

1. Create your copy of the code:
   ```bash
   cd welcome-malta
   git init
   git add -A
   git commit -m "Welcome Malta v1"
   git branch -M main
   git remote add origin https://github.com/<you>/welcome-malta.git
   git push -u origin main
   ```
2. Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
3. Pick the `welcome-malta` repo · Framework preset: **None** · Build command: *(empty)* ·
   Output directory: `/` (root)
4. **Deploy** → your site is live at `https://welcome-malta.pages.dev`
5. Every `git push` now redeploys automatically (HTTPS handled for you)

## Route B — direct upload (no git, fastest)

Cloudflare dashboard → Workers & Pages → Create → Pages → **Direct Upload** → drag the
`welcome-malta` folder → live at the same `*.pages.dev` URL.

> Note: with Route B the code is not on GitHub, so enable the monthly content-watch by
> running `python3 tools/check_links.py index.html` and `tools/watch_sources.py`
> yourself in a personal monthly reminder instead.

## Optional: GitHub Actions deploy (Route A+)

If you prefer GitHub Actions to perform the deploy (instead of Pages' built-in git
connection), `.github/workflows/deploy.yml` is included — add two repository secrets
(`secrets.Cloudflare` docs in that file) and it deploys on every push to `main`.
Don't enable it *and* the git connection; pick one deployer.

## After go-live (5 minutes)

| Step | Where | Why |
|---|---|---|
| Enable **Web Analytics** | Pages project → Analytics | cookieless stats, no consent banner (verify with your privacy counsel) |
| Custom domain (optional, ~€12/yr) | Pages project → Custom domains | e.g. `welcomemalta.eu` — HTTPS auto-issued |
| Confirm **no Access rules** | (decision: fully open) | nothing to do — open by default |
| Smoke-test | open the live URL | checklist + demo chat + health dashboard all work offline-logic |

The `404.html` fallback and `_headers` security headers in this folder are picked up by
Cloudflare Pages automatically — no configuration needed.
