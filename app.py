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

# ---------- FORCE VISIBLE OPTIONS WITH HIGH CONTRAST ----------
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* Background */
    .stApp { background-color: #f8fafc; }

    /* Header */
    .header {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid #e2e8f0;
    }
    .header h1 {
        color: #0f172a;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .header p {
        color: #475569;
        font-size: 1rem;
    }

    /* Subject Cards */
    .subject-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        border: 1px solid #e2e8f0;
        transition: 0.2s;
        height: 100%;
    }
    .subject-card:hover {
        border-color: #2563eb;
        box-shadow: 0 4px 12px rgba(37,99,235,0.1);
    }
    .subject-icon { font-size: 2.5rem; }
    .subject-card h3 {
        color: #0f172a;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 0.5rem 0 0.25rem;
    }
    .subject-card p {
        color: #64748b;
        font-size: 0.85rem;
    }

    /* Question Box */
    .question-box {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    .question-box h3 {
        color: #2563eb;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    .question-box p {
        color: #0f172a;
        font-size: 1.2rem;
        font-weight: 600;
        line-height: 1.5;
        margin-bottom: 0.75rem;
    }
    .subject-tag {
        background: #e2e8f0;
        color: #334155;
        padding: 0.25rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
    }

    /* ===== RADIO BUTTONS – FULLY VISIBLE ===== */
    div.row-widget.stRadio > div {
        background: transparent !important;
        padding: 0 !important;
    }
    div.row-widget.stRadio label {
        background: black !important;           /* Light background */
        border: 1px solid #cbd5e1 !important;   /* Visible border */
        border-radius: 12px !important;
        padding: 1rem 1.2rem !important;
        margin: 0.6rem 0 !important;
       color: #111111 !important;            /* Dark text */
        font-weight: 500 !important;
        font-size: 1.05rem !important;
        display: flex !important;
        align-items: center !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }
    div.row-widget.stRadio label:hover {
        background: #f8fafc !important;
        border-color: #2563eb !important;
        box-shadow: 0 4px 8px rgba(37,99,235,0.1) !important;
    }
    /* Radio circle (the dot) */
    div.row-widget.stRadio label div:first-child {
        background-color: white !important;
        border-color: #94a3b8 !important;
        margin-right: 12px !important;
    }
    div.row-widget.stRadio label input:checked + div div {
        background-color: #2563eb !important;
    }

    /* Buttons */
    .stButton button {
        background: #2563eb !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.2rem !important;
        font-size: 0.95rem !important;
        transition: 0.2s !important;
        border: 1px solid #1d4ed8 !important;
    }
    .stButton button:hover {
        background: #1d4ed8 !important;
        box-shadow: 0 4px 10px rgba(37,99,235,0.3) !important;
    }
    .secondary-button button {
        background: white !important;
        color: #2563eb !important;
        border: 1px solid #2563eb !important;
    }
    .secondary-button button:hover {
        background: #f1f5f9 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e2e8f0;
        padding: 1.5rem 1rem;
    }
    .sidebar-header { text-align: center; margin-bottom: 1.5rem; }
    .sidebar-header h2 { color: #0f172a; font-size: 1.8rem; font-weight: 700; }
    .sidebar-header p { color: #64748b; font-size: 0.9rem; }

    /* Metric */
    [data-testid="stMetric"] {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    [data-testid="stMetric"] label { color: #475569 !important; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    /* Progress bar */
    .stProgress > div > div { background: #2563eb; }

    /* Leaderboard */
    .leaderboard-item {
        background: #f8fafc;
        padding: 0.6rem 1rem;
        border-radius: 8px;
        margin: 0.4rem 0;
        display: flex;
        justify-content: space-between;
        border: 1px solid #e2e8f0;
    }
    .leaderboard-rank { font-weight: 700; color: #2563eb; min-width: 35px; }
    .leaderboard-name { color: #0f172a; font-weight: 500; flex: 1; }
    .leaderboard-score {
        background: #e2e8f0;
        color: #0f172a;
        font-weight: 600;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
    }

    /* Success & Info boxes */
    .success-message {
        background: #d1fae5;
        border: 1px solid #10b981;
        color: #065f46;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .info-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 1rem;
        border-radius: 8px;
        color: #0f172a;
        line-height: 1.6;
    }

    /* Select box */
    .stSelectbox label { color: #0f172a !important; font-weight: 600 !important; }
    .stSelectbox > div > div {
        background: white !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #0f172a !important;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem;
        color: #64748b;
        font-size: 0.85rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 3rem;
    }
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
        'score': 0,
        'q_index': 0,
        'answers': [],
        'quiz_started': False,
        'subject': "All",
        'feedback': None,
        'leaderboard': [],
        'questions': [],
        'total_questions': 0,
        'show_feedback': False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# ---------- LOAD QUESTIONS ----------
@st.cache_data(ttl=3600)
def load_questions():
    try:
        with open("questions.json", "r") as f:
            questions = json.load(f)
            if questions:
                return questions
    except:
        pass
    # Default questions if file not found
    return [
        {"subject": "Physics", "question": "What is the SI unit of force?",
         "options": ["Joule", "Newton", "Watt", "Pascal"], "correct_option": 1,
         "explanation": "Newton (N) is the SI unit of force."},
        {"subject": "Physics", "question": "Which of the following is a scalar quantity?",
         "options": ["Velocity", "Acceleration", "Mass", "Force"], "correct_option": 2,
         "explanation": "Mass is scalar (only magnitude)."},
        {"subject": "Chemistry", "question": "What is the pH of a neutral solution?",
         "options": ["0", "7", "14", "1"], "correct_option": 1,
         "explanation": "pH 7 is neutral."},
        {"subject": "Chemistry", "question": "What is the chemical formula for water?",
         "options": ["H2O", "CO2", "O2", "H2O2"], "correct_option": 0,
         "explanation": "Water is H₂O – two hydrogen atoms and one oxygen atom."},
        {"subject": "Biology", "question": "Which organelle is the 'powerhouse' of the cell?",
         "options": ["Nucleus", "Ribosome", "Mitochondria", "Golgi apparatus"], "correct_option": 2,
         "explanation": "Mitochondria produce ATP."},
    ]

questions_db = load_questions()

# ---------- GOOGLE SHEETS ----------
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
        if sheet.row_values(1) != ['Name', 'Score', 'Date']:
            sheet.clear()
            sheet.append_row(['Name', 'Score', 'Date'])
        return sheet
    except:
        return None

def save_score_to_sheets(name, score):
    try:
        sheet = get_google_sheets_connection()
        if sheet:
            today = datetime.now().strftime("%Y-%m-%d %H:%M")
            sheet.append_row([name, score, today])
            return True
    except:
        pass
    return False

@st.cache_data(ttl=30)
def load_leaderboard_from_sheets():
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
    st.markdown(f"""
    <div class="sidebar-header">
        <h2>{LOGO_ICON} SainsQuiz</h2>
        <p>SPM Science Practice</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    subjects = ["All", "Physics", "Chemistry", "Biology"]
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
        st.session_state.feedback = None
        if st.session_state.subject == "All":
            st.session_state.questions = random.sample(questions_db, min(10, len(questions_db)))
        else:
            filtered = [q for q in questions_db if q['subject'] == st.session_state.subject]
            st.session_state.questions = random.sample(filtered, min(10, len(filtered)))
        st.session_state.total_questions = len(st.session_state.questions)
        st.rerun()

    st.markdown("---")
    if st.session_state.quiz_started and st.session_state.total_questions > 0:
        st.metric("Current Score", f"{st.session_state.score}/{st.session_state.total_questions}")
        progress = st.session_state.q_index / st.session_state.total_questions
        st.progress(progress)

    st.markdown("### Top Players")
    leaderboard = load_leaderboard_from_sheets()
    if leaderboard:
        for i, (name, score) in enumerate(leaderboard, 1):
            if i == 1:
                rank = "🥇"
            elif i == 2:
                rank = "🥈"
            elif i == 3:
                rank = "🥉"
            else:
                rank = f"{i}."
            st.markdown(f"""
            <div class="leaderboard-item">
                <span class="leaderboard-rank">{rank}</span>
                <span class="leaderboard-name">{name}</span>
                <span class="leaderboard-score">{score}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No scores yet. Be the first!")

# ---------- MAIN CONTENT ----------
st.markdown("""
<div class="header">
    <h1>🧪 SainsQuiz</h1>
    <p>Master SPM Science • Compete with Friends</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.quiz_started:
    # Subject cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="subject-card">
            <div class="subject-icon">{PHYSICS_ICON}</div>
            <h3>Physics</h3>
            <p>Forces, Motion, Heat, Light</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="subject-card">
            <div class="subject-icon">{CHEMISTRY_ICON}</div>
            <h3>Chemistry</h3>
            <p>Periodic Table, Bonds, Acids</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="subject-card">
            <div class="subject-icon">{BIOLOGY_ICON}</div>
            <h3>Biology</h3>
            <p>Cells, Human Body, Plants</p>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("How to Play"):
        st.markdown("""
        <div class="info-box">
            • Choose your subject from the sidebar<br>
            • Click "New Quiz" to start<br>
            • Answer 10 random questions<br>
            • Get instant feedback with explanations<br>
            • Save your score to the global leaderboard
        </div>
        """, unsafe_allow_html=True)

else:
    if st.session_state.q_index < st.session_state.total_questions:
        q = st.session_state.questions[st.session_state.q_index]

        st.markdown(f"""
        <div class="question-box">
            <h3>Question {st.session_state.q_index + 1} of {st.session_state.total_questions}</h3>
            <p>{q['question']}</p>
            <span class="subject-tag">{q['subject']}</span>
        </div>
        """, unsafe_allow_html=True)

        # RADIO BUTTONS – NOW VISIBLE (light background, dark text)
        answer = st.radio("", q['options'], key=f"q_{st.session_state.q_index}",
                          index=None, label_visibility="collapsed")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Submit Answer", use_container_width=True):
                if answer is None:
                    st.warning("Please select an answer!")
                else:
                    correct = q['options'][q['correct_option']]
                    is_correct = (answer == correct)
                    st.session_state.answers.append({
                        'question': q['question'],
                        'user_answer': answer,
                        'correct': is_correct,
                        'correct_answer': correct,
                        'explanation': q['explanation']
                    })
                    if is_correct:
                        st.session_state.score += 1
                        st.session_state.feedback = "correct"
                    else:
                        st.session_state.feedback = "wrong"
                    st.session_state.show_feedback = True
                    st.rerun()

        with col2:
            if st.session_state.show_feedback:
                st.markdown('<div class="secondary-button">', unsafe_allow_html=True)
                if st.button("Next Question", use_container_width=True):
                    st.session_state.q_index += 1
                    st.session_state.show_feedback = False
                    st.session_state.feedback = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.show_feedback and st.session_state.answers:
            last = st.session_state.answers[-1]
            if last['correct']:
                st.markdown(f"""
                <div class="success-message">
                    ✅ <strong>Correct!</strong><br>
                    {last['explanation']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#fee2e2; border:1px solid #fecaca; color:#991b1b; padding:1rem; border-radius:8px; margin:1rem 0;">
                    ❌ <strong>Incorrect</strong><br>
                    Correct answer: <strong>{last['correct_answer']}</strong><br>
                    {last['explanation']}
                </div>
                """, unsafe_allow_html=True)

    else:
        # Quiz completed
        st.balloons()
        percentage = (st.session_state.score / st.session_state.total_questions) * 100
        st.markdown(f"""
        <div class="question-box" style="background:#d1fae5;">
            <h3 style="color:#065f46;">🎉 Quiz Complete!</h3>
            <p style="font-size: 3rem; color:#065f46;">{st.session_state.score}/{st.session_state.total_questions}</p>
            <p style="font-size: 1.2rem; color:#065f46;">{percentage:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Review Your Answers"):
            for i, ans in enumerate(st.session_state.answers):
                if ans['correct']:
                    st.markdown(f"✅ **Q{i+1}:** {ans['question']}")
                else:
                    st.markdown(f"❌ **Q{i+1}:** {ans['question']}")
                    st.markdown(f"*Correct: {ans['correct_answer']}*")
                    st.markdown(f"*{ans['explanation']}*")
                st.markdown("---")

        st.markdown("### Save Your Score")
        col1, col2 = st.columns([3, 1])
        with col1:
            name = st.text_input("", placeholder="Enter your name", label_visibility="collapsed")
        with col2:
            if st.button("Save", use_container_width=True):
                if name:
                    if save_score_to_sheets(name, st.session_state.score):
                        st.markdown('<div class="success-message">✅ Saved to global leaderboard!</div>',
                                    unsafe_allow_html=True)
                        st.cache_data.clear()
                    else:
                        st.session_state.leaderboard.append((name, st.session_state.score))
                        st.session_state.leaderboard.sort(key=lambda x: x[1], reverse=True)
                        st.session_state.leaderboard = st.session_state.leaderboard[:10]
                        st.markdown('<div class="success-message">✅ Saved locally!</div>',
                                    unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.warning("Please enter your name!")

        if st.button("Take Another Quiz", use_container_width=True):
            st.session_state.quiz_started = False
            st.rerun()

# ---------- FOOTER ----------
st.markdown("""
<div class="footer">
    <p>🇲🇾 SainsQuiz – Helping Malaysian students master SPM Science</p>
</div>
""", unsafe_allow_html=True)


