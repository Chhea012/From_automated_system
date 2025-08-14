import streamlit as st
from datetime import datetime
from utils.number_to_words import number_to_words_usd, usd_format
from utils.helpers import format_date_with_ordinal, format_date_without_ordinal
from db_handler import insert_contract
import uuid
import json

def create_contract_tab():
    default_deliverables = """Sign Agreement
Submit the draft outline
Submit the draft budget analysis to be submitted to NGOF
Submit the well-written and comprehensive analysis report based on the outcomes of the analysis.
Present analysis report in a multi-stakeholder workshop.
Submit invoice and receipt of the service"""

    with st.form("contract_form", clear_on_submit=True):
        st.markdown('<div class="section-header">Project & Contract Details</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1], gap="medium")
        with col1:
            project_title = st.text_input("Project Title", placeholder="e.g., Consultant for the Development of Budget Analysis on Reviewing the MAFF’s Budget Allocation Trend")
            output_description = st.text_input("Output Description", placeholder="e.g., Budget Analysis on Reviewing the MAFF’s Budget Allocation Trend")
            contract_number = st.text_input("Contract Number", placeholder="e.g., NGOF/2025-002")
        with col2:
            tax_percentage = st.selectbox("Tax Percentage (%)", [0, 5, 10, 15, 20], index=3)

        st.markdown('<div class="section-header">Party B Information</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1], gap="medium")
        with col1:
            party_b_signature_name = st.text_input("Party B Signature Name", placeholder="e.g., Mr. SEAN Bunrith")
            party_b_position = st.text_input("Party B Position", value="Freelance Consultant")
            party_b_phone = st.text_input("Party B Phone", placeholder="e.g., (+855) 11 535 354")
            party_b_email = st.text_input("Party B Email", placeholder="e.g., Seanbunrith@gmail.com")
            party_b_address = st.text_area("Party B Address", placeholder="e.g., # F22 st. 113 Trapaeng Krosang, Porsenchey, Phnom Penh", height=80)
        with col2:
            focal_person_a_name = st.text_input("Focal Person A Name", placeholder="e.g., Mr. Mar Sophal")
            focal_person_a_position = st.text_input("Focal Person A Position", placeholder="e.g., PALI Program Manager")
            focal_person_a_phone = st.text_input("Focal Person A Phone", placeholder="e.g., 012 845 091")
            focal_person_a_email = st.text_input("Focal Person A Email", placeholder="e.g., sophal@ngoforum.org.kh")

        st.markdown('<div class="section-header">Agreement Details</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1], gap="medium")
        with col1:
            agreement_start_date = st.date_input("Agreement Start Date", datetime.today())
        with col2:
            agreement_end_date = st.date_input("Agreement End Date", datetime.today())
        with col3:
            total_fee_usd = st.number_input("Total Fee USD (Gross)", min_value=0.0, step=0.01, format="%.2f")

        payment_installment_desc = st.text_input("Payment Installment Description", placeholder="e.g., Installment #1 (100%)")
        workshop_description = st.text_input("Workshop Description", placeholder="e.g., multi-stakeholder workshop")
        deliverables = st.text_area("Deliverables (one per line)", value=default_deliverables, placeholder="Enter deliverables, one per line", height=150)

        st.markdown('<div class="section-header">Custom Article Sentences</div>', unsafe_allow_html=True)
        article_number = st.selectbox("Select Article to Add Sentence", [str(i) for i in range(1, 17)], index=0)
        custom_sentence = st.text_input("Custom Sentence for Selected Article", placeholder="e.g., Additional requirements for this article...")

        st.markdown('<div class="section-header">Signatures</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1], gap="medium")
        with col1:
            party_b_signature_name_input = st.text_input("Party B Signature Name (Confirm)", placeholder="e.g., Mr. SEAN Bunrith")
        with col2:
            title = st.text_input("Title", placeholder="e.g., Consultant for the Development of Budget Analysis on Reviewing the MAFF’s Budget Allocation Trend")

        submitted = st.form_submit_button("Add Contract")

        if submitted:
            required_fields = [project_title, contract_number, party_b_signature_name, output_description, deliverables]
            if not all(required_fields):
                st.markdown('<div class="error">Please fill in all required fields</div>', unsafe_allow_html=True)
            elif agreement_end_date < agreement_start_date:
                st.markdown('<div class="error">End date cannot be before start date</div>', unsafe_allow_html=True)
            elif party_b_signature_name != party_b_signature_name_input:
                st.markdown('<div class="error">Party B Signature Name and Confirmation do not match</div>', unsafe_allow_html=True)
            else:
                party_b_full_name_with_title = f"{party_b_position} {party_b_signature_name}"
                gross_amount_usd = total_fee_usd
                tax_amount = gross_amount_usd * (tax_percentage / 100)
                payment_net = gross_amount_usd - tax_amount
                custom_article_sentences = {article_number: custom_sentence} if custom_sentence else {}

                new_data = {
                    "id": str(uuid.uuid4()),
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

                # Validate all required fields for database insertion
                missing_fields = [key for key, value in new_data.items() if value is None]
                if missing_fields:
                    st.markdown(f'<div class="error">Missing required fields: {", ".join(missing_fields)}</div>', unsafe_allow_html=True)
                elif insert_contract(new_data):
                    st.session_state.active_page = "View Contract"
                    st.markdown('<div class="success">Contract added successfully! You can now generate the DOCX in View Contracts.</div>', unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.markdown('<div class="error">Failed to insert contract into database</div>', unsafe_allow_html=True)