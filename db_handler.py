import mysql.connector
from mysql.connector import Error
import pandas as pd
import streamlit as st
from config import DB_CONFIG

def get_db_connection():
    try:
        print("DB_CONFIG:", DB_CONFIG)
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
        else:
            st.error("Failed to establish connection to MySQL")
            return None
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        if e.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            st.error("Access denied. Check username/password.")
        elif e.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            st.error("Database does not exist. Create 'contract_management'.")
        elif e.errno == mysql.connector.errorcode.ER_DBACCESS_DENIED_ERROR:
            st.error("No access to database. Grant permissions.")
        return None

def get_contracts():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM contracts")
            data = cursor.fetchall()
            cursor.close()
            connection.close()
            return pd.DataFrame(data)
        except Error as e:
            st.error(f"Error fetching contracts: {e}")
    return pd.DataFrame(columns=[
        "id", "project_title", "contract_number", "organization_name",
        "party_a_name", "party_a_position", "party_a_address",
        "party_b_full_name_with_title", "party_b_address", "party_b_phone", "party_b_email",
        "registration_number", "registration_date", "agreement_start_date", "agreement_end_date",
        "total_fee_usd", "gross_amount_usd", "tax_percentage",
        "payment_installment_desc", "payment_gross", "payment_net",
        "workshop_description", "focal_person_a_name", "focal_person_a_position",
        "focal_person_a_phone", "focal_person_a_email",
        "party_a_signature_name", "party_b_signature_name", "party_b_position",
        "total_fee_words", "title", "deliverables", "output_description"
    ])

def insert_contract(data):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO contracts (
                id, project_title, contract_number, organization_name,
                party_a_name, party_a_position, party_a_address,
                party_b_full_name_with_title, party_b_address, party_b_phone, party_b_email,
                registration_number, registration_date, agreement_start_date, agreement_end_date,
                total_fee_usd, gross_amount_usd, tax_percentage,
                payment_installment_desc, payment_gross, payment_net,
                workshop_description, focal_person_a_name, focal_person_a_position,
                focal_person_a_phone, focal_person_a_email,
                party_a_signature_name, party_b_signature_name, party_b_position,
                total_fee_words, title, deliverables, output_description
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                data["id"], data["project_title"], data["contract_number"], data["organization_name"],
                data["party_a_name"], data["party_a_position"], data["party_a_address"],
                data["party_b_full_name_with_title"], data["party_b_address"], data["party_b_phone"], data["party_b_email"],
                data["registration_number"], data["registration_date"], data["agreement_start_date"], data["agreement_end_date"],
                data["total_fee_usd"], data["gross_amount_usd"], data["tax_percentage"],
                data["payment_installment_desc"], data["payment_gross"], data["payment_net"],
                data["workshop_description"], data["focal_person_a_name"], data["focal_person_a_position"],
                data["focal_person_a_phone"], data["focal_person_a_email"],
                data["party_a_signature_name"], data["party_b_signature_name"], data["party_b_position"],
                data["total_fee_words"], data["title"], data["deliverables"], data["output_description"]
            )
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            st.error(f"Error inserting contract: {e}")
            return False
    return False

def update_contract(contract_id, data):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            UPDATE contracts SET
                project_title = %s, contract_number = %s, organization_name = %s,
                party_a_name = %s, party_a_position = %s, party_a_address = %s,
                party_b_full_name_with_title = %s, party_b_address = %s, party_b_phone = %s, party_b_email = %s,
                registration_number = %s, registration_date = %s, agreement_start_date = %s, agreement_end_date = %s,
                total_fee_usd = %s, gross_amount_usd = %s, tax_percentage = %s,
                payment_installment_desc = %s, payment_gross = %s, payment_net = %s,
                workshop_description = %s, focal_person_a_name = %s, focal_person_a_position = %s,
                focal_person_a_phone = %s, focal_person_a_email = %s,
                party_a_signature_name = %s, party_b_signature_name = %s, party_b_position = %s,
                total_fee_words = %s, title = %s, deliverables = %s, output_description = %s
            WHERE id = %s
            """
            values = (
                data["project_title"], data["contract_number"], data["organization_name"],
                data["party_a_name"], data["party_a_position"], data["party_a_address"],
                data["party_b_full_name_with_title"], data["party_b_address"], data["party_b_phone"], data["party_b_email"],
                data["registration_number"], data["registration_date"], data["agreement_start_date"], data["agreement_end_date"],
                data["total_fee_usd"], data["gross_amount_usd"], data["tax_percentage"],
                data["payment_installment_desc"], data["payment_gross"], data["payment_net"],
                data["workshop_description"], data["focal_person_a_name"], data["focal_person_a_position"],
                data["focal_person_a_phone"], data["focal_person_a_email"],
                data["party_a_signature_name"], data["party_b_signature_name"], data["party_b_position"],
                data["total_fee_words"], data["title"], data["deliverables"], data["output_description"], contract_id
            )
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            st.error(f"Error updating contract: {e}")
            return False
    return False

def delete_contract(contract_id):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "DELETE FROM contracts WHERE id = %s"
            cursor.execute(query, (contract_id,))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            st.error(f"Error deleting contract: {e}")
            return False
    return False