# codearc-backend
codearc backend


🚀 CodeArc Backend — Django REST API

This is the backend service for CodeArc, built using Django + Django REST Framework.
It handles user authentication, authorization, profile management, admin modules, and integrations such as Google OAuth and GitHub OAuth.

📌 Features

🔐 JWT Authentication (Access + Refresh Tokens)

🔑 Google Login (OAuth 2.0)

🐙 GitHub Login (OAuth 2.0)

👤 User registration, login, OTP verification

📧 Forgot Password + OTP Reset

🛠 Modular Django app structure

🗄 PostgreSQL database

📡 REST API with Django REST Framework

🔒 Security best practices (CORS, CSRF, env secrets, etc.)

📂 Project Structure
codearc-backend/
│── backend/                # Django project
│── apps/
│   ├── auth_app/           # Authentication + OAuth + OTP
│   ├── user_app/           # User profile, settings
│── venv/                   # Virtual environment (ignored)
│── manage.py
│── requirements.txt
│── .env                    # Environment variables (ignored)
│── .gitignore
└── README.md

⚙️ Tech Stack
Component	Technology
Backend Framework	Django 4.x
API Layer	Django REST Framework (DRF)
Authentication	JWT + OAuth (Google/GitHub)
Database	PostgreSQL
Environment	Python 3.10+
Deployment Ready	Yes
🔧 Setup Instructions

Follow these steps to run the backend locally.

1️⃣ Clone the repository
git clone https://github.com/SREEJITH7/codearc-backend.git
cd codearc-backend

2️⃣ Create and activate virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# or
source venv/bin/activate  # Mac/Linux

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Create .env file

Create a file named .env inside your project:

DB_NAME=codearc_db
DB_USER=postgres
DB_PASSWORD=12345
DB_HOST=localhost
DB_PORT=5432

GOOGLE_CLIENT_ID="your_google_client_id"
GOOGLE_CLIENT_SECRET="your_google_client_secret"

GITHUB_CLIENT_ID="your_github_client_id"
GITHUB_CLIENT_SECRET="your_github_client_secret"


⚠️ Never upload .env to GitHub
(It is already ignored via .gitignore)

5️⃣ Run migrations
python manage.py makemigrations
python manage.py migrate

6️⃣ Start the development server
python manage.py runserver


Your backend runs at:

👉 http://127.0.0.1:8000/

🧪 Testing API Using Postman

You can test:

Signup

Login

OTP verification

Google OAuth

GitHub OAuth

Optional: I can generate a full Postman Collection JSON for your API.

🔐 Authentication Flow
✔ Normal Login

User enters email/password

Backend returns JWT tokens

Frontend stores access token

Refresh token endpoint keeps auth alive

✔ Google OAuth

Frontend → Google → Backend callback → tokens issued

✔ GitHub OAuth

Same flow as Google.

🏗 Recommended Branch Workflow
main              → production-ready code
feature/auth-api  → authentication development
feature/user-api  → user profile system
feature/admin-api → admin endpoints


Always create PR → get review → merge to main.

🚀 Deployment (Optional)

Supports:

Docker

Nginx + Gunicorn

AWS / Render / Railway / DigitalOcean

I can create deployment configs if needed.

🤝 Contributing

Create a feature branch

Commit changes using clear messages

Open Pull Request

Follow code review guidelines

📄 License

This project is private (Internal Use Only).
