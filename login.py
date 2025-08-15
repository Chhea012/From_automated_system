
import streamlit as st
from auth import login_user, create_users_table

# Ensure users table exists
create_users_table()

def login_tab():
    st.markdown('<div class="section-header">Login</div>', unsafe_allow_html=True)
    
    with st.form(key="login_form"):
        username = st.text_input("Username", max_chars=255)
        password = st.text_input("Password", type="password", max_chars=255)
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user['username']
                st.session_state.role = user['role']
                st.success(f"Logged in successfully as {user['role']}!")
                st.rerun()  # Refresh to show main app
            else:
                st.error("Invalid username or password.")