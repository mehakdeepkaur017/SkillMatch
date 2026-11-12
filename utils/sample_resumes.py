"""
Sample Resumes Generator for SkillMatch AI
Generates realistic PDF resumes using ReportLab for instant testing.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def generate_sample_pdfs():
    os.makedirs("assets/samples", exist_ok=True)
    
    samples = [
        {
            "filename": "Sample_Data_Scientist.pdf",
            "name": "Sarah Chen",
            "title": "Data Scientist & Machine Learning Specialist",
            "email": "sarah.chen@example.com",
            "phone": "+1 (555) 234-5678",
            "linkedin": "linkedin.com/in/sarahchen-ds",
            "github": "github.com/sarahchen-ai",
            "summary": "Data Scientist with 3+ years of experience in statistical modeling, machine learning, predictive analytics, and natural language processing. Proven track record of developing end-to-end ML pipelines in Python, optimizing churn prediction algorithms, and visualizing business insights using Tableau and Power BI.",
            "skills": "Python, SQL, Machine Learning, Deep Learning, Scikit-learn, TensorFlow, PyTorch, Pandas, NumPy, Data Visualization, Matplotlib, Seaborn, Tableau, Statistical Analysis, Git, Docker, Cross-functional Collaboration, Critical Thinking",
            "experience": [
                ("Data Scientist | CloudScale Technologies (2022 - Present)", "Designed and deployed customer lifetime value and churn prediction models using Scikit-learn and XGBoost, improving retention by 18%. Executed statistical A/B testing and engineered high-throughput features using Python and SQL."),
                ("Junior Data Analyst | Apex Insights (2020 - 2022)", "Constructed automated executive dashboards in Tableau and Power BI. Wrote complex PostgreSQL queries to extract metrics for cross-functional stakeholders. Cleaned and processed raw telemetry data using Pandas.")
            ],
            "education": "Master of Science in Data Science | University of Washington (2020)\nBachelor of Technology in Computer Science (2018)"
        },
        {
            "filename": "Sample_FullStack_Developer.pdf",
            "name": "Alex Rodriguez",
            "title": "Full Stack Web Developer",
            "email": "alex.rodriguez@example.com",
            "phone": "+1 (555) 345-6789",
            "linkedin": "linkedin.com/in/alexr-dev",
            "github": "github.com/alexrodriguez-web",
            "summary": "Versatile Full Stack Developer with 4 years of hands-on experience building scalable web applications and REST APIs. Proficient in modern JavaScript, TypeScript, React, Next.js, Node.js, Express, and PostgreSQL with strong focus on responsive design and clean architecture.",
            "skills": "JavaScript, TypeScript, React, Next.js, Node.js, Express.js, PostgreSQL, MongoDB, HTML5, CSS3, Tailwind CSS, REST API, Git, Docker, CI/CD, Agile, Scrum, Unit Testing, Creative Problem Solving, Teamwork",
            "experience": [
                ("Full Stack Engineer | Horizon Digital (2022 - Present)", "Architected and delivered customer-facing dashboard using React, TypeScript, and Next.js. Engineered microservices backend with Node.js and Express, integrated PostgreSQL with Prisma ORM, and set up Dockerized CI/CD pipelines via GitHub Actions."),
                ("Frontend Developer | ByteWave Studios (2020 - 2022)", "Developed reusable UI component library using React and Tailwind CSS. Integrated RESTful endpoints and optimized web performance achieving 95+ Google Lighthouse scores.")
            ],
            "education": "Bachelor of Science in Computer Science | San Jose State University (2020)"
        },
        {
            "filename": "Sample_DevOps_Engineer.pdf",
            "name": "David Kim",
            "title": "Cloud & DevOps Engineer",
            "email": "david.kim@example.com",
            "phone": "+1 (555) 456-7890",
            "linkedin": "linkedin.com/in/davidkim-ops",
            "github": "github.com/davidkim-cloud",
            "summary": "Results-oriented Cloud & DevOps Engineer with 4+ years of expertise in AWS cloud architecture, container orchestration with Kubernetes, Infrastructure as Code with Terraform, and zero-downtime CI/CD delivery pipelines.",
            "skills": "AWS, Docker, Kubernetes, Terraform, CI/CD, GitHub Actions, Jenkins, Linux, Bash, Python, Prometheus, Grafana, Ansible, Git, Network Security, Troubleshooting, Crisis Management, Cross-functional Collaboration",
            "experience": [
                ("DevOps Engineer | NexaCloud Infrastructure (2021 - Present)", "Managed 50+ production microservices deployed on AWS EKS (Kubernetes). Automated multi-region infrastructure provisioning using Terraform. Built end-to-end automated deployment pipelines with GitHub Actions, reducing release cycle time by 45%."),
                ("Systems Administrator | CyberCore Solutions (2019 - 2021)", "Maintained Linux servers, managed Docker containers, configured firewall rules, and implemented centralized monitoring using Prometheus and Grafana.")
            ],
            "education": "Bachelor of Science in Information Technology | Purdue University (2019)"
        },
        {
            "filename": "Sample_Fresh_Graduate.pdf",
            "name": "Emily Watson",
            "title": "Aspiring Software Engineer / Computer Science Graduate",
            "email": "emily.watson@example.com",
            "phone": "+1 (555) 567-8901",
            "linkedin": "linkedin.com/in/emily-watson-cs",
            "github": "github.com/emilywatson",
            "summary": "Recent Computer Science graduate with strong theoretical foundations in algorithms, object-oriented programming, and database systems. Passionate about software development with practical internship experience in Python, SQL, and web technologies.",
            "skills": "Python, Java, C++, SQL, Data Structures & Algorithms, Object-Oriented Programming (OOP), Git, HTML, CSS, Problem Solving, Fast Learner, Written Communication, Teamwork",
            "experience": [
                ("Software Engineering Intern | TechStart Labs (Summer 2023)", "Collaborated with agile team to build backend modules in Python. Wrote unit tests and optimized SQL queries, increasing query execution speed by 15%."),
                ("Undergraduate Capstone Project (2023)", "Developed a student course scheduling web app using Python, Flask, and SQLite. Implemented graph-based conflict detection algorithms.")
            ],
            "education": "Bachelor of Technology in Computer Science | State University (Graduated May 2024, GPA: 3.8/4.0)"
        }
    ]

    styles = getSampleStyleSheet()
    name_style = ParagraphStyle('Name', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#1E293B'))
    title_style = ParagraphStyle('Title', parent=styles['Normal'], fontSize=11, leading=15, textColor=colors.HexColor('#4F46E5'))
    meta_style = ParagraphStyle('Meta', parent=styles['Normal'], fontSize=8.5, leading=12, textColor=colors.HexColor('#64748B'))
    sec_style = ParagraphStyle('Sec', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#1E293B'), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#334155'))

    for s in samples:
        path = os.path.join("assets/samples", s["filename"])
        doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=36, bottomMargin=36)
        story = []

        story.append(Paragraph(f"<b>{s['name']}</b>", name_style))
        story.append(Paragraph(f"<b>{s['title']}</b>", title_style))
        story.append(Spacer(1, 3))
        story.append(Paragraph(f"Email: {s['email']} | Phone: {s['phone']} | {s['linkedin']} | {s['github']}", meta_style))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=8))

        story.append(Paragraph("<b>PROFESSIONAL SUMMARY</b>", sec_style))
        story.append(Paragraph(s["summary"], body_style))
        story.append(Spacer(1, 6))

        story.append(Paragraph("<b>TECHNICAL & PROFESSIONAL SKILLS</b>", sec_style))
        story.append(Paragraph(s["skills"], body_style))
        story.append(Spacer(1, 6))

        story.append(Paragraph("<b>PROFESSIONAL EXPERIENCE</b>", sec_style))
        for exp_title, exp_desc in s["experience"]:
            story.append(Paragraph(f"<b>{exp_title}</b>", body_style))
            story.append(Paragraph(exp_desc, body_style))
            story.append(Spacer(1, 4))

        story.append(Paragraph("<b>EDUCATION</b>", sec_style))
        story.append(Paragraph(s["education"].replace("\n", "<br/>"), body_style))

        doc.build(story)
        print(f"Generated {path}")

if __name__ == "__main__":
    generate_sample_pdfs()

