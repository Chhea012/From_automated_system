STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
.main {
    background-color: #f5f7fa;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    font-family: 'Inter', Arial, sans-serif;
}
.header {
    background: linear-gradient(90deg, #2E86C1, #1B4F72);
    padding: 25px;
    border-radius: 12px;
    color: white;
    font-size: 32px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    font-family: 'Inter', Arial, sans-serif;
}
.section-header {
    color: #1B4F72;
    font-weight: 600;
    font-size: 22px;
    margin: 20px 0 10px;
    border-bottom: 3px solid #2E86C1;
    padding-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Inter', Arial, sans-serif;
}
.section-header::before {
    content: "➤";
    color: #2E86C1;
    font-size: 20px;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stSelectbox > div > div > select {
    border: 1px solid #d1d9e6;
    border-radius: 8px;
    padding: 12px;
    background-color: #ffffff;
    transition: border-color 0.3s ease;
    font-family: 'Inter', Arial, sans-serif;
    font-size: 14px;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus,
.stDateInput > div > div > input:focus,
.stSelectbox > div > div > select:focus {
    border-color: #2E86C1;
    box-shadow: 0 0 5px rgba(46, 134, 193, 0.3);
}
.stButton>button {
    background: linear-gradient(90deg, #2E86C1, #3498DB);
    color: white;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: 500;
    border: none;
    transition: all 0.3s ease;
    font-family: 'Inter', Arial, sans-serif;
    font-size: 14px;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #1B4F72, #2E86C1);
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
.stButton>button:active {
    transform: translateY(0);
}
.stTabs [data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 500;
    padding: 12px 24px;
    border-radius: 8px 8px 0 0;
    background-color: #e9ecef;
    color: #1B4F72;
    transition: all 0.3s ease;
    font-family: 'Inter', Arial, sans-serif;
}
.stTabs [data-baseweb="tab"]:hover {
    background-color: #d1d9e6;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: #2E86C1;
    color: white;
}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: #2E86C1;
}
.error {
    color: #D32F2F;
    font-size: 14px;
    background-color: #FFEBEE;
    padding: 10px;
    border-radius: 6px;
    margin-top: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Inter', Arial, sans-serif;
}
.error::before {
    content: "⚠";
    font-size: 16px;
}
.success {
    color: #2E7D32;
    font-size: 14px;
    background-color: #E8F5E9;
    padding: 10px;
    border-radius: 6px;
    margin-top: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Inter', Arial, sans-serif;
}
.success::before {
    content: "✔";
    font-size: 16px;
}
.stDataFrame {
    border: 1px solid #d1d9e6;
    border-radius: 8px;
    overflow: hidden;
    font-family: 'Inter', Arial, sans-serif;
}
.stDataFrame table {
    background-color: #ffffff;
}
.stDataFrame thead {
    background-color: #2E86C1;
    color: white;
    font-family: 'Inter', Arial, sans-serif;
}
.stDataFrame tbody tr:nth-child(even) {
    background-color: #f9fafb;
}
.stDataFrame tbody tr:hover {
    background-color: #e3f2fd;
}
.stDownloadButton>button {
    background-color: #28A745;
    color: white;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: 500;
    font-family: 'Inter', Arial, sans-serif;
    font-size: 14px;
}
.stDownloadButton>button:hover {
    background-color: #218838;
    transform: translateY(-1px);
}
</style>
"""