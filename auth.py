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

def create_user(username, password, email, role='Employee'):
    """Create a new user with a specified role, only allowed for Admins."""
    # Validate role
    if role not in ['Admin', 'Employee']:
        st.error("Invalid role specified.")
        return False
    
    # Check if current user is Admin
    if not st.session_state.get('logged_in') or st.session_state.get('role') != 'Admin':
        st.error("Only Admins can create new users.")
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
                st.error(f"Error creating user: {e}")
            return False
    return False

def update_user(user_id, username, email, role, password=None):
    """Update an existing user's details, only allowed for Admins."""
    if not st.session_state.get('logged_in') or st.session_state.get('role') != 'Admin':
        st.error("Only Admins can update users.")
        return False
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            if password:
                hashed_password = hash_password(password)
                query = """
                UPDATE users 
                SET username = %s, email = %s, role = %s, password = %s
                WHERE id = %s
                """
                cursor.execute(query, (username, email, role, hashed_password, user_id))
            else:
                query = """
                UPDATE users 
                SET username = %s, email = %s, role = %s
                WHERE id = %s
                """
                cursor.execute(query, (username, email, role, user_id))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            if e.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
                st.error("Username or email already exists.")
            else:
                st.error(f"Error updating user: {e}")
            return False
    return False

def delete_user(user_id):
    """Delete a user, only allowed for Admins."""
    if not st.session_state.get('logged_in') or st.session_state.get('role') != 'Admin':
        st.error("Only Admins can delete users.")
        return False
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "DELETE FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            st.error(f"Error deleting user: {e}")
            return False
    return False

def get_all_users():
    """Retrieve all users from the database, only allowed for Admins."""
    if not st.session_state.get('logged_in') or st.session_state.get('role') != 'Admin':
        st.error("Only Admins can view users.")
        return None
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT id, username, email, role, created_at FROM users"
            cursor.execute(query)
            users = cursor.fetchall()
            cursor.close()
            connection.close()
            return users
        except Error as e:
            st.error(f"Error retrieving users: {e}")
            return None
    return None

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