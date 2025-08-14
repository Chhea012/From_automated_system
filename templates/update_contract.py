import streamlit as st
from datetime import datetime
from utils.number_to_words import number_to_words_usd, usd_format
from utils.helpers import format_date_with_ordinal, format_date_without_ordinal, parse_ordinal_date
from db_handler import get_contracts, update_contract
import json

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
            contract_data['output_description'] = contract_data.get('output_description', '')
            custom_article_sentences = json.loads(contract_data.get('custom_article_sentences', '{}'))

            with st.form("update_form"):
                col1, col2 = st.columns([1, 1], gap="medium")
                with col1:
                    project_title = st.text_input("Project Title", value=contract_data['project_title'])
                    output_description = st.text_input("Output Description", value=contract_data['output_description'])
                    contract_number = st.text_input("Contract Number", value=contract_data['contract_number'])
                with col2:
                    tax_percentage = st.selectbox("Tax Percentage (%)", [0, 5, 10, 15, 20], index=[0, 5, 10, 15, 20].index(int(float(contract_data['tax_percentage']))))

                col1, col2 = st.columns([1, 1], gap="medium")
                with col1:
                    party_b_signature_name = st.text_input("Party B Signature Name", value=contract_data['party_b_signature_name'])
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

                st.markdown('<div class="section-header">Custom Article Sentences</div>', unsafe_allow_html=True)
                article_number = st.selectbox("Select Article to Add Sentence", [str(i) for i in range(1, 17)], index=0)
                custom_sentence = st.text_input("Custom Sentence for Selected Article", value=custom_article_sentences.get(article_number, ""), placeholder="e.g., Additional requirements for this article...")

                col1, col2 = st.columns([1, 1], gap="medium")
                with col1:
                    party_b_signature_name_confirm = st.text_input("Party B Signature Name (Confirm)", value=contract_data['party_b_signature_name'])
                with col2:
                    title = st.text_input("Title", value=contract_data['title'])

                update_submitted = st.form_submit_button("Update Contract")

                if update_submitted:
                    required_fields = [project_title, contract_number, party_b_signature_name, output_description, deliverables]
                    if not all(required_fields):
                        st.markdown('<div class="error">Please fill in all required fields</div>', unsafe_allow_html=True)
                    elif agreement_end_date < agreement_start_date:
                        st.markdown('<div class="error">End date cannot be before start date</div>', unsafe_allow_html=True)
                    elif party_b_signature_name != party_b_signature_name_confirm:
                        st.markdown('<div class="error">Party B Signature Name and Confirmation do not match</div>', unsafe_allow_html=True)
                    else:
                        party_b_full_name_with_title = f"{party_b_position} {party_b_signature_name}"
                        gross_amount_usd = total_fee_usd
                        tax_amount = gross_amount_usd * (tax_percentage / 100)
                        payment_net = gross_amount_usd - tax_amount

                        # Update custom_article_sentences
                        if custom_sentence:
                            custom_article_sentences[article_number] = custom_sentence
                        elif article_number in custom_article_sentences:
                            del custom_article_sentences[article_number]  # Remove sentence if cleared

                        updated_data = {
                            "project_title": project_title,
                            "contract_number": contract_number,
                            "organization_name": "The NGO Forum on Cambodia",
                            "party_a_name": "Mr. Soeung Saroeun",
                            "party_a_position": "Executive Director",
                            "party_a_address": "#9-11, Street 476, Sangkat Tuol Tumpoung I, Phnom Penh, Cambodia",
                            "party_b_full_name_with_title": party_b_full_name_with_title,
                            "party_b_address": party_b_address if party_b_address else "",
                            "party_b_phone": party_b_phone if party_b_phone else "",
                            "party_b_email": party_b_email if party_b_email else "",
                            "registration_number": "#304 សជណ",
                            "registration_date": "07 March 2012",
                            "agreement_start_date": format_date_with_ordinal(agreement_start_date),
                            "agreement_end_date": format_date_with_ordinal(agreement_end_date),
                            "total_fee_usd": total_fee_usd,
                            "gross_amount_usd": gross_amount_usd,
                            "tax_percentage": tax_percentage,
                            "payment_installment_desc": payment_installment_desc if payment_installment_desc else "",
                            "payment_gross": usd_format(gross_amount_usd),
                            "payment_net": usd_format(payment_net),
                            "workshop_description": workshop_description if workshop_description else "",
                            "focal_person_a_name": focal_person_a_name if focal_person_a_name else "",
                            "focal_person_a_position": focal_person_a_position if focal_person_a_position else "",
                            "focal_person_a_phone": focal_person_a_phone if focal_person_a_phone else "",
                            "focal_person_a_email": focal_person_a_email if focal_person_a_email else "",
                            "party_a_signature_name": "Mr. SOEUNG Saroeun",
                            "party_b_signature_name": party_b_signature_name,
                            "party_b_position": party_b_position,
                            "total_fee_words": number_to_words_usd(total_fee_usd),
                            "title": title if title else "",
                            "deliverables": deliverables,
                            "output_description": output_description,
                            "custom_article_sentences": json.dumps(custom_article_sentences)
                        }

                        # Validate all required fields for database update
                        missing_fields = [key for key, value in updated_data.items() if value is None]
                        if missing_fields:
                            st.markdown(f'<div class="error">Missing required fields: {", ".join(missing_fields)}</div>', unsafe_allow_html=True)
                        elif update_contract(contract_data['id'], updated_data):
                            st.session_state.active_page = "View Contract"
                            st.markdown('<div class="success">Contract updated successfully! You can now generate the DOCX in View Contracts.</div>', unsafe_allow_html=True)
                            st.rerun()
                        else:
                            st.markdown('<div class="error">Failed to update contract in database</div>', unsafe_allow_html=True)
    else:
        st.info("No contracts available to update. Add a contract first.")