# Vercel Deployment Guide for SimpleDB with Supabase

This guide explains how to deploy your SimpleDB RDBMS application to Vercel with Supabase PostgreSQL backend.

## Prerequisites

- Vercel account
- Supabase project with PostgreSQL database
- GitHub repository with your code

## Environment Variables

You need to configure the following environment variables in your Vercel project settings:

### Required Variables

```bash
# Supabase Configuration
# Copy this file to .env.local and fill in your actual values

# Supabase URL
SUPABASE_URL=your_supabase_url_here

# Supabase Keys
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# PostgreSQL Connection
POSTGRES_HOST=your_postgres_host_here
POSTGRES_DATABASE=postgres
POSTGRES_USER=your_postgres_user_here
POSTGRES_PASSWORD=your_postgres_password_here
POSTGRES_PORT=5432

# Direct PostgreSQL URL (non-pooling for better compatibility)
DATABASE_URL=your_database_url_here

```

## Deployment Steps

### 1. Push Code to GitHub

```bash
git add .
git commit -m "Add Supabase integration for persistent storage"
git push origin main
```

### 2. Import Project to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository
4. Vercel will auto-detect the Python/Flask project

### 3. Configure Environment Variables

In the Vercel project settings:

1. Go to **Settings** → **Environment Variables**
2. Add each variable from the list above:
   - Variable name (e.g., `DATABASE_URL`)
   - Value (paste the corresponding value)
   - Select all environments (Production, Preview, Development)
3. Click "Save"

### 4. Deploy

1. Click "Deploy" button
2. Vercel will build and deploy your application
3. Once deployed, you'll get a URL like `https://your-project.vercel.app`

## Verifying Deployment

After deployment:

1. Visit your Vercel URL
2. The web app should load with the task management interface
3. Try creating a task - it should persist in Supabase
4. Check your Supabase dashboard to see the data in PostgreSQL

## Local Development

To run locally with Supabase:

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run the Flask app
python3 webapp/app.py
```

The app will load environment variables from `.env.local` automatically.

## Troubleshooting

### Connection Errors

If you see database connection errors:

1. Verify `DATABASE_URL` is correctly set in Vercel
2. Check that your Supabase project is active
3. Ensure the connection string uses the non-pooling URL for better compatibility

### Table Not Found Errors

The application automatically creates the `tasks` table on first run. If you see table errors:

1. Check Supabase dashboard → SQL Editor
2. Verify the `_simpledb_schemas` metadata table exists
3. Manually create tables if needed using the REPL

### Build Failures

If Vercel build fails:

1. Check that `requirements.txt` includes all dependencies
2. Verify `vercel.json` configuration is correct
3. Check build logs in Vercel dashboard

## Architecture

- **Frontend**: Flask templates + vanilla JavaScript
- **Backend**: Flask API with custom SQL executor
- **Storage**: Supabase PostgreSQL (managed)
- **Hosting**: Vercel serverless functions

## Security Notes

- Never commit `.env.local` to Git (it's in `.gitignore`)
- Use environment variables for all secrets
- The `SUPABASE_SERVICE_ROLE_KEY` has admin access - keep it secure
- For production, consider using more restrictive database roles
