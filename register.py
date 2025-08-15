
import streamlit as st
from auth import register_user, create_users_table, has_admins

# Ensure users table exists
create_users_table()

def register_tab():
    st.markdown('<div class="section-header">Register New User</div>', unsafe_allow_html=True)
    
    with st.form(key="register_form"):
        username = st.text_input("Username", max_chars=255)
        email = st.text_input("Email", max_chars=255)
        password = st.text_input("Password", type="password", max_chars=255)
        confirm_password = st.text_input("Confirm Password", type="password", max_chars=255)
        
        # Role selection
        if st.session_state.get('logged_in') and st.session_state.get('role') == 'Admin':
            role = st.selectbox("Select Role", options=["Employee", "Admin"], help="Admins can assign either role.")
        elif not has_admins():
            role = st.selectbox("Select Role", options=["Employee", "Admin"], help="No Admins exist yet. You can register as an Admin.")
        else:
            role = st.selectbox("Select Role", options=["Employee"], disabled=True, help="New users are assigned the Employee role by default.")
        
        submit_button = st.form_submit_button("Register")
        
        if submit_button:
            if not username or not email or not password:
                st.error("All fields are required.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif register_user(username, password, email, role):
                st.success("Registered successfully! You can now login.")
                st.session_state.active_page = "Login"
                st.rerun()
            else:
                st.error("Registration failed.")
