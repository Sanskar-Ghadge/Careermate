import os
# --- IMPORTS FIX ---
# I moved the security imports here, where they belong
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash 
# --- END IMPORTS FIX ---


# --- THIS IS THE ONLY DATABASE IMPORT YOU NEED ---
from database import (
    create_user, get_user_by_email, authenticate_user, get_user_by_id, update_profile,
    create_company, get_company_by_email, authenticate_company, get_company_by_id, update_company_profile,
    create_job, get_jobs_by_company, get_job_by_id, get_all_jobs, update_job, 
    delete_job as db_delete_job,  # Use alias to prevent name conflict
    create_application, get_application_by_user_and_job, get_user_applications, get_job_applications,
    get_application_by_id, update_application_status, init_db, get_conn
)
# --- END OF DATABASE IMPORTS ---

from ml_model import get_jobs

app = Flask(__name__)
# Use environment variable for secret key in production; fallback for dev:
app.secret_key = os.environ.get("CAREERMATE_SECRET", "dev_secret_change_me")

# (Removed init_db() call from here - we run it manually now)

# -------- Home --------
@app.route('/')
def home():
    return render_template('home.html')

# -------- Debug Routes --------
@app.route('/debug/session')
def debug_session():
    return f"Session: {dict(session)}"

@app.route('/debug/companies')
def debug_companies():
    conn = get_conn()
    c = conn.cursor(dictionary=True) # Use dictionary=True for MySQL
    c.execute("SELECT * FROM companies")
    companies = c.fetchall()
    c.close()
    conn.close()
    return f"Companies: {companies}"

@app.route('/debug/jobs')
def debug_jobs():
    conn = get_conn()
    c = conn.cursor(dictionary=True) # Use dictionary=True for MySQL
    c.execute("SELECT * FROM jobs")
    jobs = c.fetchall()
    c.close()
    conn.close()
    return f"Jobs: {jobs}"


# -------- Current Jobs (for Employees) --------
@app.route('/current_jobs')
def current_jobs():
    if 'user_id' not in session or session.get('user_type') != 'individual':
        flash('Please log in to view this page.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = get_user_by_id(user_id)
    if not user:
        session.clear()
        return redirect(url_for('login'))

    jobs = get_all_jobs()
    
    user_applications = get_user_applications(user_id)
    applied_job_ids = [app['job_id'] for app in user_applications]
    
    return render_template('current_jobs.html', 
                             jobs=jobs, 
                             applied_job_ids=applied_job_ids,
                             user=user)

# -------- Apply for Job --------
@app.route('/apply_job/<int:job_id>', methods=['GET', 'POST'])
def apply_job(job_id):
    if 'user_id' not in session or session.get('user_type') != 'individual':
        flash('You must be logged in to apply.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Check if user already applied
    existing_application = get_application_by_user_and_job(user_id, job_id)
    if existing_application:
        flash("You have already applied to this job!", 'warning')
        return redirect(url_for('current_jobs'))
    
    job = get_job_by_id(job_id)
    if not job:
        flash("Job not found!", 'danger')
        return redirect(url_for('current_jobs'))

    # GET Request: Show the application page
    if request.method == 'GET':
        return render_template('apply_job.html', job=job)

    # POST Request: Process the application
    if request.method == 'POST':
        # cover_letter = request.form.get('cover_letter', '').strip() # DB not set up for this
        
        # We MUST get the company_id from the job object to save the application
        company_id = job['company_id'] 
        
        # Pass the correct arguments: (user_id, job_id, company_id)
        success = create_application(user_id, job_id, company_id)
        
        if success:
            flash("Application submitted successfully!", 'success')
            return redirect(url_for('my_applications')) # Go to "My Applications" page
        else:
            flash("Error submitting application. Please try again.", 'danger')
            return render_template('apply_job.html', job=job)

# -------- My Applications --------
@app.route('/my_applications')
def my_applications():
    if 'user_id' not in session or session.get('user_type') != 'individual':
        flash('Please log in to view this page.', 'danger')
        return redirect(url_for('login'))
    
    applications = get_user_applications(session['user_id'])
    return render_template('my_applications.html', applications=applications)

# -------- View Job Applications (for Company) --------
@app.route('/view_applications/<int:job_id>')
def view_job_applications(job_id):
    if 'company_id' not in session or session.get('user_type') != 'company':
        flash('Please log in as a company to view this page.', 'danger')
        return redirect(url_for('company_login'))
    
    # 1. Get the job by its ID (only 1 argument)
    job = get_job_by_id(job_id)
    
    # 2. Add a security check to make sure this company OWNS this job
    if not job or job['company_id'] != session['company_id']:
        flash('Job not found or you do not have permission to view this.', 'danger')
        return redirect(url_for('company_dashboard'))
    
    # 3. Get the applications for that job (only 1 argument)
    applications = get_job_applications(job_id)
    
    return render_template('view_applications.html', job=job, applications=applications)

# -------- Update Application Status (for Company) --------
@app.route('/update_application_status/<int:app_id>', methods=['POST'])
def update_status(app_id):
    if 'company_id' not in session or session.get('user_type') != 'company':
        flash('You are not authorized to do this.', 'danger')
        return redirect(url_for('company_login'))

    new_status = request.form.get('status')
    job_id = request.form.get('job_id') 
    
    if not new_status or not job_id:
        flash('Invalid request.', 'danger')
        return redirect(url_for('company_dashboard'))

    app_to_update = get_application_by_id(app_id)
    
    if not app_to_update or app_to_update['company_id'] != session['company_id']:
        flash('Application not found or you do not have permission.', 'danger')
        return redirect(url_for('company_dashboard'))

    update_application_status(app_id, new_status)
    flash(f"Applicant's status updated to '{new_status}'!", 'success')
    
    return redirect(url_for('view_job_applications', job_id=job_id))

# -------- Individual User Routes --------

# -------- Signup --------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash("Please fill all required fields.", 'warning')
            return render_template('signup.html')

        if password != confirm_password:
            flash("Passwords do not match!", 'warning')
            return render_template('signup.html')

        if get_user_by_email(email):
            flash("Email already registered! Please login.", 'warning')
            return redirect(url_for('login'))

        # --- PASSWORD HASHING FIX ---
        # 1. Hash the password
        hashed_password = generate_password_hash(password)
        # 2. Save the HASH, not the original password
        create_user(name, email, hashed_password)
        # --- END OF FIX ---

        flash("Account created. Please log in.", 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# -------- Login --------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # NOTE: This will fail until you update 'authenticate_user' in database.py
        user = authenticate_user(email, password) 
        
        if user:
            session.clear()
            session['user_id'] = user['id']
            session['user_type'] = 'individual'
            flash("Logged in successfully.", 'success')
            return redirect(url_for('dashboard'))
            
        flash("Invalid credentials.", 'danger')
        return render_template('login.html')
    return render_template('login.html')

# -------- Dashboard --------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('user_type') != 'individual':
        flash('Please log in to view your dashboard.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = get_user_by_id(user_id)
    if not user:
        session.clear()
        return redirect(url_for('login'))

    strength = user.get('profile_strength', 0) or 0
    incomplete = (strength < 100 or not user.get('skills'))

    applications = get_user_applications(user_id)
    application_count = len(applications)
    
    interview_count = 0
    for app in applications:
        if app['status'] == 'Interviewing':
            interview_count += 1
            
    all_jobs = get_all_jobs()
    total_jobs_count = len(all_jobs)

    return render_template(
        'dashboard.html', 
        name=user.get('name'), 
        strength=strength, 
        incomplete=incomplete,
        application_count=application_count,
        interview_count=interview_count,
        total_jobs_count=total_jobs_count
    )

# -------- Profile --------
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session or session.get('user_type') != 'individual':
        flash('Please log in to view this page.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = get_user_by_id(user_id)
    if not user:
        session.clear()
        return redirect(url_for('login'))

    if request.method == 'POST':
        skills = request.form.get('skills', '').strip()
        experience = request.form.get('experience', '').strip()
        education = request.form.get('education', '').strip()
        location = request.form.get('location', '').strip()

        update_profile(user_id, skills, experience, education, location)
        flash("Profile updated successfully.", 'success')
        return redirect(url_for('dashboard'))

    return render_template('profile.html', user=user)

# -------- Results (Job Recommendations) --------
@app.route('/results')
def results():
    if 'user_id' not in session or session.get('user_type') != 'individual':
        flash('Please log in to view this page.', 'danger')
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))

    if not user.get('skills') or (user.get('profile_strength', 0) < 100):
        flash("Please complete your profile (skills, experience, education, location) to get job recommendations.", 'warning')
        return redirect(url_for('profile'))

    jobs = get_jobs(user.get('skills'))
    return render_template('results.html', jobs=jobs)

# -------- Company Routes --------

# -------- Company Signup --------
@app.route('/company_signup', methods=['GET', 'POST'])
def company_signup():
    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not company_name or not email or not password:
            flash("Please fill all required fields.", 'warning')
            return render_template('company_signup.html')

        if password != confirm_password:
            flash("Passwords do not match!", 'warning')
            return render_template('company_signup.html')

        if get_company_by_email(email):
            flash("Company email already registered! Please login.", 'warning')
            return redirect(url_for('company_login'))

        # --- PASSWORD HASHING FIX ---
        # 1. Hash the password
        hashed_password = generate_password_hash(password)
        # 2. Save the HASH, not the original password
        create_company(company_name, email, hashed_password)
        # --- END OF FIX ---
        
        flash("Company account created. Please log in.", 'success')
        return redirect(url_for('company_login'))

    return render_template('company_signup.html')

# -------- Company Login --------
@app.route('/company_login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # NOTE: This will fail until you update 'authenticate_company' in database.py
        company = authenticate_company(email, password)
        
        if company:
            session.clear()
            session['company_id'] = company['id']
            session['user_type'] = 'company'
            flash("Company login successful.", 'success')
            return redirect(url_for('company_dashboard'))
            
        flash("Invalid credentials.", 'danger')
        return render_template('company_login.html')
    return render_template('company_login.html')

# -------- Company Dashboard --------
@app.route('/company_dashboard')
def company_dashboard():
    if 'company_id' not in session or session.get('user_type') != 'company':
        flash('Please log in to view this page.', 'danger')
        return redirect(url_for('company_login'))
    
    company_id = session['company_id']
    company = get_company_by_id(company_id)
    if not company:
        session.clear()
        return redirect(url_for('company_login'))

    jobs = get_jobs_by_company(company_id)
    
    total_applications = 0
    status_counts = {'Interviewing': 0, 'Hired': 0}
    
    for job in jobs:
        applications = get_job_applications(job['id'])
        job['application_count'] = len(applications) 
        total_applications += len(applications)
        
        for app in applications:
            if app['status'] == 'Interviewing':
                status_counts['Interviewing'] += 1
            elif app['status'] == 'Hired':
                status_counts['Hired'] += 1

    return render_template(
        'company_dashboard.html', 
        company=company, 
        jobs=jobs,
        total_applications=total_applications, 
        interview_count=status_counts['Interviewing'], 
        hire_count=status_counts['Hired'] 
    )

# -------- Company Profile --------
@app.route('/company_profile', methods=['GET', 'POST'])
def company_profile():
    if 'company_id' not in session or session.get('user_type') != 'company':
        flash('Please log in to view this page.', 'danger')
        return redirect(url_for('company_login'))
    
    company_id = session['company_id']
    company = get_company_by_id(company_id)
    if not company:
        session.clear()
        return redirect(url_for('company_login'))

    if request.method == 'POST':
        # Note: You cannot change company_name or email from this form
        industry = request.form.get('industry', '').strip()
        size = request.form.get('size', '').strip()
        description = request.form.get('description', '').strip()
        website = request.form.get('website', '').strip()

        update_company_profile(company_id, industry, size, description, website)
        flash("Company profile updated successfully.", 'success')
        return redirect(url_for('company_dashboard'))

    return render_template('company_profile.html', company=company)

# -------- Post Job --------
@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if 'company_id' not in session or session.get('user_type') != 'company':
        flash('Please log in to post a job.', 'danger')
        return redirect(url_for('company_login'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        requirements = request.form.get('requirements', '').strip()
        job_type = request.form.get('job_type', '').strip()
        location = request.form.get('location', '').strip()
        salary_range = request.form.get('salary_range', '').strip()
        experience_level = request.form.get('experience_level', '').strip()

        if not title or not description or not job_type or not location:
            flash("Please fill all required fields.", 'warning')
            return render_template('post_job.html')

        create_job(
            session['company_id'], 
            title, 
            description, 
            requirements, 
            location, 
            salary_range, 
            job_type,
            experience_level
        )
        flash("Job posted successfully!", 'success')
        return redirect(url_for('company_dashboard'))

    return render_template('post_job.html')

# -------- Edit Job --------
@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    if 'company_id' not in session or session.get('user_type') != 'company':
        flash('You are not authorized to do this.', 'danger')
        return redirect(url_for('company_login'))

    company_id = session['company_id']

    # 1. Get the job and check ownership
    job = get_job_by_id(job_id) 
    if not job or job['company_id'] != company_id:
        flash('Job not found or you do not have permission to edit it.', 'danger')
        return redirect(url_for('company_dashboard'))

    # If we are submitting the form (POST)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        requirements = request.form.get('requirements', '').strip()
        job_type = request.form.get('job_type', '').strip()
        location = request.form.get('location', '').strip()
        salary_range = request.form.get('salary_range', '').strip()
        experience_level = request.form.get('experience_level', '').strip()

        if not title or not description or not job_type or not location:
            flash("Please fill all required fields.", 'warning')
            return render_template('edit_job.html', job=job)

        # 2. Call update_job with the correct 8 arguments
        update_job(
            job_id, title, description, requirements, 
            location, salary_range, job_type, experience_level
        )
        
        flash("Job updated successfully!", 'success')
        return redirect(url_for('company_dashboard'))

    # If we are just visiting the page (GET)
    return render_template('edit_job.html', job=job)

# -------- Delete Job --------
@app.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if 'company_id' not in session or session.get('user_type') != 'company':
        flash('You are not authorized to do this.', 'danger')
        return redirect(url_for('company_login'))

    company_id = session['company_id']

    # 1. Get the job first to check who owns it
    job = get_job_by_id(job_id) 

    # 2. Add a security check 
    if not job or job['company_id'] != company_id:
        flash('Job not found or you do not have permission to delete it.', 'danger')
        return redirect(url_for('company_dashboard'))
    
    # 3. If security passes, call the aliased db_delete_job()
    db_delete_job(job_id) # Uses the alias
    flash(f"Job '{job['title']}' (and all its applications) deleted successfully!", 'success')
    
    return redirect(url_for('company_dashboard'))

# -------- Company Analytics --------
@app.route('/company_analytics')
def company_analytics():
    if 'company_id' not in session:
        flash('Please log in to view this page.', 'danger')
        return redirect(url_for('company_login')) 
    
    company_id = session['company_id']
    company = get_company_by_id(company_id)
    jobs = get_jobs_by_company(company_id)
    total_jobs = len(jobs)
    
    total_applications = 0
    status_counts = {'Pending': 0, 'Interviewing': 0, 'Rejected': 0, 'Hired': 0}

    for job in jobs:
        applications = get_job_applications(job['id'])
        job['application_count'] = len(applications)
        total_applications += len(applications)
        
        for app in applications:
            status = app['status']
            if status == 'Submitted':
                status = 'Pending'
                
            if status in status_counts:
                status_counts[status] += 1

    status_data = [
        status_counts['Pending'],
        status_counts['Interviewing'],
        status_counts['Rejected'],
        status_counts['Hired']
    ]
    
    return render_template(
        'company_analytics.html', 
        company=company, 
        jobs=jobs, 
        total_jobs=total_jobs,
        total_applications=total_applications,
        status_data=status_data,
        interview_count=status_counts['Interviewing'],
        hire_count=status_counts['Hired']
    )

# -------- Common Routes --------

# -------- Feedback --------
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        
        print(f"Feedback received: {name}, {email}, {message}")
        flash("Thank you for your feedback.", 'success')
        
        if session.get('user_type') == 'company':
            return redirect(url_for('company_dashboard'))
        elif session.get('user_type') == 'individual':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('home'))
    
    return render_template('feedback.html')

# -------- Logout --------
@app.route('/logout')
def logout():
    user_type = session.get('user_type')
    session.clear()
    
    if user_type == 'company':
        flash("Company logged out successfully.")
        return redirect(url_for('company_login'))
    else:
        flash("Logged out successfully.")
        return redirect(url_for('login'))

# -------- Company Logout (specific) --------
@app.route('/company_logout')
def company_logout():
    session.clear()
    flash("Company logged out successfully.")
    return redirect(url_for('company_login'))

# -------- Run --------
if __name__ == "__main__":
    app.run(debug=True)