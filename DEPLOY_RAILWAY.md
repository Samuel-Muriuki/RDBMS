# Deploying to Railway

Follow these steps to deploy the RDBMS project to [Railway](https://railway.app).

### 1. Start a New Project
- Sign in to Railway.
- Click **New Project** -> **Deploy from GitHub repo**.
- Select your RDBMS repository.

### 2. Configure Service Settings
Railway usually auto-detects the `Procfile`.
- Ensure the **Start Command** is `gunicorn webapp.app:app`.
- **Port**: Set to `5000` (Railway often defaults to 8080 or detection, but our app prefers 5000 or the `$PORT` env var).
  > [!NOTE]
  > Gunicorn will automatically bind to the `$PORT` environment variable provided by Railway.

### 3. Environment Variables
Add your Supabase connection string:
- `DATABASE_URL`: Your connection string.

### 4. Deploy
Railway will trigger a build and deploy. You can view the live URL in the service dashboard.
