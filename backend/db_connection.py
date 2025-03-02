import psycopg2
from psycopg2 import sql
from contextlib import closing
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Database configuration from environment variables
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "resume_system"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "Password@1"),  # Change this or set in env variables
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

# Establish database connection
def get_db_connection():
    """Returns a PostgreSQL database connection."""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as e:
        logging.error(f"Database connection error: {e}")
        raise  # Optional: raise error to halt execution, or handle it appropriately

# ✅ Generic Query Executor for INSERT, UPDATE, DELETE
def execute_query(query, values=None, fetch_one=False, fetch_all=False):
    """Execute database queries with error handling."""
    try:
        with closing(get_db_connection()) as conn:
            if conn is None:
                logging.error("Connection failed.")
                return None
            with closing(conn.cursor()) as cur:
                cur.execute(query, values)
                if fetch_one:
                    return cur.fetchone()
                if fetch_all:
                    return cur.fetchall()
                conn.commit()
                return True
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
        return None  # Optional: raise exception if critical, or provide custom error handling

# ✅ Insert Resume Function with Ranking Score
def insert_resume(name, email, phone, skills, experience, education, file_path, file_format, job_description, ranking_score=0.0):
    """Insert resume details into the database."""
    
    # Delay the import to avoid circular import
    from db_connection import get_db_connection
    
    query = """
        INSERT INTO resumes (name, email, phone, skills, experience, education, file_path, file_format, job_description, ranking_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (name, email, phone, skills, experience, education, file_path, file_format, job_description, ranking_score)
    return execute_query(query, values)
    
# ✅ Update Resume Status
def update_resume_status(resume_id, status):
    """Update the status of a resume."""
    query = "UPDATE resumes SET status = %s WHERE id = %s"
    return execute_query(query, (status, resume_id))

# ✅ Update Ranking Score
def update_ranking_score(resume_id, new_score):
    """Update ranking score of a resume."""
    query = "UPDATE resumes SET ranking_score = %s WHERE id = %s"
    return execute_query(query, (new_score, resume_id))

# ✅ Update Resume Fields Dynamically
def update_resume(resume_id, **fields):
    """Update specific fields of a resume dynamically."""
    if not fields:
        logging.warning("No fields provided for update.")
        return False

    query = sql.SQL("UPDATE resumes SET {} WHERE id = %s").format(
        sql.SQL(", ").join([sql.SQL(f"{key} = %s") for key in fields.keys()])
    )
    values = list(fields.values()) + [resume_id]
    return execute_query(query, values)

# ✅ Delete Resume
def delete_resume(resume_id):
    """Delete a resume from the database."""
    query = "DELETE FROM resumes WHERE id = %s"
    return execute_query(query, (resume_id,))

# ✅ Fetch Top Resumes by Ranking Score
def get_top_resumes(limit=10):
    """Fetch resumes sorted by ranking score."""
    query = "SELECT * FROM resumes ORDER BY ranking_score DESC LIMIT %s"
    return execute_query(query, (limit,), fetch_all=True)

# ✅ Fetch All Resumes
def get_all_resumes():
    """Fetch all resumes from the database."""
    query = "SELECT * FROM resumes"
    return execute_query(query, fetch_all=True)

# ✅ Fetch Resume by ID
def get_resume_by_id(resume_id):
    """Fetch resume details by ID."""
    query = "SELECT * FROM resumes WHERE id = %s"
    return execute_query(query, (resume_id,), fetch_one=True)

# ✅ Fetch Resume by Email
def get_resume_by_email(email):
    """Fetch resume details by Email."""
    query = "SELECT * FROM resumes WHERE email = %s"
    return execute_query(query, (email,), fetch_one=True)
