import streamlit as st
import pandas as pd
import io
from db_handler import get_contracts
from templates.generate_contract import generate_docx

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def view_contracts_tab():
    contracts_data = get_contracts()
    if not contracts_data.empty:
        st.markdown('<div class="section-header">Current Contracts</div>', unsafe_allow_html=True)
        search_term = st.text_input("Search Contracts", placeholder="Enter project title or contract number...")
        if search_term:
            filtered_data = contracts_data[
                contracts_data['project_title'].str.contains(search_term, case=False, na=False) |
                contracts_data['contract_number'].str.contains(search_term, case=False, na=False)
            ]
        else:
            filtered_data = contracts_data

        st.dataframe(
            filtered_data,
            column_config={
                "id": None,
                "total_fee_usd": st.column_config.NumberColumn(format="%.2f", label="Total Fee (USD)"),
                "gross_amount_usd": st.column_config.NumberColumn(format="%.2f", label="Gross Amount (USD)"),
                "payment_gross": st.column_config.TextColumn(label="Gross Payment"),
                "payment_net": st.column_config.TextColumn(label="Net Payment"),
            },
            hide_index=True,
            use_container_width=True
        )

        excel_data = to_excel(contracts_data)
        st.download_button(
            label="📥 Download Contracts as Excel",
            data=excel_data,
            file_name="contracts_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.markdown('<div class="section-header">Generate Contract DOCX</div>', unsafe_allow_html=True)
        selected_contract = st.selectbox(
            "Select Contract to Generate DOCX",
            options=contracts_data['contract_number'],
            format_func=lambda x: f"{x} - {contracts_data[contracts_data['contract_number'] == x]['project_title'].iloc[0]}"
        )
        if st.button("Generate and Download DOCX"):
            if selected_contract:
                contract_data = contracts_data[contracts_data['contract_number'] == selected_contract].iloc[0].to_dict()
                # Ensure output_description exists
                contract_data['output_description'] = contract_data.get('output_description', '')
                docx_bytes = generate_docx(contract_data)
                st.download_button(
                    label="Download Generated Contract",
                    data=docx_bytes,
                    file_name=f"{selected_contract}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="download_docx"
                )
                st.markdown('<div class="success">DOCX generated successfully!</div>', unsafe_allow_html=True)
    else:
        st.info("No contracts available. Add a contract using the 'Create Contract' tab.")