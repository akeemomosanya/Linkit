# LinkIt
LinkIT allows to easily save and retrieve links/urls from around the web

## Before
A broken FastAPI project with unfinished endpoints, wrong relationship references and no frontend.

## After
- Full auth flow (register, login, JWT)
- Link management (save, search, edit, copy, delete)
- Frontend (landing page, auth, dashboard)

## Stack
- **Backend:** FastAPI, SQLAlchemy, PyJWT, passlib
- **Frontend:** Vanilla HTML/CSS/JS
- **DB:** Postgresgl

## Run locally
After cloning the repository
cd backend && uvicorn main:app --reload
# open frontend/Index.html in your browser