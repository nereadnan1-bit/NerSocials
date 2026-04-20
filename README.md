# Personal Portfolio with Admin Blog

A modern portfolio site with an admin panel for managing blog posts. Authentication is handled via Supabase Email OTP.

## Features
- Email OTP login (no passwords)
- Admin dashboard for creating/editing/deleting blog posts
- Public blog listing with markdown support
- Responsive design

## Tech Stack
- **Backend**: Flask, Supabase
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Render

## Setup Locally
1. Clone the repo
2. `cd backend && python -m venv venv && source venv/bin/activate`
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your Supabase credentials
5. Run `flask run` from the backend directory
6. Serve the frontend folder with a static server (e.g., `python -m http.server 8000` in `frontend/`)

## Environment Variables
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SECRET_KEY` (for Flask session)