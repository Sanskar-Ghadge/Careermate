# In ml_model.py

from database import get_all_jobs

def get_jobs(user_skills):
    """
    Simple rule-based matcher that reads from the LIVE database:
    - user_skills: a comma-separated string of skills
    - returns top 5 job dicts with 'company','role','confidence'
    """
    if not user_skills:
        return []

    # Normalize user skills
    if isinstance(user_skills, str):
        user_skills_list = [s.strip().lower() for s in user_skills.split(',') if s.strip()]
    else:
        user_skills_list = [s.strip().lower() for s in user_skills if s and s.strip()]

    all_jobs_from_db = get_all_jobs()
    matched_jobs = []

    for job in all_jobs_from_db:
        requirements_str = job.get('requirements', '')
        if not requirements_str:
            continue
            
        job_skills = [s.strip().lower() for s in requirements_str.split(',') if s.strip()]
        if not job_skills:
            continue

        matches = sum(1 for skill in user_skills_list if skill in job_skills)
        
        if matches > 0:
            # We save confidence as a number (e.g., 100)
            confidence_score = int((matches / len(job_skills)) * 100)
            
            matched_jobs.append({
                'id': job.get('id'),  # <-- Sends the job ID
                'company': job.get('company_name', '').strip(),
                'role': job.get('title', '').strip(),
                'confidence': confidence_score  # <-- Sends the number 100
            })

    # Sort by the number
    matched_jobs.sort(key=lambda x: x['confidence'], reverse=True)
    return matched_jobs[:5]