<div align="center">

#  CodeArc Backend

**Django REST API powering the CodeArc developer platform.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![Django](https://img.shields.io/badge/Django-4.x-092E20?style=flat-square&logo=django)](https://djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-REST_Framework-A30000?style=flat-square&logo=django)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org/)
[![License](https://img.shields.io/badge/License-Private-red?style=flat-square)](./LICENSE)

[Getting Started](#-getting-started) · [Architecture](#-architecture) · [Features](#-features) · [Auth Flow](#-authentication-flow) · [Deployment](#-deployment) · [Contributing](#-contributing)

</div>

---

## Overview

CodeArc Backend is the Django REST API service that powers the CodeArc platform. It handles user authentication (JWT + OAuth), profile management, OTP verification, and exposes a structured REST API consumed by the React frontend.

---

## Features

### Authentication & Authorization
- JWT access and refresh token lifecycle
- Google OAuth 2.0 login
- GitHub OAuth 2.0 login
- User registration with OTP email verification
- Forgot password and OTP-based reset flow

### API & Infrastructure
- RESTful API built with Django REST Framework
- PostgreSQL database
- Modular Django app structure for clean separation of concerns
- CORS, CSRF, and secret management via environment variables
- Deployment-ready configuration

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django 4.x |
| API Layer | Django REST Framework |
| Authentication | JWT + OAuth 2.0 (Google / GitHub) |
| Database | PostgreSQL |
| Runtime | Python 3.10+ |
| Deployment | Docker / Gunicorn + Nginx |

---

## Architecture

```
codearc-backend/
├── backend/                # Django project settings and root config
├── apps/
│   ├── auth_app/           # Authentication, OAuth, OTP, token management
│   └── user_app/           # User profiles and settings
├── manage.py
├── requirements.txt
├── .env                    # Environment secrets (never committed)
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites

- Python `>= 3.10`
- PostgreSQL (running locally or via Docker)
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/SREEJITH7/codearc-backend.git
cd codearc-backend
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Database
DB_NAME=codearc_db
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

> **Warning:** Never commit `.env` to version control. It is already listed in `.gitignore`.

### 5. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

The API will be available at **http://127.0.0.1:8000/**

---

## Authentication Flow

### JWT (Email / Password)
1. User submits credentials to the login endpoint
2. Backend validates and returns `access` + `refresh` tokens
3. Frontend attaches the `access` token to all subsequent requests
4. When the `access` token expires, the frontend calls the refresh endpoint to obtain a new one silently

### Google OAuth
1. Frontend redirects or opens a popup to Google's OAuth consent screen
2. Google redirects back to the backend callback URL with an auth code
3. Backend exchanges the code for user info and issues JWT tokens
4. User session is established — no separate login step required

### GitHub OAuth
Identical flow to Google OAuth above.

---

## API Reference

Key endpoints to verify during setup and testing:

| Flow | Method | Endpoint |
|---|---|---|
| Register | `POST` | `/api/auth/register/` |
| Login | `POST` | `/api/auth/login/` |
| OTP Verify | `POST` | `/api/auth/verify-otp/` |
| Token Refresh | `POST` | `/api/auth/token/refresh/` |
| Google OAuth | `POST` | `/api/auth/google/` |
| GitHub OAuth | `POST` | `/api/auth/github/` |
| Forgot Password | `POST` | `/api/auth/forgot-password/` |

These can be tested with [Postman](https://postman.com/) or any HTTP client.

---

## Scripts

| Command | Description |
|---|---|
| `python manage.py runserver` | Start development server |
| `python manage.py makemigrations` | Generate migration files |
| `python manage.py migrate` | Apply migrations to the database |
| `python manage.py createsuperuser` | Create a Django admin superuser |
| `python manage.py shell` | Open the Django interactive shell |

---

## Git Workflow

```
main
├── feature/auth-api
├── feature/user-api
└── feature/admin-api
```

**Process:** `feature branch` → Pull Request → Code Review → Merge to `main`

Use conventional commit messages:
```bash
git commit -m "feat(auth): implement GitHub OAuth callback handler"
git commit -m "fix(user): resolve profile update 400 error on empty fields"
```

---

## Deployment

The backend is ready for production deployment via the following stacks:

| Platform | Notes |
|---|---|
| Docker + Gunicorn + Nginx | Recommended for self-hosted VPS |
| [Render](https://render.com) | Simple Django deploys with managed PostgreSQL |
| [Railway](https://railway.app) | One-click deploys with env var management |
| [AWS EC2](https://aws.amazon.com/ec2/) / [DigitalOcean](https://digitalocean.com) | Full control, requires manual server setup |

Configure all `.env` variables in your hosting provider's environment settings before deploying.

---

## Contributing

1. Fork the repo and create a feature branch from `main`
2. Follow the existing app structure — new features belong in dedicated apps under `apps/`
3. Write descriptive commit messages using conventional format
4. Ensure migrations are included with any model changes
5. Open a Pull Request with a clear description of what changed and why

> This is a private/internal project. Please coordinate with the team before making significant architectural changes.

---

## License

**Private — Internal Use Only.**
Unauthorized distribution or use outside the CodeArc organization is not permitted.

---

<div align="center">
Built with ❤️ by the CodeArc team
</div>
