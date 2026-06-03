# College Server

Clean FastAPI backend for the core College Management System.

This service should own normal CMS features:

- Authentication and users
- Students, teachers, staff
- Courses and subjects
- Admissions
- Attendance
- Fees
- Marks
- Dashboards and reports

Meeting and chat logic should live in separate services later.

## Structure

```text
college_server/
|-- app/
|   |-- api/
|   |-- common/
|   |-- core/
|   |-- db/
|   `-- modules/
|-- alembic/
|-- docs/
|-- scripts/
|-- tests/
|-- main.py
|-- requirements.txt
`-- .env.example
```

## First Build Steps

1. Create the clean service structure. Done.
2. Add settings, logging, security middleware, and health endpoints. Done.
3. Port auth and user code from `Backend_final`. Done.
4. Port courses and subjects. Done.
5. Port students, teachers, staff, and teacher assignments. Done.
6. Port admissions, attendance, fees, and marks. Done.
7. Port dashboard and reports. Done.
8. Run final tests, migrations, route import, and server smoke checks. Done.

## Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn main:app --reload --port 8000
```

Shortcut:

```powershell
.\scripts\run-dev.ps1
```

## Verify

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m app.db.migrations --database-url sqlite+pysqlite:///:memory: upgrade head
.\.venv\Scripts\python.exe -B -c "from app.main import app; print(app.title); print(len(app.routes))"
```

## Implemented API Groups

- `/api/auth`
- `/api/users`
- `/api/courses`
- `/api/subjects`
- `/api/students`
- `/api/admissions`
- `/api/attendance`
- `/api/fees`
- `/api/marks`
- `/api/staff`
- `/api/teachers`
- `/api/dashboard`
- `/api/reports`

## Student Self-Registration

After an admin enters a student through admissions/students, the student can create their own login:

```http
POST /api/auth/register/student
```

```json
{
  "studentId": 1,
  "email": "student@example.com",
  "dob": "2005-01-10",
  "password": "student12345"
}
```

The request can use `studentCode` instead of `studentId`. The backend verifies the student record, email, and DOB before creating a `Student` user account.
