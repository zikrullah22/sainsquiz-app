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

# ---------- FINAL CSS WITH MAXIMUM VISIBILITY ----------
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* Background */
    .stApp { background-color: #f3f4f6; }

    /* Header & Cards */
    .header {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 0px #000000;
        text-align: center;
        margin-bottom: 2rem;
        border: 3px solid #000000;
    }
    .header h1 { color: #111827; font-size: 2.2rem; font-weight: 800; margin-bottom: 0.25rem; }

    /* Subject Cards */
    .subject-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        border: 3px solid #000000;
        transition: 0.2s;
        height: 100%;
        box-shadow: 0 4px 0px #000000;
    }
    .subject-card:hover { transform: translateY(-3px); border-color: #2563eb; }

    /* Question Box */
    .question-box {
        background: white;
        padding: 1.8rem;
        border-radius: 16px;
        border: 3px solid #000000;
        margin-bottom: 1.8rem;
        box-shadow: 0 6px 0px #000000;
    }
    .subject-tag {
        background: #2563eb;
        color: white;
        padding: 0.3rem 1.2rem;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 10px;
    }

    /* ===== RADIO BUTTONS – NEUBRUTALISM STYLE ===== */
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
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 0px #000000 !important;
        cursor: pointer !important;
    }

    div.row-widget.stRadio label:hover {
        background-color: #f8fafc !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 0px #2563eb !important;
        border-color: #2563eb !important;
    }

    /* Force visibility on the text */
    div.row-widget.stRadio label p {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
    }

    /* Highlight when selected */
    div.row-widget.stRadio label:has(input:checked) {
        background-color: #eff6ff !important;
        border-color: #2563eb !important;
        box-shadow: 0 2px 0px #2563eb !important;
    }

    /* ===== BUTTONS ===== */
    .stButton button {
        background: #000000 !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        padding: 0.7rem 1.5rem !important;
        border: 2px solid #000000 !important;
        box-shadow: 0 4px 0px #2563eb !important;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 0px #2563eb !important;
    }

    /* Leaderboard */
    .leaderboard-item {
        background: white;
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

# ---------- GOOGLE SHEETS & DATA ----------
@st.cache_data(ttl=3600)
def load_questions():
    try:
        with open("questions.json", "r") as f: return json.load(f)
    except:
        return [
            {"subject": "Physics", "question": "What is the SI unit of force?", "options": ["Joule", "Newton", "Watt", "Pascal"], "correct_option": 1, "explanation": "Newton (N) is the SI unit of force."},
            {"subject": "Chemistry", "question": "What is the pH of a neutral solution?", "options": ["0", "7", "14", "1"], "correct_option": 1, "explanation": "pH 7 is neutral."},
            {"subject": "Biology", "question": "Which organelle is the 'powerhouse' of the cell?", "options": ["Nucleus", "Ribosome", "Mitochondria", "Golgi"], "correct_option": 2, "explanation": "Mitochondria produce ATP."}
        ]

questions_db = load_questions()

@st.cache_resource
def get_google_sheets_connection():
    try:
        if "gcp_service_account" not in st.secrets: return None
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
        client = gspread.authorize(creds)
        sheet = client.open("SainsQuiz Leaderboard").sheet1
        return sheet
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
def load_leaderboard():
    sheet = get_google_sheets_connection()
    if sheet:
        try:
            records = sheet.get_all_records()
            lb = [(r['Name'], int(r['Score'])) for r in records if 'Name' in r and 'Score' in r]
            return sorted(lb, key=lambda x: x[1], reverse=True)[:10]
        except: return None
    return None

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## 🧪 SainsQuiz")
    st.divider()
    subjects = ["All", "Physics", "Chemistry", "Biology"]
    selected = st.selectbox("Choose Subject", subjects, index=subjects.index(st.session_state.subject))
    
    if selected != st.session_state.subject:
        st.session_state.subject = selected
        st.session_state.quiz_started = False
        st.rerun()

    if st.button("New Quiz 🚀", use_container_width=True):
        st.session_state.quiz_started = True
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.answers = []
        st.session_state.show_feedback = False
        
        filtered = questions_db if selected == "All" else [q for q in questions_db if q['subject'] == selected]
        st.session_state.questions = random.sample(filtered, min(10, len(filtered)))
        st.session_state.total_questions = len(st.session_state.questions)
        st.rerun()

    if st.session_state.quiz_started:
        st.divider()
        st.metric("Progress", f"{st.session_state.q_index}/{st.session_state.total_questions}")
        st.progress(st.session_state.q_index / st.session_state.total_questions)

    st.markdown("### 🏆 Leaderboard")
    lb = load_leaderboard()
    if lb:
        for i, (name, score) in enumerate(lb, 1):
            st.markdown(f'<div class="leaderboard-item"><span>{i}. {name}</span><span>{score}</span></div>', unsafe_allow_html=True)

# ---------- MAIN CONTENT ----------
st.markdown('<div class="header"><h1>🧪 SainsQuiz</h1><p>Master SPM Science • Compete with Friends</p></div>', unsafe_allow_html=True)

if not st.session_state.quiz_started:
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown('<div class="subject-card">📚<br><h3>Physics</h3></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="subject-card">🧪<br><h3>Chemistry</h3></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="subject-card">🔬<br><h3>Biology</h3></div>', unsafe_allow_html=True)
    
    with st.expander("How to Play"):
        st.write("1. Pick a subject. 2. Answer 10 questions. 3. Save your score!")

else:
    if st.session_state.q_index < st.session_state.total_questions:
        q = st.session_state.questions[st.session_state.q_index]
        
        st.markdown(f"""
        <div class="question-box">
            <span class="subject-tag">{q['subject']}</span>
            <h3>Question {st.session_state.q_index + 1} of {st.session_state.total_questions}</h3>
            <p style="font-size:1.3rem; font-weight:700;">{q['question']}</p>
        </div>
        """, unsafe_allow_html=True)

        ans = st.radio("Options", q['options'], key=f"q_{st.session_state.q_index}", index=None, label_visibility="collapsed")

        col_sub, col_next = st.columns(2)
        
        with col_sub:
            if not st.session_state.show_feedback:
                if st.button("Submit Answer", use_container_width=True):
                    if ans:
                        correct_ans = q['options'][q['correct_option']]
                        is_correct = (ans == correct_ans)
                        if is_correct: st.session_state.score += 1
                        st.session_state.answers.append({'q': q['question'], 'user': ans, 'correct': is_correct, 'exp': q['explanation'], 'ans': correct_ans})
                        st.session_state.show_feedback = True
                        st.rerun()
                    else: st.warning("Pick an option!")

        if st.session_state.show_feedback:
            last = st.session_state.answers[-1]
            color = "#dcfce7" if last['correct'] else "#fee2e2"
            border = "#166534" if last['correct'] else "#991b1b"
            
            st.markdown(f"""
            <div style="background:{color}; border:3px solid {border}; padding:1.2rem; border-radius:12px; margin-bottom:1rem; color:{border}; font-weight:700;">
                {"✅ Correct!" if last['correct'] else "❌ Incorrect. Correct: " + last['ans']}<br>
                <small style="font-weight:500;">{last['exp']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            with col_next:
                if st.button("Next Question ➡️", use_container_width=True):
                    st.session_state.q_index += 1
                    st.session_state.show_feedback = False
                    st.rerun()

    else:
        st.balloons()
        st.markdown(f'<div class="header"><h1>🎉 Finished!</h1><p style="font-size:3rem; font-weight:800;">{st.session_state.score}/{st.session_state.total_questions}</p></div>', unsafe_allow_html=True)
        
        name = st.text_input("Enter name to save score:")
        if st.button("Save to Leaderboard"):
            if name:
                if save_score_to_sheets(name, st.session_state.score):
                    st.success("Score Saved!")
                    st.cache_data.clear()
                    st.session_state.quiz_started = False
                    st.rerun()
            else: st.error("Enter a name!")

st.markdown('<div style="text-align:center; padding:20px; color:#6b7280;">SainsQuiz 🇲🇾 Master SPM Science</div>', unsafe_allow_html=True)
