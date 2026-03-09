# -*- coding: utf-8 -*-
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

os.makedirs("data/resumes", exist_ok=True)

def create_resume(filename, name, email, skills, experience):
    c = canvas.Canvas(f"data/resumes/{filename}", pagesize=letter)
    
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 750, name)
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, f"Email: {email}")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 680, "Skills")
    
    c.setFont("Helvetica", 11)
    y = 660
    for skill in skills:
        c.drawString(120, y, f"� {skill}")
        y -= 20
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y-20, "Experience")
    
    c.setFont("Helvetica", 11)
    y -= 40
    for exp in experience:
        c.drawString(120, y, f"� {exp}")
        y -= 20
    
    c.save()
    print(f"? Created: data/resumes/{filename}")

# Create 5 diverse sample resumes
resumes_data = [
    {
        "filename": "alex_chen_python.pdf",
        "name": "Alex Chen",
        "email": "alex.chen@email.com",
        "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "AWS", "Docker"],
        "experience": [
            "Senior Backend Developer at FinTech Co - 4 years",
            "Built scalable APIs serving 1M+ users",
            "Led migration to microservices architecture"
        ]
    },
    {
        "filename": "sarah_johnson_ml.pdf",
        "name": "Sarah Johnson",
        "email": "sarah.j@email.com",
        "skills": ["Python", "TensorFlow", "PyTorch", "Computer Vision", "NLP", "SQL"],
        "experience": [
            "ML Engineer at AI Startup - 3 years",
            "Developed computer vision models for autonomous vehicles",
            "Published 2 papers at NeurIPS"
        ]
    },
    {
        "filename": "mike_zhang_devops.pdf",
        "name": "Mike Zhang",
        "email": "mike.zhang@email.com",
        "skills": ["Kubernetes", "Docker", "Terraform", "AWS", "Jenkins", "Python"],
        "experience": [
            "DevOps Lead at CloudScale - 5 years",
            "Managed 200+ microservices in production",
            "Reduced deployment time by 70%"
        ]
    },
    {
        "filename": "emily_davis_fullstack.pdf",
        "name": "Emily Davis",
        "email": "emily.davis@email.com",
        "skills": ["React", "Node.js", "TypeScript", "MongoDB", "GraphQL", "AWS"],
        "experience": [
            "Full Stack Developer at TechStartup - 4 years",
            "Built real-time dashboard used by 500+ clients",
            "Implemented CI/CD pipeline"
        ]
    },
    {
        "filename": "david_kim_data.pdf",
        "name": "David Kim",
        "email": "david.kim@email.com",
        "skills": ["Python", "R", "Tableau", "SQL", "Spark", "Statistics"],
        "experience": [
            "Data Analyst at E-commerce Co - 3 years",
            "Created dashboards for executive team",
            "Increased revenue by 15% through data insights"
        ]
    }
]

for r in resumes_data:
    create_resume(r["filename"], r["name"], r["email"], r["skills"], r["experience"])

print("\n?? 5 sample resumes created successfully!")
