# 💶 The Receivables Ledger — AR Dashboard

一个本地运行的、editorial 风格的应收账款（AR）追款 dashboard。
读取你自己的 SharePoint 上的 Master Report Excel，计算优先级、追账客户排名、FC Month 收款率等关键指标。

> **All computation runs locally in your browser — no data leaves your machine.**

📖 **在线用户指南 (一页 slide):** [guide.html](https://camille1223.github.io/money-money-wanna-money/guide.html)
*(GitHub Pages 启用后生效，见仓库 Settings → Pages)*

---

## 📑 目录
1. [前置条件](#1--前置条件)
2. [安装](#2--安装)
3. [第一次配置](#3--第一次配置)
4. [日常使用](#4--日常使用)
5. [关键指标说明](#5--关键指标说明)
6. [故障排查](#6--故障排查)
7. [文件结构](#7--文件结构)
8. [数据安全](#8--数据安全)
9. [给 fork 这个 repo 的人](#9--给-fork-这个-repo-的人)

---

## 1 · 前置条件

在使用之前，确认你机器上有这些：

### 1.1 Python 3.10+
打开 PowerShell 输入 `python --version`，看到 `Python 3.10.x` 或更高即可。
没装的话从 [python.org/downloads](https://www.python.org/downloads/) 下载，**安装时务必勾选 "Add Python to PATH"**。

### 1.2 sap-mcp（用于读 SharePoint）
Dashboard 通过 Microsoft Graph 拉取 SharePoint 文件，token 来自 sap-mcp 在你登录后写的 `~/.sap-mcp/auth.json`。

确认方法：在 Claude Code 里随便用一次 Outlook / Teams MCP 工具（比如 `outlook_mail_summary` 或 `teams_web_my_profile`），完成登录流程。如果 `C:\Users\<你>\.sap-mcp\auth.json` 存在就 OK。

> Token 大约每小时刷新一次，平时跑任何 sap-mcp 工具都会自动续期。如果 dashboard 报 "no Graph token"，到 Claude Code 里跑一下任意 Teams/Outlook 工具就行。

### 1.3 你自己的 SharePoint Master Report 链接
在 SharePoint 里找到它：
1. 打开你那份 `Master Report_GC_ YYYYMM_<YourName>.xlsx`
2. 点右上角 **Share** → **Copy link**
3. 链接形如 `https://sap.sharepoint.com/teams/.../Master%20Report_GC_%20...xlsx`

> 必须是**文件**链接，不是文件夹链接。

---

## 2 · 安装

### 选项 A：从 GitHub clone
```bash
git clone https://github.com/Camille1223/money-money-wanna-money.git
cd money-money-wanna-money
```

### 选项 B：下载 ZIP
仓库主页 → **Code** → **Download ZIP** → 解压到任意位置（比如 `C:\Users\<你>\Documents\AR_Dashboard`）。

然后双击 `AR_Dashboard.bat` 启动。

第一次启动会：
- 端口 8765 起静态服务（serving HTML）
- 端口 8766 起 sync 服务（拉 SharePoint）
- 浏览器自动打开 `http://localhost:8765/index.html`

> 如果想要桌面图标，在 PowerShell 里跑 `powershell -ExecutionPolicy Bypass -File make_shortcut.ps1`，会在桌面创建一个 € 图标的快捷方式。

---

## 3 · 第一次配置

浏览器打开后会显示 "Awaiting the Ledger"。

1. 点右上角 **⚙ Source**
2. 把你 SharePoint 文件链接粘进去
3. 点 **Save & Sync**
4. 等几秒，dashboard 自动加载你的数据

链接保存在本地 `config.json`，下次启动直接用，不需要再设置。

> 需要快速参考？打开 [`guide.html`](./guide.html) — 一页 slide 涵盖前置条件 + 4 步安装 + 日常使用，可以打印或截图发给同事。

---

## 4 · 日常使用

- **⟲ Sync Now** — 立即从 SharePoint 拉最新版本
- **↧ Pull Latest** — 加载已同步到本地的 Excel（不重新下载）
- **⌘ Load / Refresh Excel** — 手动从本机选一个 .xlsx（绕过 SharePoint）
- **⚙ Source** — 改 SharePoint 链接（比如月份变了）

后台 sync 服务每分钟自动拉一次最新版。Dashboard 关掉浏览器无所谓，bat 命令行窗口关掉就停了。

### 月份变更时（每月初）
SharePoint 上的文件夹会从 `202606` 换成 `202607`，文件名也会换。
**只需点 ⚙ Source，把链接里的月份替换一下、保存即可。**

---

## 5 · 关键指标说明

- **Priority** = `Open EUR × (1 + OD天数 / 30)` —— 综合金额和逾期严重程度的追账优先级。[完整公式解读 →](./PRIORITY.md)
- **FC Recovery** = 当月 FC Month 已收款 / 总开单
- **Max OD** = 该客户所有未付单据中最大的逾期天数

点表格任意一行可打开 dossier drawer，看该客户的所有未付/已付单据明细。

---

## 6 · 故障排查

| 现象 | 原因 / 解决 |
|---|---|
| 启动时浏览器打不开 | 端口 8765 被占。先关掉占用进程，或改 `AR_Dashboard.bat` 里的 `set PORT=` |
| ⚙ Source 报 "确认 sync 服务在 :8766 运行" | sync 服务没起来。查 cmd 窗口里有没有 Python 报错 |
| "no Graph token" / "shares lookup failed (401)" | sap-mcp 的 token 过期了。在 Claude Code 里随便跑一个 Outlook/Teams 工具触发刷新 |
| "shares lookup failed (403)" | 你对那个 SharePoint 文件没有读权限。确认链接对不对、是不是你自己 collector 的文件 |
| 数据没更新 | 点 ⟲ Sync Now 强制拉一次；或检查 SharePoint 上文件的 lastModified 是否真的变了 |

---

## 7 · 文件结构

```
money-money-wanna-money/
├── AR_Dashboard.bat        启动入口（双击）
├── index.html              所有前端（HTML / CSS / JS / 图表 / 表格）
├── guide.html              一页 slide 形式的用户指南
├── sync_sharepoint.py      后台 sync 服务（Graph API + HTTP API）
├── make_icon.py            生成 euro.ico（已生成，不需重跑）
├── make_shortcut.ps1       生成桌面快捷方式
├── euro.ico                € 图标
├── money_bag.ico           备用图标
├── README.md               本文档
├── .gitignore              排除运行时数据
│
│   ── 以下 4 个不在 repo 里，运行时会自动生成在你本机 ──
├── config.json             [自动生成] 你的 SharePoint 链接
├── current.xlsx            [自动同步] 最新版数据
├── current.meta.json       [自动生成] 同步元数据
└── *.log                   [自动生成] 运行日志
```

`config.json` / `current.xlsx` / `current.meta.json` / `*.log` 都是运行时产物，**不要 commit / 不要分享**。`.gitignore` 已经帮你挡住了。

---

## 8 · 数据安全

- 所有 Excel 解析、KPI 计算都在浏览器里跑（用的是 `xlsx.full.min.js`），数据不上传任何服务器
- SharePoint 同步走 Microsoft Graph 官方 API，token 是你本机已登录的 SAP 身份
- 本地 8765 / 8766 端口仅监听 `127.0.0.1`（localhost），不对外暴露
- 不要把自己的 `current.xlsx` 或 `config.json` 通过共享盘 / 截图发给别人——这是你账上的客户应收数据
- 这个 repo 里**没有**任何真实客户数据；每个使用者用自己的 SharePoint 链接生成自己那份

---

## 9 · 给 fork 这个 repo 的人

这是一个 **per-user, local-only** 的工具。fork 之后：

1. 每个人配置自己的 SharePoint 链接 → 看到自己的客户数据
2. 仓库里的代码每个人都一样，layout / KPI 计算逻辑统一
3. 想自定义 KPI 公式或新增图表？改 `index.html` 即可，所有逻辑都在这一个文件里
4. PR / Issue 欢迎，但请确保截图里**没有真实客户名 / 金额**

---

*Made with 💶 for AR collectors. All your collections in one ledger.*
