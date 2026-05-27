import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

# --- NEW: LOAD .env FILE ---
from dotenv import load_dotenv
load_dotenv() # This automatically reads from your .env file
# --- END NEW ---

# We only need ONE config, which now reads the password from the .env file
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD'), # This now works automatically!
    'database': os.environ.get('DB_NAME', 'careermate_db')
}

# We only need ONE connection function
def get_conn():
    """Establishes a new MySQL connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG, buffered=True)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        print("---")
        print("DATABASE CONNECTION FAILED.")
        print("1. Is your MySQL server (XAMPP, etc) running?")
        print(f"2. Is the password in your .env file correct?")
        print("---")
        return None

def init_db():
    """Initializes all tables in the database."""
    conn = get_conn()
    if not conn:
        print("Could not connect to database to initialize.")
        return
        
    # We use dictionary=True so c.fetchone() returns a dict, just like your old code!
    c = conn.cursor(dictionary=True) 
    
    # --- Users table (MySQL syntax) ---
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                  id INT AUTO_INCREMENT PRIMARY KEY,
                  name TEXT NOT NULL,
                  email VARCHAR(255) UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  profile_strength INT DEFAULT 0,
                  skills TEXT,
                  experience TEXT,
                  education TEXT,
                  location TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                 )''')
    
    # --- Companies table (MySQL syntax) ---
    c.execute('''CREATE TABLE IF NOT EXISTS companies (
                  id INT AUTO_INCREMENT PRIMARY KEY,
                  company_name TEXT NOT NULL,
                  email VARCHAR(255) UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  industry TEXT,
                  size TEXT,
                  description TEXT,
                  website TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                 )''')
    
    # --- Jobs table (MySQL syntax) ---
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
                  id INT AUTO_INCREMENT PRIMARY KEY,
                  company_id INT NOT NULL,
                  title TEXT NOT NULL,
                  description TEXT NOT NULL,
                  requirements TEXT,
                  location TEXT,
                  salary_range TEXT,
                  job_type TEXT,
                  experience_level TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
                 )''')

    # --- Applications table (MySQL syntax) ---
    c.execute('''CREATE TABLE IF NOT EXISTS applications (
                  id INT AUTO_INCREMENT PRIMARY KEY,
                  user_id INT NOT NULL,
                  job_id INT NOT NULL,
                  company_id INT NOT NULL,
                  status VARCHAR(50) DEFAULT 'Submitted',
                  applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                  FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
                  FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
                 )''')
    
    print("MySQL tables initialized successfully.")
    conn.commit()
    c.close()
    conn.close()

# -------- User Functions (Job Seekers) --------
# Note: We now use %s instead of ? for placeholders

# -------- User Functions (Job Seekers) --------
# ...

def create_user(name, email, hashed_password):  # <-- 1. Rename 'raw_password'
    # hashed = generate_password_hash(raw_password) # <-- 2. DELETE THIS LINE
    conn = get_conn()
    if not conn: # <-- 3. Add this check
        print("Create user failed: Could not connect to DB")
        return

    c = conn.cursor()
    # 4. Use the 'hashed_password' variable directly
    c.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
    conn.commit()
    c.close()
    conn.close()

def get_user_by_email(email):
    conn = get_conn()# <-- ADD THIS LINE
    if not conn:
        return None # Failed to connect

    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = c.fetchone()
    c.close()
    conn.close()
    return user # No conversion needed!

def get_user_by_id(user_id):
    conn = get_conn()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    row = c.fetchone()
    c.close()
    conn.close()
    return row

def authenticate_user(email, password):
    user = get_user_by_email(email)
    
    # Check if user exists AND the password hash matches
    if user and check_password_hash(user['password'], password):
        return user
    
    return None

def update_profile(user_id, skills, experience, education, location):
    strength = calculate_strength(skills, experience, education, location)
    conn = get_conn()
    c = conn.cursor()
    c.execute('''UPDATE users SET skills=%s, experience=%s, education=%s, location=%s, profile_strength=%s
                 WHERE id=%s''', (skills, experience, education, location, strength, user_id))
    conn.commit()
    c.close()
    conn.close()
    return strength

# -------- Company Functions (Employers) --------

# -------- Company Functions (Employers) --------

def create_company(company_name, email, hashed_password): # <-- 1. Rename
    # hashed = generate_password_hash(raw_password) # <-- 2. DELETE THIS LINE
    conn = get_conn()
    if not conn: # <-- 3. Add this check
        print("Create company failed: Could not connect to DB")
        return
        
    c = conn.cursor()
    # 4. Use the 'hashed_password' variable directly
    c.execute("INSERT INTO companies (company_name, email, password) VALUES (%s, %s, %s)", 
              (company_name, email, hashed_password))
    conn.commit()
    c.close()
    conn.close()

def get_company_by_email(email):
    conn = get_conn() # <-- ADD THIS LINE
    if not conn:
        return None # Failed to connect
        
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM companies WHERE email = %s", (email,))
    company = c.fetchone()
    c.close()
    conn.close()
    return company

def get_company_by_id(company_id):
    conn = get_conn()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM companies WHERE id=%s", (company_id,))
    row = c.fetchone()
    c.close()
    conn.close()
    return row

def authenticate_company(email, password):
    company = get_company_by_email(email)
    
    # Check if company exists AND the password hash matches
    if company and check_password_hash(company['password'], password):
        return company
        
    return None

def update_company_profile(company_id, industry, size, description, website):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''UPDATE companies SET industry=%s, size=%s, description=%s, website=%s
                 WHERE id=%s''', (industry, size, description, website, company_id))
    conn.commit()
    c.close()
    conn.close()

# -------- Job Functions --------

def create_job(company_id, title, description, requirements, location, salary_range, job_type, experience_level):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT INTO jobs (company_id, title, description, requirements, location, salary_range, job_type, experience_level)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', 
              (company_id, title, description, requirements, location, salary_range, job_type, experience_level))
    conn.commit()
    c.close()
    conn.close()

def get_jobs_by_company(company_id):
    conn = get_conn()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM jobs WHERE company_id=%s ORDER BY created_at DESC", (company_id,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows

def get_job_by_id(job_id):
    conn = get_conn()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM jobs WHERE id=%s", (job_id,))
    row = c.fetchone()
    c.close()
    conn.close()
    return row

def get_all_jobs():
    conn = get_conn()
    c = conn.cursor(dictionary=True)
    c.execute('''SELECT j.*, c.company_name 
                 FROM jobs j 
                 JOIN companies c ON j.company_id = c.id 
                 ORDER BY j.created_at DESC''')
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows
    
def update_job(job_id, title, description, requirements, location, salary_range, job_type, experience_level):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''UPDATE jobs SET title=%s, description=%s, requirements=%s, location=%s, salary_range=%s, job_type=%s, experience_level=%s
                 WHERE id=%s''', (title, description, requirements, location, salary_range, job_type, experience_level, job_id))
    conn.commit()
    c.close()
    conn.close()

def delete_job(job_id):
    conn = get_conn()
    c = conn.cursor()
    # ON DELETE CASCADE in the DB definition will handle applications.
    # We just need to delete the job.
    c.execute("DELETE FROM jobs WHERE id=%s", (job_id,))
    conn.commit()
    c.close()
    conn.close()

# -------- Application Functions --------

def create_application(user_id, job_id, company_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM applications WHERE user_id=%s AND job_id=%s", (user_id, job_id))
    if c.fetchone():
        c.close()
        conn.close()
        return False # Already applied
    
    c.execute("INSERT INTO applications (user_id, job_id, company_id) VALUES (%s, %s, %s)", 
              (user_id, job_id, company_id))
    conn.commit()
    c.close()
    conn.close()
    return True # Application successful

def get_application_by_user_and_job(user_id, job_id):
    conn = get_conn()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM applications WHERE user_id=%s AND job_id=%s", (user_id, job_id))
    row = c.fetchone()
    c.close()
    conn.close()
    return row

def get_user_applications(user_id):
    conn = get_conn()
    c = conn.cursor(dictionary=True)
    c.execute('''SELECT a.*, j.title, c.company_name 
                 FROM applications a
                 JOIN jobs j ON a.job_id = j.id
                 JOIN companies c ON a.company_id = c.id
                 WHERE a.user_id = %s
                 ORDER BY a.applied_at DESC''', (user_id,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows

def get_job_applications(job_id):
    conn = get_conn()
    c = conn.cursor(dictionary=True)
    c.execute('''SELECT a.*, u.name, u.email, u.profile_strength
                 FROM applications a
                 JOIN users u ON a.user_id = u.id
                 WHERE a.job_id = %s
                 ORDER BY a.applied_at DESC''', (job_id,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows

def get_application_by_id(app_id):
    conn = get_conn()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM applications WHERE id=%s", (app_id,))
    row = c.fetchone()
    c.close()
    conn.close()
    return row
    
def update_application_status(app_id, status):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE applications SET status=%s WHERE id=%s", (status, app_id))
    conn.commit()
    c.close()
    conn.close()

# -------- Utility Functions --------
# (We don't need row_to_dict functions anymore!)

def calculate_strength(skills, experience, education, location):
    score = 0
    if skills and skills.strip(): score += 25
    if experience and experience.strip(): score += 25
    if education and education.strip(): score += 25
    if location and location.strip(): score += 25
    return score

# This block allows you to run `py database.py` to create the tables
if __name__ == "__main__":
    # Check if password is set
    if not os.environ.get('DB_PASSWORD'):
        print("Error: DB_PASSWORD environment variable is not set.")
        print("Please set it before running this script in PowerShell:")
        print("$env:DB_PASSWORD = 'MyNewAppPassword123!'")
    else:
        print("Initializing MySQL database...")
        init_db()


# Example: Add this to the end of your database.py
# (Your function names might be different)

def check_connection():
    print("Attempting to connect to the database...")
    try:
        # CHANGE THIS LINE:
        conn = get_conn() # <--- USE THE NEW FUNCTION

        # Now, 'conn' will be a real connection object (or None if it failed)
        if conn:
            print("Connection object created. Running test query...")
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"[OK] Connection successful! Query result: {result}")
            conn.close()
        else:
            print("[ERROR] DATABASE CONNECTION FAILED: get_db_connection() returned None.")
            
    except Exception as e:
        print(f"[ERROR] DATABASE CONNECTION FAILED with error: {e}")

# This part stays the same
# ... (all your functions) ...

# This block allows you to run `py database.py` to create the tables
if __name__ == "__main__":
    
    # 1. Check if password is set
    if not os.environ.get('DB_PASSWORD'):
        print("Error: DB_PASSWORD environment variable is not set.")
        print("Please set it before running this script in PowerShell:")
        print("$env:DB_PASSWORD = '12410670'")
    
    else:
        # 2. Initialize the database
        print("Initializing MySQL database...")
        init_db()
        
        # 3. Check the connection
        check_connection()