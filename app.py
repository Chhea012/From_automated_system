import streamlit as st
from templates.create_contract import create_contract_tab
from templates.view_contracts import view_contracts_tab, to_excel
from templates.update_contract import update_contract_tab
from templates.delete_contract import delete_contract_tab
from templates.generate_contract import generate_docx
from db_handler import get_contracts
from utils.styles import STYLES

# Set page configuration
st.set_page_config(page_title="Contract Management System", layout="wide")

# Enhanced custom CSS for sidebar and main content (without tooltip styling)
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
    width: 100%; /* Match HTML style */
    max-width: 100%; /* Match HTML style */
    height: auto;
}
img.stImage[alt="0"] {
    display: block;
    margin: 0 auto 20px auto;
    width: 100% !important; /* Ensure width override */
    max-width: 100% !important; /* Ensure max-width override */
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
</style>
"""

# Apply custom CSS
st.markdown(CUSTOM_STYLES, unsafe_allow_html=True)

# Main header
st.markdown('<div class="header">Contract Management System</div>', unsafe_allow_html=True)

# Initialize session state for active page
if "active_page" not in st.session_state:
    st.session_state.active_page = "View Contract"

# Navigation options with icons (no tooltips)
navigation_options = {
    "Create Contract": "📝",
    "View Contract": "👁️‍🗨️",
    "Update Contract": "✏️",
    "Delete Contract": "🗑️",
    "Download Contract as Excel": "📊",
    "Generate and Download Docx": "📄"
}

# Sidebar navigation with logo and buttons
st.sidebar.image(
    "https://static.wixstatic.com/media/ce57de_ad8103b00f6546ae877ec10a2ec81dfd~mv2.png/v1/fit/w_2500,h_1330,al_c/ce57de_ad8103b00f6546ae877ec10a2ec81dfd~mv2.png",
    use_container_width=False,
    clamp=True,
    output_format="auto"
)
for page_name, icon in navigation_options.items():
    # Apply 'active' class to the current page
    button_class = "nav-button active" if page_name == st.session_state.active_page else "nav-button"
    if st.sidebar.button(
        f"{icon} {page_name}",
        key=f"nav_{page_name.lower().replace(' ', '_')}",
        use_container_width=True
    ):
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

# Render content based on selected page
page = st.session_state.active_page
if page == "Create Contract":
    create_contract_tab()
elif page == "View Contract":
    view_contracts_tab()
elif page == "Update Contract":
    update_contract_tab()
elif page == "Delete Contract":
    delete_contract_tab()
elif page == "Download Contract as Excel":
    st.markdown('<div class="section-header">Download Contracts as Excel</div>', unsafe_allow_html=True)
    contracts_data = get_contracts()
    if not contracts_data.empty:
        try:
            excel_data = to_excel(contracts_data)
            st.download_button(
                label="📥 Download Contracts as Excel",
                data=excel_data,
                file_name="contracts_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel"
            )
        except Exception as e:
            st.error(f"Error generating Excel file: {str(e)}")
    else:
        st.info("No contracts available to download. Add a contract using the 'Create Contract' option.")
elif page == "Generate and Download Docx":
    st.markdown('<div class="section-header">Generate and Download DOCX</div>', unsafe_allow_html=True)
    contracts_data = get_contracts()
    if not contracts_data.empty:
        selected_contract = st.selectbox(
            "Select Contract to Generate DOCX",
            options=contracts_data['contract_number'],
            format_func=lambda x: f"{x} - {contracts_data[contracts_data['contract_number'] == x]['project_title'].iloc[0]}",
            key="select_contract_docx"
        )
        if st.button("Generate and Download DOCX", key="generate_docx_button"):
            try:
                contract_data = contracts_data[contracts_data['contract_number'] == selected_contract].iloc[0].to_dict()
                # Validate required fields
                missing_fields = [field for field in required_fields if field not in contract_data or not contract_data[field]]
                if missing_fields:
                    st.error(f"Missing or empty required fields: {', '.join(missing_fields)}")
                else:
                    contract_data['output_description'] = contract_data.get('output_description', '')
                    docx_bytes = generate_docx(contract_data)
                    st.download_button(
                        label="Download Generated Contract",
                        data=docx_bytes,
                        file_name=f"Consultant_Contract_{selected_contract}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"download_docx_{selected_contract}"
                    )
                    st.markdown('<div class="success">DOCX generated successfully!</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error generating DOCX: {str(e)}")
    else:
        st.info("No contracts available to generate DOCX. Add a contract using the 'Create Contract' option.")