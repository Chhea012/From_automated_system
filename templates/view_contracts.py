import streamlit as st
import pandas as pd
import io
import zipfile
from db_handler import get_contracts
from templates.generate_contract import generate_docx

def to_excel(df):
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()
    except Exception as e:
        st.error(f"Error generating Excel file: {str(e)}")
        return None

def generate_all_docx(contracts_data):
    try:
        zip_buffer = io.BytesIO()
        used_filenames = set()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, contract_data in contracts_data.iterrows():
                contract_data = contract_data.to_dict()
                contract_data['output_description'] = contract_data.get('output_description', '')
                
                party_b_name = contract_data.get('party_b_signature_name', f'Unknown_{idx}')
                party_b_name = ''.join(c for c in party_b_name if c.isalnum() or c in '._- ')
                party_b_name = party_b_name.strip() or f'Unknown_{idx}'
                
                contract_number = contract_data.get('contract_number', f'Contract_{idx}')
                contract_number = ''.join(c for c in contract_number if c.isalnum() or c in '._- ')
                contract_number = contract_number.strip() or f'Contract_{idx}'
                
                base_file_name = f"{party_b_name}.docx"
                file_name = base_file_name
                counter = 1
                
                while file_name in used_filenames:
                    file_name = f"{party_b_name}_{contract_number}_{counter}.docx"
                    counter += 1
                
                used_filenames.add(file_name)
                
                try:
                    docx_bytes = generate_docx(contract_data)
                    zip_file.writestr(file_name, docx_bytes)
                except Exception as e:
                    st.error(f"Error generating DOCX for contract {contract_data.get('contract_number', f'Unknown_{idx}')}: {str(e)}")
                    continue
        return zip_buffer.getvalue()
    except Exception as e:
        st.error(f"Error creating ZIP file: {str(e)}")
        return None

def view_contracts_tab():
    try:
        contracts_data = get_contracts()
        if contracts_data is None or not isinstance(contracts_data, pd.DataFrame):
            raise ValueError("Failed to retrieve contracts data or invalid data format")
        
        if not contracts_data.empty:
            st.markdown('<div class="section-header">Current Contracts</div>', unsafe_allow_html=True)
            search_term = st.text_input("Search Contracts", placeholder="Enter project title or contract number...", key="search_contracts")
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
                },
                hide_index=True,
                use_container_width=True
            )

            excel_data = to_excel(contracts_data)
            if excel_data:
                st.download_button(
                    label="📥 Download Contracts as Excel",
                    data=excel_data,
                    file_name="contracts_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_excel_contracts"
                )

            st.markdown('<div class="section-header">Generate Contract DOCX</div>', unsafe_allow_html=True)
            selected_contract = st.selectbox(
                "Select Contract to Generate DOCX",
                options=contracts_data['contract_number'],
                format_func=lambda x: f"{contracts_data[contracts_data['contract_number'] == x]['party_b_signature_name'].iloc[0]} - {contracts_data[contracts_data['contract_number'] == x]['project_title'].iloc[0]}",
                key="select_contract_docx"
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Generate and Download DOCX", key="generate_docx"):
                    if selected_contract:
                        contract_data = contracts_data[contracts_data['contract_number'] == selected_contract].iloc[0].to_dict()
                        contract_data['output_description'] = contract_data.get('output_description', '')
                        party_b_name = contract_data.get('party_b_signature_name', f'Unknown_{selected_contract}')
                        party_b_name = ''.join(c for c in party_b_name if c.isalnum() or c in '._- ')
                        party_b_name = party_b_name.strip() or f'Unknown_{selected_contract}'
                        try:
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
                if st.button("Generate All and Download All DOCX", key="generate_all_docx"):
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
            st.info("No contracts available. Add a contract using the 'Create Contract' tab.")
    except Exception as e:
        st.error(f"Error loading contracts: {str(e)}")