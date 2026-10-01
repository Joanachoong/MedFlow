# MedFlow

**A modern multi-role Hospital & Patient Management System**

MedFlow connects Patients, Doctors, Nurses, and Administrators in one seamless medical platform. Doctors keep track of their patients, Nurses support daily care, Patients access their own information, and Admins oversee the entire system.

---

## What Are We Building

MedFlow is a full-stack healthcare application that brings hospital workflows into a clean, role-based digital system.

- **Patients** can view their profile, medical history, appointments, and care updates.
- **Doctors** manage assigned patients, write clinical notes, update diagnoses, and create treatment plans.
- **Nurses** add care notes, update patient status, and assist the care team.
- **Admins** manage users, roles, departments, and view system-wide overview.

The system focuses on clear patient tracking, secure role-based access, and practical hospital workflows, with optional AI support for summaries and insights.

---

## Tech Stack

| Layer          | Technology                                      |
|----------------|-------------------------------------------------|
| Frontend       | Next.js 14+ (App Router), React 18, TypeScript  |
| UI             | Tailwind CSS, shadcn/ui                         |
| Backend        | Python 3.11, FastAPI, SQLAlchemy, Alembic       |
| Database       | Supabase (PostgreSQL 15 + pgvector)             |
| Auth           | Supabase Auth (Google SSO + email/password)     |
| AI             | Google Gemini 2.5 Pro, Gemini 2.5 Flash, gemini-embedding-001 |
| Hosting        | Vercel (frontend), Railway / Render (backend)   |

---

## Folder Structure

```
careflow/
├── backend/                      # FastAPI application
│   ├── app/
│   │   ├── core/                 # Config, database, Supabase client, security
│   │   ├── middleware/           # Auth (JWT validation, role checks)
│   │   ├── models/               # SQLAlchemy models
│   │   ├── routers/              # API endpoints (patients, doctors, nurses, admin, ai)
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── services/             # Business logic + Gemini AI services
│   │   └── main.py               # FastAPI app entrypoint
│   └── requirements.txt
├── frontend/                     # Next.js application
│   ├── src/
│   │   ├── app/                  # App Router pages
│   │   ├── components/           # React components
│   │   ├── lib/                  # Supabase client, API helpers, utilities
│   │   ├── hooks/                # Custom React hooks
│   │   └── types/                # TypeScript interfaces
│   └── package.json
├── database/
│   ├── schema.sql                # Full PostgreSQL schema (run in Supabase SQL editor)
│   └── seed.py                   # Seed script
├── build_plan.md                 # Step-by-step build plan
└── README.md
```

---

## Features

### Core (MVP)
- Multi-role authentication (Patient / Doctor / Nurse / Admin)
- Patient profiles and basic medical records
- Doctor: view assigned patients + write clinical notes
- Nurse: add care notes and update patient status
- Role-based dashboards
- Secure access control (users only see what their role allows)

### Extended
- Appointments scheduling
- Treatment plans and medication notes
- AI-assisted clinical summaries (Gemini)
- Department / ward management
- Admin user management and system analytics
- Audit logs for medical record changes

---

## Deployment

| Service   | Platform          | Notes                                      |
|-----------|-------------------|--------------------------------------------|
| Frontend  | Vercel            | Connect GitHub repo, set environment variables |
| Backend   | Railway or Render | Deploy FastAPI, set `DATABASE_URL`, secrets |
| Database  | Supabase          | Create project, run `schema.sql`, enable Auth |
| Auth      | Supabase Auth     | Configure Google OAuth + email/password    |

### Environment Variables (examples)

**Frontend (`.env.local`)**
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend (`.env`)**
```
DATABASE_URL=
SUPABASE_URL=
SUPABASE_JWT_SECRET=
SUPABASE_SERVICE_ROLE_KEY=
GEMINI_API_KEY=
```

---

## Getting Started (Local)

1. Create a Supabase project and run `database/schema.sql`.
2. Set up environment variables for both frontend and backend.
3. Backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
4. Frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## run the code 

Terminal,Command,URL
Terminal 1,uvicorn app.main:app --reload,http://localhost:8000
Terminal 2,npm run dev,http://localhost:3000


