import os
from dotenv import load_dotenv
load_dotenv()

from database import create_company, get_company_by_email, update_company_profile
from werkzeug.security import generate_password_hash

companies_to_add = [
    {
        "name": "Google",
        "email": "google@company.com",
        "industry": "Technology",
        "size": "10,000+",
        "desc": "Organizing the world's information and making it universally accessible and useful.",
        "web": "https://www.google.com"
    },
    {
        "name": "Microsoft",
        "email": "microsoft@company.com",
        "industry": "Technology",
        "size": "10,000+",
        "desc": "Empower every person and every organization on the planet to achieve more.",
        "web": "https://www.microsoft.com"
    },
    {
        "name": "Amazon",
        "email": "amazon@company.com",
        "industry": "E-Commerce & Cloud Computing",
        "size": "10,000+",
        "desc": "Earth's most customer-centric company, best employer, and safest place to work.",
        "web": "https://www.amazon.com"
    },
    {
        "name": "Meta",
        "email": "meta@company.com",
        "industry": "Social Media & Metaverse",
        "size": "10,000+",
        "desc": "Giving people the power to build community and bring the world closer together.",
        "web": "https://meta.com"
    },
    {
        "name": "Tesla",
        "email": "tesla@company.com",
        "industry": "Automotive & Clean Energy",
        "size": "10,000+",
        "desc": "Accelerating the world's transition to sustainable energy.",
        "web": "https://www.tesla.com"
    }
]

# We will hash the default password 'password123'
default_password = "password123"
hashed_password = generate_password_hash(default_password)

print("Starting database seeding...")

for comp in companies_to_add:
    existing = get_company_by_email(comp["email"])
    if not existing:
        # Create company login credentials
        create_company(comp["name"], comp["email"], hashed_password)
        
        # Retrieve the generated company to update the rest of its profile details
        created_comp = get_company_by_email(comp["email"])
        update_company_profile(
            created_comp["id"],
            comp["industry"],
            comp["size"],
            comp["desc"],
            comp["web"]
        )
        print(f"Successfully seeded: {comp['name']} ({comp['email']})")
    else:
        print(f"Company '{comp['name']}' already exists in the database.")

print("\nSeeding completed successfully!")
print("Credentials for all seeded companies:")
print("- Password: password123")
