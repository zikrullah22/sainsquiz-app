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
    initial_sidebar_state="expanded"
)

# ---------- FINAL CSS (FORCED READABILITY & NEUBRUTALISM) ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Global Text Reset: Force EVERYTHING to be black to fix visibility issues */
    * { font-family: 'Inter', sans-serif; }
    
    .stApp { background-color: #f3f4f6; }

    /* Force visibility on all headers and paragraphs in white boxes */
    .header h1, .header p, .question-box h3, .question-box p, 
    .subject-card h3, .subject-card p,
    .leaderboard-item span, .info-box {
        color: #000000 !important;
    }

    /* Header */
    .header {
        background: white !important;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 0px #000000;
        text-align: center;
        margin-bottom: 2rem;
        border: 3px solid #000000;
    }

    /* Subject Cards */
    .subject-card {
        background: white !important;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        border: 3px solid #000000;
        box-shadow: 0 4px 0px #000000;
        transition: 0.2s;
    }
    .subject-card:hover { transform: translateY(-3px); }

    /* Question Box */
    .question-box {
        background: white !important;
        padding: 1.8rem;
        border-radius: 16px;
        border: 3px solid #000000;
        margin-bottom: 1.8rem;
        box-shadow: 0 6px 0px #000000;
    }

    .subject-tag {
        background: #2563eb !important;
        color: white !important;
        padding: 0.3rem 1.2rem;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 10px;
    }

    /* ===== RADIO BUTTONS – FORCED VISIBILITY ===== */
    div.row-widget.stRadio > div[role="radiogroup"] {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    
    div.row-widget.stRadio label {
        background-color: #ffffff !important;
        border: 3px solid #000000 !important;
        border-radius: 14px !important;
        padding: 1.2rem 1.5rem !important;
        margin: 0px !important;
        box-shadow: 0 4px 0px #000000 !important;
        transition: all 0.2s ease !important;
    }

    /* Target the text inside the radio option labels */
    div.row-widget.stRadio label p {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        margin: 0 !important;
    }

    div.row-widget.stRadio label:hover {
        background-color: #f0f7ff !important;
        border-color: #2563eb !important;
        box-shadow: 0 6px 0px #2563eb !important;
    }

    /* Radio Selection Circle */
    div.row-widget.stRadio [data-baseweb="radio"] > div:first-child {
        border: 2px solid black !important;
        background-color: white !important;
    }

    /* ===== BUTTONS ===== */
    .stButton button {
        background: #000000 !important;
        color: white !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        padding: 0.7rem 1.5rem !important;
        border: 3px solid #000000 !important;
        box-shadow: 0 4px 0px #2563eb !important;
        width: 100%;
        transition: 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 0px #2563eb !important;
    }

    /* Sidebar Fixes */
    [data-testid="stSidebar"] { background-color: #ffffff; }
    .leaderboard-item {
        background: white !important;
        padding: 0.7rem 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        border: 2px solid #000000;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
def init_session_state():
    defaults = {
        'score': 0, 'q_index': 0, 'answers': [], 'quiz_started': False,
        'subject': "All", 'feedback': None, 'leaderboard': [],
        'questions': [], 'total_questions': 0, 'show_feedback': False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# ---------- GOOGLE SHEETS CONNECTION ----------
@st.cache_resource
def get_google_sheets_connection():
    try:
        if "gcp_service_account" not in st.secrets: return None
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
        client = gspread.authorize(creds)
        return client.open("SainsQuiz Leaderboard").sheet1
    except: return None

def save_score_to_sheets(name, score):
    sheet = get_google_sheets_connection()
    if sheet:
        try:
            sheet.append_row([name, score, datetime.now().strftime("%Y-%m-%d %H:%M")])
            return True
        except: return False
    return False

@st.cache_data(ttl=30)
def load_leaderboard_from_sheets():
    sheet = get_google_sheets_connection()
    if sheet:
        try:
            records = sheet.get_all_records()
            lb = [(str(r['Name']), int(r['Score'])) for r in records if 'Name' in r and 'Score' in r]
            return sorted(lb, key=lambda x: x[1], reverse=True)[:10]
        except: return None
    return None

# ---------- LOAD QUESTIONS ----------
@st.cache_data
def load_questions():
    try:
        with open("questions.json", "r") as f: return json.load(f)
    except:
        return [
            {"subject": "Chemistry", "question": "What is the chemical symbol for gold?", "options": ["Go", "Gd", "Au", "Ag"], "correct_option": 2, "explanation": "Au comes from the Latin word 'Aurum'."},
            {"subject": "Physics", "question": "Which law states that F = ma?", "options": ["Newton's 1st", "Newton's 2nd", "Newton's 3rd", "Hooke's Law"], "correct_option": 1, "explanation": "Newton's Second Law describes the relationship between force, mass, and acceleration."},
            {"subject": "Biology", "question": "Which organelle is known as the powerhouse of the cell?", "options": ["Nucleus", "Ribosome", "Mitochondria", "Vacuole"], "correct_option": 2, "explanation": "Mitochondria generate cellular energy (ATP)."}
        ]

questions_db = load_questions()

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## 🧪 SainsQuiz")
    st.divider()
    
    subj_list = ["All", "Physics", "Chemistry", "Biology"]
    selected = st.selectbox("Choose Subject", subj_list, index=subj_list.index(st.session_state.subject))
    
    if selected != st.session_state.subject:
        st.session_state.subject = selected
        st.session_state.quiz_started = False

    if st.button("New Quiz 🚀", use_container_width=True):
        st.session_state.quiz_started = True
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.show_feedback = False
        st.session_state.answers = []
        
        pool = questions_db if selected == "All" else [q for q in questions_db if q['subject'] == selected]
        st.session_state.questions = random.sample(pool, min(10, len(pool)))
        st.session_state.total_questions = len(st.session_state.questions)
        st.rerun()

    if st.session_state.quiz_started:
        st.divider()
        st.metric("Progress", f"{st.session_state.q_index}/{st.session_state.total_questions}")
        st.progress(st.session_state.q_index / st.session_state.total_questions if st.session_state.total_questions > 0 else 0)

    st.markdown("### 🏆 Top Players")
    lb = load_leaderboard_from_sheets()
    if lb:
        for i, (name, score) in enumerate(lb, 1):
            st.markdown(f'<div class="leaderboard-item"><span>{i}. {name}</span><span>{score}</span></div>', unsafe_allow_html=True)
    else:
        st.info("No scores yet!")

# ---------- MAIN CONTENT ----------
st.markdown('<div class="header"><h1>🧪 SainsQuiz</h1><p>Master SPM Science • Compete with Friends</p></div>', unsafe_allow_html=True)

if not st.session_state.quiz_started:
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown('<div class="subject-card"><h3>Physics</h3><p>Forces & Motion</p></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="subject-card"><h3>Chemistry</h3><p>Acids & Bonds</p></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="subject-card"><h3>Biology</h3><p>Cells & Human Body</p></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="header" style="margin-top:20px; text-align:left;">
        <h3 style="margin-bottom:10px;">How to Play:</h3>
        <p>1. Choose your subject in the sidebar.<br>2. Click 'New Quiz' to start.<br>3. Earn points and save your name to the leaderboard!</p>
    </div>
    """, unsafe_allow_html=True)

else:
    if st.session_state.q_index < st.session_state.total_questions:
        q = st.session_state.questions[st.session_state.q_index]
        
        st.markdown(f"""
        <div class="question-box">
            <span class="subject-tag">{q['subject']}</span>
            <h3>Question {st.session_state.q_index + 1} of {st.session_state.total_questions}</h3>
            <p style="font-size:1.4rem;">{q['question']}</p>
        </div>
        """, unsafe_allow_html=True)

        user_choice = st.radio("Options", q['options'], key=f"q_{st.session_state.q_index}", index=None, label_visibility="collapsed")

        col_a, col_b = st.columns(2)
        
        if not st.session_state.show_feedback:
            with col_a:
                if st.button("Submit Answer"):
                    if user_choice:
                        correct_val = q['options'][q['correct_option']]
                        is_correct = (user_choice == correct_val)
                        if is_correct: st.session_state.score += 1
                        st.session_state.answers.append({'correct': is_correct, 'exp': q['explanation'], 'val': correct_val})
                        st.session_state.show_feedback = True
                        st.rerun()
                    else: st.error("Please select an answer!")
        else:
            feedback = st.session_state.answers[-1]
            f_bg = "#dcfce7" if feedback['correct'] else "#fee2e2"
            f_txt = "#166534" if feedback['correct'] else "#991b1b"
            
            st.markdown(f"""
            <div style="background:{f_bg}; border:3px solid #000000; padding:1.2rem; border-radius:12px; margin-bottom:1rem; color:{f_txt}; font-weight:700;">
                {"✅ Correct!" if feedback['correct'] else "❌ Incorrect. Correct: " + feedback['val']}<br>
                <p style="color:black; font-weight:400; margin-top:5px;">{feedback['exp']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            with col_b:
                if st.button("Next Question ➡️"):
                    st.session_state.q_index += 1
                    st.session_state.show_feedback = False
                    st.rerun()
    else:
        st.balloons()
        st.markdown(f'<div class="header"><h1>🎉 Quiz Complete!</h1><p style="font-size:3rem; font-weight:800;">{st.session_state.score} / {st.session_state.total_questions}</p></div>', unsafe_allow_html=True)
        
        col_name, col_save = st.columns([3, 1])
        with col_name:
            player_name = st.text_input("Enter your name to save score:", placeholder="Your Name")
        with col_save:
            st.write("") # Spacer
            if st.button("Save"):
                if player_name:
                    if save_score_to_sheets(player_name, st.session_state.score):
                        st.success("Saved!")
                        st.cache_data.clear()
                        st.session_state.quiz_started = False
                        st.rerun()
                    else: st.error("Save failed.")
                else: st.warning("Enter name!")

st.markdown('<div style="text-align:center; padding:30px; color:#6b7280;">SainsQuiz 🇲🇾 Master SPM Science</div>', unsafe_allow_html=True)
