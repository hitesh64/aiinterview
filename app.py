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

# --- Embedded Secure Server for VAPI & MongoDB Webhook ---
@st.cache_resource
def start_local_server():
    class RequestHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(self.path)
            if parsed_url.path == '/interview':
                query_params = parse_qs(parsed_url.query)
                candidate_name = query_params.get('name', ['Unknown Candidate'])[0]
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                # CLEAN, MODERN, ANIMATED VAPI UI
                vapi_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <script src="https://cdn.jsdelivr.net/gh/VapiAI/html-script-tag@latest/dist/assets/index.js"></script>
                    <style>
                        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; overflow: hidden; }
                        .container { text-align: center; display: flex; flex-direction: column; align-items: center; }
                        
                        /* Premium Pulsing Animation */
                        .pulse-ring {
                            width: 70px; height: 70px; background: #3b82f6; border-radius: 50%;
                            display: flex; align-items: center; justify-content: center;
                            box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.5);
                            animation: pulse 2.5s infinite;
                            margin-bottom: 25px;
                            color: white; font-size: 24px; font-weight: bold; font-family: 'Inter', sans-serif;
                        }
                        @keyframes pulse {
                            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }
                            70% { transform: scale(1); box-shadow: 0 0 0 20px rgba(59, 130, 246, 0); }
                            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
                        }
                        
                        h2 { color: #0f172a; margin-bottom: 10px; font-size: 1.6rem; font-weight: 800; letter-spacing: -0.5px; }
                        p { color: #64748b; font-size: 1.05rem; max-width: 320px; line-height: 1.6; font-weight: 500; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="pulse-ring">AI</div>
                        <h2>Your AI Interviewer is Ready</h2>
                        <p>Welcome, __CANDIDATE_NAME__! I am ready to begin our conversation. Please ensure you are in a quiet environment, then click the phone icon in the bottom right corner to start.</p>
                    </div>
                    <script>
                        window.onload = function() {
                            if (window.vapiSDK) {
                                const vapiInstance = window.vapiSDK.run({
                                    apiKey: "635c8d91-9f2d-4de6-bb4f-67c1f493fa0d",
                                    assistant: "793df902-6bd1-4f7f-b4a8-f9737b211180",
                                    config: {}
                                });

                                let liveTranscript = "";

                                // Capture real-time conversation
                                vapiInstance.on('message', (message) => {
                                    if (message.type === 'transcript' && message.transcriptType === 'final') {
                                        let speaker = message.role === 'user' ? '__CANDIDATE_NAME__' : 'AI';
                                        liveTranscript += speaker + ": " + message.transcript + "\\n";
                                    }
                                });

                                // Call Ended -> Save Transcript
                                vapiInstance.on('call-end', () => {
                                    let finalStatus = liveTranscript.trim() === "" ? "Call Cut (No Audio)" : "Completed Interview";
                                    
                                    fetch('/save', {
                                        method: 'POST',
                                        headers: { 'Content-Type': 'application/json' },
                                        body: JSON.stringify({
                                            name: "__CANDIDATE_NAME__",
                                            status: finalStatus,
                                            transcript: liveTranscript || "Candidate hung up before speaking.",
                                            summary: "Check Vapi Dashboard for AI Summary.",
                                            is_name_verified: true,
                                            timestamp: new Date().toLocaleString()
                                        })
                                    });
                                    // Reset transcript for the next call
                                    liveTranscript = ""; 
                                });
                            }
                        };
                    </script>
                </body>
                </html>
                """.replace("__CANDIDATE_NAME__", candidate_name)
                self.wfile.write(vapi_html.encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            if self.path == '/save':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                try:
                    import json
                    from pymongo import MongoClient
                    data = json.loads(post_data.decode('utf-8'))
                    
                    client = MongoClient("mongodb+srv://kunal:KdVygwFo0Anau8uX@hitesh.cqczgkd.mongodb.net/")
                    db = client["AI_Interviews"]
                    collection = db["candidates"]
                    collection.insert_one(data)
                    
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"Saved to DB")
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(e).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()

    def run_server():
        try:
            with socketserver.TCPServer(("", 8506), RequestHandler) as httpd:
                httpd.serve_forever()
        except OSError:
            pass

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    return True

start_local_server()

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
        # Center the iframe using columns for a cleaner, focused look
        col_left, col_center, col_right = st.columns([1, 8, 1])
        
        from urllib.parse import quote
        safe_name = quote(st.session_state.candidate_name)
        
        with col_center:
            iframe_html = f"""
            <iframe 
                src="http://localhost:8506/interview?name={safe_name}" 
                width="100%" 
                height="450" 
                allow="microphone; autoplay; clipboard-read; clipboard-write" 
                frameborder="0"
                style="border: 1px solid #e2e8f0; border-radius: 20px; background: #ffffff; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);">
            </iframe>
            """
            st.markdown(iframe_html, unsafe_allow_html=True)
            
            # Allow user to restart with a new name
            if st.button("Start a New Interview", type="secondary", use_container_width=True):
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
                
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.success("✨ Database is clean and ready. Awaiting your first test call.")

    except Exception as e:
        st.error(f"Database connection error: {e}")