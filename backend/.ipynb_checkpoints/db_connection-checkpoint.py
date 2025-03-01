import psycopg2
from psycopg2 import sql
from contextlib import closing
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Database configuration
DB_CONFIG = {
    "dbname": "resume_system",
    "user": "postgres",
    "password": "Password@1",  # Change this to your actual DB password
    "host": "localhost",
    "port": "5432",
}

# Establish database connection
def get_db_connection():
    """Returns a PostgreSQL database connection."""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

# ✅ Insert Resume Function with Ranking Score
def insert_resume(name, email, phone, skills, experience, education, file_path, file_format, job_description, ranking_score=0.0):
    """Insert resume details into the database with ranking score."""
    query = """
        INSERT INTO resumes (name, email, phone, skills, experience, education, file_path, file_format, job_description, ranking_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (name, email, phone, skills, experience, education, file_path, file_format, job_description, ranking_score)

    try:
        with closing(get_db_connection()) as conn:
            if conn is None:
                return False
            with closing(conn.cursor()) as cur:
                cur.execute(query, values)
                conn.commit()
                logging.info("Resume details inserted successfully.")
                return True
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
        return False

# ✅ Update Resume Status Function (Missing Function Added)
def update_resume_status(resume_id, status):
    """Update the status of a resume."""
    query = "UPDATE resumes SET status = %s WHERE id = %s"

    try:
        with closing(get_db_connection()) as conn:
            if conn is None:
                return False
            with closing(conn.cursor()) as cur:
                cur.execute(query, (status, resume_id))
                conn.commit()
                logging.info(f"Updated status for Resume ID {resume_id} to '{status}'.")
                return True
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
        return False

# ✅ Update Ranking Score Function
def update_ranking_score(resume_id, new_score):
    """Update ranking score of a resume."""
    query = "UPDATE resumes SET ranking_score = %s WHERE id = %s"

    try:
        with closing(get_db_connection()) as conn:
            if conn is None:
                return False
            with closing(conn.cursor()) as cur:
                cur.execute(query, (new_score, resume_id))
                conn.commit()
                logging.info(f"Updated ranking score for Resume ID {resume_id}.")
                return True
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
        return False

# ✅ Update Resume Function
def update_resume(resume_id, name=None, email=None, phone=None, skills=None, experience=None, education=None, ranking_score=None):
    """Update specific fields of a resume."""
    fields = []
    values = []

    if name:
        fields.append("name = %s")
        values.append(name)
    if email:
        fields.append("email = %s")
        values.append(email)
    if phone:
        fields.append("phone = %s")
        values.append(phone)
    if skills:
        fields.append("skills = %s")
        values.append(skills)
    if experience:
        fields.append("experience = %s")
        values.append(experience)
    if education:
        fields.append("education = %s")
        values.append(education)
    if ranking_score is not None:
        fields.append("ranking_score = %s")
        values.append(ranking_score)

    if not fields:
        logging.warning("No fields provided for update.")
        return False

    values.append(resume_id)
    query = f"UPDATE resumes SET {', '.join(fields)} WHERE id = %s"

    try:
        with closing(get_db_connection()) as conn:
            if conn is None:
                return False
            with closing(conn.cursor()) as cur:
                cur.execute(query, values)
                conn.commit()
                logging.info(f"Resume ID {resume_id} updated successfully.")
                return True
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
        return False

# ✅ Delete Resume Function
def delete_resume(resume_id):
    """Delete a resume from the database."""
    query = "DELETE FROM resumes WHERE id = %s"

    try:
        with closing(get_db_connection()) as conn:
            if conn is None:
                return False
            with closing(conn.cursor()) as cur:
                cur.execute(query, (resume_id,))
                conn.commit()
                logging.info(f"Resume ID {resume_id} deleted successfully.")
                return True
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
        return False

# ✅ Fetch Top Resumes by Ranking Score
def get_top_resumes(limit=10):
    """Fetch resumes sorted by ranking score."""
    query = "SELECT * FROM resumes ORDER BY ranking_score DESC LIMIT %s"

    try:
        with closing(get_db_connection()) as conn:
            if conn is None:
                return []
            with closing(conn.cursor()) as cur:
                cur.execute(query, (limit,))
                return cur.fetchall()
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
        return []

# ✅ Fetch All Resumes
def get_all_resumes():
    """Fetch all resumes from the database."""
    query = "SELECT * FROM resumes"

    try:
        with closing(get_db_connection()) as conn:
            if conn is None:
                return []
            with closing(conn.cursor()) as cur:
                cur.execute(query)
                return cur.fetchall()
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
        return []

# ✅ Fetch Resume by ID
def get_resume_by_id(resume_id):
    """Fetch resume details by ID."""
    query = "SELECT * FROM resumes WHERE id = %s"

    try:
        with closing(get_db_connection()) as conn:
            if conn is None:
                return None
            with closing(conn.cursor()) as cur:
                cur.execute(query, (resume_id,))
                return cur.fetchone()
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
        return None

# ✅ Fetch Resume by Email
def get_resume_by_email(email):
    """Fetch resume details by Email."""
    query = "SELECT * FROM resumes WHERE email = %s"

    try:
        with closing(get_db_connection()) as conn:
            if conn is None:
                return None
            with closing(conn.cursor()) as cur:
                cur.execute(query, (email,))
                return cur.fetchone()
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
        return None
