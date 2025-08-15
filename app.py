import streamlit as st
import pandas as pd
from templates.create_contract import create_contract_tab
from templates.view_contracts import view_contracts_tab, to_excel
from templates.update_contract import update_contract_tab
from templates.delete_contract import delete_contract_tab
from templates.generate_contract import generate_docx
from db_handler import get_contracts
from utils.styles import STYLES
from auth import create_users_table
from login import login_tab
from register import register_tab
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
        "Login": "🔑",
        "Register": "📝"
    }
else:
    # Same navigation options for both Admin and Employee
    navigation_options = {
        "Create Contract": "📝",
        "View Contract": "👁️‍🗨️",
        "Update Contract": "✏️",
        "Delete Contract": "🗑️",
        "Download Contract as Excel": "📊",
        "Generate and Download Docx": "📄",
        "Logout": "🚪"
    }

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
        login_tab()
    elif page == "Register":
        register_tab()
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