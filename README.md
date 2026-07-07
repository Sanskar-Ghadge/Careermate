# CareerMate 🚀
CareerMate is a full-stack job portal and candidate-matching web application designed to connect job seekers with employers. It features a custom rule-based recommendation engine that evaluates seeker skill sets against active job requirements to calculate matching confidence scores, alongside employer analytics and application management portals.
---
## 🌟 Key Features
### 👤 For Job Seekers
*   **Profile Completion Tracker**: Interactive profile page tracking fields (skills, experience, education, location) with a progress meter indicating profile strength.
*   **Skill-Based Recommendations**: Tailored job recommendations based on skills entered in the profile.
*   **Job Application History**: Track current status (e.g., *Submitted*, *Interviewing*, *Hired*, *Rejected*) of all submitted applications.
### 🏢 For Employers (Companies)
*   **Job Management (CRUD)**: Create, read, update, and delete job postings with specific requirements, salary ranges, and job types.
*   **Applicant Screening**: View incoming applications for each job with applicant details, emails, and profile strengths.
*   **Status Workflow**: Manage applicant progress by changing application states.
*   **Company Analytics Dashboard**: Interactive dashboard displaying visual metrics of posted jobs, total applications, and applicant status distribution.
---
## 🛠️ Tech Stack
*   **Backend**: Python, Flask, Gunicorn (production server), bcrypt (password hashing)
*   **Database**: MySQL (hosted on Clever Cloud for production)
*   **Frontend**: HTML5, Vanilla CSS3, Jinja2 template engine
*   **Deployment**: GitHub, Render (web server), Clever Cloud (database)
---
## 📂 Project Structure
```text
├── app.py                  # Main Flask application entry point
├── database.py             # MySQL database configurations and CRUD queries
├── ml_model.py             # Rule-based job matching recommendation engine
├── seed_db.py              # Seeding script for mock companies
├── seed_jobs.py            # Seeding script for mock jobs
├── seed_user_and_apply.py  # Seeding script for mock job seeker and applications
├── requirements.txt        # Project dependencies
├── static/
│   └── style.css           # Custom stylesheets
└── templates/              # HTML layout templates using Jinja2
⚙️ Local Installation & Setup
1. Prerequisites
Ensure you have the following installed on your machine:

Python (3.8 or higher)
MySQL Server (XAMPP, WampServer, or local MySQL instance)
2. Clone the Repository
bash


git clone https://github.com/YOUR_GITHUB_USERNAME/Careermate.git
cd Careermate
3. Set Up Virtual Environment
bash


# Create a virtual environment
python -m venv venv
# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Activate on macOS/Linux
source venv/bin/activate
4. Install Dependencies
bash


pip install -r requirements.txt
pip install python-dotenv
5. Environment Configuration
Create a .env file in the root directory and add your MySQL database credentials:

ini


DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=careermate_db
DB_PORT=3306
CAREERMATE_SECRET=your_secret_session_key
6. Create Database and Setup Tables
Create the database inside your MySQL client:

sql


CREATE DATABASE careermate_db;
Then, initialize the database tables by running the database script:

bash


python database.py
🗃️ Seeding the Database (Optional)
To quickly populate the database with mock companies, jobs, and a job seeker for testing, run these three scripts in order:

bash


# 1. Seed Google, Microsoft, Amazon, Meta, and Tesla
python seed_db.py
# 2. Seed job postings for each company
python seed_jobs.py
# 3. Seed job seeker (Alex Carter) and apply to matching roles
python seed_user_and_apply.py
Mock Login Credentials:

Job Seeker: alex@example.com (Password: password123)
Company (e.g., Google): google@company.com (Password: password123)
🚀 Running the Web Application
To start the local development server:

bash


python app.py
Open your browser and navigate to: http://127.0.0.1:5000
