"""
Script to generate the comprehensive skills taxonomy, job roles dataset,
and verified learning resources for SkillMatch AI.
"""
import json
import os
import pandas as pd

def build_skills_taxonomy():
    taxonomy = {
        "technical_skills": {
            "Programming Languages": [
                "Python", "Java", "C++", "C#", "C", "JavaScript", "TypeScript",
                "Go", "Rust", "Ruby", "PHP", "Kotlin", "Swift", "Scala", "R",
                "SQL", "Bash", "Shell", "PowerShell", "Dart", "HTML5", "CSS3"
            ],
            "Web & Frameworks": [
                "React", "Angular", "Vue.js", "Next.js", "Node.js", "Express.js",
                "Django", "Flask", "FastAPI", "Spring Boot", "ASP.NET", "Ruby on Rails",
                "GraphQL", "REST API", "Tailwind CSS", "Bootstrap", "Redux", "WebSockets",
                "HTML", "CSS", "Sass", "jQuery", "Microfrontends"
            ],
            "Machine Learning & AI": [
                "Machine Learning", "Deep Learning", "Natural Language Processing",
                "Computer Vision", "Scikit-learn", "TensorFlow", "PyTorch", "Keras",
                "Hugging Face", "Transformers", "Large Language Models", "LLMs",
                "LangChain", "OpenCV", "NLTK", "spaCy", "Pandas", "NumPy", "SciPy",
                "Matplotlib", "Seaborn", "Statsmodels", "XGBoost", "LightGBM", "CatBoost",
                "Prompt Engineering", "Fine-tuning", "Retrieval-Augmented Generation (RAG)",
                "Vector Databases", "ChromaDB", "FAISS", "Pinecone"
            ],
            "Data Engineering & Databases": [
                "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Cassandra",
                "Snowflake", "Databricks", "Apache Spark", "Apache Kafka", "Hadoop",
                "Apache Airflow", "dbt", "ETL", "ELT", "Data Warehousing", "Data Modeling",
                "Google BigQuery", "Amazon Redshift", "Elasticsearch", "Neo4j", "DynamoDB"
            ],
            "Cloud & DevOps": [
                "AWS", "Microsoft Azure", "Google Cloud Platform (GCP)", "Docker",
                "Kubernetes", "Terraform", "CI/CD", "GitHub Actions", "Jenkins",
                "Linux", "Ansible", "Helm", "Prometheus", "Grafana", "Serverless",
                "AWS Lambda", "CloudFormation", "Nginx", "Git", "GitHub", "GitLab"
            ],
            "Business Intelligence & Analytics": [
                "Power BI", "Tableau", "Excel", "Advanced Excel", "Looker",
                "Google Analytics", "DAX", "Data Visualization", "Statistical Analysis",
                "A/B Testing", "Business Intelligence", "KPI Dashboards", "Metabase"
            ],
            "Cybersecurity & Networking": [
                "Network Security", "Penetration Testing", "Vulnerability Assessment",
                "SIEM", "Cryptography", "OWASP", "Firewall", "Wireshark", "Ethical Hacking",
                "Incident Response", "Identity and Access Management (IAM)", "Zero Trust"
            ],
            "Software Engineering & Architecture": [
                "Data Structures & Algorithms", "Object-Oriented Programming (OOP)",
                "System Design", "Microservices", "Design Patterns", "Unit Testing",
                "Test-Driven Development (TDD)", "Agile", "Scrum", "Jira", "Software Architecture",
                "Clean Code", "API Design", "Code Review"
            ]
        },
        "soft_skills": {
            "Communication": [
                "Written Communication", "Verbal Communication", "Presentation Skills",
                "Public Speaking", "Active Listening", "Technical Writing", "Documentation"
            ],
            "Leadership & Management": [
                "Team Leadership", "Project Management", "Mentorship", "Stakeholder Management",
                "Agile Leadership", "Decision Making", "Conflict Resolution", "Strategic Thinking"
            ],
            "Problem Solving": [
                "Critical Thinking", "Analytical Skills", "Creative Problem Solving",
                "Troubleshooting", "Root Cause Analysis", "Debugging", "Research Skills"
            ],
            "Collaboration & Teamwork": [
                "Cross-functional Collaboration", "Teamwork", "Empathy", "Adaptability",
                "Interpersonal Skills", "Relationship Building", "Peer Review"
            ],
            "Work Ethic & Productivity": [
                "Time Management", "Attention to Detail", "Fast Learner", "Self-motivation",
                "Work Prioritization", "Accountability", "Stress Management", "Resilience"
            ]
        },
        "aliases": {
            "js": "JavaScript",
            "ts": "TypeScript",
            "py": "Python",
            "reactjs": "React",
            "react.js": "React",
            "vue": "Vue.js",
            "vuejs": "Vue.js",
            "nodejs": "Node.js",
            "node": "Node.js",
            "express": "Express.js",
            "expressjs": "Express.js",
            "k8s": "Kubernetes",
            "postgres": "PostgreSQL",
            "pgsql": "PostgreSQL",
            "sklearn": "Scikit-learn",
            "scikit learn": "Scikit-learn",
            "tf": "TensorFlow",
            "torch": "PyTorch",
            "powerbi": "Power BI",
            "power-bi": "Power BI",
            "aws cloud": "AWS",
            "amazon web services": "AWS",
            "gcp": "Google Cloud Platform (GCP)",
            "google cloud": "Google Cloud Platform (GCP)",
            "azure": "Microsoft Azure",
            "ms azure": "Microsoft Azure",
            "ml": "Machine Learning",
            "dl": "Deep Learning",
            "nlp": "Natural Language Processing",
            "cv": "Computer Vision",
            "llm": "Large Language Models",
            "llms": "Large Language Models",
            "rag": "Retrieval-Augmented Generation (RAG)",
            "ci-cd": "CI/CD",
            "cicd": "CI/CD",
            "continuous integration": "CI/CD",
            "oop": "Object-Oriented Programming (OOP)",
            "dsa": "Data Structures & Algorithms",
            "tdd": "Test-Driven Development (TDD)",
            "bi": "Business Intelligence",
            "ms excel": "Excel",
            "bigquery": "Google BigQuery",
            "redshift": "Amazon Redshift",
            "airflow": "Apache Airflow",
            "kafka": "Apache Kafka",
            "spark": "Apache Spark",
            "gh actions": "GitHub Actions",
            "problem-solving": "Creative Problem Solving",
            "critical-thinking": "Critical Thinking",
            "leadership": "Team Leadership",
            "communication": "Verbal Communication",
            "team player": "Teamwork",
            "team-player": "Teamwork"
        }
    }
    
    with open("data/skills_taxonomy.json", "w", encoding="utf-8") as f:
        json.dump(taxonomy, f, indent=2)
    print("Created data/skills_taxonomy.json")

def build_job_roles_dataset():
    roles = [
        {
            "role_id": "role_da",
            "job_title": "Data Analyst",
            "category": "Data & Analytics",
            "experience_level": "Entry to Mid-Level",
            "education_required": "Bachelor's in Computer Science, Statistics, Mathematics, Economics, or related quantitative field",
            "job_description": "We are seeking a motivated Data Analyst to transform data into meaningful insights. The role involves collecting, cleaning, and analyzing complex datasets to support strategic business decisions. You will design interactive dashboards using Power BI or Tableau, write advanced SQL queries, perform statistical analysis, and collaborate with cross-functional teams to translate business requirements into actionable metrics.",
            "required_technical_skills": "SQL;Python;Power BI;Tableau;Excel;Data Visualization;Statistical Analysis",
            "required_soft_skills": "Analytical Skills;Written Communication;Critical Thinking;Attention to Detail;Presentation Skills",
            "preferred_skills": "R;A/B Testing;Google BigQuery;DAX;ETL",
            "industry_growth_outlook": "High (23% projected growth over the decade)",
            "typical_salary_range": "$65,000 - $95,000"
        },
        {
            "role_id": "role_ds",
            "job_title": "Data Scientist",
            "category": "Data & Analytics",
            "experience_level": "Mid to Senior-Level",
            "education_required": "Bachelor's or Master's in Data Science, Computer Science, Statistics, or Machine Learning",
            "job_description": "Join our analytics team as a Data Scientist to build predictive models and extract value from multi-terabyte datasets. You will be responsible for end-to-end machine learning workflows including exploratory data analysis, feature engineering, model training using Scikit-learn and XGBoost, hyperparameter tuning, and hypothesis testing. Strong proficiency in Python, statistical modeling, and communicating mathematical findings to non-technical stakeholders is required.",
            "required_technical_skills": "Python;Machine Learning;Scikit-learn;SQL;Pandas;NumPy;Statistical Analysis;Data Visualization",
            "required_soft_skills": "Critical Thinking;Verbal Communication;Creative Problem Solving;Research Skills;Teamwork",
            "preferred_skills": "Deep Learning;PyTorch;TensorFlow;Apache Spark;A/B Testing;Docker",
            "industry_growth_outlook": "Very High (35% projected growth)",
            "typical_salary_range": "$95,000 - $145,000"
        },
        {
            "role_id": "role_mle",
            "job_title": "Machine Learning Engineer",
            "category": "Data & Analytics",
            "experience_level": "Mid to Senior-Level",
            "education_required": "Bachelor's or Master's in Computer Science, AI, or Software Engineering",
            "job_description": "As a Machine Learning Engineer, you will bridge the gap between theoretical data science and robust production software. You will design, train, evaluate, and deploy scalable ML systems and deep learning models into microservices. You must possess deep expertise in Python, PyTorch or TensorFlow, Docker containerization, MLOps practices, model monitoring, and REST API development for model inference.",
            "required_technical_skills": "Python;Machine Learning;Deep Learning;PyTorch;TensorFlow;Docker;FastAPI;Scikit-learn;Git",
            "required_soft_skills": "Analytical Skills;Troubleshooting;Cross-functional Collaboration;Fast Learner;Technical Writing",
            "preferred_skills": "Kubernetes;MLflow;AWS;CI/CD;Large Language Models;Vector Databases",
            "industry_growth_outlook": "Exceptional (40% projected growth)",
            "typical_salary_range": "$115,000 - $170,000"
        },
        {
            "role_id": "role_aie",
            "job_title": "AI Engineer",
            "category": "Data & Analytics",
            "experience_level": "Mid-Level",
            "education_required": "Bachelor's in Computer Science, Artificial Intelligence, or equivalent practical experience",
            "job_description": "We are looking for an AI Engineer to build generative AI solutions and LLM-powered applications. Responsibilities include building Retrieval-Augmented Generation (RAG) pipelines, fine-tuning foundation models, managing vector databases like ChromaDB or Pinecone, implementing agentic workflows using LangChain, and integrating AI models into existing enterprise products.",
            "required_technical_skills": "Python;Natural Language Processing;Large Language Models;LangChain;Retrieval-Augmented Generation (RAG);Vector Databases;FastAPI;PyTorch",
            "required_soft_skills": "Creative Problem Solving;Self-motivation;Agile Leadership;Written Communication;Adaptability",
            "preferred_skills": "Prompt Engineering;Hugging Face;Docker;AWS;ChromaDB;Fine-tuning",
            "industry_growth_outlook": "Extremely High (50%+ boom in Generative AI roles)",
            "typical_salary_range": "$120,000 - $180,000"
        },
        {
            "role_id": "role_pydev",
            "job_title": "Python Developer",
            "category": "Software Engineering",
            "experience_level": "Entry to Mid-Level",
            "education_required": "Bachelor's in Computer Science, Software Engineering, or equivalent experience",
            "job_description": "We are seeking a talented Python Developer to engineer backend services, web applications, and automation scripts. You will develop RESTful APIs using Django or FastAPI, optimize database queries in PostgreSQL, write automated unit tests, and maintain clean, well-documented code adhering to PEP 8 standards. Familiarity with Git workflows and Docker is required.",
            "required_technical_skills": "Python;Django;FastAPI;PostgreSQL;REST API;Git;Unit Testing;Docker",
            "required_soft_skills": "Problem Solving;Teamwork;Code Review;Attention to Detail;Time Management",
            "preferred_skills": "Redis;Celery;AWS;Linux;GraphQL;Microservices",
            "industry_growth_outlook": "Steady & High (20% projected growth)",
            "typical_salary_range": "$75,000 - $115,000"
        },
        {
            "role_id": "role_fullstack",
            "job_title": "Full Stack Web Developer",
            "category": "Software Engineering",
            "experience_level": "Mid-Level",
            "education_required": "Bachelor's in Computer Science, Information Technology, or Bootcamp graduate",
            "job_description": "Looking for a versatile Full Stack Developer to build responsive, modern web applications from frontend interfaces to backend microservices. You will architect UI components using React and TypeScript, build scalable APIs in Node.js or Python, design database schemas in MongoDB/PostgreSQL, and deploy cloud applications using modern CI/CD pipelines.",
            "required_technical_skills": "JavaScript;TypeScript;React;Node.js;Express.js;PostgreSQL;HTML5;CSS3;Git;REST API",
            "required_soft_skills": "Cross-functional Collaboration;Critical Thinking;Active Listening;Adaptability;Fast Learner",
            "preferred_skills": "Next.js;Docker;Tailwind CSS;GraphQL;AWS;Redux",
            "industry_growth_outlook": "High (25% projected growth)",
            "typical_salary_range": "$85,000 - $130,000"
        },
        {
            "role_id": "role_frontend",
            "job_title": "Frontend Developer",
            "category": "Software Engineering",
            "experience_level": "Entry to Mid-Level",
            "education_required": "Bachelor's in Computer Science, Design, or equivalent portfolio experience",
            "job_description": "Seeking a creative and detail-oriented Frontend Developer to build intuitive, accessible, and high-performance user interfaces. You will translate Figma wireframes into modular React or Vue.js components, style with Tailwind CSS, manage state with Redux or Context API, optimize Core Web Vitals, and ensure cross-browser compatibility.",
            "required_technical_skills": "JavaScript;TypeScript;React;HTML5;CSS3;Tailwind CSS;Redux;Git;REST API",
            "required_soft_skills": "Attention to Detail;Creative Problem Solving;Teamwork;Verbal Communication;Empathy",
            "preferred_skills": "Next.js;Vue.js;Unit Testing;Jest;Figma;WebSockets",
            "industry_growth_outlook": "High (18% projected growth)",
            "typical_salary_range": "$70,000 - $110,000"
        },
        {
            "role_id": "role_backend",
            "job_title": "Backend Developer",
            "category": "Software Engineering",
            "experience_level": "Mid-Level",
            "education_required": "Bachelor's in Computer Science or Software Engineering",
            "job_description": "We need a Backend Developer to build high-concurrency microservices, robust data ingestion pipelines, and resilient APIs. You will write efficient server-side logic in Java (Spring Boot) or Node.js/Go, optimize relational and NoSQL databases, handle caching strategies using Redis, and design scalable asynchronous event-driven architectures with Apache Kafka.",
            "required_technical_skills": "Java;Spring Boot;PostgreSQL;Redis;REST API;Docker;Git;Microservices;System Design",
            "required_soft_skills": "Analytical Skills;Troubleshooting;Strategic Thinking;Team Leadership;Technical Writing",
            "preferred_skills": "Apache Kafka;Kubernetes;AWS;GraphQL;CI/CD;Unit Testing",
            "industry_growth_outlook": "High (21% projected growth)",
            "typical_salary_range": "$90,000 - $135,000"
        },
        {
            "role_id": "role_de",
            "job_title": "Data Engineer",
            "category": "Data & Analytics",
            "experience_level": "Mid to Senior-Level",
            "education_required": "Bachelor's in Computer Science, Data Engineering, or related technical field",
            "job_description": "Join our data infrastructure team as a Data Engineer to design, build, and maintain mission-critical data pipelines. You will develop automated ETL/ELT workflows using Apache Airflow and dbt, write distributed data transformations in PySpark, manage cloud data warehouses like Snowflake and BigQuery, and ensure strict data quality, governance, and low-latency availability.",
            "required_technical_skills": "Python;SQL;Apache Spark;Apache Airflow;Snowflake;ETL;Data Warehousing;PostgreSQL;Git",
            "required_soft_skills": "Analytical Skills;Problem Solving;Stakeholder Management;Attention to Detail;Resilience",
            "preferred_skills": "dbt;Apache Kafka;Databricks;AWS;Docker;Google BigQuery",
            "industry_growth_outlook": "Very High (30% projected growth)",
            "typical_salary_range": "$105,000 - $155,000"
        },
        {
            "role_id": "role_devops",
            "job_title": "Cloud / DevOps Engineer",
            "category": "Cloud & Infrastructure",
            "experience_level": "Mid-Level",
            "education_required": "Bachelor's in Computer Science, Information Systems, or relevant certifications",
            "job_description": "We are hiring a Cloud & DevOps Engineer to automate and scale our cloud platform. You will manage AWS/Azure infrastructure using Terraform Infrastructure-as-Code, configure Kubernetes clusters, set up robust CI/CD deployment pipelines using GitHub Actions, monitor system health with Prometheus and Grafana, and implement security hardening best practices.",
            "required_technical_skills": "AWS;Docker;Kubernetes;Terraform;CI/CD;GitHub Actions;Linux;Bash;Git",
            "required_soft_skills": "Troubleshooting;Crisis Management;Cross-functional Collaboration;Fast Learner;Decision Making",
            "preferred_skills": "Ansible;Prometheus;Grafana;Microsoft Azure;Python;Helm;Serverless",
            "industry_growth_outlook": "Very High (28% projected growth)",
            "typical_salary_range": "$100,000 - $150,000"
        },
        {
            "role_id": "role_sec",
            "job_title": "Cyber Security Analyst",
            "category": "Cybersecurity",
            "experience_level": "Entry to Mid-Level",
            "education_required": "Bachelor's in Cybersecurity, Computer Science, or Security Certifications (CompTIA Security+, CEH)",
            "job_description": "Protect our organization's information assets as a Cyber Security Analyst. You will monitor security incident and event management (SIEM) systems, perform vulnerability assessments, investigate security alerts, conduct penetration testing, enforce zero-trust security policies, and respond to potential breach incidents in real time.",
            "required_technical_skills": "Network Security;Penetration Testing;SIEM;Vulnerability Assessment;Firewall;Wireshark;Linux;Cryptography",
            "required_soft_skills": "Critical Thinking;Attention to Detail;Crisis Management;Technical Writing;Ethical Hacking Mindset",
            "preferred_skills": "Python;OWASP;Incident Response;Identity and Access Management (IAM);CISSP;Bash",
            "industry_growth_outlook": "Exceptional (32% projected growth)",
            "typical_salary_range": "$80,000 - $125,000"
        },
        {
            "role_id": "role_dba",
            "job_title": "Database Administrator",
            "category": "Cloud & Infrastructure",
            "experience_level": "Mid-Level",
            "education_required": "Bachelor's in Computer Science, Database Administration, or Information Technology",
            "job_description": "Seeking an experienced Database Administrator to ensure database performance, high availability, security, and disaster recovery. You will administer PostgreSQL, MySQL, and MongoDB instances, perform index tuning, manage automated backups and replication, configure data encryption, and optimize high-throughput database queries for production applications.",
            "required_technical_skills": "PostgreSQL;MySQL;SQL;MongoDB;Database Administration;Linux;Performance Tuning;Bash",
            "required_soft_skills": "Attention to Detail;Root Cause Analysis;Time Management;Stress Management;Documentation",
            "preferred_skills": "Redis;Snowflake;AWS;Docker;Python;Disaster Recovery",
            "industry_growth_outlook": "Moderate (12% projected growth)",
            "typical_salary_range": "$85,000 - $120,000"
        },
        {
            "role_id": "role_ba",
            "job_title": "Business Analyst",
            "category": "Business & Analytics",
            "experience_level": "Entry to Mid-Level",
            "education_required": "Bachelor's in Business Administration, Information Systems, Economics, or Computer Science",
            "job_description": "We are seeking a Business Analyst to serve as the vital link between our business objectives and technology solutions. You will gather business requirements, document user stories in Jira, analyze business processes, create financial and operational dashboards in Excel and Power BI, conduct stakeholder interviews, and support user acceptance testing (UAT).",
            "required_technical_skills": "Excel;Power BI;SQL;Business Intelligence;Jira;Agile;Data Visualization",
            "required_soft_skills": "Stakeholder Management;Presentation Skills;Active Listening;Written Communication;Strategic Thinking",
            "preferred_skills": "Tableau;Python;Scrum;Process Mapping;A/B Testing",
            "industry_growth_outlook": "High (15% projected growth)",
            "typical_salary_range": "$70,000 - $105,000"
        },
        {
            "role_id": "role_qa",
            "job_title": "QA Automation Engineer",
            "category": "Software Engineering",
            "experience_level": "Entry to Mid-Level",
            "education_required": "Bachelor's in Computer Science, Software Engineering, or equivalent testing experience",
            "job_description": "Ensure the highest product quality standards as a QA Automation Engineer. You will design, develop, and maintain automated test suites for web applications and REST APIs using Python or Java, execute regression tests, integrate test automation into CI/CD pipelines, and collaborate with software developers to identify, log, and resolve defects quickly.",
            "required_technical_skills": "Python;Selenium;Unit Testing;REST API;Git;CI/CD;Test-Driven Development (TDD);SQL",
            "required_soft_skills": "Attention to Detail;Analytical Skills;Troubleshooting;Verbal Communication;Teamwork",
            "preferred_skills": "Postman;PyTest;Docker;Jira;JavaScript;Performance Testing",
            "industry_growth_outlook": "High (16% projected growth)",
            "typical_salary_range": "$75,000 - $115,000"
        },
        {
            "role_id": "role_mobile",
            "job_title": "Mobile App Developer",
            "category": "Software Engineering",
            "experience_level": "Mid-Level",
            "education_required": "Bachelor's in Computer Science, Software Engineering, or proven App Store portfolio",
            "job_description": "We are looking for a Mobile Application Developer to build captivating, smooth native and cross-platform mobile apps for iOS and Android. You will write clean mobile application code in Flutter/Dart or React Native or Swift/Kotlin, integrate mobile apps with cloud REST APIs, optimize app memory and battery performance, and manage app store publishing workflows.",
            "required_technical_skills": "Flutter;React Native;Swift;Kotlin;JavaScript;REST API;Git;Mobile App Development",
            "required_soft_skills": "Creative Problem Solving;Self-motivation;Attention to Detail;Teamwork;Fast Learner",
            "preferred_skills": "TypeScript;Firebase;GraphQL;CI/CD;UI/UX Design;Redux",
            "industry_growth_outlook": "High (20% projected growth)",
            "typical_salary_range": "$85,000 - $130,000"
        }
    ]
    
    df = pd.DataFrame(roles)
    df.to_csv("data/job_roles.csv", index=False, encoding="utf-8")
    print(f"Created data/job_roles.csv with {len(roles)} roles.")

def build_learning_resources_catalog():
    resources = {
        "Python": {
            "importance": "Critical",
            "description": "General-purpose programming language essential for Data Science, Backend, and ML.",
            "stages": {
                "Beginner": {
                    "topics": "Syntax, loops, conditionals, functions, lists, dicts, file I/O, error handling",
                    "resources": [
                        {"title": "Python Official Tutorial", "url": "https://docs.python.org/3/tutorial/", "type": "Documentation", "free": True},
                        {"title": "Scientific Computing with Python", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "type": "Interactive Course", "free": True}
                    ]
                },
                "Intermediate": {
                    "topics": "OOP, list comprehensions, decorators, generators, virtual environments, unit tests",
                    "resources": [
                        {"title": "Real Python Tutorials", "url": "https://realpython.com/", "type": "Articles & Guides", "free": True},
                        {"title": "Python for Everybody (Coursera)", "url": "https://www.coursera.org/specializations/python", "type": "Course", "free": True}
                    ]
                },
                "Advanced": {
                    "topics": "Concurrency, asyncio, profiling, memory management, C extensions, metaclasses",
                    "resources": [
                        {"title": "Fluent Python Book / Guide", "url": "https://docs.python.org/3/library/asyncio.html", "type": "Documentation", "free": True}
                    ]
                }
            }
        },
        "SQL": {
            "importance": "Critical",
            "description": "Relational database querying and management standard for extracting business data.",
            "stages": {
                "Beginner": {
                    "topics": "SELECT, WHERE, ORDER BY, GROUP BY, aggregates (COUNT, SUM, AVG), INNER/LEFT JOIN",
                    "resources": [
                        {"title": "SQLBolt - Interactive SQL Lessons", "url": "https://sqlbolt.com/", "type": "Interactive", "free": True},
                        {"title": "W3Schools SQL Tutorial", "url": "https://www.w3schools.com/sql/", "type": "Tutorial", "free": True}
                    ]
                },
                "Intermediate": {
                    "topics": "Subqueries, CTEs (WITH clause), Window Functions (ROW_NUMBER, RANK, OVER), indexes",
                    "resources": [
                        {"title": "Mode Analytics SQL Tutorial", "url": "https://mode.com/sql-tutorial/", "type": "Tutorial", "free": True},
                        {"title": "PostgreSQL Official Documentation", "url": "https://www.postgresql.org/docs/", "type": "Documentation", "free": True}
                    ]
                },
                "Advanced": {
                    "topics": "Query plan optimization (EXPLAIN ANALYZE), partitioning, stored procedures, transactions",
                    "resources": [
                        {"title": "Use The Index, Luke (SQL Performance)", "url": "https://use-the-index-luke.com/", "type": "Guide", "free": True}
                    ]
                }
            }
        },
        "Machine Learning": {
            "importance": "Critical",
            "description": "Algorithmic modeling for regression, classification, clustering, and pattern discovery.",
            "stages": {
                "Beginner": {
                    "topics": "Supervised vs unsupervised, train/test split, linear regression, logistic regression",
                    "resources": [
                        {"title": "Scikit-Learn Getting Started Guide", "url": "https://scikit-learn.org/stable/getting_started.html", "type": "Documentation", "free": True},
                        {"title": "Kaggle Intro to Machine Learning", "url": "https://www.kaggle.com/learn/intro-to-machine-learning", "type": "Interactive Course", "free": True}
                    ]
                },
                "Intermediate": {
                    "topics": "Decision trees, Random Forests, XGBoost, cross-validation, feature engineering, evaluation metrics (ROC-AUC, F1)",
                    "resources": [
                        {"title": "Machine Learning Specialization (Andrew Ng)", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "type": "Course", "free": True},
                        {"title": "Kaggle Intermediate Machine Learning", "url": "https://www.kaggle.com/learn/intermediate-machine-learning", "type": "Interactive", "free": True}
                    ]
                },
                "Advanced": {
                    "topics": "Hyperparameter optimization, pipeline automation, model explainability (SHAP, LIME), MLOps",
                    "resources": [
                        {"title": "Google Machine Learning Crash Course", "url": "https://developers.google.com/machine-learning/crash-course", "type": "Course", "free": True}
                    ]
                }
            }
        },
        "Deep Learning": {
            "importance": "High",
            "description": "Neural network architectures for vision, speech, sequential data, and generative models.",
            "stages": {
                "Beginner": {
                    "topics": "Feedforward neural networks, backpropagation, activation functions, loss functions",
                    "resources": [
                        {"title": "DeepLearning.AI Deep Learning Specialization", "url": "https://www.deeplearning.ai/courses/deep-learning-specialization/", "type": "Course", "free": True},
                        {"title": "PyTorch 60-Minute Blitz", "url": "https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html", "type": "Tutorial", "free": True}
                    ]
                },
                "Intermediate": {
                    "topics": "Convolutional Neural Networks (CNNs), Recurrent Networks (LSTMs), transfer learning",
                    "resources": [
                        {"title": "Fast.ai Practical Deep Learning for Coders", "url": "https://course.fast.ai/", "type": "Course", "free": True}
                    ]
                },
                "Advanced": {
                    "topics": "Transformer architecture, attention mechanisms, fine-tuning LLMs, multi-modal systems",
                    "resources": [
                        {"title": "Hugging Face NLP Course", "url": "https://huggingface.co/learn/nlp-course/chapter1/1", "type": "Interactive Course", "free": True}
                    ]
                }
            }
        },
        "Power BI": {
            "importance": "High",
            "description": "Enterprise business intelligence tool for interactive reports, KPIs, and dashboards.",
            "stages": {
                "Beginner": {
                    "topics": "Importing data, standard chart visuals, filtering, slicers, basic formatting",
                    "resources": [
                        {"title": "Microsoft Power BI Guided Learning", "url": "https://learn.microsoft.com/en-us/power-bi/guided-learning/", "type": "Official Microsoft Learn", "free": True}
                    ]
                },
                "Intermediate": {
                    "topics": "Data modeling, relationships (star schema), DAX calculated columns and basic measures",
                    "resources": [
                        {"title": "SQLBI DAX Guide and Articles", "url": "https://www.sqlbi.com/articles/", "type": "Resource", "free": True}
                    ]
                },
                "Advanced": {
                    "topics": "Advanced DAX (CALCULATE, time intelligence), row-level security (RLS), incremental refresh",
                    "resources": [
                        {"title": "Microsoft Power BI Documentation", "url": "https://learn.microsoft.com/en-us/power-bi/", "type": "Documentation", "free": True}
                    ]
                }
            }
        },
        "Docker": {
            "importance": "High",
            "description": "Container platform standard for isolating dependencies and deploying applications.",
            "stages": {
                "Beginner": {
                    "topics": "Images, containers, Dockerfile creation, docker run, port mapping, environment variables",
                    "resources": [
                        {"title": "Docker Official Getting Started", "url": "https://docs.docker.com/get-started/", "type": "Documentation", "free": True}
                    ]
                },
                "Intermediate": {
                    "topics": "Docker Compose for multi-container apps, volumes, networking, multi-stage builds",
                    "resources": [
                        {"title": "freeCodeCamp Docker Course", "url": "https://www.freecodecamp.org/news/what-is-docker-used-for-a-docker-container-tutorial-for-beginners/", "type": "Tutorial", "free": True}
                    ]
                },
                "Advanced": {
                    "topics": "Production image security, caching optimization, rootless containers, orchestration integration",
                    "resources": [
                        {"title": "Docker Best Practices Guide", "url": "https://docs.docker.com/develop/develop-images/dockerfile_best-practices/", "type": "Documentation", "free": True}
                    ]
                }
            }
        },
        "React": {
            "importance": "Critical",
            "description": "Front-end JavaScript component library powering modern interactive user interfaces.",
            "stages": {
                "Beginner": {
                    "topics": "JSX, functional components, props, state with useState, basic event handling",
                    "resources": [
                        {"title": "React.dev Official Documentation & Quick Start", "url": "https://react.dev/learn", "type": "Official Docs", "free": True}
                    ]
                },
                "Intermediate": {
                    "topics": "useEffect, custom hooks, Context API, React Router, form handling, HTTP requests",
                    "resources": [
                        {"title": "freeCodeCamp React Full Course", "url": "https://www.freecodecamp.org/news/free-react-course-2022/", "type": "Course", "free": True}
                    ]
                },
                "Advanced": {
                    "topics": "Performance optimization (useMemo, useCallback), Server Components, SSR with Next.js, Redux Toolkit",
                    "resources": [
                        {"title": "Next.js Learn Course", "url": "https://nextjs.org/learn", "type": "Interactive Tutorial", "free": True}
                    ]
                }
            }
        },
        "AWS": {
            "importance": "High",
            "description": "Leading cloud platform providing scalable compute, storage, databases, and networking.",
            "stages": {
                "Beginner": {
                    "topics": "EC2 virtual servers, S3 object storage, IAM user roles and permissions, basic networking (VPC)",
                    "resources": [
                        {"title": "AWS Skill Builder Free Cloud Practitioner Path", "url": "https://explore.skillbuilder.aws/", "type": "Official Course", "free": True}
                    ]
                },
                "Intermediate": {
                    "topics": "RDS databases, Lambda serverless functions, ECS container services, CloudWatch monitoring",
                    "resources": [
                        {"title": "AWS Free Tier Hands-on Labs", "url": "https://aws.amazon.com/getting-started/hands-on/", "type": "Hands-on", "free": True}
                    ]
                },
                "Advanced": {
                    "topics": "Infrastructure as Code (Terraform / CloudFormation), multi-region architectures, cost optimization",
                    "resources": [
                        {"title": "AWS Well-Architected Framework", "url": "https://aws.amazon.com/architecture/well-architected/", "type": "Whitepapers", "free": True}
                    ]
                }
            }
        },
        "Git": {
            "importance": "Critical",
            "description": "Distributed version control system for source code tracking and team collaboration.",
            "stages": {
                "Beginner": {
                    "topics": "git init, clone, add, commit, push, pull, status, log",
                    "resources": [
                        {"title": "Git Official Documentation Book", "url": "https://git-scm.com/book/en/v2", "type": "Official Book", "free": True},
                        {"title": "Learn Git Branching (Interactive)", "url": "https://learngitbranching.js.org/", "type": "Interactive Game", "free": True}
                    ]
                },
                "Intermediate": {
                    "topics": "Branching, merging, pull requests, resolving merge conflicts, git stash, rebase",
                    "resources": [
                        {"title": "GitHub Git Handbook", "url": "https://docs.github.com/en/get-started/using-git/about-git", "type": "Documentation", "free": True}
                    ]
                },
                "Advanced": {
                    "topics": "Interactive rebase, cherry-pick, reflog recovery, submodules, Git hooks, commit conventions",
                    "resources": [
                        {"title": "Pro Git Advanced Topics", "url": "https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History", "type": "Documentation", "free": True}
                    ]
                }
            }
        },
        "FastAPI": {
            "importance": "High",
            "description": "Modern, high-performance web framework for building REST APIs with Python 3.8+.",
            "stages": {
                "Beginner": {
                    "topics": "Path parameters, query parameters, request bodies with Pydantic, automatic Swagger docs",
                    "resources": [
                        {"title": "FastAPI Official Tutorial", "url": "https://fastapi.tiangolo.com/tutorial/", "type": "Documentation", "free": True}
                    ]
                },
                "Intermediate": {
                    "topics": "Dependency injection, authentication (OAuth2 / JWT), database integration with SQLAlchemy",
                    "resources": [
                        {"title": "TestDriven.io FastAPI Guides", "url": "https://testdriven.io/guides/", "type": "Tutorials", "free": True}
                    ]
                },
                "Advanced": {
                    "topics": "Background tasks, WebSockets, Docker deployment, production ASGI tuning with Gunicorn/Uvicorn",
                    "resources": [
                        {"title": "FastAPI Deployment Documentation", "url": "https://fastapi.tiangolo.com/deployment/", "type": "Documentation", "free": True}
                    ]
                }
            }
        },
        "Kubernetes": {
            "importance": "High",
            "description": "Automated container orchestration system for deploying, scaling, and managing containerized applications.",
            "stages": {
                "Beginner": {
                    "topics": "Pods, Deployments, Services, Namespaces, basic kubectl commands",
                    "resources": [
                        {"title": "Kubernetes Official Tutorials", "url": "https://kubernetes.io/docs/tutorials/", "type": "Documentation", "free": True}
                    ]
                },
                "Intermediate": {
                    "topics": "ConfigMaps, Secrets, Ingress controllers, PersistentVolumes, Helm package manager",
                    "resources": [
                        {"title": "Kubernetes Basics & Hands-on Labs", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "type": "Tutorials", "free": True}
                    ]
                },
                "Advanced": {
                    "topics": "Custom Resource Definitions (CRDs), Operators, Horizontal Pod Autoscaling, Service Mesh (Istio)",
                    "resources": [
                        {"title": "Kubernetes Production Best Practices", "url": "https://learnk8s.io/production-best-practices", "type": "Guide", "free": True}
                    ]
                }
            }
        },
        "Tableau": {
            "importance": "Medium",
            "description": "Visual analytics platform transforming the way we use data to solve problems.",
            "stages": {
                "Beginner": {
                    "topics": "Dimensions vs Measures, connecting to data, building bar charts, line graphs, maps",
                    "resources": [
                        {"title": "Tableau Free Training Videos", "url": "https://www.tableau.com/learn/training", "type": "Official Videos", "free": True}
                    ]
                },
                "Intermediate": {
                    "topics": "Calculated fields, Table Calculations, Level of Detail (LOD) expressions, interactive dashboards",
                    "resources": [
                        {"title": "Tableau Community Forums & Tutorials", "url": "https://community.tableau.com/", "type": "Community Guides", "free": True}
                    ]
                },
                "Advanced": {
                    "topics": "Performance recording, parameters and dynamic queries, Tableau Server/Cloud administration",
                    "resources": [
                        {"title": "Tableau Documentation & Whitepapers", "url": "https://help.tableau.com/current/pro/desktop/en-us/default.htm", "type": "Documentation", "free": True}
                    ]
                }
            }
        },
        "Default_Resource": {
            "importance": "Medium",
            "description": "Skill foundational concepts, practical application, and integration into projects.",
            "stages": {
                "Beginner": {
                    "topics": "Core syntax, primary concepts, fundamental terminology, and getting-started tutorials",
                    "resources": [
                        {"title": "Roadmap.sh Developer Roadmaps", "url": "https://roadmap.sh/", "type": "Interactive Roadmaps", "free": True},
                        {"title": "freeCodeCamp Tech Curriculum", "url": "https://www.freecodecamp.org/", "type": "Course", "free": True}
                    ]
                },
                "Intermediate": {
                    "topics": "Standard design patterns, testing, performance best practices, and real-world project usage",
                    "resources": [
                        {"title": "MDN Web & Tech Docs", "url": "https://developer.mozilla.org/", "type": "Documentation", "free": True},
                        {"title": "GeeksforGeeks Tech Guides", "url": "https://www.geeksforgeeks.org/", "type": "Tutorials", "free": True}
                    ]
                },
                "Advanced": {
                    "topics": "System architecture, scalability, optimization, production maintenance, and team best practices",
                    "resources": [
                        {"title": "Awesome Cheat Sheets & Curated Guides", "url": "https://github.com/vinta/awesome-python", "type": "Curated List", "free": True}
                    ]
                }
            }
        }
    }
    
    with open("data/learning_resources.json", "w", encoding="utf-8") as f:
        json.dump(resources, f, indent=2)
    print("Created data/learning_resources.json")

if __name__ == "__main__":
    build_skills_taxonomy()
    build_job_roles_dataset()
    build_learning_resources_catalog()

