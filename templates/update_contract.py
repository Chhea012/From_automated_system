import streamlit as st
from datetime import datetime
from utils.number_to_words import number_to_words_usd, usd_format
from utils.helpers import format_date_with_ordinal, format_date_without_ordinal, parse_ordinal_date
from db_handler import get_contracts, update_contract

def update_contract_tab():
    contracts_data = get_contracts()
    if not contracts_data.empty:
        st.markdown('<div class="section-header">Update Contract</div>', unsafe_allow_html=True)
        contract_to_update = st.selectbox(
            "Select Contract to Update",
            options=contracts_data['contract_number'],
            format_func=lambda x: f"{x} - {contracts_data[contracts_data['contract_number'] == x]['project_title'].iloc[0]}"
        )

        if contract_to_update:
            contract_data = contracts_data[contracts_data['contract_number'] == contract_to_update].iloc[0].to_dict()
            # Ensure output_description has a default value if missing
            contract_data['output_description'] = contract_data.get('output_description', '')

            with st.form("update_form"):
                col1, col2 = st.columns([1, 1], gap="medium")
                with col1:
                    project_title = st.text_input("Project Title", value=contract_data['project_title'])
                    output_description = st.text_input("Output Description", value=contract_data['output_description'])
                    contract_number = st.text_input("Contract Number", value=contract_data['contract_number'])
                    organization_name = st.text_input("Organization Name", value=contract_data['organization_name'])
                with col2:
                    registration_number = st.text_input("Registration Number", value=contract_data['registration_number'])
                    registration_date = st.date_input("Registration Date", value=parse_ordinal_date(contract_data['registration_date']))
                    tax_percentage = st.selectbox("Tax Percentage (%)", [0, 5, 10, 15, 20], index=[0, 5, 10, 15, 20].index(int(contract_data['tax_percentage'])))

                col1, col2 = st.columns([1, 1], gap="medium")
                with col1:
                    party_a_name = st.text_input("Party A Name", value=contract_data['party_a_name'])
                    party_a_position = st.text_input("Party A Position", value=contract_data['party_a_position'])
                with col2:
                    party_a_address = st.text_area("Party A Address", value=contract_data['party_a_address'], height=80)

                col1, col2 = st.columns([1, 1], gap="medium")
                with col1:
                    party_b_full_name_with_title = st.text_input("Party B Full Name with Title", value=contract_data['party_b_full_name_with_title'])
                    party_b_position = st.text_input("Party B Position", value=contract_data['party_b_position'])
                    party_b_phone = st.text_input("Party B Phone", value=contract_data['party_b_phone'])
                    party_b_email = st.text_input("Party B Email", value=contract_data['party_b_email'])
                    party_b_address = st.text_area("Party B Address", value=contract_data['party_b_address'], height=80)
                with col2:
                    focal_person_a_name = st.text_input("Focal Person A Name", value=contract_data['focal_person_a_name'])
                    focal_person_a_position = st.text_input("Focal Person A Position", value=contract_data['focal_person_a_position'])
                    focal_person_a_phone = st.text_input("Focal Person A Phone", value=contract_data['focal_person_a_phone'])
                    focal_person_a_email = st.text_input("Focal Person A Email", value=contract_data['focal_person_a_email'])

                col1, col2, col3 = st.columns([1, 1, 1], gap="medium")
                with col1:
                    agreement_start_date = st.date_input("Agreement Start Date", value=parse_ordinal_date(contract_data['agreement_start_date']))
                with col2:
                    agreement_end_date = st.date_input("Agreement End Date", value=parse_ordinal_date(contract_data['agreement_end_date']))
                with col3:
                    total_fee_usd = st.number_input("Total Fee USD", value=float(contract_data['total_fee_usd']), min_value=0.0, step=0.01, format="%.2f")

                payment_installment_desc = st.text_input("Payment Installment Description", value=contract_data['payment_installment_desc'])
                workshop_description = st.text_input("Workshop Description", value=contract_data['workshop_description'])
                deliverables = st.text_area("Deliverables (one per line)", value=contract_data['deliverables'], height=150)

                col1, col2 = st.columns([1, 1], gap="medium")
                with col1:
                    party_a_signature_name = st.text_input("Party A Signature Name", value=contract_data['party_a_signature_name'])
                    party_b_signature_name = st.text_input("Party B Signature Name", value=contract_data['party_b_signature_name'])
                with col2:
                    title = st.text_input("Title", value=contract_data['title'])

                update_submitted = st.form_submit_button("Update Contract")

                if update_submitted:
                    required_fields = [project_title, contract_number, party_a_name, party_b_full_name_with_title, output_description, deliverables]
                    if not all(required_fields):
                        st.markdown('<div class="error">Please fill in all required fields</div>', unsafe_allow_html=True)
                    elif agreement_end_date < agreement_start_date:
                        st.markdown('<div class="error">End date cannot be before start date</div>', unsafe_allow_html=True)
                    else:
                        gross_amount_usd = total_fee_usd
                        tax_amount = gross_amount_usd * (tax_percentage / 100)
                        payment_net = gross_amount_usd - tax_amount

                        updated_data = {
                            "project_title": project_title,
                            "contract_number": contract_number,
                            "organization_name": organization_name,
                            "party_a_name": party_a_name,
                            "party_a_position": party_a_position,
                            "party_a_address": party_a_address,
                            "party_b_full_name_with_title": party_b_full_name_with_title,
                            "party_b_address": party_b_address,
                            "party_b_phone": party_b_phone,
                            "party_b_email": party_b_email,
                            "registration_number": registration_number,
                            "registration_date": format_date_without_ordinal(registration_date),
                            "agreement_start_date": format_date_with_ordinal(agreement_start_date),
                            "agreement_end_date": format_date_with_ordinal(agreement_end_date),
                            "total_fee_usd": total_fee_usd,
                            "gross_amount_usd": gross_amount_usd,
                            "tax_percentage": tax_percentage,
                            "payment_installment_desc": payment_installment_desc,
                            "payment_gross": usd_format(gross_amount_usd),
                            "payment_net": usd_format(payment_net),
                            "workshop_description": workshop_description,
                            "focal_person_a_name": focal_person_a_name,
                            "focal_person_a_position": focal_person_a_position,
                            "focal_person_a_phone": focal_person_a_phone,
                            "focal_person_a_email": focal_person_a_email,
                            "party_a_signature_name": party_a_signature_name,
                            "party_b_signature_name": party_b_signature_name,
                            "party_b_position": party_b_position,
                            "total_fee_words": number_to_words_usd(total_fee_usd),
                            "title": title,
                            "deliverables": deliverables,
                            "output_description": output_description
                        }

                        if update_contract(contract_data['id'], updated_data):
                            st.session_state.active_tab = "View Contracts"
                            st.markdown('<div class="success">Contract updated successfully! You can now generate the DOCX in View Contracts.</div>', unsafe_allow_html=True)
                            st.rerun()
    else:
        st.info("No contracts available to update. Add a contract first.")