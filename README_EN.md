# 💶 The Receivables Ledger — AR Dashboard

> **🌐 Language:** **English** · [中文](./README_CN.md)

A locally-run, editorial-style accounts receivable (AR) collections dashboard.
Reads your own SharePoint Master Report Excel and computes priority scores, top-debtor rankings, FC Month recovery rates, and other key collections KPIs.

> **All computation runs locally in your browser — no data ever leaves your machine.**

📖 **Online user guide (single slide):** [guide.html](https://camille1223.github.io/money-money-wanna-money/guide.html)
*(Available once GitHub Pages is enabled — see repo Settings → Pages)*

---

## 📑 Table of contents
1. [Prerequisites](#1--prerequisites)
2. [Install](#2--install)
3. [First-time setup](#3--first-time-setup)
4. [Daily use](#4--daily-use)
5. [Key metrics](#5--key-metrics)
6. [Troubleshooting](#6--troubleshooting)
7. [Project layout](#7--project-layout)
8. [Data security](#8--data-security)
9. [For people forking this repo](#9--for-people-forking-this-repo)

---

## 1 · Prerequisites

Before you start, make sure your machine has:

### 1.1 Python 3.10+
Open PowerShell and run `python --version`. You should see `Python 3.10.x` or higher.
If not, install from [python.org/downloads](https://www.python.org/downloads/) — **make sure to tick "Add Python to PATH"** during install.

### 1.2 sap-mcp (for SharePoint access)
The dashboard pulls SharePoint files via Microsoft Graph. The token comes from sap-mcp, which writes `~/.sap-mcp/auth.json` after you log in.

To verify: in Claude Code, run any Outlook / Teams MCP tool (e.g. `outlook_mail_summary` or `teams_web_my_profile`) once and complete the login flow. You're good if `C:\Users\<you>\.sap-mcp\auth.json` exists.

> The token refreshes roughly hourly — any sap-mcp tool call renews it. If the dashboard reports "no Graph token", just trigger any Outlook/Teams tool in Claude Code.

### 1.3 Your own SharePoint Master Report link
Find it in SharePoint:
1. Open your `Master Report_GC_ YYYYMM_<YourName>.xlsx`
2. Click **Share** (top right) → **Copy link**
3. The URL looks like `https://sap.sharepoint.com/teams/.../Master%20Report_GC_%20...xlsx`

> Must be a **file** link, not a folder link.

---

## 2 · Install

### Option A: Clone from GitHub
```bash
git clone https://github.com/Camille1223/money-money-wanna-money.git
cd money-money-wanna-money
```

### Option B: Download ZIP
Repo home → **Code** → **Download ZIP** → unzip anywhere (e.g. `C:\Users\<you>\Documents\AR_Dashboard`).

Then double-click `AR_Dashboard.bat` to launch.

The first launch will:
- Start a static server on port 8765 (serves the HTML)
- Start a sync service on port 8766 (pulls from SharePoint)
- Open `http://localhost:8765/index.html` in your browser automatically

> Want a desktop shortcut? Run `powershell -ExecutionPolicy Bypass -File make_shortcut.ps1` — it creates a € icon on your desktop.

---

## 3 · First-time setup

Once the browser opens you'll see "Awaiting the Ledger".

1. Click **⚙ Source** (top right)
2. Paste your SharePoint file link
3. Click **Save & Sync**
4. Wait a few seconds — the dashboard loads your data

The link is saved in a local `config.json` and re-used on next launch.

> Need a quick reference? Open [`guide.html`](./guide.html) — a single-slide overview covering prerequisites + 4-step setup + daily use, printable or screenshot-friendly to share with colleagues.

---

## 4 · Daily use

- **⟲ Sync Now** — pull the latest version from SharePoint right now
- **↧ Pull Latest** — load the already-synced local Excel (no re-download)
- **⌘ Load / Refresh Excel** — pick an `.xlsx` from your machine manually (bypasses SharePoint)
- **⚙ Source** — change the SharePoint link (e.g. when the month rolls over)

The background sync service auto-pulls every 10 minutes. Closing the browser is fine; the dashboard only stops when you close the bat command window.

### When the month changes (start of each month)
The SharePoint folder name flips from `202606` to `202607`, and the file name changes too.
**Just open ⚙ Source, replace the month in the link, and save.**

---

## 5 · Key metrics

- **Priority** = `Open EUR × (1 + OD days / 30)` — combined weight of amount and overdue severity
- **FC Recovery** = current FC Month received / total billed
- **Max OD** = the largest overdue-day count among that customer's open invoices

Click any row in the customer table to open a dossier drawer with that customer's full open / paid invoice detail. Documents with the same `Ref. document number` are merged into one row, with the EUR column summed across the group. Status / AR Plan / Promised notes sit inline beneath each merged ref.

---

## 6 · Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| Browser doesn't open on launch | Port 8765 is taken. Kill the offending process or change `set PORT=` in `AR_Dashboard.bat` |
| ⚙ Source says "make sure sync service is running on :8766" | Sync service didn't start. Check the cmd window for Python errors |
| "no Graph token" / "shares lookup failed (401)" | sap-mcp token expired. Trigger any Outlook/Teams tool in Claude Code to refresh it |
| "shares lookup failed (403)" | You don't have read access to that SharePoint file. Verify the link belongs to your own collector account |
| Data not updating | Click ⟲ Sync Now to force-pull; or check whether the SharePoint file's lastModified actually changed |

---

## 7 · Project layout

```
money-money-wanna-money/
├── AR_Dashboard.bat        Launch entry point (double-click)
├── index.html              All frontend (HTML / CSS / JS / charts / tables)
├── guide.html              Single-slide user guide
├── sync_sharepoint.py      Background sync service (Graph API + HTTP API)
├── make_icon.py            Generates euro.ico (already generated, no need to rerun)
├── make_shortcut.ps1       Creates desktop shortcut
├── euro.ico                € icon
├── money_bag.ico           Backup icon
├── README.md               Bilingual landing
├── README_EN.md            English README (this file)
├── README_CN.md            Chinese README
├── .gitignore              Excludes runtime artifacts
│
│   ── The 4 below are NOT in the repo — auto-generated locally at runtime ──
├── config.json             [auto] your SharePoint link
├── current.xlsx            [auto-synced] latest data
├── current.meta.json       [auto] sync metadata
└── *.log                   [auto] runtime logs
```

`config.json` / `current.xlsx` / `current.meta.json` / `*.log` are runtime artifacts — **do not commit, do not share**. `.gitignore` already excludes them.

---

## 8 · Data security

- All Excel parsing and KPI computation runs in the browser (via `xlsx.full.min.js`); data is never uploaded to any server
- SharePoint sync uses Microsoft Graph's official API; the token is your own logged-in SAP identity on this machine
- Local ports 8765 / 8766 only listen on `127.0.0.1` (localhost) — not exposed externally
- Don't share your `current.xlsx` or `config.json` via shared drives or screenshots — that's your customers' real AR data
- This repo contains **zero** real customer data; each user generates their own from their own SharePoint link

---

## 9 · For people forking this repo

This is a **per-user, local-only** tool. After forking:

1. Each person configures their own SharePoint link → sees their own customer data
2. The repo code is identical for everyone — layout / KPI logic is shared
3. Want to customize a KPI formula or add a chart? Edit `index.html` — all logic lives in that one file
4. PRs / Issues welcome, but please make sure screenshots contain **no real customer names / amounts**

---

*Made with 💶 for AR collectors. All your collections in one ledger.*
