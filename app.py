import streamlit as st
import pandas as pd
from pymongo import MongoClient
import threading
import http.server
import socketserver

# --- Page Setup & Premium UI ---
st.set_page_config(page_title="AI Interview Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Custom sleek CSS for a clean white UI
st.markdown("""
    <style>
        .main-header { font-family: 'Inter', sans-serif; font-size: 2.2rem; font-weight: 700; color: #111827; }
        .sub-text { font-family: 'Inter', sans-serif; color: #4B5563; font-size: 1.1rem; margin-bottom: 20px;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Force White Background for Main App (overrides dark mode without restart) */
        [data-testid="stAppViewContainer"], .stApp {
            background-color: #ffffff !important;
        }
        [data-testid="stHeader"] {
            background-color: #ffffff !important;
        }
        
        /* Premium Sidebar & Nav Pills Styling */
        [data-testid="stSidebar"] {
            background-color: #f8fafc;
            border-right: 1px solid #e2e8f0;
        }
        div[role="radiogroup"] > label {
            background: white !important;
            border-radius: 12px !important;
            padding: 12px 15px !important;
            margin-bottom: 12px !important;
            border: 1px solid #e2e8f0 !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            cursor: pointer !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        }
        div[role="radiogroup"] > label:hover {
            border-color: #3b82f6 !important;
            box-shadow: 0 6px 12px rgba(59,130,246,0.1) !important;
            transform: translateY(-2px) !important;
        }
        div[role="radiogroup"] > label > div:first-child {
            display: none !important; /* Hides the native radio circle */
        }
        div[role="radiogroup"] > label p {
            font-family: 'Inter', sans-serif;
            font-size: 1.05rem !important;
            color: #475569 !important;
            margin-left: 5px !important;
        }
        div[role="radiogroup"] > label[data-checked="true"] {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
            border: none !important;
            box-shadow: 0 8px 16px rgba(37,99,235,0.25) !important;
            transform: translateY(-1px) !important;
        }
        div[role="radiogroup"] > label[data-checked="true"] p {
            color: white !important;
            font-weight: 600 !important;
        }
        
        /* Stylish Sidebar Toggle Button (>) */
        [data-testid="collapsedControl"] {
            background-color: #ffffff !important;
            border-radius: 50% !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
            color: #3b82f6 !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="collapsedControl"]:hover {
            background-color: #eff6ff !important;
            transform: scale(1.1) !important;
        }
    </style>
""", unsafe_allow_html=True)

import streamlit.components.v1 as components
import os

# Declare the custom native Streamlit component
COMPONENT_DIR = os.path.join(os.path.dirname(__file__), "vapi_component_auto")
vapi_interview = components.declare_component(
    "vapi_interview",
    path=COMPONENT_DIR
)


@st.cache_resource
def init_connection():
    return MongoClient("mongodb+srv://kunal:KdVygwFo0Anau8uX@hitesh.cqczgkd.mongodb.net/")

try:
    client = init_connection()
    db = client["AI_Interviews"] 
    collection = db["candidates"]
except Exception:
    collection = None

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 20px 0; margin-bottom: 10px;">
            <div style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); width: 64px; height: 64px; border-radius: 18px; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px auto; box-shadow: 0 10px 20px -5px rgba(37,99,235,0.4);">
                <span style="font-size: 32px; color: white;">⚡</span>
            </div>
            <h2 style="font-family: 'Inter', sans-serif; font-size: 1.4rem; font-weight: 800; color: #0f172a; margin: 0;">GenAI System</h2>
            <p style="color: #64748b; font-size: 0.9rem; margin-top: 5px;">Dashboard Menu</p>
        </div>
    """, unsafe_allow_html=True)
    
    page = st.radio("", ["🎙️ Interview Portal", "📊 Admin Dashboard"])
    st.write("---")

# --- Main Content Routing ---
if page == "🎙️ Interview Portal":
    # Premium Gradient Banner
    st.markdown("""
        <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); padding: 40px; border-radius: 16px; margin-bottom: 30px; border: 1px solid #bfdbfe; box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
            <h1 style="color: #1e3a8a; margin-top: 0; font-family: 'Inter', sans-serif; font-size: 2.2rem; font-weight: 800;">🎙️ AI Interview Portal</h1>
            <p style="color: #3b82f6; font-size: 1.1rem; margin-bottom: 0; font-weight: 500;">Welcome! Your personalized AI interviewer is ready to speak with you.</p>
        </div>
    """, unsafe_allow_html=True)

    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    if 'candidate_name' not in st.session_state:
        st.session_state.candidate_name = ""

    if not st.session_state.interview_started:
        candidate_name = st.text_input("Please enter your name to start the interview:", placeholder="e.g. John Doe")
        if st.button("Go", type="primary", use_container_width=True):
            if candidate_name:
                if collection is not None and collection.find_one({"name": candidate_name}):
                    st.error(f"❌ A candidate with the name '{candidate_name}' has already completed an interview.")
                else:
                    st.session_state.interview_started = True
                    st.session_state.candidate_name = candidate_name
                    st.rerun()
            else:
                st.warning("Please enter your name first!")

    if st.session_state.interview_started:
        # Center the component using columns for a cleaner, focused look
        col_left, col_center, col_right = st.columns([1, 8, 1])
        
        with col_center:
            if st.session_state.get("interview_finished"):
                st.success("✅ Interview Completed & Saved to Database!")
                if st.button("Start Another Interview", type="primary", use_container_width=True):
                    st.session_state.interview_started = False
                    st.session_state.interview_finished = False
                    st.session_state.candidate_name = ""
                    st.rerun()
            else:
                # Mount the Vapi Component
                result = vapi_interview(name=st.session_state.candidate_name, key="vapi_widget")
                
                # result will be populated when the JS component calls sendMessageToStreamlit
                if result is not None:
                    if collection is not None:
                        collection.insert_one(result)
                    st.session_state.interview_finished = True
                    st.rerun()
                    
                # Allow user to restart manually if they haven't finished
                if st.button("Cancel & Start a New Interview", type="secondary", use_container_width=True):
                    st.session_state.interview_started = False
                    st.session_state.candidate_name = ""
                    st.rerun()

elif page == "📊 Admin Dashboard":
    st.markdown('<div class="main-header">📊 Live Candidate Database</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-text">Monitor interview transcripts and live candidate data securely.</div>', unsafe_allow_html=True)
    st.write("---")
    
    try:
        if collection is None:
            raise Exception("Collection is not initialized")
            
        # Add a clear database button for testing purposes
        col_title, col_btn = st.columns([8, 2])
        with col_title:
            st.write("Live data streaming from MongoDB:")
        with col_btn:
            if st.button("🗑️ Clear All Data", use_container_width=True, help="Delete all test records from the database"):
                collection.delete_many({})
                st.rerun()

        items = list(collection.find())
        if items:
            # Sort items so newest are at the top (assuming timestamp is stored)
            items.reverse()
            for item in items:
                item["_id"] = str(item["_id"]) 
            df = pd.DataFrame(items)
            
            # Remove candidate_number column as requested by user
            if 'candidate_number' in df.columns:
                df = df.drop(columns=['candidate_number'])
                
            # Changed st.dataframe to st.table to prevent Javascript chunk loading 404 errors on Render
            if '_id' in df.columns:
                df = df.set_index('_id')
            st.table(df)
        else:
            st.success("✨ Database is clean and ready. Awaiting your first test call.")

    except Exception as e:
        st.error(f"Database connection error: {e}")