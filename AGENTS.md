# AGENTS.md - Prenatal Control System

## Essential Commands
- **Run dev server**: `python web/run.py` (app at http://localhost:5000)
- **Install deps**: `pip install -r requirements.txt`
- **Setup DB**: Manually execute `script.sql` in Supabase SQL editor
- **Env vars**: Create `.env` with `SUPABASE_URL`, `SUPABASE_KEY`, and `SECRET_KEY` (no `.env.example`)
- **Activate venv**: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)

## Project Structure
- `web/` - Flask app
  - `controllers/` - Blueprint route handlers
    - `auth.py` - `/auth` prefix
    - `dashboard.py` - `/dashboard` prefix
    - `pacientes.py`, `citas.py`, `inasistencias.py`, `censo.py`, `reportes.py` - all under `/gestion` prefix
  - `models/` - Database models (Pydantic for validation)
  - `services/` - Business logic
  - `templates/` - Jinja2 HTML templates
  - `static/` - CSS, JS, images
  - `utils/` - Utility functions
  - `config.py` - App configuration (loads SECRET_KEY from env)
  - `init.py` - App factory (`create_app()`)
  - `run.py` - Entrypoint
- `script.sql` - Supabase database schema

## Key Notes
- No automated tests - manual browser testing only
- Uses Flask blueprints for route organization
- Supabase PostgreSQL via `supabase` Python package
- SECRET_KEY required in `.env` for Flask sessions (fallback to "dev_secret_key" in config)
- Follow existing patterns in controllers when adding new features