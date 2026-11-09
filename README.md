# WhatsApp AI Agent

A starter WhatsApp automation project with a Flask webhook, rule-based auto-replies, SQLite message storage, and a responsive dashboard.

## Important: GitHub Pages cannot run Python

Use GitHub to store your code and host the static dashboard. Deploy the Python backend separately (Render is configured as an example). The WhatsApp Cloud API also requires a Meta developer app and approved WhatsApp Business Platform setup.

## Project structure

```text
whatsapp-ai-agent/
├── app.py                 # Flask API + Meta webhook
├── bot.py                 # Auto-reply rules + WhatsApp send function
├── database.py            # SQLite operations
├── schema.sql             # Database schema
├── requirements.txt
├── Procfile
├── render.yaml
├── .env.example
└── static/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

## 1. Run locally

Install Python 3.11+ and then:

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env`, fill in your Meta credentials, and run:

```bash
python app.py
```

Open `http://localhost:5000`.

## 2. Configure Meta WhatsApp Cloud API

1. Create an app at the Meta for Developers website.
2. Add the WhatsApp product and complete the WhatsApp Business Platform setup.
3. Get the Phone Number ID and a valid access token from the WhatsApp API setup.
4. Set these backend environment variables:
   - `WHATSAPP_ACCESS_TOKEN`
   - `WHATSAPP_PHONE_NUMBER_ID`
   - `WHATSAPP_VERIFY_TOKEN` (a secret string you choose)
   - `META_APP_SECRET` (from your Meta app settings)
   - `DASHBOARD_API_KEY` (another secret string you choose)
5. Set the webhook callback URL to `https://YOUR-BACKEND-DOMAIN/webhook`.
6. Enter the same `WHATSAPP_VERIFY_TOKEN` in Meta's webhook verification form.
7. Subscribe the webhook to the `messages` field.

Use Meta's test number and test recipient first. Follow WhatsApp's current opt-in, template, messaging-window, and business policies. Do not message people who have not agreed to receive messages.

## 3. Deploy the Python backend on Render

1. Push this folder to a new GitHub repository.
2. In Render, choose **New → Blueprint** and connect the repository.
3. Render reads `render.yaml`. Add the secret environment variables listed above.
4. Deploy and copy your backend URL, for example `https://your-service.onrender.com`.
5. Open `static/config.js` and replace `https://YOUR-BACKEND-URL.onrender.com` with your actual backend URL.
6. Set `CORS_ORIGINS` to your GitHub Pages origin, for example `https://YOUR-USERNAME.github.io` (or the exact repository Pages URL if using a project site), then redeploy.

**Database note:** SQLite is suitable for a starter/demo. On free or ephemeral hosting, local files may be reset when the service restarts or redeploys. For durable production message history, use managed PostgreSQL or a persistent disk.

## 4. Publish the dashboard with GitHub Pages

1. In GitHub, open the repository **Settings → Pages**.
2. Under Build and deployment, choose **Deploy from a branch**.
3. Select `main` and `/ (root)` if you keep the files at the repository root.
4. Save and wait for the Pages URL.
5. If you use a project site, set `CORS_ORIGINS` to the exact Pages URL, such as `https://YOUR-USERNAME.github.io/REPOSITORY-NAME`.
6. Open the published site and click **Set dashboard key**. Enter the value of `DASHBOARD_API_KEY` from Render.

## 5. Customize auto-replies

Edit `create_reply()` in `bot.py`. Add your own keywords and response text. Keep replies accurate and provide a way for customers to reach a human when needed.

## Security checklist

- Never upload `.env`, access tokens, app secrets, or real customer data to GitHub.
- Keep `META_APP_SECRET` configured so webhook signatures are checked.
- Use a strong `DASHBOARD_API_KEY`.
- Restrict `CORS_ORIGINS` to your actual dashboard domain.
- Use a persistent production database for important conversations.
- Obtain user consent and follow WhatsApp policies and applicable privacy laws.

## Current starter capabilities

- Receives incoming WhatsApp text messages through a Meta webhook.
- Sends simple keyword-based automatic replies.
- Saves inbound and outbound messages to SQLite.
- Displays recent messages in a protected dashboard.
- Includes a health-check endpoint at `/api/health`.

This is a starter integration, not a fully autonomous AI model. You can later connect an LLM provider in `bot.py` after adding appropriate API credentials and safety controls.
