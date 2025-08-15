
import streamlit as st
from db_handler import get_contract_count, get_employee_count

def dashboard_tab():
    st.markdown('<div class="section-header">Dashboard</div>', unsafe_allow_html=True)
    
    # Fetch metrics
    total_contracts = get_contract_count()
    total_employees = get_employee_count()
    
    # Create a responsive layout with two cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;">
            <h3 style="color: #34495e; margin-bottom: 10px;">Total Contracts</h3>
            <p style="font-size: 2em; color: #6366f1; font-weight: bold;">{}</p>
        </div>
        """.format(total_contracts if total_contracts is not None else 0), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;">
            <h3 style="color: #34495e; margin-bottom: 10px;">Total Employees</h3>
            <p style="font-size: 2em; color: #6366f1; font-weight: bold;">{}</p>
        </div>
        """.format(total_employees if total_employees is not None else 0), unsafe_allow_html=True)
    
    st.markdown('<div style="margin-top: 20px; text-align: center; color: #34495e;">Welcome to the Contract Management System. Use the sidebar to navigate.</div>', unsafe_allow_html=True)
