"""
Database Module for SkillMatch AI
Implements permanent local persistence via SQLite (database/skillmatch.db).
Manages candidates, resume profiles, analysis history, job matches, skill gaps,
career recommendations, and roadmap milestones with full CRUD operations.
"""
import os
import sqlite3
import json
import uuid
import datetime
from typing import Dict, List, Optional, Any, Tuple

DEFAULT_DB_PATH = os.path.join("database", "skillmatch.db")

class DatabaseManager:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """
        Creates and returns a connection to SQLite database with foreign keys enabled
        and Row factory for dictionary-like access.
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        """
        Automatically initializes all 7 required relational tables with indexes.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # 1. Candidates table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            linkedin TEXT,
            github TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Resume profiles table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resume_profiles (
            id TEXT PRIMARY KEY,
            candidate_id TEXT,
            filename TEXT,
            summary TEXT,
            education_json TEXT,
            experience_json TEXT,
            extracted_skills_json TEXT,
            technical_skills_json TEXT,
            soft_skills_json TEXT,
            raw_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        );
        """)

        # 3. Analysis history table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id TEXT PRIMARY KEY,
            candidate_id TEXT,
            resume_profile_id TEXT,
            analysis_title TEXT,
            target_role TEXT,
            job_source TEXT,
            job_description TEXT,
            overall_score REAL,
            technical_score REAL,
            tfidf_score REAL,
            soft_score REAL,
            coverage_percentage REAL,
            weights_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE SET NULL,
            FOREIGN KEY (resume_profile_id) REFERENCES resume_profiles(id) ON DELETE SET NULL
        );
        """)

        # 4. Job matches table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_matches (
            id TEXT PRIMARY KEY,
            analysis_id TEXT UNIQUE,
            matched_technical_json TEXT,
            missing_technical_json TEXT,
            matched_soft_json TEXT,
            missing_soft_json TEXT,
            additional_skills_json TEXT,
            scoring_formula_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id) REFERENCES analysis_history(id) ON DELETE CASCADE
        );
        """)

        # 5. Skill gaps table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS skill_gaps (
            id TEXT PRIMARY KEY,
            analysis_id TEXT UNIQUE,
            prioritized_gaps_json TEXT,
            action_recommendations_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id) REFERENCES analysis_history(id) ON DELETE CASCADE
        );
        """)

        # 6. Career recommendations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_recommendations (
            id TEXT PRIMARY KEY,
            analysis_id TEXT UNIQUE,
            recommendations_json TEXT,
            domain_affinities_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id) REFERENCES analysis_history(id) ON DELETE CASCADE
        );
        """)

        # 7. Learning roadmaps table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_roadmaps (
            id TEXT PRIMARY KEY,
            analysis_id TEXT UNIQUE,
            target_role TEXT,
            roadmap_steps_json TEXT,
            completed_steps_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id) REFERENCES analysis_history(id) ON DELETE CASCADE
        );
        """)

        # Create indexes for fast lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_created ON analysis_history(created_at DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_profile_created ON resume_profiles(created_at DESC);")

        conn.commit()
        conn.close()

    # ----------------------------------------------------
    # CANDIDATE & RESUME PROFILE OPERATIONS
    # ----------------------------------------------------
    def save_or_update_candidate(
        self,
        name: str = "Anonymous Candidate",
        email: str = "",
        phone: str = "",
        linkedin: str = "",
        github: str = "",
        candidate_id: Optional[str] = None
    ) -> str:
        """
        Creates a new candidate record or updates existing if candidate_id provided.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        if not candidate_id:
            # Check if candidate with same email exists
            if email and email.strip():
                cursor.execute("SELECT id FROM candidates WHERE email = ? LIMIT 1", (email.strip(),))
                row = cursor.fetchone()
                if row:
                    candidate_id = row["id"]

        if not candidate_id:
            candidate_id = str(uuid.uuid4())
            cursor.execute("""
            INSERT INTO candidates (id, name, email, phone, linkedin, github, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (candidate_id, name, email, phone, linkedin, github))
        else:
            cursor.execute("""
            UPDATE candidates
            SET name = ?, email = ?, phone = ?, linkedin = ?, github = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (name, email, phone, linkedin, github, candidate_id))

        conn.commit()
        conn.close()
        return candidate_id

    def save_resume_profile(
        self,
        candidate_id: str,
        filename: str,
        summary: str,
        education: list,
        experience: dict,
        all_skills: list,
        technical_skills: list,
        soft_skills: list,
        raw_text: str = ""
    ) -> str:
        """
        Persists extracted resume profile data.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        profile_id = str(uuid.uuid4())

        cursor.execute("""
        INSERT INTO resume_profiles (
            id, candidate_id, filename, summary,
            education_json, experience_json, extracted_skills_json,
            technical_skills_json, soft_skills_json, raw_text, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            profile_id,
            candidate_id,
            filename,
            summary,
            json.dumps(education),
            json.dumps(experience),
            json.dumps(all_skills),
            json.dumps(technical_skills),
            json.dumps(soft_skills),
            raw_text
        ))

        conn.commit()
        conn.close()
        return profile_id

    def get_latest_profile(self) -> Optional[dict]:
        """
        Retrieves the most recent candidate profile to auto-restore session state upon browser refresh.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT p.*, c.name, c.email, c.phone, c.linkedin, c.github
        FROM resume_profiles p
        LEFT JOIN candidates c ON p.candidate_id = c.id
        ORDER BY p.created_at DESC LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None

        return {
            "profile_id": row["id"],
            "candidate_id": row["candidate_id"],
            "filename": row["filename"],
            "summary": row["summary"],
            "education": json.loads(row["education_json"] or "[]"),
            "experience": json.loads(row["experience_json"] or "{}"),
            "candidate_skills": json.loads(row["extracted_skills_json"] or "[]"),
            "technical_skills": json.loads(row["technical_skills_json"] or "[]"),
            "soft_skills": json.loads(row["soft_skills_json"] or "[]"),
            "raw_text": row["raw_text"] or "",
            "contact_info": {
                "name": row["name"],
                "email": row["email"],
                "phone": row["phone"],
                "linkedin": row["linkedin"],
                "github": row["github"]
            },
            "created_at": row["created_at"]
        }

    # ----------------------------------------------------
    # ANALYSIS HISTORY & RESULTS PERSISTENCE
    # ----------------------------------------------------
    def save_full_analysis(
        self,
        candidate_id: Optional[str],
        profile_id: Optional[str],
        target_role: str,
        job_source: str,
        job_description: str,
        match_result: dict,
        gap_result: Optional[dict] = None,
        recommendations: Optional[list] = None,
        domain_affinities: Optional[list] = None,
        roadmap: Optional[list] = None
    ) -> str:
        """
        Atomically saves a complete analysis record across all relational tables:
        analysis_history, job_matches, skill_gaps, career_recommendations, learning_roadmaps.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        analysis_id = str(uuid.uuid4())
        analysis_title = f"{target_role} Compatibility Analysis"

        overall_score = match_result.get("overall_compatibility_score", 0.0)
        breakdown = match_result.get("breakdown", {})
        tech_score = breakdown.get("technical_score", 0.0)
        tfidf_score = breakdown.get("tfidf_similarity_score", 0.0)
        soft_score = breakdown.get("soft_score", 0.0)
        coverage_pct = match_result.get("coverage_percentage", 0.0)
        weights = breakdown.get("weights", {})
        skills_dict = match_result.get("skills", {})

        # Insert analysis_history
        cursor.execute("""
        INSERT INTO analysis_history (
            id, candidate_id, resume_profile_id, analysis_title, target_role,
            job_source, job_description, overall_score, technical_score,
            tfidf_score, soft_score, coverage_percentage, weights_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            analysis_id, candidate_id, profile_id, analysis_title, target_role,
            job_source, job_description, overall_score, tech_score,
            tfidf_score, soft_score, coverage_pct, json.dumps(weights)
        ))

        # Insert job_matches
        match_id = str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO job_matches (
            id, analysis_id, matched_technical_json, missing_technical_json,
            matched_soft_json, missing_soft_json, additional_skills_json,
            scoring_formula_notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            match_id,
            analysis_id,
            json.dumps(skills_dict.get("matched_technical", [])),
            json.dumps(skills_dict.get("missing_technical", [])),
            json.dumps(skills_dict.get("matched_soft", [])),
            json.dumps(skills_dict.get("missing_soft", [])),
            json.dumps(skills_dict.get("additional_skills", [])),
            match_result.get("scoring_formula", {}).get("notes", "")
        ))

        # Insert skill_gaps if present
        if gap_result:
            gap_id = str(uuid.uuid4())
            cursor.execute("""
            INSERT INTO skill_gaps (
                id, analysis_id, prioritized_gaps_json, action_recommendations_json, created_at
            ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                gap_id,
                analysis_id,
                json.dumps(gap_result.get("prioritized_gaps", [])),
                json.dumps(gap_result.get("action_recommendations", []))
            ))

        # Insert career_recommendations if present
        if recommendations or domain_affinities:
            rec_id = str(uuid.uuid4())
            cursor.execute("""
            INSERT INTO career_recommendations (
                id, analysis_id, recommendations_json, domain_affinities_json, created_at
            ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                rec_id,
                analysis_id,
                json.dumps(recommendations or []),
                json.dumps(domain_affinities or [])
            ))

        # Insert learning_roadmaps if present
        if roadmap:
            road_id = str(uuid.uuid4())
            cursor.execute("""
            INSERT INTO learning_roadmaps (
                id, analysis_id, target_role, roadmap_steps_json, completed_steps_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                road_id,
                analysis_id,
                target_role,
                json.dumps(roadmap),
                json.dumps([])  # Initially zero steps completed
            ))

        conn.commit()
        conn.close()
        return analysis_id

    def get_all_analyses(self, limit: int = 50) -> List[dict]:
        """
        Returns summary list of all stored analyses for the history list.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT a.id, a.analysis_title, a.target_role, a.job_source, a.overall_score,
               a.technical_score, a.coverage_percentage, a.created_at,
               p.filename, c.name as candidate_name
        FROM analysis_history a
        LEFT JOIN resume_profiles p ON a.resume_profile_id = p.id
        LEFT JOIN candidates c ON a.candidate_id = c.id
        ORDER BY a.created_at DESC
        LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "title": r["analysis_title"],
                "target_role": r["target_role"],
                "job_source": r["job_source"],
                "overall_score": float(r["overall_score"] or 0.0),
                "technical_score": float(r["technical_score"] or 0.0),
                "coverage_percentage": float(r["coverage_percentage"] or 0.0),
                "created_at": r["created_at"],
                "filename": r["filename"] or "Uploaded Resume",
                "candidate_name": r["candidate_name"] or "Candidate"
            })
        return results

    def get_analysis_details(self, analysis_id: str) -> Optional[dict]:
        """
        Performs a full relational retrieval of an analysis session including:
        history record, profile, job matches, skill gaps, recommendations, and roadmap.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # 1. Base analysis
        cursor.execute("""
        SELECT a.*, p.filename, p.raw_text, p.extracted_skills_json,
               p.technical_skills_json, p.soft_skills_json, p.education_json, p.experience_json,
               c.name as candidate_name, c.email, c.phone, c.linkedin, c.github
        FROM analysis_history a
        LEFT JOIN resume_profiles p ON a.resume_profile_id = p.id
        LEFT JOIN candidates c ON a.candidate_id = c.id
        WHERE a.id = ?
        """, (analysis_id,))
        base = cursor.fetchone()
        if not base:
            conn.close()
            return None

        # 2. Job Matches
        cursor.execute("SELECT * FROM job_matches WHERE analysis_id = ?", (analysis_id,))
        jm = cursor.fetchone()

        # 3. Skill Gaps
        cursor.execute("SELECT * FROM skill_gaps WHERE analysis_id = ?", (analysis_id,))
        sg = cursor.fetchone()

        # 4. Career Recommendations
        cursor.execute("SELECT * FROM career_recommendations WHERE analysis_id = ?", (analysis_id,))
        cr = cursor.fetchone()

        # 5. Learning Roadmaps
        cursor.execute("SELECT * FROM learning_roadmaps WHERE analysis_id = ?", (analysis_id,))
        lr = cursor.fetchone()

        conn.close()

        # Reconstruct match result
        match_result = {
            "overall_compatibility_score": base["overall_score"],
            "coverage_percentage": base["coverage_percentage"],
            "breakdown": {
                "technical_score": base["technical_score"],
                "tfidf_similarity_score": base["tfidf_score"],
                "soft_score": base["soft_score"],
                "weights": json.loads(base["weights_json"] or "{}")
            },
            "skills": {
                "matched_technical": json.loads(jm["matched_technical_json"] if jm else "[]"),
                "missing_technical": json.loads(jm["missing_technical_json"] if jm else "[]"),
                "matched_soft": json.loads(jm["matched_soft_json"] if jm else "[]"),
                "missing_soft": json.loads(jm["missing_soft_json"] if jm else "[]"),
                "additional_skills": json.loads(jm["additional_skills_json"] if jm else "[]")
            }
        }

        gap_result = {
            "prioritized_gaps": json.loads(sg["prioritized_gaps_json"] if sg else "[]"),
            "action_recommendations": json.loads(sg["action_recommendations_json"] if sg else "[]")
        } if sg else None

        recommendations = json.loads(cr["recommendations_json"] if cr else "[]")
        domain_affinities = json.loads(cr["domain_affinities_json"] if cr else "[]")
        
        roadmap_steps = json.loads(lr["roadmap_steps_json"] if lr else "[]")
        completed_steps = json.loads(lr["completed_steps_json"] if lr else "[]")

        return {
            "id": base["id"],
            "title": base["analysis_title"],
            "target_role": base["target_role"],
            "job_source": base["job_source"],
            "job_description": base["job_description"],
            "overall_score": base["overall_score"],
            "created_at": base["created_at"],
            "filename": base["filename"],
            "raw_text": base["raw_text"],
            "candidate_skills": json.loads(base["extracted_skills_json"] or "[]"),
            "technical_skills": json.loads(base["technical_skills_json"] or "[]"),
            "soft_skills": json.loads(base["soft_skills_json"] or "[]"),
            "education": json.loads(base["education_json"] or "[]"),
            "experience": json.loads(base["experience_json"] or "{}"),
            "contact_info": {
                "name": base["candidate_name"],
                "email": base["email"],
                "phone": base["phone"],
                "linkedin": base["linkedin"],
                "github": base["github"]
            },
            "match_result": match_result,
            "gap_result": gap_result,
            "career_recommendations": recommendations,
            "domain_affinities": domain_affinities,
            "roadmap": roadmap_steps,
            "completed_steps": completed_steps
        }

    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Deletes a specific analysis session and cascades to related tables.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analysis_history WHERE id = ?", (analysis_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    def clear_all_history(self) -> int:
        """
        Deletes all analysis history records and associated match, gap, recommendation, and roadmap rows.
        Leaves candidate profiles intact for re-analysis.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analysis_history;")
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_count

    def update_roadmap_progress(self, analysis_id: str, completed_steps: List[int]) -> bool:
        """
        Updates the list of completed step numbers for a specific analysis roadmap.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE learning_roadmaps
        SET completed_steps_json = ?, updated_at = CURRENT_TIMESTAMP
        WHERE analysis_id = ?
        """, (json.dumps(completed_steps), analysis_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    def get_completed_roadmap_steps(self, analysis_id: str) -> List[int]:
        """
        Retrieves list of completed step indices for an analysis.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT completed_steps_json FROM learning_roadmaps WHERE analysis_id = ?", (analysis_id,))
        row = cursor.fetchone()
        conn.close()
        if row and row["completed_steps_json"]:
            return json.loads(row["completed_steps_json"])
        return []

