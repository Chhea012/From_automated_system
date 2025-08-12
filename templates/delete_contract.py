import streamlit as st
from db_handler import get_contracts, delete_contract

def delete_contract_tab():
    contracts_data = get_contracts()
    if not contracts_data.empty:
        st.markdown('<div class="section-header">Delete Contract</div>', unsafe_allow_html=True)
        contract_to_delete = st.selectbox(
            "Select Contract to Delete",
            options=contracts_data['contract_number'],
            format_func=lambda x: f"{x} - {contracts_data[contracts_data['contract_number'] == x]['project_title'].iloc[0]}"
        )

        if st.button("Delete Contract", type="primary"):
            if contract_to_delete:
                contract_id = contracts_data[contracts_data['contract_number'] == contract_to_delete]['id'].iloc[0]
                if delete_contract(contract_id):
                    st.session_state.active_tab = "View Contracts"
                    st.markdown('<div class="success">Contract deleted successfully!</div>', unsafe_allow_html=True)
                    st.rerun()
    else:
        st.info("No contracts available to delete. Add a contract using the 'Create Contract' tab.")