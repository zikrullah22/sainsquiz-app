import streamlit as st
import pandas as pd
import random
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="SainsQuiz - SPM Science",
    page_icon="🧪",
    layout="centered",
)

# ---------- THE "THEME-PROOF" CSS (FORCES BLACK TEXT ON WHITE) ----------
st.markdown("""
<style>
    /* 1. Force the main background and sidebar to be Light */
    .stApp { background-color: #f3f4f6 !important; }
    [data-testid="stSidebar"] { 
        background-color: #ffffff !important; 
        border-right: 3px solid #000000 !important; 
    }

    /* 2. FORCE ALL TEXT TO BE DEEP BLACK regardless of system theme */
    h1, h2, h3, h4, h5, h6, p, span, label, li, div, .stMarkdown, .stSelectbox label {
        color: #000000 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* 3. FIX RADIO BUTTON OPTIONS (The White-on-White Issue) */
    div.row-widget.stRadio > div[role="radiogroup"] {
        background-color: transparent !important;
    }

    div.row-widget.stRadio label {
        background-color: #ffffff !important;
        border: 3px solid #000000 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin-bottom: 10px !important;
        box-shadow: 4px 4px 0px #000000 !important;
        display: flex !important;
        align-items: center !important;
    }

    /* Target the text inside the radio labels specifically */
    div.row-widget.stRadio label div[data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        margin: 0px !important;
    }

    /* Selection circle visibility */
    div.row-widget.stRadio [data-baseweb="radio"] > div:first-child {
        border: 2px solid #000000 !important;
    }

    /* 4. FIX CARDS AND HEADERS */
    .header-box {
        background: #ffffff !important;
        border: 4px solid #000000 !important;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 8px 8px 0px #2563eb !important;
        text-align: center;
        margin-bottom: 25px;
    }

    .question-card {
        background: #ffffff !important;
        border: 4px solid #000000 !important;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 8px 8px 0px #000000 !important;
        margin-bottom: 20px;
    }

    /* 5. LEADERBOARD STYLING */
    .lb-item {
        background: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 8px;
        padding: 10px;
        margin: 8px 0;
        display: flex;
        justify-content: space-between;
        font-weight: 800;
        color: #000000 !important;
        box-shadow: 2px 2px 0px #000000 !important;
    }

    /* 6. BUTTONS */
    .stButton>button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        padding: 10px 20px !important;
        box-shadow: 4px 4px 0px #2563eb !important;
        width: 100% !important;
    }
    
    .stButton>button:hover {
        background-color: #2563eb !important;
        color: white !important;
        transform: translate(-2px, -2px);
    }

    /* Hide Streamlit elements that cause color confusion */
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
def init_state():
    if 'score' not in st.session_state:
        st.session_state.update({
            'score': 0, 'q_index': 0, 'quiz_started': False,
            'subject': "All", 'questions': [], 'total_questions': 0, 'show_feedback': False
        })

init_state()

# ---------- GOOGLE SHEETS SETUP ----------
@st.cache_resource
def get_sheet():
    try:
        if "gcp_service_account" not in st.secrets: return None
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
        client = gspread.authorize(creds)
        return client.open("SainsQuiz Leaderboard").sheet1
    except: return None

def save_score(name, score):
    s = get_sheet()
    if s:
        try:
            s.append_row([name, score, datetime.now().strftime("%Y-%m-%d %H:%M")])
            return True
        except: return False
    return False

@st.cache_data(ttl=30)
def get_leaderboard():
    s = get_sheet()
    if s:
        try:
            records = s.get_all_records()
            lb = [(str(r['Name']), int(r['Score'])) for r in records if 'Name' in r and 'Score' in r]
            return sorted(lb, key=lambda x: x[1], reverse=True)[:5]
        except: return []
    return []

# ---------- QUESTIONS DB ----------
@st.cache_data
def load_questions():
    return [
        {"subject": "Chemistry", "question": "What is the chemical symbol for gold?", "options": ["Go", "Gd", "Au", "Ag"], "correct_option": 2, "explanation": "Au comes from the Latin word 'Aurum'."},
        {"subject": "Physics", "question": "What type of energy does a moving car have?", "options": ["Potential energy", "Kinetic energy", "Chemical energy", "Nuclear energy"], "correct_option": 1, "explanation": "Kinetic energy is the energy possessed by an object due to its motion."},
        {"subject": "Biology", "question": "Which organelle is known as the powerhouse of the cell?", "options": ["Nucleus", "Ribosome", "Mitochondria", "Golgi Body"], "correct_option": 2, "explanation": "Mitochondria are the sites of aerobic respiration which produces ATP (energy)."}
    ]

questions_db = load_questions()

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown('<h1 style="font-size: 1.8rem;">🧪 SainsQuiz</h1>', unsafe_allow_html=True)
    subj = st.selectbox("Choose Subject", ["All", "Physics", "Chemistry", "Biology"])
    
    if st.button("New Quiz 🚀"):
        st.session_state.quiz_started = True
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.show_feedback = False
        pool = questions_db if subj == "All" else [q for q in questions_db if q['subject'] == subj]
        st.session_state.questions = random.sample(pool, min(10, len(pool)))
        st.session_state.total_questions = len(st.session_state.questions)
        st.rerun()

    st.markdown("<br><h3 style='margin-bottom:0;'>🏆 Top Players</h3>", unsafe_allow_html=True)
    lb_data = get_leaderboard()
    if lb_data:
        for p, s in lb_data:
            st.markdown(f'<div class="lb-item"><span>{p}</span><span>{s} pts</span></div>', unsafe_allow_html=True)
    else:
        st.write("No scores yet!")

# ---------- MAIN CONTENT ----------
if not st.session_state.quiz_started:
    st.markdown('<div class="header-box"><h1>🧪 SainsQuiz</h1><p>Master SPM Science with Ease</p></div>', unsafe_allow_html=True)
    st.markdown("""
        <div style="background:white; border:3px solid black; padding:20px; border-radius:15px; box-shadow:5px 5px 0px black;">
            <h4>Ready to test your knowledge?</h4>
            <p>1. Select a subject in the sidebar.<br>2. Complete 10 questions.<br>3. Save your score to the global leaderboard!</p>
        </div>
    """, unsafe_allow_html=True)
else:
    if st.session_state.q_index < st.session_state.total_questions:
        q = st.session_state.questions[st.session_state.q_index]
        
        st.markdown(f"""
        <div class="question-card">
            <span style="background:#2563eb; color:white; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:bold;">{q['subject']}</span>
            <h3 style="margin-top:10px;">Question {st.session_state.q_index + 1} of {st.session_state.total_questions}</h3>
            <p style="font-size:1.3rem; font-weight:700;">{q['question']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Radio options
        user_choice = st.radio("Choose answer:", q['options'], key=f"q_{st.session_state.q_index}", index=None, label_visibility="collapsed")

        col_left, col_right = st.columns(2)
        
        if not st.session_state.show_feedback:
            with col_left:
                if st.button("Submit Answer"):
                    if user_choice:
                        st.session_state.show_feedback = True
                        if user_choice == q['options'][q['correct_option']]:
                            st.session_state.score += 1
                        st.rerun()
                    else:
                        st.warning("Please choose an answer first!")
        else:
            is_correct = (user_choice == q['options'][q['correct_option']])
            bg_col = "#dcfce7" if is_correct else "#fee2e2"
            border_col = "#166534" if is_correct else "#991b1b"
            
            st.markdown(f"""
            <div style="background:{bg_col}; border:3px solid {border_col}; padding:15px; border-radius:12px; color:black; margin-bottom:15px;">
                <h4 style="margin:0; color:{border_col};">{"✅ Correct!" if is_correct else "❌ Incorrect"}</h4>
                <p style="margin:5px 0 0 0;"><strong>Correct Answer:</strong> {q['options'][q['correct_option']]}</p>
                <p style="font-size:0.9rem; margin-top:5px;">{q['explanation']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            with col_right:
                if st.button("Next Question ➡️"):
                    st.session_state.q_index += 1
                    st.session_state.show_feedback = False
                    st.rerun()
    else:
        st.balloons()
        st.markdown(f'<div class="header-box"><h1>🎊 Quiz Complete!</h1><h2>Your Score: {st.session_state.score} / {st.session_state.total_questions}</h2></div>', unsafe_allow_html=True)
        
        name_input = st.text_input("Enter your name for the leaderboard:", placeholder="Ex: Einstein Jr")
        if st.button("Save & Return Home"):
            if name_input:
                save_score(name_input, st.session_state.score)
                st.cache_data.clear()
            st.session_state.quiz_started = False
            st.rerun()

st.markdown('<p style="text-align:center; margin-top:50px; color:#6b7280 !important;">SainsQuiz 🇲🇾 Master SPM Science</p>', unsafe_allow_html=True)
