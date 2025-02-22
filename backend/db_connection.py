import psycopg2

def insert_resume(name, email, phone, skills, experience, education, file_path, file_type, job_description):
    """ Inserts resume details into the database. """
    conn = psycopg2.connect(
        dbname="your_database",
        user="your_user",
        password="your_password",
        host="your_host",
        port="your_port"
    )
    cur = conn.cursor()

    sql = """INSERT INTO resumes (name, email, phone, skills, experience, education, file_path, file_type, job_description)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    cur.execute(sql, (name, email, phone, skills, experience, education, file_path, file_type, job_description))
    
    conn.commit()
    cur.close()
    conn.close()
