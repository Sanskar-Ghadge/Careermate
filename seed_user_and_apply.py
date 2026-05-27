import os
from dotenv import load_dotenv
load_dotenv()

from database import (
    create_user, get_user_by_email, update_profile, 
    get_all_jobs, create_application, get_user_applications
)
from werkzeug.security import generate_password_hash

print("Starting user creation and application seeding...")

# 1. Create a dummy user 'Alex Carter'
user_email = "alex@example.com"
existing_user = get_user_by_email(user_email)

if not existing_user:
    # Hash the password 'password123'
    hashed_password = generate_password_hash("password123")
    create_user("Alex Carter", user_email, hashed_password)
    print(f"Successfully registered user: Alex Carter ({user_email})")
    
    # Retrieve user to update profile details
    user = get_user_by_email(user_email)
    user_id = user["id"]
    
    # Update profile to 100% completion strength with some key matching skills
    update_profile(
        user_id=user_id,
        skills="Python, SQL, Machine Learning, TensorFlow, Pandas",
        experience="2 years as a Junior Data Scientist, worked on ML pipelines.",
        education="B.S. in Computer Science",
        location="Seattle, WA"
    )
    print("Successfully populated Alex Carter's profile skills, education, and location.")
else:
    user = existing_user
    user_id = user["id"]
    print(f"User Alex Carter already exists in the database.")

# 2. Retrieve all open jobs in the database
jobs = get_all_jobs()
if len(jobs) == 0:
    print("Error: No open jobs found in the database. Run seed_jobs.py first!")
    exit(1)

# 3. Apply to a couple of jobs (e.g., Google's Software Engineer and Amazon's ML Engineer)
applied_count = 0
for job in jobs:
    job_id = job["id"]
    company_name = job["company_name"]
    company_id = job["company_id"]
    job_title = job["title"]
    
    # Let's apply to up to 2 matching jobs for demo purposes
    if job_title in ["Software Engineer", "ML Engineer"]:
        success = create_application(user_id, job_id, company_id)
        if success:
            print(f"Alex Carter successfully applied for the '{job_title}' role at {company_name}!")
            applied_count += 1
        else:
            print(f"Alex Carter has already applied for the '{job_title}' role at {company_name}.")

# 4. Print results
apps = get_user_applications(user_id)
print(f"\nCompleted user application seeding! Alex Carter has {len(apps)} active application(s).")
print("User Credentials:")
print("- Email: alex@example.com")
print("- Password: password123")
