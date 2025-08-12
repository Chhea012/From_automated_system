import streamlit as st
from templates.create_contract import create_contract_tab
from templates.view_contracts import view_contracts_tab
from templates.update_contract import update_contract_tab
from templates.delete_contract import delete_contract_tab
from utils.styles import STYLES

# Set page configuration
st.set_page_config(page_title="Contract Management System", layout="wide")

# Apply custom CSS
st.markdown(STYLES, unsafe_allow_html=True)

# Main header
st.markdown('<div class="header">Contract Management System</div>', unsafe_allow_html=True)

# Initialize session state for active tab
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "View Contracts"  # Set default to View Contracts

# Create tabs for CRUD operations
tab1, tab2, tab3, tab4 = st.tabs(["📝 Create Contract", "📋 View Contracts", "✏️ Update Contract", "🗑️ Delete Contract"])

# Set tab content
with tab1:
    create_contract_tab()
with tab2:
    view_contracts_tab()
with tab3:
    update_contract_tab()
with tab4:
    delete_contract_tab()