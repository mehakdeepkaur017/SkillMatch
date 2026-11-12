"""
Script to train and serialize the NLP models for SkillMatch AI:
1. TF-IDF Vectorizer for semantic text representation and cosine similarity.
2. Supervised Job-Role & Category Classification Model (Multinomial Logistic Regression)
   evaluated rigorously using Stratified K-Fold Cross-Validation.

DATASET NOTE:
This training set is a curated starter benchmark dataset composed of representative job descriptions,
skill requirement variations, and candidate experience patterns across 15 technical roles and 5 domains.
It serves as a benchmark model for domain affinity ranking and prototype categorization.
"""
import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

def train_and_save_models():
    os.makedirs("models", exist_ok=True)
    df_roles = pd.read_csv("data/job_roles.csv")
    
    # 1. Prepare corpus for TF-IDF Vectorizer
    corpus = []
    for _, row in df_roles.iterrows():
        tech_skills = " ".join(row['required_technical_skills'].split(';'))
        soft_skills = " ".join(row['required_soft_skills'].split(';'))
        pref_skills = " ".join(str(row['preferred_skills']).split(';'))
        text = f"{row['job_title']} {row['category']} {row['job_description']} {tech_skills} {soft_skills} {pref_skills}"
        corpus.append(text)
        
    # Fit TF-IDF Vectorizer with unigrams & bigrams, sublinear tf scaling
    tfidf_vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words='english',
        sublinear_tf=True,
        max_features=5000,
        token_pattern=r'(?u)\b[a-zA-Z0-9_.+#]{2,}\b'
    )
    tfidf_vectorizer.fit(corpus)
    joblib.dump(tfidf_vectorizer, "models/tfidf_vectorizer.pkl")
    print("✓ TF-IDF Vectorizer fitted and saved to models/tfidf_vectorizer.pkl")

    # 2. Build Supervised Dataset for Role & Category Classification
    variations = [
        # Data Analyst
        ("Data Analyst", "Data & Analytics", "Experienced data analyst skilled in SQL, Power BI, Excel data modeling, Tableau dashboards, reporting metrics and business intelligence. Conducted exploratory data analysis, A/B test reporting, and data hygiene."),
        ("Data Analyst", "Data & Analytics", "Junior analyst with strong Python, pandas, SQL queries, Excel pivot tables, data visualization in Matplotlib and Power BI. Experience translating operational requirements into KPI dashboards."),
        ("Data Analyst", "Data & Analytics", "Business data specialist with proficiency in PostgreSQL, BigQuery, Google Analytics, Tableau visual storytelling, statistical summary, and executive presentation."),
        
        # Data Scientist
        ("Data Scientist", "Data & Analytics", "Data Scientist with background in machine learning, statistical modeling, Scikit-learn, XGBoost, feature engineering, hypothesis testing, Python, pandas, and SQL. Deployed predictive customer churn models."),
        ("Data Scientist", "Data & Analytics", "Quantitative researcher proficient in statistical analysis, Python, R, TensorFlow, deep neural networks, clustering, regression models, and data mining on multi-terabyte datasets."),
        ("Data Scientist", "Data & Analytics", "Machine learning practitioner experienced in NLP, supervised classification, random forest, cross validation, Pandas, NumPy, data visualization, and ML model evaluation."),
        
        # Machine Learning Engineer
        ("Machine Learning Engineer", "Data & Analytics", "ML Engineer focusing on productionizing deep learning models using PyTorch, FastAPI microservices, Docker containers, MLflow tracking, and model monitoring in AWS."),
        ("Machine Learning Engineer", "Data & Analytics", "Software engineer turned machine learning practitioner. Skilled in Python, Scikit-learn, TensorFlow, container orchestration, CI/CD pipelines, MLOps, and scalable REST API development."),
        ("Machine Learning Engineer", "Data & Analytics", "Senior AI and ML Engineer with expertise in transformer models, PyTorch, model quantization, ONNX runtime, vector search, Docker, and distributed GPU training."),
        
        # AI Engineer
        ("AI Engineer", "Data & Analytics", "AI Engineer specializing in Generative AI, Retrieval-Augmented Generation (RAG), LangChain, ChromaDB vector databases, prompt engineering, and fine-tuning Llama/OpenAI models using Python."),
        ("AI Engineer", "Data & Analytics", "NLP and AI Specialist with hands-on experience in Hugging Face transformers, PyTorch, semantic search, vector embeddings, FastAPI backend, and conversational AI agents."),
        ("AI Engineer", "Data & Analytics", "Software developer building enterprise generative AI tools. Proficient in Python, LangChain, vector databases, LLM orchestration, Docker, and automated agent workflows."),

        # Python Developer
        ("Python Developer", "Software Engineering", "Backend Python Developer experienced with Django REST framework, FastAPI, PostgreSQL database optimization, Celery asynchronous tasks, Redis caching, and PyTest."),
        ("Python Developer", "Software Engineering", "Python Software Engineer with focus on building scalable web services, microservices, API integrations, Docker deployment, Git version control, and clean architecture."),
        ("Python Developer", "Software Engineering", "Full lifecycle software developer skilled in Python 3, Flask, SQL, ORM, object-oriented programming, unit testing, automated scripts, and cloud backend engineering."),

        # Full Stack Web Developer
        ("Full Stack Web Developer", "Software Engineering", "Full Stack Developer proficient in React, TypeScript, Node.js, Express, MongoDB, PostgreSQL, Tailwind CSS, REST APIs, Git, and deploying on AWS cloud."),
        ("Full Stack Web Developer", "Software Engineering", "Web application engineer with strong skills in JavaScript, HTML5, CSS3, React frontend, Node backend, RESTful services, Redux state management, and responsive UI design."),
        ("Full Stack Web Developer", "Software Engineering", "Modern full-stack developer skilled in Next.js, React, TypeScript, GraphQL, PostgreSQL, Docker, CI/CD pipelines, and responsive mobile-first web apps."),

        # Frontend Developer
        ("Frontend Developer", "Software Engineering", "Frontend specialist with mastery in React, TypeScript, JavaScript, CSS3, Tailwind CSS, HTML5, Redux, user experience, cross-browser compatibility, and Figma to code."),
        ("Frontend Developer", "Software Engineering", "UI Developer experienced in Vue.js, React, modern web standards, CSS animations, responsive layouts, web accessibility WCAG, and front-end performance tuning."),
        ("Frontend Developer", "Software Engineering", "Web developer focusing on frontend interfaces using JavaScript ES6, React, Next.js, state management, REST API integration, and component testing with Jest."),

        # Backend Developer
        ("Backend Developer", "Software Engineering", "Backend Software Engineer specializing in Java, Spring Boot, microservices architecture, PostgreSQL, Redis caching, Apache Kafka event streaming, and high throughput APIs."),
        ("Backend Developer", "Software Engineering", "Server-side developer with experience in Java, Spring, RESTful API design, database connection pooling, Docker, Kubernetes, CI/CD, and system scalability."),
        ("Backend Developer", "Software Engineering", "Backend architect with expertise in Go, Node.js, relational database indexing, distributed systems, gRPC, Docker microservices, and Linux server environments."),

        # Data Engineer
        ("Data Engineer", "Data & Analytics", "Data Engineer experienced in designing distributed data pipelines with Apache Spark, PySpark, Apache Airflow DAGs, Snowflake data warehousing, and ETL workflow automation."),
        ("Data Engineer", "Data & Analytics", "Big Data Developer skilled in SQL, Python, dbt, Apache Kafka real-time streaming, AWS Redshift, data modeling, schema design, and data lake architectures."),
        ("Data Engineer", "Data & Analytics", "Data infrastructure engineer proficient in ETL pipelines, Python, PostgreSQL, Google BigQuery, Databricks, Apache Airflow, and data quality validation."),

        # Cloud / DevOps Engineer
        ("Cloud / DevOps Engineer", "Cloud & Infrastructure", "DevOps Engineer with expertise in AWS, Docker containers, Kubernetes orchestration, Terraform Infrastructure as Code, GitHub Actions CI/CD, and Linux administration."),
        ("Cloud / DevOps Engineer", "Cloud & Infrastructure", "Cloud Platform Engineer experienced in Microsoft Azure, Docker, Helm, Prometheus and Grafana monitoring, shell scripting, Ansible automation, and security hardening."),
        ("Cloud / DevOps Engineer", "Cloud & Infrastructure", "Site Reliability Engineer (SRE) proficient in CI/CD pipeline automation, Kubernetes clusters, AWS cloud infrastructure, Terraform, Linux bash scripting, and zero downtime deployments."),

        # Cyber Security Analyst
        ("Cyber Security Analyst", "Cybersecurity", "Cyber Security Analyst with experience in network security, SIEM monitoring, vulnerability assessment, Wireshark packet analysis, firewall configuration, and incident response."),
        ("Cyber Security Analyst", "Cybersecurity", "Information security specialist skilled in penetration testing, ethical hacking, OWASP Top 10 vulnerabilities, cryptography, threat hunting, and security compliance."),
        ("Cyber Security Analyst", "Cybersecurity", "Security operations center (SOC) analyst proficient in SIEM alert triage, incident investigation, Linux security, identity and access management, and threat intelligence."),

        # Database Administrator
        ("Database Administrator", "Cloud & Infrastructure", "Database Administrator (DBA) experienced in PostgreSQL and MySQL administration, high availability clusters, replication, backup recovery, query optimization, and index tuning."),
        ("Database Administrator", "Cloud & Infrastructure", "Database Engineer skilled in SQL server, MongoDB NoSQL, database performance profiling, data migration, security access controls, and Linux server configuration."),
        ("Database Administrator", "Cloud & Infrastructure", "Senior DBA proficient in relational schema design, database clustering, PostgreSQL vacuuming and query plan analysis, automated backups, and disaster recovery planning."),

        # Business Analyst
        ("Business Analyst", "Business & Analytics", "Business Analyst with expertise in requirements gathering, agile user stories, Jira, process modeling, stakeholder communication, Excel financial modeling, and Power BI reporting."),
        ("Business Analyst", "Business & Analytics", "Product-oriented business analyst experienced in gap analysis, workflow diagrams, SQL queries for business data, acceptance criteria definition, and UAT coordination."),
        ("Business Analyst", "Business & Analytics", "Operations Analyst skilled in business process improvement, executive KPI dashboards, Power BI, Excel pivot tables, cross-functional collaboration, and strategic analysis."),

        # QA Automation Engineer
        ("QA Automation Engineer", "Software Engineering", "QA Automation Engineer skilled in Python test automation, Selenium WebDriver, PyTest, REST API testing with Postman, CI/CD test integration, and bug tracking in Jira."),
        ("QA Automation Engineer", "Software Engineering", "Software Development Engineer in Test (SDET) experienced in automated end-to-end testing, test framework development, performance testing, and regression suites."),
        ("QA Automation Engineer", "Software Engineering", "Quality assurance professional proficient in test plan creation, test-driven development (TDD), automated UI testing, API verification, and defect reporting."),

        # Mobile App Developer
        ("Mobile App Developer", "Software Engineering", "Mobile Application Developer with experience in Flutter, Dart, React Native, cross-platform iOS and Android apps, REST API integration, and app store deployment."),
        ("Mobile App Developer", "Software Engineering", "iOS and Android Engineer skilled in Swift, Kotlin, mobile UI design, state management, mobile database SQLite, push notifications, and mobile app performance optimization."),
        ("Mobile App Developer", "Software Engineering", "React Native developer experienced in TypeScript, mobile navigation, Redux, REST API consumption, responsive mobile interfaces, and debugging mobile crashes.")
    ]
    
    # Add official benchmark descriptions
    for _, row in df_roles.iterrows():
        variations.append((
            row['job_title'],
            row['category'],
            f"{row['job_title']}: {row['job_description']} Requires: {row['required_technical_skills']} {row['required_soft_skills']}"
        ))

    df_train = pd.DataFrame(variations, columns=['job_title', 'category', 'text'])
    
    # Encoders
    le_cat = LabelEncoder()
    y_cat = le_cat.fit_transform(df_train['category'])
    
    le_role = LabelEncoder()
    y_role = le_role.fit_transform(df_train['job_title'])
    
    X = tfidf_vectorizer.transform(df_train['text'])
    
    # 3. Stratified K-Fold Cross-Validation for Category Model
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    clf_cat = LogisticRegression(C=1.0, max_iter=200, class_weight='balanced', random_state=42)
    cv_scores_cat = cross_val_score(clf_cat, X, y_cat, cv=skf, scoring='accuracy')
    mean_cat_acc = float(np.mean(cv_scores_cat))
    std_cat_acc = float(np.std(cv_scores_cat))
    print(f"✓ Category Classifier 5-Fold CV Accuracy: {mean_cat_acc * 100:.2f}% (±{std_cat_acc * 100:.2f}%)")

    # Fit final models on full benchmark dataset
    clf_cat.fit(X, y_cat)
    
    clf_role = LogisticRegression(C=1.0, max_iter=200, class_weight='balanced', random_state=42)
    clf_role.fit(X, y_role)
    
    # Save artifacts
    joblib.dump(clf_cat, "models/category_classifier.pkl")
    joblib.dump(le_cat, "models/category_label_encoder.pkl")
    joblib.dump(clf_role, "models/role_classifier.pkl")
    joblib.dump(le_role, "models/role_label_encoder.pkl")
    
    # Save model metadata with validation disclosure
    metadata = {
        "dataset_type": "Curated Starter Benchmark Dataset (15 Roles, 5 Categories)",
        "num_roles": len(df_roles),
        "num_training_samples": len(df_train),
        "validation_strategy": "Stratified 5-Fold Cross-Validation",
        "category_cv_accuracy_mean": mean_cat_acc,
        "category_cv_accuracy_std": std_cat_acc,
        "categories": list(le_cat.classes_),
        "roles": list(le_role.classes_),
        "note": (
            "Metrics reflect performance on the curated starter benchmark corpus. "
            "Confidence levels represent softmax class probabilities and should be interpreted "
            "as domain alignment indicators rather than real-world hiring probabilities."
        )
    }
    with open("models/model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print("✓ Model training and metadata serialization completed successfully!")

if __name__ == "__main__":
    train_and_save_models()
