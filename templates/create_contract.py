import streamlit as st
from datetime import datetime
from utils.number_to_words import number_to_words_usd, usd_format
from utils.helpers import format_date_with_ordinal, format_date_without_ordinal
from db_handler import insert_contract
import uuid

def create_contract_tab():
    with st.form("contract_form", clear_on_submit=True):
        st.markdown('<div class="section-header">Project & Contract Details</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1], gap="medium")
        with col1:
            project_title = st.text_input("Project Title", placeholder="e.g., Consultant for the Development of Budget Analysis on Reviewing the MAFF’s Budget Allocation Trend")
            output_description = st.text_input("Output Description", placeholder="e.g., Budget Analysis on Reviewing the MAFF’s Budget Allocation Trend")
            contract_number = st.text_input("Contract Number", placeholder="e.g., NGOF/2025-002")
            organization_name = st.text_input("Organization Name", value="The NGO Forum on Cambodia")
        with col2:
            registration_number = st.text_input("Registration Number", placeholder="e.g., #304 សជណ")
            registration_date = st.date_input("Registration Date", datetime.today())
            tax_percentage = st.selectbox("Tax Percentage (%)", [0, 5, 10, 15, 20], index=3)

        st.markdown('<div class="section-header">Party A Information</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1], gap="medium")
        with col1:
            party_a_name = st.text_input("Party A Name", placeholder="e.g., Mr. Soeung Saroeun")
            party_a_position = st.text_input("Party A Position", placeholder="e.g., Executive Director")
        with col2:
            party_a_address = st.text_area("Party A Address", placeholder="e.g., #9-11, Street 476, Sangkat Tuol Tumpoung I, Phnom Penh, Cambodia", height=80)

        st.markdown('<div class="section-header">Party B Information</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1], gap="medium")
        with col1:
            party_b_full_name_with_title = st.text_input("Party B Full Name with Title", placeholder="e.g., Freelance Consultant Mr. SEAN Bunrith")
            party_b_position = st.text_input("Party B Position", placeholder="e.g., Freelance Consultant")
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
        deliverables = st.text_area("Deliverables (one per line)", placeholder="Sign Agreement\nSubmit the draft outline\nSubmit the draft budget analysis to be submitted to NGOF\nSubmit the well-written and comprehensive analysis report based on the outcomes of the analysis.\nPresent analysis report in a multi-stakeholder workshop.\nSubmit invoice and receipt of the service", height=150)

        st.markdown('<div class="section-header">Signatures</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1], gap="medium")
        with col1:
            party_a_signature_name = st.text_input("Party A Signature Name", placeholder="e.g., Mr. SOEUNG Saroeun")
            party_b_signature_name = st.text_input("Party B Signature Name", placeholder="e.g., Mr. SEAN Bunrith")
        with col2:
            title = st.text_input("Title", placeholder="e.g., Consultant for the Development of Budget Analysis on Reviewing the MAFF’s Budget Allocation Trend")

        submitted = st.form_submit_button("Add Contract")

        if submitted:
            required_fields = [project_title, contract_number, party_a_name, party_b_full_name_with_title, output_description, deliverables]
            if not all(required_fields):
                st.markdown('<div class="error">Please fill in all required fields</div>', unsafe_allow_html=True)
            elif agreement_end_date < agreement_start_date:
                st.markdown('<div class="error">End date cannot be before start date</div>', unsafe_allow_html=True)
            else:
                gross_amount_usd = total_fee_usd
                tax_amount = gross_amount_usd * (tax_percentage / 100)
                payment_net = gross_amount_usd - tax_amount

                new_data = {
                    "id": str(uuid.uuid4()),
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

                if insert_contract(new_data):
                    st.session_state.active_tab = "View Contracts"
                    st.markdown('<div class="success">Contract added successfully! You can now generate the DOCX in View Contracts.</div>', unsafe_allow_html=True)
                    st.rerun()