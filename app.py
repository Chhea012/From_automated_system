import streamlit as st
import pandas as pd
from templates.create_contract import create_contract_tab
from templates.view_contracts import view_contracts_tab, to_excel
from templates.update_contract import update_contract_tab
from templates.delete_contract import delete_contract_tab
from templates.generate_contract import generate_docx
from db_handler import get_contracts
from utils.styles import STYLES
from auth import create_users_table, login_user, create_user, get_all_users, update_user, delete_user
import io
import zipfile

# Set page configuration
st.set_page_config(page_title="Contract Management System", layout="wide")

# Ensure users table exists
create_users_table()

# Enhanced custom CSS for sidebar and main content
CUSTOM_STYLES = STYLES + """
<style>
/* Sidebar styling */
.sidebar .sidebar-content {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.sidebar-logo {
    display: block;
    margin: 0 auto 20px auto;
    width: 100%;
    max-width: 100%;
    height: auto;
}
img.stImage[alt="0"] {
    display: block;
    margin: 0 auto 20px auto;
    width: 100% !important;
    max-width: 100% !important;
    height: auto;
}
.nav-button {
    display: block;
    width: 100%;
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 5px;
    font-size: 1.1em;
    color: #34495e;
    background-color: #ffffff;
    border: 1px solid #dcdcdc;
    text-align: left;
    transition: all 0.3s ease;
}
.nav-button:hover {
    background-color: #e0e7ff;
    border-color: #6366f1;
    cursor: pointer;
}
.nav-button.active {
    background-color: #6366f1;
    color: #ffffff;
    border-color: #6366f1;
    font-weight: bold;
}
.nav-button > span {
    margin-right: 10px;
}
/* Main content styling */
.header {
    font-size: 2em;
    color: #fff;
    text-align: center;
    margin-bottom: 30px;
}
.section-header {
    font-size: 1.5em;
    color: #34495e;
    margin-bottom: 20px;
}
.success {
    color: #27ae60;
    font-weight: bold;
}
/* Column gap for buttons */
div[data-testid="column"] {
    margin-right: 5px;
}
div[data-testid="column"]:last-child {
    margin-right: 0;
}
</style>
"""

# Apply custom CSS
st.markdown(CUSTOM_STYLES, unsafe_allow_html=True)

# Initialize session state only if not already set
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "active_page" not in st.session_state:
    st.session_state.active_page = "Login"
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

# Main header
st.markdown('<div class="header">Contract Management System</div>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.image(
    "https://static.wixstatic.com/media/ce57de_ad8103b00f6546ae877ec10a2ec81dfd~mv2.png/v1/fit/w_2500,h_1330,al_c/ce57de_ad8103b00f6546ae877ec10a2ec81dfd~mv2.png",
    use_container_width=False,
    clamp=True,
    output_format="auto"
)

# Display logged-in user info
if st.session_state.logged_in:
    st.sidebar.markdown(f"**Logged in as:** {st.session_state.username} ({st.session_state.role})")

# Define navigation options based on login status
if not st.session_state.logged_in:
    navigation_options = {
        "Login": "🔑"
    }
else:
    navigation_options = {
        "Create Contract": "📝",
        "View Contract": "👁️‍🗨️",
        "Update Contract": "✏️",
        "Delete Contract": "🗑️",
        "Download Contract as Excel": "📊",
        "Generate and Download Docx": "📄",
        "Logout": "🚪"
    }
    # Add "Manage Users" option only for Admins
    if st.session_state.role == "Admin":
        navigation_options["Manage Users"] = "👤"

# Sidebar navigation buttons
for page_name, icon in navigation_options.items():
    button_class = "nav-button active" if page_name == st.session_state.active_page else "nav-button"
    if st.sidebar.button(
        f"{icon} {page_name}",
        key=f"nav_{page_name.lower().replace(' ', '_')}",
        use_container_width=True
    ):
        if page_name == "Logout":
            # Clear session state and set page to Login
            st.session_state.logged_in = False
            st.session_state.active_page = "Login"
            st.session_state.role = None
            st.session_state.username = None
            st.rerun()
        else:
            # Update active page without rerunning unless necessary
            if st.session_state.active_page != page_name:
                st.session_state.active_page = page_name

# Required fields for generate_docx
required_fields = [
    'party_b_full_name_with_title', 'project_title', 'contract_number', 'organization_name',
    'party_a_name', 'party_a_position', 'party_a_address', 'party_b_address', 'party_b_phone',
    'party_b_email', 'registration_number', 'registration_date', 'agreement_start_date',
    'agreement_end_date', 'total_fee_usd', 'total_fee_words', 'tax_percentage',
    'payment_installment_desc', 'deliverables', 'focal_person_a_name', 'focal_person_a_position',
    'focal_person_a_phone', 'focal_person_a_email', 'party_a_signature_name',
    'party_b_signature_name', 'party_b_position'
]

def generate_all_docx(contracts_data):
    try:
        zip_buffer = io.BytesIO()
        used_filenames = set()  # Track used filenames to avoid overwrites
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, contract_data in contracts_data.iterrows():
                contract_data = contract_data.to_dict()
                contract_data['output_description'] = contract_data.get('output_description', '')
                
                # Get and sanitize party_b_signature_name
                party_b_name = contract_data.get('party_b_signature_name', f'Unknown_{idx}')
                party_b_name = ''.join(c for c in party_b_name if c.isalnum() or c in '._- ')  # Strict sanitization
                party_b_name = party_b_name.strip() or f'Unknown_{idx}'  # Ensure non-empty
                
                # Get and sanitize contract_number for fallback
                contract_number = contract_data.get('contract_number', f'Contract_{idx}')
                contract_number = ''.join(c for c in contract_number if c.isalnum() or c in '._- ')  # Strict sanitization
                contract_number = contract_number.strip() or f'Contract_{idx}'
                
                # Start with base filename
                base_file_name = f"{party_b_name}.docx"
                file_name = base_file_name
                counter = 1
                
                # Handle duplicate filenames
                while file_name in used_filenames:
                    file_name = f"{party_b_name}_{contract_number}_{counter}.docx"
                    counter += 1
                
                used_filenames.add(file_name)
                
                try:
                    docx_bytes = generate_docx(contract_data)
                    zip_file.writestr(file_name, docx_bytes)
                except Exception as e:
                    st.error(f"Error generating DOCX for contract {contract_data.get('contract_number', f'Unknown_{idx}')}: {str(e)}")
                    continue  # Skip to next contract
        return zip_buffer.getvalue()
    except Exception as e:
        st.error(f"Error creating ZIP file: {str(e)}")
        return None

# Render content based on selected page and login status
page = st.session_state.active_page

if not st.session_state.logged_in:
    if page == "Login":
        st.markdown('<div class="section-header">Login</div>', unsafe_allow_html=True)
        with st.form(key="login_form"):
            username = st.text_input("Username", max_chars=255)
            password = st.text_input("Password", type="password", max_chars=255)
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if not username or not password:
                    st.error("Username and password are required.")
                else:
                    user = login_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = user['username']
                        st.session_state.role = user['role']
                        st.session_state.active_page = "View Contract"
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
else:
    if page == "Create Contract":
        create_contract_tab()
    elif page == "View Contract":
        view_contracts_tab()
    elif page == "Update Contract":
        update_contract_tab()
    elif page == "Delete Contract":
        delete_contract_tab()
    elif page == "Download Contract as Excel":
        try:
            st.markdown('<div class="section-header">Download Contracts as Excel</div>', unsafe_allow_html=True)
            contracts_data = get_contracts()
            if contracts_data is None or not isinstance(contracts_data, pd.DataFrame):
                raise ValueError("Failed to retrieve contracts data or invalid data format")
            if not contracts_data.empty:
                excel_data = to_excel(contracts_data)
                if excel_data:
                    st.download_button(
                        label="📥 Download Contracts as Excel",
                        data=excel_data,
                        file_name="contracts_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_excel"
                    )
            else:
                st.info("No contracts available to download. Add a contract using the 'Create Contract' option.")
        except Exception as e:
            st.error(f"Error generating Excel file: {str(e)}")
    elif page == "Generate and Download Docx":
        try:
            st.markdown('<div class="section-header">Generate and Download DOCX</div>', unsafe_allow_html=True)
            contracts_data = get_contracts()
            if contracts_data is None or not isinstance(contracts_data, pd.DataFrame):
                raise ValueError("Failed to retrieve contracts data or invalid data format")
            if not contracts_data.empty:
                selected_contract = st.selectbox(
                    "Select Contract to Generate DOCX",
                    options=contracts_data['contract_number'],
                    format_func=lambda x: f"{contracts_data[contracts_data['contract_number'] == x]['party_b_signature_name'].iloc[0]} - {contracts_data[contracts_data['contract_number'] == x]['project_title'].iloc[0]}",
                    key="select_contract_docx"
                )
                col1, col2 = st.columns([1, 1], gap="small")  # 5px gap approximation
                with col1:
                    if st.button("Generate and Download DOCX", key="generate_docx_button"):
                        try:
                            contract_data = contracts_data[contracts_data['contract_number'] == selected_contract].iloc[0].to_dict()
                            missing_fields = [field for field in required_fields if field not in contract_data or not contract_data[field]]
                            if missing_fields:
                                st.error(f"Missing or empty required fields: {', '.join(missing_fields)}")
                            else:
                                contract_data['output_description'] = contract_data.get('output_description', '')
                                party_b_name = contract_data.get('party_b_signature_name', f'Unknown_{selected_contract}')
                                party_b_name = ''.join(c for c in party_b_name if c.isalnum() or c in '._- ')  # Strict sanitization
                                party_b_name = party_b_name.strip() or f'Unknown_{selected_contract}'
                                docx_bytes = generate_docx(contract_data)
                                st.download_button(
                                    label="Download Generated Contract",
                                    data=docx_bytes,
                                    file_name=f"{party_b_name}.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key=f"download_docx_{selected_contract}"
                                )
                                st.markdown('<div class="success">DOCX generated successfully!</div>', unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error generating DOCX: {str(e)}")
                with col2:
                    if st.button("Generate All and Download All DOCX", key="generate_all_docx_button"):
                        zip_data = generate_all_docx(contracts_data)
                        if zip_data:
                            st.download_button(
                                label="Download All Contracts as ZIP",
                                data=zip_data,
                                file_name="all_contracts.zip",
                                mime="application/zip",
                                key="download_all_docx"
                            )
                            st.markdown('<div class="success">All DOCX files generated and zipped successfully!</div>', unsafe_allow_html=True)
            else:
                st.info("No contracts available to generate DOCX. Add a contract using the 'Create Contract' option.")
        except Exception as e:
            st.error(f"Error loading contracts: {str(e)}")
    elif page == "Manage Users" and st.session_state.role == "Admin":
        st.markdown('<div class="section-header">Manage Users</div>', unsafe_allow_html=True)
        
        # View Users
        st.markdown('### View Users', unsafe_allow_html=True)
        users = get_all_users()
        if users:
            users_df = pd.DataFrame(users)
            st.dataframe(users_df[['id', 'username', 'email', 'role', 'created_at']], use_container_width=True)
        else:
            st.info("No users found.")
        
        # Create User
        st.markdown('### Create New User', unsafe_allow_html=True)
        with st.form(key="create_user_form"):
            new_username = st.text_input("New Username", max_chars=255, key="create_username")
            new_email = st.text_input("New Email", max_chars=255, key="create_email")
            new_password = st.text_input("New Password", type="password", max_chars=255, key="create_password")
            confirm_password = st.text_input("Confirm Password", type="password", max_chars=255, key="create_confirm_password")
            new_role = st.selectbox("Select Role", options=["Employee", "Admin"], key="create_role")
            create_submit = st.form_submit_button("Create User")
            
            if create_submit:
                if not new_username or not new_email or not new_password:
                    st.error("All fields are required.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif create_user(new_username, new_password, new_email, new_role):
                    st.success("User created successfully!")
                    st.rerun()
                else:
                    st.error("Failed to create user.")
        
        # Edit User
        st.markdown('### Edit User', unsafe_allow_html=True)
        if users:
            selected_user = st.selectbox("Select User to Edit", options=[user['username'] for user in users], key="edit_user_select")
            selected_user_data = next(user for user in users if user['username'] == selected_user)
            with st.form(key="edit_user_form"):
                edit_username = st.text_input("Username", value=selected_user_data['username'], max_chars=255, key="edit_username")
                edit_email = st.text_input("Email", value=selected_user_data['email'], max_chars=255, key="edit_email")
                edit_role = st.selectbox("Role", options=["Employee", "Admin"], index=0 if selected_user_data['role'] == "Employee" else 1, key="edit_role")
                edit_password = st.text_input("New Password (leave blank to keep unchanged)", type="password", max_chars=255, key="edit_password")
                edit_submit = st.form_submit_button("Update User")
                
                if edit_submit:
                    if not edit_username or not edit_email:
                        st.error("Username and email are required.")
                    elif update_user(selected_user_data['id'], edit_username, edit_email, edit_role, edit_password):
                        st.success("User updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update user.")
        else:
            st.info("No users available to edit.")
        
        # Delete User
        st.markdown('### Delete user', unsafe_allow_html=True)
        if users:
            delete_user_select = st.selectbox("Select User to Delete", options=[user['username'] for user in users], key="delete_user_select")
            if st.button("Delete Selected User", key="delete_user_button"):
                selected_user_data = next(user for user in users if user['username'] == delete_user_select)
                if delete_user(selected_user_data['id']):
                    st.success("User deleted successfully!")
                    st.rerun()
                # Error handling is managed in delete_user function
        else:
            st.info("No users available to delete.")