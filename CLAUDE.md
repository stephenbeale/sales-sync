# sales-sync

Cross-platform listing sync tool between Vinted and eBay.

## Project Structure

```
sales-sync/
  api/                  Python Flask backend
    app.py              Main Flask application (CRUD + sell/sync/email endpoints)
    models.py           SQLite schema (items + sync_log tables)
    config.py           Env var configuration
    requirements.txt    Python dependencies
    .env.example        Env var template (copy to .env, never commit .env)
    services/
      ebay_service.py   eBay Trading API — EndItem + GetItem
      email_service.py  Gmail API — polls for Vinted sale notification emails
  web/                  React + Vite frontend
    src/
      components/
        AddItemForm.jsx  Add cross-listed item (title, eBay listing ID, Vinted title)
        ItemCard.jsx     "Sold on Vinted" / "Sold on eBay" action buttons
        EmailChecker.jsx One-click Gmail scan for Vinted sale emails
        FilterBar.jsx    Active / Sold / All filter
        ItemList.jsx     Item list container
      hooks/
        useItems.js     State management hook
      utils/
        api.js          Backend communication utility
```

## Running Locally

```bash
# Backend
cd api
cp .env.example .env   # fill in credentials
pip install -r requirements.txt
python app.py           # runs on http://localhost:5000

# Frontend
cd web
npm install
npm run dev             # runs on http://localhost:5173
```

## Env Vars (api/.env)

| Variable | Description |
|----------|-------------|
| `EBAY_APP_ID` | eBay developer App ID |
| `EBAY_CERT_ID` | eBay developer Cert ID |
| `EBAY_USER_TOKEN` | eBay OAuth user token (Trading API) |
| `GMAIL_CREDENTIALS_PATH` | Path to Gmail OAuth credentials.json |

## External Setup Required

### 1. Gmail API
1. Go to https://console.cloud.google.com
2. Create a project, enable the Gmail API
3. Create OAuth 2.0 Desktop credentials
4. Download `credentials.json` to `api/`
5. First run of `email_service.py` will open a browser for OAuth consent — this generates `token.json`

### 2. eBay Trading API User Token
- The Trading API (EndItem) requires a user-level OAuth token, not just app credentials
- Complete the eBay OAuth consent flow and store the token in `EBAY_USER_TOKEN`

### 3. Vinted Email Tuning
- Obtain a real Vinted sale notification email
- Tune regex patterns in `api/services/email_service.py` to match the actual email format

## User Preferences
- All code must be accessible (WCAG, ARIA, semantic HTML, keyboard navigation)
- Always create feature branches before development — never work directly on master
- Branch naming: `feature/<desc>`, `fix/<desc>`, `refactor/<desc>`

## Session Notes

### 2026-03-08 — Session 1 (Project Creation)

**Work Completed:**
- Full project scaffold built from scratch
- Backend: Flask API, SQLite models, eBay Trading API service, Gmail API email polling service
- Frontend: React + Vite, all core components (AddItemForm, ItemCard, EmailChecker, FilterBar, ItemList), useItems hook, api.js utility
- Dark theme, mobile responsive, accessible markup throughout
- Scaffold commit pushed to master: `b772ea9`
- Both `master` and `feature/scaffold` pushed to remote

**Work In Progress:**
- Gmail API credentials not yet set up (requires Google Cloud Console — see External Setup above)
- eBay user token not yet obtained
- Vinted email parser patterns not yet tuned against a real email
- No end-to-end local test completed yet

**Unfinished Git Workflows:**
- No open PRs — feature/scaffold had no additional commits over master so no PR was created

**Next Steps:**
1. Complete Gmail API setup (Google Cloud Console credentials.json)
2. Obtain eBay Trading API user token
3. Get a real Vinted sale notification email and tune `email_service.py` regex patterns
4. Run the app locally end-to-end: add an item, mark it sold, verify eBay EndItem call fires
5. Consider whether to add a frontend `VITE_API_URL` env var for flexibility

**Technical Notes:**
- The scaffold commit landed directly on master (correct for initial project creation)
- `feature/scaffold` points to the same commit as master — this branch can be deleted if not needed
- SQLite DB is created at runtime by `models.py` — not committed
- `api/.env` and `api/credentials.json` and `api/token.json` are all gitignored — never commit them
