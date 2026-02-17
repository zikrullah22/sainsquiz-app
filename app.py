import streamlit as st
import pandas as pd
import random
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="SainsQuiz", page_icon="🧪", layout="centered")

# ---------- MINIMAL CSS TO FORCE VISIBLE OPTIONS ----------
st.markdown("""
<style>
    /* Force radio options to be visible */
    div.row-widget.stRadio > div {
        background-color: transparent !important;
        padding: 0 !important;
    }
    div.row-widget.stRadio label {
        background-color: #f0f2f6 !important;   /* Light gray background */
        border: 1px solid #ccc !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        margin: 8px 0 !important;
        color: #111 !important;                  /* Dark text */
        font-weight: 500 !important;
        font-size: 1rem !important;
        display: flex !important;
        align-items: center !important;
        cursor: pointer !important;
        transition: 0.2s;
    }
    div.row-widget.stRadio label:hover {
        background-color: #e0e2e6 !important;
        border-color: #1e88e5 !important;
    }
    /* Radio circle */
    div.row-widget.stRadio label div:first-child {
        background-color: white !important;
        border-color: #777 !important;
        margin-right: 12px !important;
    }
    div.row-widget.stRadio label input:checked + div div {
        background-color: #1e88e5 !important;
    }
    /* Header and other elements remain clean */
    .header {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 2rem;
    }
    .header h1 { color: #1e1e1e; }
    .question-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1.5rem;
    }
    .sidebar .sidebar-content { background: white; }
</style>
""", unsafe_allow_html=True)

# ---------- ICONS ----------
PHYSICS_ICON = "📚"
CHEMISTRY_ICON = "🧪"
BIOLOGY_ICON = "🔬"
LOGO_ICON = "🧪"

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

# ---------- LOAD QUESTIONS ----------
@st.cache_data
def load_questions():
    try:
        with open("questions.json") as f:
            return json.load(f)
    except:
        return [
            {"subject": "Physics", "question": "SI unit of force?",
             "options": ["Joule","Newton","Watt","Pascal"], "correct_option": 1,
             "explanation": "Newton (N) is the SI unit."},
            {"subject": "Physics", "question": "Scalar quantity?",
             "options": ["Velocity","Acceleration","Mass","Force"], "correct_option": 2,
             "explanation": "Mass is scalar."},
            {"subject": "Chemistry", "question": "pH of neutral?",
             "options": ["0","7","14","1"], "correct_option": 1,
             "explanation": "pH 7 is neutral."},
            {"subject": "Chemistry", "question": "Formula for water?",
             "options": ["H2O","CO2","O2","H2O2"], "correct_option": 0,
             "explanation": "Water is H₂O."},
            {"subject": "Biology", "question": "Powerhouse of the cell?",
             "options": ["Nucleus","Ribosome","Mitochondria","Golgi"], "correct_option": 2,
             "explanation": "Mitochondria produce ATP."},
        ]
questions_db = load_questions()

# ---------- GOOGLE SHEETS (same as before) ----------
@st.cache_resource
def get_google_sheets_connection():
    try:
        if "gcp_service_account" not in st.secrets:
            return None
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("SainsQuiz Leaderboard").sheet1
        if sheet.row_values(1) != ['Name','Score','Date']:
            sheet.clear()
            sheet.append_row(['Name','Score','Date'])
        return sheet
    except:
        return None

def save_score_to_sheets(name, score):
    try:
        sheet = get_google_sheets_connection()
        if sheet:
            sheet.append_row([name, score, datetime.now().strftime("%Y-%m-%d %H:%M")])
            return True
    except:
        pass
    return False

@st.cache_data(ttl=30)
def load_leaderboard():
    try:
        sheet = get_google_sheets_connection()
        if sheet:
            records = sheet.get_all_records()
            lb = []
            for r in records:
                if 'Name' in r and 'Score' in r:
                    try:
                        lb.append((str(r['Name']).strip(), int(r['Score'])))
                    except:
                        pass
            lb.sort(key=lambda x: x[1], reverse=True)
            return lb[:10]
    except:
        pass
    return None

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown(f"## {LOGO_ICON} SainsQuiz\nSPM Science Practice")
    st.markdown("---")
    subjects = ["All","Physics","Chemistry","Biology"]
    selected = st.selectbox("Choose Subject", subjects, index=subjects.index(st.session_state.subject))
    if selected != st.session_state.subject:
        st.session_state.subject = selected
        st.session_state.quiz_started = False
        st.rerun()
    if st.button("New Quiz", use_container_width=True):
        st.session_state.quiz_started = True
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.answers = []
        if st.session_state.subject == "All":
            st.session_state.questions = random.sample(questions_db, min(10, len(questions_db)))
        else:
            filtered = [q for q in questions_db if q['subject'] == st.session_state.subject]
            st.session_state.questions = random.sample(filtered, min(10, len(filtered)))
        st.session_state.total_questions = len(st.session_state.questions)
        st.rerun()
    if st.session_state.quiz_started and st.session_state.total_questions > 0:
        st.metric("Current Score", f"{st.session_state.score}/{st.session_state.total_questions}")
        st.progress(st.session_state.q_index / st.session_state.total_questions)
    st.markdown("### Top Players")
    lb = load_leaderboard()
    if lb:
        for i, (name, score) in enumerate(lb, 1):
            medal = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"{i}."
            st.markdown(f"{medal} {name} – {score}")
    else:
        st.info("No scores yet.")

# ---------- MAIN CONTENT ----------
st.markdown('<div class="header"><h1>🧪 SainsQuiz</h1><p>Practice SPM Science</p></div>', unsafe_allow_html=True)

if not st.session_state.quiz_started:
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"<div class='subject-card'><div style='font-size:2rem;'>{PHYSICS_ICON}</div><h3>Physics</h3><p>Forces, Motion</p></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='subject-card'><div style='font-size:2rem;'>{CHEMISTRY_ICON}</div><h3>Chemistry</h3><p>Periodic Table</p></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div class='subject-card'><div style='font-size:2rem;'>{BIOLOGY_ICON}</div><h3>Biology</h3><p>Cells</p></div>", unsafe_allow_html=True)
    with st.expander("How to Play"):
        st.info("Choose subject → New Quiz → Answer questions → Save score")
else:
    if st.session_state.q_index < st.session_state.total_questions:
        q = st.session_state.questions[st.session_state.q_index]
        st.markdown(f"""
        <div class="question-box">
            <h3>Question {st.session_state.q_index+1} of {st.session_state.total_questions}</h3>
            <p>{q['question']}</p>
            <span style="background:#e0e0e0; padding:4px 12px; border-radius:20px;">{q['subject']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # RADIO BUTTONS – they will now be visible due to the CSS above
        answer = st.radio("", q['options'], key=f"q_{st.session_state.q_index}", index=None, label_visibility="collapsed")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Submit Answer", use_container_width=True):
                if answer is None:
                    st.warning("Select an answer!")
                else:
                    correct = q['options'][q['correct_option']]
                    is_correct = answer == correct
                    st.session_state.answers.append({
                        'question': q['question'], 'user_answer': answer, 'correct': is_correct,
                        'correct_answer': correct, 'explanation': q['explanation']
                    })
                    if is_correct:
                        st.session_state.score += 1
                    st.session_state.show_feedback = True
                    st.rerun()
        with col2:
            if st.session_state.show_feedback:
                if st.button("Next Question", use_container_width=True):
                    st.session_state.q_index += 1
                    st.session_state.show_feedback = False
                    st.rerun()
        
        if st.session_state.show_feedback and st.session_state.answers:
            last = st.session_state.answers[-1]
            if last['correct']:
                st.success(f"✅ Correct! {last['explanation']}")
            else:
                st.error(f"❌ Incorrect. Correct: {last['correct_answer']}. {last['explanation']}")
    else:
        st.balloons()
        percentage = (st.session_state.score / st.session_state.total_questions) * 100
        st.markdown(f"<div class='question-box'><h2>Quiz Complete!</h2><h1>{st.session_state.score}/{st.session_state.total_questions}</h1><h3>{percentage:.1f}%</h3></div>", unsafe_allow_html=True)
        
        with st.expander("Review Answers"):
            for i, ans in enumerate(st.session_state.answers):
                st.markdown(f"**Q{i+1}:** {'✅' if ans['correct'] else '❌'} {ans['question']}")
                if not ans['correct']:
                    st.markdown(f"*Correct: {ans['correct_answer']}*")
                st.markdown(f"*{ans['explanation']}*")
                st.markdown("---")
        
        name = st.text_input("Your name:", placeholder="Enter name")
        if st.button("Save Score"):
            if name:
                if save_score_to_sheets(name, st.session_state.score):
                    st.success("Saved to global leaderboard!")
                    st.cache_data.clear()
                else:
                    st.session_state.leaderboard.append((name, st.session_state.score))
                    st.session_state.leaderboard.sort(key=lambda x: x[1], reverse=True)
                    st.session_state.leaderboard = st.session_state.leaderboard[:10]
                    st.success("Saved locally!")
                st.rerun()
            else:
                st.warning("Enter name!")
        if st.button("Take Another Quiz"):
            st.session_state.quiz_started = False
            st.rerun()

st.markdown("---")
st.caption("🇲🇾 SainsQuiz – Helping Malaysian students")
