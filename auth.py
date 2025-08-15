
import streamlit as st
import hashlib
from db_handler import get_db_connection
import mysql.connector
from mysql.connector import Error

def hash_password(password):
    """Hash the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_users_table():
    """Create the users table if it doesn't exist."""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                role ENUM('Admin', 'Employee') NOT NULL DEFAULT 'Employee',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(query)
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            st.error(f"Error creating users table: {e}")
            return False
    return False

def has_admins():
    """Check if any Admin users exist in the database."""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT COUNT(*) FROM users WHERE role = 'Admin'"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            cursor.close()
            connection.close()
            return count > 0
        except Error as e:
            st.error(f"Error checking for admins: {e}")
            return False
    return False

def register_user(username, password, email, role='Employee'):
    """Register a new user with a specified role."""
    # Validate role
    if role not in ['Admin', 'Employee']:
        st.error("Invalid role specified.")
        return False
    
    # Allow Admin role only if no Admins exist or the current user is an Admin
    if role == 'Admin' and has_admins() and (not st.session_state.get('logged_in') or st.session_state.get('role') != 'Admin'):
        st.error("Only Admins can register new Admin users.")
        return False

    hashed_password = hash_password(password)
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO users (username, password, email, role)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (username, hashed_password, email, role))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            if e.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
                st.error("Username or email already exists.")
            else:
                st.error(f"Error registering user: {e}")
            return False
    return False

def login_user(username, password):
    """Login a user and return user data if successful."""
    hashed_password = hash_password(password)
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT id, username, email, role FROM users WHERE username = %s AND password = %s
            """
            cursor.execute(query, (username, hashed_password))
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            return user
        except Error as e:
            st.error(f"Error logging in: {e}")
            return None
    return None
