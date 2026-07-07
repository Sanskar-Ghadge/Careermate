# CareerMate

CareerMate is a job portal that matches candidates to job openings using a rule-based scoring engine. Job seekers build a profile, get matched against open roles based on their skills, and track their applications. Companies post jobs, review applicants, and manage hiring status through a simple dashboard.

Built as a full-stack project using Flask and MySQL.

## Features

**Job seekers**
- Profile page with a completion tracker (skills, experience, education, location)
- Job recommendations based on skill match
- Application history with status updates (Submitted, Interviewing, Hired, Rejected)

**Companies**
- Create, edit, and delete job postings (requirements, salary range, job type)
- View applicants for each job along with their profile strength
- Update application status
- Basic analytics dashboard for jobs posted, total applications, and applicant status breakdown

## Tech stack

- Backend: Python, Flask, Gunicorn
- Database: MySQL (Clever Cloud in production)
- Frontend: HTML, CSS, Jinja2
- Auth: bcrypt for password hashing
- Hosting: Render (app), Clever Cloud (database)

## Project structure

```
├── app.py                  # Flask app entry point
├── database.py             # DB config and CRUD queries
├── ml_model.py              # Rule-based matching engine
├── seed_db.py               # Seeds mock companies
├── seed_jobs.py              # Seeds mock job postings
├── seed_user_and_apply.py    # Seeds a mock job seeker + applications
├── requirements.txt
├── static/
│   └── style.css
└── templates/
```

## Setup

**Requirements:** Python 3.8+, MySQL (local install, XAMPP, or WampServer)

Clone the repo:
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/Careermate.git
cd Careermate
```

Set up a virtual environment:
```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
pip install python-dotenv
```

Create a `.env` file in the project root:
```ini
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=careermate_db
DB_PORT=3306
CAREERMATE_SECRET=your_secret_session_key
```

Create the database:
```sql
CREATE DATABASE careermate_db;
```

Then run the setup script to create tables:
```bash
python database.py
```

## Seeding test data (optional)

Run these in order to populate the database with sample companies, jobs, and a test job seeker:

```bash
python seed_db.py              # Google, Microsoft, Amazon, Meta, Tesla
python seed_jobs.py             # job postings for each company
python seed_user_and_apply.py   # a job seeker (Alex Carter) + sample applications
```

Test login credentials:
- Job seeker: `alex@example.com` / `password123`
- Company (Google): `google@company.com` / `password123`

## Running locally

```bash
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.
