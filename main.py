import streamlit as st
import numpy as np
from PIL import Image
import qrcode
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64
import tempfile
import os
import time
import threading

# Set page config
st.set_page_config(
    page_title="Dragon 80 ATE - Table Scanner",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Restaurant-style CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
        color: white;
        padding: 0;
    }
    
    .scanner-header {
        background: linear-gradient(90deg, #8B0000, #B22222);
        padding: 20px;
        text-align: center;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .scanner-title {
        color: #FFD700;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .scanner-subtitle {
        color: white;
        font-size: 1.2rem;
        margin: 10px 0 0 0;
        opacity: 0.9;
    }
    
    .camera-container {
        background: #000;
        border: 4px solid #FFD700;
        border-radius: 20px;
        padding: 10px;
        margin: 20px auto;
        max-width: 640px;
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
    }
    
    .scanner-status {
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        font-size: 1.1rem;
        font-weight: bold;
    }
    
    .status-ready {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        animation: pulse 2s infinite;
    }
    
    .status-scanning {
        background: linear-gradient(45deg, #FF9800, #F57C00);
        color: white;
        animation: blink 1s infinite;
    }
    
    .status-success {
        background: linear-gradient(45deg, #4CAF50, #2E7D32);
        color: white;
        animation: success-flash 0.5s;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.02); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.7; }
    }
    
    @keyframes success-flash {
        0% { background: #4CAF50; transform: scale(1); }
        50% { background: #81C784; transform: scale(1.05); }
        100% { background: #4CAF50; transform: scale(1); }
    }
    
    .scan-instructions {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
        backdrop-filter: blur(10px);
    }
    
    .menu-container {
        background: linear-gradient(135deg, #8B0000, #B22222);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    
    .menu-title {
        color: #FFD700;
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 10px;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.5);
    }
    
    .menu-subtitle {
        color: #FFD700;
        text-align: center;
        font-size: 1.8rem;
        margin-bottom: 20px;
    }
    
    .menu-tagline {
        color: white;
        text-align: center;
        font-size: 1.3rem;
        font-style: italic;
        margin-bottom: 30px;
        opacity: 0.9;
    }
    
    .contact-info {
        color: white;
        text-align: center;
        margin-bottom: 30px;
        font-size: 1.1rem;
        background: rgba(0,0,0,0.2);
        padding: 15px;
        border-radius: 10px;
    }
    
    .section-header {
        background: linear-gradient(90deg, #FFD700, #FFA500);
        color: #8B0000;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 1.3rem;
        margin: 25px 0 15px 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    .menu-item {
        background: rgba(255, 255, 255, 0.95);
        color: #333;
        padding: 15px;
        border-radius: 8px;
        margin: 8px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .menu-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    .item-code {
        color: #8B0000;
        font-weight: bold;
        margin-right: 10px;
        font-size: 0.9rem;
    }
    
    .item-name {
        flex: 1;
        font-weight: 500;
    }
    
    .item-price {
        color: #8B0000;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .control-button {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: #8B0000;
        border: none;
        padding: 15px 30px;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        margin: 10px;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        transition: all 0.3s;
    }
    
    .control-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
    }
    
    .qr-display {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 20px auto;
        max-width: 300px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    .footer-text {
        color: #FFD700;
        text-align: center;
        margin-top: 30px;
        font-size: 1.2rem;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Menu data
menu_sections = [
    {
        "title": "CHOW MEIN & FRIED RICE",
        "items": [
            {"name": "Chicken or Vegetable Chow Mein", "price": "$13.98"},
            {"name": "Beef or Prawn Chow Mein", "price": "$15.98"},
            {"name": "Mixed Chow Mein (Chicken, Beef & Prawn)", "price": "$16.98"},
            {"name": "Chicken or Vegetable Fried Rice", "price": "$13.98"},
            {"name": "Beef or Prawn Fried Rice", "price": "$15.98"},
            {"name": "Mixed Fried Rice (Chicken, Beef & Prawn)", "price": "$16.98"},
        ]
    },
    {
        "title": "HOT PLATE SIZZLERS",
        "items": [
            {"code": "HP1", "name": "Sliced Beef or Chicken with Black Pepper Sauce", "price": "$17.00"},
            {"code": "HP2", "name": "Sliced Beef or Chicken with Black Bean Sauce", "price": "$17.00"},
            {"code": "HP3", "name": "Prawn & Fish with Szechuan Style Sauce", "price": "$19.00"},
            {"code": "HP4", "name": "Seafood with Black Bean Sauce", "price": "$19.00"},
            {"code": "HP5", "name": "Chicken & Prawn in Honey Black Pepper Sauce", "price": "$18.00"},
            {"code": "HP6", "name": "Prawn & Fish with Broccoli in Garlic Butter", "price": "$19.88"},
            {"code": "HP7", "name": "Mongolian Beef", "price": "$17.00"},
        ]
    },
    {
        "title": "CHICKEN SPECIALTIES",
        "items": [
            {"code": "C1", "name": "Sweet & Sour Chicken", "price": "$15.00"},
            {"code": "C2", "name": "Palace Style Chicken", "price": "$15.00"},
            {"code": "C3", "name": "Chicken with Szechuan Sauce", "price": "$15.00"},
            {"code": "C4", "name": "Ginger Chicken", "price": "$15.00"},
            {"code": "C5", "name": "Sliced Chicken with Broccoli", "price": "$15.00"},
            {"code": "C7", "name": "Lemon Chicken", "price": "$15.00"},
            {"code": "C9", "name": "General Tso's Chicken", "price": "$15.00"},
            {"code": "C13", "name": "Kung Pao Chicken", "price": "$15.00"},
        ]
    },
    {
        "title": "BEEF DISHES",
        "items": [
            {"code": "B1", "name": "Ginger Beef", "price": "$16.00"},
            {"code": "B2", "name": "Beef in Oyster Sauce", "price": "$16.00"},
            {"code": "B3", "name": "Beef with Broccoli", "price": "$16.00"},
            {"code": "B4", "name": "Beef with Szechuan Sauce", "price": "$16.00"},
            {"code": "B6", "name": "Chilli Beef Hakka Style", "price": "$16.00"},
            {"code": "B8", "name": "Kung Pao Beef", "price": "$16.00"},
        ]
    },
    {
        "title": "SEAFOOD DELIGHTS",
        "items": [
            {"code": "S1", "name": "Steam Fish (Boneless)", "price": "$28.00"},
            {"code": "S2", "name": "Ginger Fish or Ginger Squid", "price": "$17.00"},
            {"code": "S3", "name": "Chili Prawns Hakka Style", "price": "$17.00"},
            {"code": "S5", "name": "Palace Style Prawns (12 pcs)", "price": "$17.00"},
            {"code": "S6", "name": "Sweet & Sour Pineapple Prawns", "price": "$17.00"},
            {"code": "S11", "name": "Salt and Pepper Prawns (12 pcs)", "price": "$17.00"},
        ]
    },
    {
        "title": "RICE VARIETIES",
        "items": [
            {"code": "R1", "name": "Steam Rice", "price": "$4.00"},
            {"code": "R4", "name": "Chicken Fried Rice", "price": "$12.00"},
            {"code": "R5", "name": "Beef Fried Rice", "price": "$13.00"},
            {"code": "R6", "name": "Szechuan Fried Rice", "price": "$15.00"},
            {"code": "R9", "name": "Dragon 80ATE Special Fried Rice", "price": "$15.00"},
            {"code": "R11", "name": "Prawn Fried Rice", "price": "$15.00"},
        ]
    },
    {
        "title": "VEGETARIAN OPTIONS",
        "items": [
            {"name": "Mixed Vegetable in Oyster Sauce", "price": "$13.98"},
            {"name": "Mixed Vegetable in Black Bean Sauce", "price": "$13.98"},
            {"name": "Mixed Vegetable in Garlic Sauce", "price": "$13.98"},
            {"name": "Tofu with Mixed Vegetables", "price": "$14.98"},
        ]
    }
]

# Initialize session state
if 'scanner_active' not in st.session_state:
    st.session_state.scanner_active = False
if 'menu_visible' not in st.session_state:
    st.session_state.menu_visible = False
if 'scan_success' not in st.session_state:
    st.session_state.scan_success = False

def generate_qr_code(text):
    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def detect_qr_code_simulation():
    """Simulate QR code detection"""
    time.sleep(2)  # Simulate scanning time
    return True

def display_scanner_interface():
    # Header
    st.markdown("""
    <div class="scanner-header">
        <h1 class="scanner-title">Dragon 80 ATE</h1>
        <p class="scanner-subtitle">Table Scanner - Point camera at QR code to view menu</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Scanner status
    if not st.session_state.scanner_active and not st.session_state.menu_visible:
        st.markdown("""
        <div class="scanner-status status-ready">
            📱 Ready to Scan - Tap "Start Scanner" to begin
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.scanner_active:
        st.markdown("""
        <div class="scanner-status status-scanning">
            🔍 Scanning... Point camera at QR code
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.scan_success:
        st.markdown("""
        <div class="scanner-status status-success">
            ✅ QR Code Detected! Menu loaded successfully
        </div>
        """, unsafe_allow_html=True)
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if not st.session_state.scanner_active and not st.session_state.menu_visible:
            if st.button("📱 Start Scanner", key="start_scan", help="Activate camera to scan QR code"):
                st.session_state.scanner_active = True
                st.rerun()
        
        elif st.session_state.scanner_active:
            if st.button("⏹️ Stop Scanner", key="stop_scan"):
                st.session_state.scanner_active = False
                st.rerun()
        
        elif st.session_state.menu_visible:
            if st.button("🔄 Scan Again", key="scan_again"):
                st.session_state.menu_visible = False
                st.session_state.scan_success = False
                st.rerun()
    
    # Scanner simulation
    if st.session_state.scanner_active:
        # Camera placeholder
        st.markdown("""
        <div class="camera-container">
            <div style="height: 400px; display: flex; align-items: center; justify-content: center; background: #1a1a1a; border-radius: 15px;">
                <div style="text-align: center; color: #FFD700;">
                    <div style="font-size: 4rem; margin-bottom: 20px;">📷</div>
                    <div style="font-size: 1.2rem;">Camera Active</div>
                    <div style="font-size: 1rem; opacity: 0.8;">Point at QR code to scan</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Auto-detect simulation
        with st.spinner("Scanning for QR codes..."):
            if detect_qr_code_simulation():
                st.session_state.scanner_active = False
                st.session_state.menu_visible = True
                st.session_state.scan_success = True
                st.balloons()
                st.rerun()
    
    # Instructions when not scanning
    if not st.session_state.scanner_active and not st.session_state.menu_visible:
        st.markdown("""
        <div class="scan-instructions">
            <h3>📋 How to Use</h3>
            <p>1. Tap "Start Scanner" to activate the camera</p>
            <p>2. Point your device at the QR code on your table</p>
            <p>3. The menu will appear automatically when detected</p>
            <br>
            <p><strong>💡 Tip:</strong> Make sure the QR code is well-lit and clearly visible</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Demo QR code
        st.markdown("### 🧪 Demo QR Code")
        st.markdown("Scan this code to test the scanner:")
        
        qr_img = generate_qr_code("")
        st.markdown(f"""
        <div class="qr-display">
            <img src="{qr_img}" width="200" alt="Demo QR Code">
            <p style="color: #333; margin-top: 10px; font-weight: bold;"></p>
        </div>
        """, unsafe_allow_html=True)

def display_menu():
    st.markdown("""
    <div class="menu-container">
        <h1 class="menu-title">Dragon 80 ATE</h1>
        <h2 class="menu-subtitle">FOOD MENU</h2>
        <p class="menu-tagline">Treat yourself to our exquisite cuisine, where every dish tells a story!</p>
        
        <div class="contact-info">
            📍 4408 17 Avenue South East, Calgary Alberta T2A0B6<br>
            📞 403-272-8701 | 🌐 www.Dragon80Ate.com
        </div>
    """, unsafe_allow_html=True)
    
    # Menu sections
    for section in menu_sections:
        st.markdown(f'<div class="section-header">{section["title"]}</div>', unsafe_allow_html=True)
        
        for item in section["items"]:
            code_display = f'<span class="item-code">{item["code"]}</span>' if "code" in item else ""
            st.markdown(f"""
            <div class="menu-item">
                <div class="item-name">
                    {code_display}{item['name']}
                </div>
                <div class="item-price">{item['price']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("""
        <p class="footer-text"></p>
    </div>
    """, unsafe_allow_html=True)

# Main app
def main():
    if st.session_state.menu_visible:
        display_menu()
    else:
        display_scanner_interface()

if __name__ == "__main__":
    main()