import os
from dotenv import load_dotenv
load_dotenv()

from database import get_company_by_email, create_job

# We will define a set of jobs for each seeded company
jobs_to_seed = {
    "google@company.com": [
        {
            "title": "Software Engineer",
            "desc": "Join Google's core search infrastructure team to build highly scalable services.",
            "reqs": "Python, Java, SQL",
            "location": "Mountain View, CA",
            "salary": "$120,000 - $160,000",
            "type": "Full-Time",
            "level": "Mid-Level"
        },
        {
            "title": "Site Reliability Engineer",
            "desc": "Optimize, automate and support critical production infrastructure across Google global datacenters.",
            "reqs": "Linux, Python, Cloud",
            "location": "Sunnyvale, CA",
            "salary": "$130,000 - $175,000",
            "type": "Full-Time",
            "level": "Senior"
        }
    ],
    "microsoft@company.com": [
        {
            "title": "Data Analyst",
            "desc": "Transform large-scale enterprise data sets into actionable product insights for Microsoft 365.",
            "reqs": "Python, SQL, Excel",
            "location": "Redmond, WA",
            "salary": "$90,000 - $125,000",
            "type": "Full-Time",
            "level": "Entry-Level"
        },
        {
            "title": "Cloud Solutions Architect",
            "desc": "Design and architect migration strategies for enterprise customers moving workload to Azure Cloud.",
            "reqs": "Azure, C#, SQL",
            "location": "Seattle, WA",
            "salary": "$140,000 - $185,000",
            "type": "Full-Time",
            "level": "Senior"
        }
    ],
    "amazon@company.com": [
        {
            "title": "ML Engineer",
            "desc": "Build next-generation recommendation algorithms powering Amazon's Retail personalization engines.",
            "reqs": "Python, Machine Learning, TensorFlow",
            "location": "Seattle, WA",
            "salary": "$150,000 - $190,000",
            "type": "Full-Time",
            "level": "Senior"
        },
        {
            "title": "Backend Developer",
            "desc": "Design and support highly available order fulfillment microservices using Amazon Web Services (AWS).",
            "reqs": "Java, AWS, SQL",
            "location": "Austin, TX",
            "salary": "$110,000 - $145,000",
            "type": "Full-Time",
            "level": "Mid-Level"
        }
    ],
    "meta@company.com": [
        {
            "title": "Frontend Developer",
            "desc": "Build smooth, premium user interfaces for Facebook, Instagram, and Horizon Worlds.",
            "reqs": "JavaScript, React, HTML, CSS",
            "location": "Menlo Park, CA",
            "salary": "$115,000 - $155,000",
            "type": "Full-Time",
            "level": "Mid-Level"
        },
        {
            "title": "Fullstack Engineer",
            "desc": "Support end-to-end product features for Meta's advertising dashboard from DB schema to UI panels.",
            "reqs": "React, Node.js, Python",
            "location": "New York, NY",
            "salary": "$130,000 - $170,000",
            "type": "Full-Time",
            "level": "Mid-Level"
        }
    ],
    "tesla@company.com": [
        {
            "title": "Data Scientist",
            "desc": "Analyze petabytes of telemetry data collected from Tesla's fleet to optimize Full Self-Driving behaviors.",
            "reqs": "Python, Data Analysis, Pandas, Machine Learning",
            "location": "Palo Alto, CA",
            "salary": "$125,000 - $165,000",
            "type": "Full-Time",
            "level": "Mid-Level"
        },
        {
            "title": "Firmware Engineer",
            "desc": "Develop low-level C/C++ embedded code for Tesla vehicle powertrain control systems.",
            "reqs": "C, C++, Embedded Systems",
            "location": "Austin, TX",
            "salary": "$135,000 - $180,000",
            "type": "Full-Time",
            "level": "Senior"
        }
    ]
}

print("Starting database seeding for jobs...")

total_seeded = 0
for email, jobs in jobs_to_seed.items():
    company = get_company_by_email(email)
    if not company:
        print(f"Error: Company '{email}' not found. Run seed_db.py first!")
        continue
        
    company_id = company["id"]
    company_name = company["company_name"]
    
    # Check if this company already has jobs posted to prevent duplicates
    from database import get_jobs_by_company
    existing_jobs = get_jobs_by_company(company_id)
    
    if len(existing_jobs) > 0:
        print(f"Company '{company_name}' already has {len(existing_jobs)} jobs posted. Skipping to avoid duplicates.")
        continue

    for j in jobs:
        create_job(
            company_id=company_id,
            title=j["title"],
            description=j["desc"],
            requirements=j["reqs"],
            location=j["location"],
            salary_range=j["salary"],
            job_type=j["type"],
            experience_level=j["level"]
        )
        print(f"Successfully posted: '{j['title']}' for {company_name}")
        total_seeded += 1

print(f"\nCompleted job seeding! Seeded {total_seeded} jobs across companies.")
