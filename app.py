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

# ---------- CLEAN PROFESSIONAL CSS ----------
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Clean background */
    .stApp {
        background-color: #f3f4f6;
    }
    
    /* Header */
    .header {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        text-align: center;
        border: 1px solid #e5e7eb;
    }
    
    .header h1 {
        color: #111827;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    
    .header p {
        color: #6b7280;
        font-size: 0.9rem;
    }
    
    /* Subject cards */
    .subject-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .subject-card h3 {
        color: #111827;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0.5rem 0 0.25rem;
    }
    
    .subject-card p {
        color: #6b7280;
        font-size: 0.8rem;
    }
    
    .subject-icon {
        font-size: 2rem;
    }
    
    /* Question box */
    .question-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }
    
    .question-box h3 {
        color: #3b82f6;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.75rem;
    }
    
    .question-box p {
        color: #111827;
        font-size: 1.2rem;
        font-weight: 600;
        line-height: 1.5;
        margin-bottom: 0.75rem;
    }
    
    .subject-tag {
        display: inline-block;
        background: #e5e7eb;
        color: #4b5563;
        padding: 0.2rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* ===== RADIO BUTTONS - LIGHT BACKGROUND, DARK TEXT ===== */
    div.row-widget.stRadio > div {
        background-color: transparent !important;
        padding: 0 !important;
        border: none !important;
    }
    
    /* Style each option as a light card */
    div.row-widget.stRadio label {
        background-color: white !important;      /* Light background */
        border: 1px solid #d1d5db !important;    /* Light gray border */
        border-radius: 10px !important;
        padding: 1rem 1.2rem !important;
        margin: 0.6rem 0 !important;
        color: #111827 !important;                /* Dark text */
        font-weight: 500 !important;
        font-size: 1.1rem !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        cursor: pointer !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    
    div.row-widget.stRadio label:hover {
        background-color: #f9fafb !important;    /* Slightly darker on hover */
        border-color: #3b82f6 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }
    
    /* Selected option highlight */
    div.row-widget.stRadio label[data-baseweb="radio"] input:checked + div {
        background-color: #3b82f6 !important;
        border-color: #3b82f6 !important;
    }
    
    /* Radio circle */
    div.row-widget.stRadio label div:first-child {
        background-color: white !important;
        border-color: #9ca3af !important;
        margin-right: 12px !important;
    }
    
    /* Selected radio circle */
    div.row-widget.stRadio label input:checked + div div {
        background-color: #3b82f6 !important;
    }
    
    /* ===== BUTTONS ===== */
    .stButton button {
        background-color: #3b82f6 !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        border: 1px solid #2563eb !important;
    }
    
    .stButton button:hover {
        background-color: #2563eb !important;
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3) !important;
    }
    
    .secondary-button button {
        background-color: white !important;
        color: #3b82f6 !important;
        border: 1px solid #3b82f6 !important;
    }
    
    .secondary-button button:hover {
        background-color: #f9fafb !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #e5e7eb;
        padding: 1.5rem 1rem;
    }
    
    .sidebar-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .sidebar-header h2 {
        color: #111827;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .sidebar-header p {
        color: #6b7280;
        font-size: 0.85rem;
    }
    
    /* Metric */
    [data-testid="stMetric"] {
        background-color: #f9fafb;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    
    [data-testid="stMetric"] label {
        color: #6b7280 !important;
        font-size: 0.85rem !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #111827 !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #3b82f6;
    }
    
    /* Leaderboard */
    .leaderboard-item {
        background-color: #f9fafb;
        padding: 0.6rem 1rem;
        border-radius: 8px;
        margin: 0.4rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #e5e7eb;
    }
    
    .leaderboard-rank {
        font-weight: 700;
        color: #3b82f6;
        min-width: 35px;
    }
    
    .leaderboard-name {
        color: #111827;
        font-weight: 500;
        flex: 1;
    }
    
    .leaderboard-score {
        background-color: #e5e7eb;
        color: #111827;
        font-weight: 600;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    
    /* Success message */
    .success-message {
        background-color: #d1fae5;
        border: 1px solid #10b981;
        color: #065f46;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Info box */
    .info-box {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        padding: 1rem;
        border-radius: 8px;
        color: #111827;
        line-height: 1.6;
    }
    
    /* Select box */
    .stSelectbox label {
        color: #111827 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    .stSelectbox > div > div {
        background-color: white !important;
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        color: #111827 !important;
    }
    
    /* Warning message */
    .stAlert {
        background-color: #fee2e2 !important;
        color: #991b1b !important;
        border: 1px solid #fecaca !important;
        border-radius: 8px !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem;
        color: #6b7280;
        font-size: 0.8rem;
        border-top: 1px solid #e5e7eb;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------- SIMPLE ICONS ----------
PHYSICS_ICON = "📚"
CHEMISTRY_ICON = "🧪"
BIOLOGY_ICON = "🔬"
LOGO_ICON = "🧪"

# ---------- INITIALIZE SESSION STATE ----------
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
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

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
    
    # Default questions
    return [
        {
            "subject": "Physics",
            "question": "What is the SI unit of force?",
            "options": ["Joule", "Newton", "Watt", "Pascal"],
            "correct_option": 1,
            "explanation": "Newton (N) is the SI unit of force."
        },
        {
            "subject": "Physics",
            "question": "Which of the following is a scalar quantity?",
            "options": ["Velocity", "Acceleration", "Mass", "Force"],
            "correct_option": 2,
            "explanation": "Mass is scalar (only magnitude). The others are vectors."
        },
        {
            "subject": "Chemistry",
            "question": "What is the pH of a neutral solution?",
            "options": ["0", "7", "14", "1"],
            "correct_option": 1,
            "explanation": "pH 7 is neutral."
        },
        {
            "subject": "Biology",
            "question": "Which organelle is the 'powerhouse' of the cell?",
            "options": ["Nucleus", "Ribosome", "Mitochondria", "Golgi apparatus"],
            "correct_option": 2,
            "explanation": "Mitochondria produce ATP."
        },
        {
            "subject": "Chemistry",
            "question": "What is the most abundant element in the universe?",
            "options": ["Oxygen", "Carbon", "Helium", "Hydrogen"],
            "correct_option": 3,
            "explanation": "Hydrogen makes up about 75% of the universe's elemental mass."
        }
    ]

questions_db = load_questions()

# ---------- GOOGLE SHEETS ----------
@st.cache_resource
def get_google_sheets_connection():
    try:
        if "gcp_service_account" not in st.secrets:
            return None
            
        scope = ["https://spreadsheets.google.com/feeds", 
                 "https://www.googleapis.com/auth/drive"]
        
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        sheet = client.open("SainsQuiz Leaderboard").sheet1
        
        headers = sheet.row_values(1)
        if headers != ['Name', 'Score', 'Date']:
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
            leaderboard = []
            for r in records:
                if 'Name' in r and 'Score' in r:
                    try:
                        score = int(r['Score'])
                        name = str(r['Name']).strip()
                        if name and score > 0:
                            leaderboard.append((name, score))
                    except:
                        pass
            leaderboard.sort(key=lambda x: x[1], reverse=True)
            return leaderboard[:10]
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
    
    # Subject selection
    subjects = ["All", "Physics", "Chemistry", "Biology"]
    selected = st.selectbox("Choose Subject", subjects, 
                          index=subjects.index(st.session_state.subject))
    
    if selected != st.session_state.subject:
        st.session_state.subject = selected
        st.session_state.quiz_started = False
        st.rerun()
    
    # New quiz button
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
    
    # Current score
    if st.session_state.quiz_started and st.session_state.total_questions > 0:
        st.metric("Current Score", 
                 f"{st.session_state.score}/{st.session_state.total_questions}")
        
        # Progress
        progress = st.session_state.q_index / st.session_state.total_questions
        st.progress(progress)
    
    # Leaderboard
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
    <p>Practice SPM Science • Compete with Friends</p>
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
    
    # How to play
    with st.expander("How to Play"):
        st.markdown("""
        <div class="info-box">
            • Choose your subject from the sidebar<br>
            • Click "New Quiz" to start<br>
            • Answer 10 random questions<br>
            • Get instant feedback<br>
            • Save your score to leaderboard
        </div>
        """, unsafe_allow_html=True)

else:
    if st.session_state.q_index < st.session_state.total_questions:
        q = st.session_state.questions[st.session_state.q_index]
        
        # Question
        st.markdown(f"""
        <div class="question-box">
            <h3>Question {st.session_state.q_index + 1} of {st.session_state.total_questions}</h3>
            <p>{q['question']}</p>
            <span class="subject-tag">{q['subject']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Options - NOW LIGHT BACKGROUND, DARK TEXT
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
        
        # Feedback
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
                <div style="background-color:#fee2e2; border:1px solid #fecaca; color:#991b1b; padding:1rem; border-radius:8px; margin:1rem 0;">
                    ❌ <strong>Incorrect</strong><br>
                    Correct answer: <strong>{last['correct_answer']}</strong><br>
                    {last['explanation']}
                </div>
                """, unsafe_allow_html=True)
    
    else:
        # Quiz complete
        st.balloons()
        
        percentage = (st.session_state.score / st.session_state.total_questions) * 100
        
        st.markdown(f"""
        <div class="question-box" style="background-color:#d1fae5;">
            <h3 style="color:#065f46;">🎉 Quiz Complete!</h3>
            <p style="font-size: 3rem; color:#065f46;">{st.session_state.score}/{st.session_state.total_questions}</p>
            <p style="font-size: 1.2rem; color:#065f46;">{percentage:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Review
        with st.expander("Review Your Answers"):
            for i, ans in enumerate(st.session_state.answers):
                if ans['correct']:
                    st.markdown(f"✅ **Q{i+1}:** {ans['question']}")
                else:
                    st.markdown(f"❌ **Q{i+1}:** {ans['question']}")
                    st.markdown(f"*Correct: {ans['correct_answer']}*")
                    st.markdown(f"*{ans['explanation']}*")
                st.markdown("---")
        
        # Save score
        st.markdown("### Save Your Score")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            name = st.text_input("", placeholder="Enter your name", 
                                label_visibility="collapsed")
        
        with col2:
            if st.button("Save", use_container_width=True):
                if name:
                    if save_score_to_sheets(name, st.session_state.score):
                        st.markdown('<div class="success-message">✅ Saved to leaderboard!</div>', 
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
        
        # New quiz
        if st.button("Take Another Quiz", use_container_width=True):
            st.session_state.quiz_started = False
            st.rerun()

# ---------- FOOTER ----------
st.markdown("""
<div class="footer">
    <p>🇲🇾 SainsQuiz – Helping Malaysian students master SPM Science</p>
</div>
""", unsafe_allow_html=True)
