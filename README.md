# 🤖 Uptime Keeper

[![Keep Bot Alive](https://github.com/Sandeepchch/uptime-keeper/actions/workflows/keep_alive.yml/badge.svg)](https://github.com/Sandeepchch/uptime-keeper/actions/workflows/keep_alive.yml)

> A **self-healing automation system** that keeps your Render free-tier services alive using GitHub Actions.

---

## 🧩 The Problem

Render's free tier **spins down** your server after **15 minutes of inactivity**. This means your Telegram Bot (or any other service) goes offline until the next request wakes it up — causing delays and missed messages.

## 💡 The Solution

This project uses a **GitHub Actions cron job** to ping your Render service URL every **3 hours**, preventing the server from ever going idle. It's completely free, serverless, and requires zero maintenance.

---

## 🏗️ Architecture

```
┌─────────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│   GitHub Actions     │       │   main.py         │       │   Render Server  │
│   (Cron: */3 hrs)    │──────▶│   (Ping Script)   │──────▶│   (Your Bot)     │
│                      │       │   + Retry Logic   │       │                  │
│   ┌──────────────┐   │       │   + Logging       │       │   Stays Alive!   │
│   │ RENDER_URL   │───┘       └──────────────────┘       └─────────────────┘
│   │ (Secret)     │
│   └──────────────┘
└─────────────────────┘
```

---

## 📁 Project Structure

```
uptime-keeper/
├── .github/
│   └── workflows/
│       └── keep_alive.yml    # GitHub Actions workflow (cron + manual trigger)
├── main.py                   # Python ping script with retry & logging
├── requirements.txt          # Python dependencies
└── README.md                 # You are here!
```

---

## 🚀 Quick Setup

### 1. Fork or Clone

```bash
git clone https://github.com/Sandeepchch/uptime-keeper.git
```

### 2. Add Your Render URL as a GitHub Secret

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Set:
   - **Name:** `RENDER_URL`
   - **Value:** Your Render service URL (e.g., `https://my-bot.onrender.com`)
5. Click **"Add secret"**

### 3. Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. The workflow will automatically run every 3 hours

### 4. Test It (Optional)

1. Go to **Actions** → **🤖 Keep Bot Alive**
2. Click **"Run workflow"** → **"Run workflow"**
3. Watch the logs to confirm it's working ✅

---

## 🔐 How Security Works

| Layer | Implementation |
|-------|---------------|
| **Secret Storage** | Render URL stored in GitHub Secrets (encrypted at rest) |
| **Runtime Injection** | Secret injected as environment variable only during workflow execution |
| **Code Security** | URL is **never** hardcoded in any file |
| **Permissions** | Workflow runs with minimal `read` permissions |
| **Visibility** | Secret values are masked in logs automatically by GitHub |

---

## 🔧 Configuration

You can customize the behavior by editing these constants in `main.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_RETRIES` | `3` | Number of ping attempts before giving up |
| `INITIAL_BACKOFF_SECONDS` | `5` | Initial wait time between retries (doubles each attempt) |
| `REQUEST_TIMEOUT_SECONDS` | `60` | Maximum time to wait for a response |

To change the schedule, edit the cron expression in `.github/workflows/keep_alive.yml`:

```yaml
schedule:
  - cron: "0 */3 * * *"   # Every 3 hours (default)
  # - cron: "*/30 * * * *"  # Every 30 minutes (uses more quota)
  # - cron: "0 */6 * * *"   # Every 6 hours (more conservative)
```

---

## 📊 Reading the Logs

Go to **Actions** → click any workflow run to see logs like:

```
2026-02-18 10:00:00 | INFO     | ═══════════════════════════════════════════════════════
2026-02-18 10:00:00 | INFO     | 🚀  Uptime Keeper  |  Run started at 2026-02-18 10:00:00 UTC
2026-02-18 10:00:00 | INFO     | ═══════════════════════════════════════════════════════
2026-02-18 10:00:00 | INFO     | Attempt 1/3 — Pinging: https://my-bot.onrender.com
2026-02-18 10:00:02 | INFO     | ✅ Success | Status: 200 | Response Time: 2034 ms
2026-02-18 10:00:02 | INFO     | ═══════════════════════════════════════════════════════
2026-02-18 10:00:02 | INFO     | 🎉 Service is alive and responding!
2026-02-18 10:00:02 | INFO     | ═══════════════════════════════════════════════════════
```

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Workflow not running | Go to **Actions** tab and enable workflows if disabled |
| `RENDER_URL is not set` error | Add the secret in **Settings → Secrets → Actions** |
| All ping attempts fail | Verify your Render URL is correct and the service is deployed |
| Workflow runs but bot still sleeps | Check if the cron interval is too long; try `*/14 * * * *` |

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ to keep bots alive
</p>
