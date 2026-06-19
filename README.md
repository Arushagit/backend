# ExpertiseCo CRM Backend
### Django + MongoDB REST API | JWT Auth | Gmail Email | Railway Deployment

---

## 🗂️ Project Structure

```
backend/
├── manage.py
├── requirements.txt
├── .env                    ← Create from .env.example
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── railway.toml            ← Railway deployment config
├── Procfile
├── crm_backend/
│   ├── settings.py         ← All configuration
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── enquiries/
    ├── models.py           ← Enquiry MongoDB model
    ├── serializers.py      ← DRF serializers
    ├── views.py            ← Public contact form API
    ├── admin_views.py      ← JWT-protected admin API
    ├── email_utils.py      ← Gmail SMTP email logic
    └── urls.py             ← All URL routes
```

---

## 🚀 Local Development Setup

### Prerequisites
- Python 3.11+
- MongoDB running locally (`mongod`)
- Gmail account with [App Password](https://myaccount.google.com/apppasswords) enabled

### 1. Setup Virtual Environment
```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
```
Edit `.env` and set:
- `EMAIL_HOST_USER` — your Gmail address
- `EMAIL_HOST_PASSWORD` — your Gmail App Password (16-char)
- `ADMIN_USERNAME` / `ADMIN_PASSWORD` — admin login credentials
- `MONGODB_URI` — MongoDB connection string

### 4. Initialize Database
```bash
python manage.py migrate --run-syncdb
```

### 5. Start Development Server
```bash
python manage.py runserver
```

API available at: `http://localhost:8000/api/`

---

## 📡 API Reference

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/contact/` | Submit contact form |
| `GET`  | `/api/health/` | Health check |

#### POST /api/contact/
```json
// Request
{
  "name": "John Doe",
  "email": "john@company.com",
  "message": "Hello, I'd like to discuss..."
}

// Response 201
{
  "success": true,
  "message": "Thank you! We'll be in touch within 1 business day.",
  "id": 42
}
```

### Admin Endpoints (JWT Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/admin/login/` | Get JWT tokens |
| `POST` | `/api/admin/token/refresh/` | Refresh access token |
| `GET`  | `/api/admin/stats/` | Dashboard statistics |
| `GET`  | `/api/admin/enquiries/` | List enquiries |
| `GET`  | `/api/admin/enquiries/{id}/` | Get single enquiry |
| `PATCH`| `/api/admin/enquiries/{id}/` | Update status |
| `DELETE`| `/api/admin/enquiries/{id}/` | Delete enquiry |

#### POST /api/admin/login/
```json
// Request
{ "username": "admin", "password": "AdminPass@123" }

// Response 200
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "admin": { "username": "admin", "email": "admin@site.com" }
}
```

#### GET /api/admin/enquiries/ (with filters)
```
GET /api/admin/enquiries/?status=new&search=john&page=1&page_size=20
Authorization: Bearer eyJ...
```

---

## 📧 Gmail SMTP Setup

1. Enable **2-Factor Authentication** on your Google account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Generate a new App Password for "Mail"
4. Copy the 16-character password into `.env` as `EMAIL_HOST_PASSWORD`

---

## 🐳 Docker Deployment

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

---

## 🚂 Railway Deployment

1. Push code to GitHub repository
2. Connect repo to [Railway](https://railway.app)
3. Add a **MongoDB** plugin in Railway dashboard
4. Set environment variables in Railway (use `.env.example` as reference):
   - Set `MONGODB_URI` to the Railway MongoDB URL
   - Set `DEBUG=False`
   - Set `SECRET_KEY` to a long random string
   - Set `ALLOWED_HOSTS` to your Railway domain
   - Set all email variables
5. Railway auto-deploys from `railway.toml` config

### Generate a secure SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🔐 Security Notes

- Admin credentials are stored in environment variables (no database user)
- JWT tokens expire after 60 minutes (configurable)
- Contact form is rate-limited to 5 submissions/minute per IP
- All security headers enabled in production (`DEBUG=False`)
- `.env` is git-ignored — never commit secrets
