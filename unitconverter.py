import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import base64

# Constants
CONVERSION_TYPES = {
    "Length": {"Meter": 1, "Kilometer": 0.001, "Centimeter": 100, "Millimeter": 1000, "Mile": 0.000621371, "Yard": 1.09361, "Foot": 3.28084, "Inch": 39.3701},
    "Weight/Mass": {"Kilogram": 1, "Gram": 1000, "Milligram": 1000000, "Pound": 2.20462, "Ounce": 35.274},
    "Temperature": {"Celsius": "C", "Fahrenheit": "F", "Kelvin": "K"},
    "Volume": {"Liter": 1, "Milliliter": 1000, "Gallon (US)": 0.264172, "Cubic Meter": 0.001},
    "Time": {"Second": 1, "Minute": 1/60, "Hour": 1/3600, "Day": 1/86400},
    "Speed": {"Meter per second": 1, "Kilometer per hour": 3.6, "Mile per hour": 2.23694},
    "Energy": {"Joule": 1, "Kilojoule": 0.001, "Calorie": 0.239006, "Kilocalorie": 0.000239006},
    "Data": {"Bit": 1, "Byte": 0.125, "Kilobyte": 0.000125, "Megabyte": 1.25e-7}
}

# Helper Functions
def convert_temperature(value, from_unit, to_unit):
    if from_unit == to_unit: return value
    celsius = value - 273.15 if from_unit == "Kelvin" else (value - 32) * 5/9 if from_unit == "Fahrenheit" else value
    return celsius + 273.15 if to_unit == "Kelvin" else (celsius * 9/5) + 32 if to_unit == "Fahrenheit" else celsius

def get_conversion_factor(category, from_unit, to_unit):
    return CONVERSION_TYPES[category][to_unit] / CONVERSION_TYPES[category][from_unit]

def format_result(result):
    return f"{result:.6e}" if abs(result) >= 1e6 or abs(result) <= 1e-6 and result != 0 else f"{result:.6g}"

def export_to_csv(data):
    csv = data.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="conversion_results.csv">Download CSV</a>'

# UI Components
def sidebar():
    st.sidebar.markdown('<h1 style="color:#00bcd4; font-size:24px;"><span style="background-color:#00bcd; color:white; padding:5px 10px; border-radius:5px; margin-right:10px;">⚡</span> ConvertXpert</h1>', unsafe_allow_html=True)
    st.sidebar.markdown("### Select Unit Type")
    selected_tab = option_menu(None, ["Basic", "Science", "Digital"], icons=["house", "flask", "cpu"], menu_icon="cast", default_index=0, orientation="horizontal")
    categories = {"Basic": ["Length", "Weight/Mass", "Volume", "Temperature"], "Science": ["Energy", "Speed"], "Digital": ["Data"]}[selected_tab]
    for category in categories:
        if st.sidebar.button(f"{category}", use_container_width=True):
            st.session_state.category = category
    st.sidebar.markdown("### Recent Conversions")
    if 'history' in st.session_state and st.session_state.history:
        for i, (from_val, from_unit, to_val, to_unit, category) in enumerate(st.session_state.history[-5:]):
            st.sidebar.markdown(f"<div style='font-size:12px; padding:5px 0;'>{from_val} {from_unit} = {to_val} {to_unit}</div>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<div style='font-size:12px; color:#666;'>No recent conversions</div>", unsafe_allow_html=True)

def main_content():
    st.markdown('<div class="main-header">Unit Converter</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Convert between different units with precision and ease</div>', unsafe_allow_html=True)
    
    col1, col_mid, col2 = st.columns([5, 1, 5])
    with col1:
        from_unit = st.selectbox("From", list(CONVERSION_TYPES[st.session_state.category].keys()), key="from_unit")
        input_value = st.number_input("Enter Value", value=1.0, format="%.6f", key="input_value")
    with col_mid:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🔄 Swap", help="Swap the 'from' and 'to' units"):
            st.session_state.from_unit, st.session_state.to_unit = st.session_state.to_unit, st.session_state.from_unit
            st.experimental_rerun()
    with col2:
        to_unit = st.selectbox("To", list(CONVERSION_TYPES[st.session_state.category].keys()), key="to_unit")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<button class="convert-button" id="convert">Convert</button>', unsafe_allow_html=True)
    
    result = convert_temperature(input_value, from_unit, to_unit) if st.session_state.category == "Temperature" else input_value * get_conversion_factor(st.session_state.category, from_unit, to_unit)
    result_display = format_result(result)
    
    st.markdown(f'<div class="result-container">{input_value} {from_unit} = {result_display} {to_unit}</div>', unsafe_allow_html=True)
    
    if 'history' not in st.session_state or st.session_state.history[-1] != (input_value, from_unit, result_display, to_unit, st.session_state.category):
        st.session_state.history = st.session_state.history[-9:] + [(input_value, from_unit, result_display, to_unit, st.session_state.category)] if 'history' in st.session_state else [(input_value, from_unit, result_display, to_unit, st.session_state.category)]

# Main Function
def main():
    st.set_page_config(page_title="ConvertXpert", page_icon="🔄", layout="wide", initial_sidebar_state="expanded")
    st.markdown("""
    <style>
    /* Main Container */
    .main { background-color: #1E3A8A; padding: 0 !important; }

    /* Sidebar */
    .css-1d391kg { background-color: #263238; color: white; }

    /* Header */
    .main-header { font-size: 32px; font-weight: 600; color: #424242; margin-bottom: 10px; }
    .sub-header { font-size: 16px; color: #757575; margin-bottom: 25px; }

    /* Card Styling */
    .card { background-color: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); margin-bottom: 20px; }

    /* Result Container */
    .result-container {
        background: linear-gradient(135deg, #1E3A8A, #3B82F6);
        border-radius: 12px;
        padding: 20px;
        color: white;
        font-size: 24px;
        font-weight: 600;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    /* Buttons */
    .convert-button {
        background: linear-gradient(135deg, #1E3A8A, #3B82F6);
        color: white;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        border: none;
        width: 100%;
        cursor: pointer;
        text-align: center;
        margin: 10px 0;
        transition: all 0.3s ease;
    }

    .convert-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }

    .swap-button {
         background-color:#3B82F6;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .swap-button:hover {
        background-color: #3B82F6;
        transform: translateY(-2px);
    }

    /* Table Styling */
    .reference-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
    }

    .reference-table th {
        background-color: #3B82F6;
        color: white;
        text-align: left;
        padding: 12px;
    }

    .reference-table tr:nth-child(even) {
        background-color: #f5f5f5;
    }

    .reference-table td {
        padding: 10px 12px;
        border-bottom: 1px solid #ddd;
    }

    /* Footer */
    .footer {
        text-align: center;
        margin-top: 30px;
        font-size: 14px;
        color: #757575;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if 'category' not in st.session_state: st.session_state.category = "Length"
    sidebar()
    main_content()

if __name__ == "__main__":
    main()