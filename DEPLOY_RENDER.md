# Deploying to Render

Follow these steps to deploy the RDBMS project to [Render](https://render.com).

### 1. Create a Web Service
- Sign in to your Render dashboard.
- Click **New +** and select **Web Service**.
- Connect your GitHub repository.

### 2. Configure Build and Start Commands
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn webapp.app:app`

### 3. Environment Variables
Add the following environment variables in the **Environment** tab:
- `DATABASE_URL`: Your Supabase PostgreSQL connection string (or use `POSTGRES_URL`).
- `PYTHON_VERSION`: `3.12.0` (optional if using `runtime.txt`).

### 4. Deploy
Render will automatically build and deploy your app. Once finished, your site will be live at the provided `.onrender.com` URL.
