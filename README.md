<div align="center">

# 💶 The Receivables Ledger
### AR Dashboard

*A locally-run, editorial-style accounts receivable collections dashboard.*
*本地运行的 editorial 风格应收账款追款 dashboard。*

[![Made for](https://img.shields.io/badge/made_for-AR_collectors-475E75?style=flat-square)](#)
[![Runs](https://img.shields.io/badge/runs-locally_in_browser-5B738B?style=flat-square)](#)
[![Source](https://img.shields.io/badge/data-your_SharePoint-8B5B5B?style=flat-square)](#)

**🌐 Full docs:** [English](./README_EN.md) · [中文](./README_CN.md) · [Single-slide guide](https://camille1223.github.io/money-money-wanna-money/guide.html)

</div>

---

<table>
<tr>
<th width="50%">🇬🇧 English</th>
<th width="50%">🇨🇳 中文</th>
</tr>
<tr>
<td valign="top">

### What it is
Reads your own SharePoint **Master Report Excel** and renders an editorial-style dashboard of priority scores, top-debtor rankings, FC Month recovery rates, and per-customer dossiers.

**All computation runs locally in your browser — no data ever leaves your machine.**

### Who it's for
AR collectors at SAP who want a faster way to triage their book without uploading anything.

### How it works
1. Local static server (`:8765`) serves `index.html`
2. Local sync service (`:8766`) pulls your `Master Report_GC_*.xlsx` from SharePoint via Microsoft Graph
3. Browser parses the Excel and renders KPIs / charts / tables — entirely client-side

### Key features
- 🎯 **Priority score** — `Open EUR × (1 + OD/30)` · [why this formula →](./PRIORITY.md)
- 📊 **FC Month recovery** — billed vs received per forecast month
- 📁 **Customer dossier** — open / paid invoice detail, merged by `Ref. document number`
- 📝 **Inline notes** — Status / AR Plan / Promised dates beneath each ref
- ⏱ **Auto-sync** — every minute in background
- 🎨 **Editorial aesthetic** — Playfair Display + IBM Plex Mono, no chart noise

### Quick start
```bash
git clone https://github.com/Camille1223/money-money-wanna-money.git
cd money-money-wanna-money
# Double-click AR_Dashboard.bat
```
Then click **⚙ Source**, paste your SharePoint link, **Save & Sync**.

📖 **Full docs →** [README_EN.md](./README_EN.md)

</td>
<td valign="top">

### 这是什么
读取你自己 SharePoint 上的 **Master Report Excel**，渲染成 editorial 风格的 dashboard——展示优先级评分、追账客户排名、FC Month 收款率，以及每家客户的 dossier。

**所有计算都在你的浏览器本地运行 — 数据不会离开你的电脑。**

### 适合谁用
SAP 内部 AR collector，想要一个不用上传任何数据、快速 triage 自己 book 的工具。

### 工作原理
1. 本地静态服务器（`:8765`）提供 `index.html`
2. 本地 sync 服务（`:8766`）通过 Microsoft Graph 从 SharePoint 拉取 `Master Report_GC_*.xlsx`
3. 浏览器解析 Excel，渲染 KPI / 图表 / 表格 — 全部客户端运行

### 核心功能
- 🎯 **优先级评分** — `Open EUR × (1 + OD/30)` · [公式解读 →](./PRIORITY.md)
- 📊 **FC Month 收款率** — 每个预测月的开单 vs 收款
- 📁 **客户 dossier** — 未付/已付单据明细，按 `Ref. document number` 合并
- 📝 **内联备注** — Status / AR Plan / Promised 日期挂在每条 ref 下方
- ⏱ **自动同步** — 后台每分钟拉一次
- 🎨 **editorial 美学** — Playfair Display + IBM Plex Mono，去除图表噪声

### 快速开始
```bash
git clone https://github.com/Camille1223/money-money-wanna-money.git
cd money-money-wanna-money
# 双击 AR_Dashboard.bat
```
然后点 **⚙ Source**，粘贴你的 SharePoint 链接，**Save & Sync**。

📖 **完整文档 →** [README_CN.md](./README_CN.md)

</td>
</tr>
</table>

---

## 🔑 Prerequisites · 前置条件

| | English | 中文 |
|---|---|---|
| **Python 3.10+** | `python --version` ≥ 3.10. Tick "Add Python to PATH" when installing | `python --version` ≥ 3.10。安装时勾选 "Add Python to PATH" |
| **sap-mcp** | Run any Outlook/Teams MCP tool once in Claude Code so `~/.sap-mcp/auth.json` exists | 在 Claude Code 里跑一次 Outlook/Teams MCP 工具，让 `~/.sap-mcp/auth.json` 存在 |
| **SharePoint link** | A **file** link to your own `Master Report_GC_*.xlsx`, not a folder link | 指向你自己 `Master Report_GC_*.xlsx` 的**文件**链接，不是文件夹链接 |

---

## 🚀 Setup in 4 steps · 4 步配置

| | Step | English | 中文 |
|---|---|---|---|
| **1** | Get the code | Clone the repo, or download ZIP | clone 仓库，或下载 ZIP |
| **2** | Launch | Double-click `AR_Dashboard.bat` | 双击 `AR_Dashboard.bat` |
| **3** | Configure | Click **⚙ Source**, paste your SharePoint link | 点 **⚙ Source**，粘贴 SharePoint 链接 |
| **4** | Save & sync | Click **Save & Sync**, wait a few seconds | 点 **Save & Sync**，等几秒 |

---

## 📂 What's in this repo · 仓库结构

```
money-money-wanna-money/
├── AR_Dashboard.bat       Launch · 启动入口
├── index.html             All frontend (single file) · 所有前端（单文件）
├── guide.html             Single-slide user guide · 单页指南
├── sync_sharepoint.py     SharePoint sync service · SharePoint 同步服务
├── make_icon.py           Icon generator · 图标生成器
├── make_shortcut.ps1      Desktop shortcut · 桌面快捷方式
├── euro.ico               € icon · 图标
├── README.md              This file · 当前文件
├── README_EN.md           Full English docs · 英文完整文档
├── README_CN.md           Full Chinese docs · 中文完整文档
└── .gitignore             Excludes runtime data · 排除运行时数据
```

> Runtime files (`config.json`, `current.xlsx`, `current.meta.json`, `*.log`) are auto-generated on your machine and **never committed** — they contain real customer data.
>
> 运行时文件（`config.json`, `current.xlsx`, `current.meta.json`, `*.log`）在你本机自动生成，**绝不 commit** —— 里面是真实客户数据。

---

## 🔒 Data security · 数据安全

| English | 中文 |
|---|---|
| All Excel parsing & KPI computation runs in the browser (`xlsx.full.min.js`) | 所有 Excel 解析、KPI 计算都在浏览器里跑（`xlsx.full.min.js`） |
| SharePoint sync uses Microsoft Graph official API with your own SAP identity | SharePoint 同步走 Microsoft Graph 官方 API，用你本机的 SAP 身份 |
| Local ports `8765` / `8766` listen on `127.0.0.1` only — not exposed | 本地 `8765` / `8766` 端口只监听 `127.0.0.1`，不对外暴露 |
| This repo contains **zero** real customer data | 仓库里**没有**任何真实客户数据 |
| Don't share `current.xlsx` / `config.json` — that's your customers' AR | 不要分享 `current.xlsx` / `config.json` —— 这是你客户的应收数据 |

---

## 🤝 For forks & contributors · 给 fork 与贡献者

This is a **per-user, local-only** tool. 这是一个 **per-user, local-only** 工具。

- Each fork user configures their own SharePoint link → sees their own data
  每个 fork 用户配置自己的 SharePoint 链接 → 看到自己的数据
- All KPI / chart / layout logic lives in `index.html` — single file, easy to fork
  所有 KPI / 图表 / 布局逻辑都在 `index.html` —— 单文件，方便 fork
- PRs / Issues welcome — but please ensure screenshots contain **no real customer names / amounts**
  欢迎 PR / Issue —— 但请确保截图里**没有真实客户名 / 金额**

---

<div align="center">

*Made with 💶 for AR collectors. All your collections in one ledger.*
*为 AR collector 而做。所有追账，一本账册。*

**[📖 English docs](./README_EN.md) · [📖 中文文档](./README_CN.md) · [🎯 Single-slide guide](https://camille1223.github.io/money-money-wanna-money/guide.html)**

</div>
