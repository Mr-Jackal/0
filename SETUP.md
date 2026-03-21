# Repo Mirror — Setup Guide

## Files Overview

```
your-workflow-repo/
├── mirror.py                        # Main script
├── repos.txt                        # List of 23 repos to upload
├── uploaded.txt                     # Tracks what's been uploaded (starts empty)
└── .github/
    └── workflows/
        └── mirror.yml               # GitHub Actions workflow
```

---

## Step 1 — Create a Workflow Repo on Primary Account (Ns81000)

1. Go to **github.com/Ns81000**
2. Create a **new private repo** — name it something like `mirror-workflow`
3. Upload all 4 files maintaining the folder structure above

---

## Step 2 — Create a Personal Access Token for Secondary Account (Mr-Jackal)

1. Log into **github.com/Mr-Jackal**
2. Go to **Settings → Developer Settings → Personal Access Tokens → Tokens (classic)**
3. Click **Generate new token (classic)**
4. Set expiration to **90 days** or **No expiration**
5. Check these scopes:
   - ✅ `repo` (full control)
   - ✅ `workflow`
6. Copy the token — you won't see it again

---

## Step 3 — Create a Personal Access Token for Primary Account (Ns81000)

This is needed so the workflow can commit `uploaded.txt` back to itself.

1. Log into **github.com/Ns81000**
2. Go to **Settings → Developer Settings → Personal Access Tokens → Tokens (classic)**
3. Click **Generate new token (classic)**
4. Check these scopes:
   - ✅ `repo`
   - ✅ `workflow`
5. Copy the token

---

## Step 4 — Add Secrets to the Workflow Repo

Go to your `mirror-workflow` repo on **Ns81000** →
**Settings → Secrets and variables → Actions → New repository secret**

Add these one by one:

| Secret Name | Value |
|---|---|
| `SOURCE_OWNER` | `Ns81000` |
| `TARGET_OWNER` | `Mr-Jackal` |
| `TARGET_EMAIL` | Email address of Mr-Jackal account |
| `TARGET_GH_TOKEN` | PAT you created for Mr-Jackal (Step 2) |
| `WORKFLOW_TOKEN` | PAT you created for Ns81000 (Step 3) |

---

## Step 5 — Test It Manually First

Before letting it run on schedule:

1. Go to your `mirror-workflow` repo
2. Click **Actions** tab
3. Click **Daily Repo Mirror**
4. Click **Run workflow → Run workflow**
5. Watch the logs — it should upload the first repo (`webcam-login-monitor_v2.1_Enhanced`) to Mr-Jackal

---

## Step 6 — Let It Run Daily

After the manual test works, the workflow will automatically run every day at **10:00 AM UTC** and upload one repo per day.

Progress is tracked in `uploaded.txt` — you can check it anytime to see what's been done.

---

## Schedule

| Day | Repo |
|---|---|
| Day 1 | webcam-login-monitor_v2.1_Enhanced |
| Day 2 | Summer-Training |
| Day 3 | SpotDL_Wrape |
| Day 4 | Realtek-RTW89-Wi-Fi-Driver |
| Day 5 | TMDB_LSA |
| Day 6 | code-weavers |
| Day 7 | py_visualer |
| Day 8 | Chat-With-Cat-v2.1 |
| Day 9 | Chat_With_Cat-v2.0- |
| Day 10 | Chat_With_Cat |
| Day 11 | ai-chat-web-crawler |
| Day 12 | fraud-detection-system |
| Day 13 | Exposed |
| Day 14 | imdb-list-injector |
| Day 15 | quietude |
| Day 16 | aletheia |
| Day 17 | PeerChat |
| Day 18 | Vision-Mouse |
| Day 19 | Personality-Decoder |
| Day 20 | glassedit-pro |
| Day 21 | unified-library |
| Day 22 | RainbowLab |
| Day 23 | SecureStego |

---

## Troubleshooting

**Workflow fails with 401 Unauthorized**
→ Your `TARGET_GH_TOKEN` is wrong or expired. Regenerate it on Mr-Jackal account.

**Repo already exists error**
→ The script handles this automatically and force pushes anyway.

**uploaded.txt not updating**
→ Check that `WORKFLOW_TOKEN` secret is set correctly (Step 3).

**Want to re-upload a repo**
→ Simply remove its name from `uploaded.txt` and run the workflow manually.
