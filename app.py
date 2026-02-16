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

# ---------- CLEAN, PROFESSIONAL CSS ----------
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Reset */
    * {
        font-family: 'Inter', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Main app background */
    .stApp {
        background: #f0f2f6;
    }
    
    /* Main container */
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    /* Header with Malaysia flag */
    .header {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
        text-align: center;
        border-bottom: 4px solid #010066;
    }
    
    .header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #cc0000 0%, #010066 50%, #ffcc00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .header p {
        color: #4a5568;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    /* Subject Cards */
    .subject-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .subject-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        cursor: pointer;
        border: 1px solid #e2e8f0;
    }
    
    .subject-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px rgba(0, 0, 0, 0.1);
        border-color: #010066;
    }
    
    .subject-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .subject-card h3 {
        color: #1e293b;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    
    .subject-card p {
        color: #64748b;
        font-size: 0.85rem;
        line-height: 1.4;
    }
    
    /* Question Box */
    .question-box {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        border-left: 4px solid #010066;
    }
    
    .question-box h3 {
        color: #64748b;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 1rem;
    }
    
    .question-box p {
        color: #1e293b;
        font-size: 1.3rem;
        font-weight: 600;
        line-height: 1.5;
    }
    
    .subject-tag {
        display: inline-block;
        background: #f1f5f9;
        color: #475569;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 1rem;
    }
    
    /* Options styling */
    .stRadio > div {
        background: white;
        padding: 1rem;
        border-radius: 16px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
    }
    
    .stRadio label {
        color: #1e293b !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        padding: 0.75rem !important;
        background: #f8fafc;
        border-radius: 12px;
        margin: 0.25rem 0 !important;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
    }
    
    .stRadio label:hover {
        background: #e2e8f0;
        border-color: #010066;
    }
    
    .stRadio [data-testid="StyledFullScreenButton"] {
        display: none;
    }
    
    /* Feedback messages */
    .correct-feedback {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #166534;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(34, 197, 94, 0.1);
    }
    
    .wrong-feedback {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #991b1b;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.1);
    }
    
    /* Button styling */
    .stButton button {
        background: #010066 !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(1, 0, 102, 0.2) !important;
    }
    
    .stButton button:hover {
        background: #020180 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(1, 0, 102, 0.3) !important;
    }
    
    .stButton button:active {
        transform: translateY(0) !important;
    }
    
    /* Secondary button */
    .secondary-button button {
        background: white !important;
        color: #010066 !important;
        border: 2px solid #010066 !important;
        box-shadow: none !important;
    }
    
    .secondary-button button:hover {
        background: #f8fafc !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: white;
        padding: 2rem 1rem;
        box-shadow: -2px 0 10px rgba(0, 0, 0, 0.05);
    }
    
    .sidebar-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .sidebar-header h2 {
        color: #010066;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    
    .sidebar-header p {
        color: #64748b;
        font-size: 0.9rem;
    }
    
    /* Metric styling */
    [data-testid="stMetric"] {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
    }
    
    [data-testid="stMetric"] label {
        color: #64748b !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #010066 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #010066, #4f46e5);
        border-radius: 10px;
    }
    
    /* Leaderboard items */
    .leaderboard-item {
        background: #f8fafc;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
    }
    
    .leaderboard-item:hover {
        border-color: #010066;
        background: white;
    }
    
    .leaderboard-rank {
        font-weight: 700;
        color: #010066;
        min-width: 40px;
    }
    
    .leaderboard-name {
        color: #1e293b;
        font-weight: 600;
        flex: 1;
    }
    
    .leaderboard-score {
        background: #010066;
        color: white;
        padding: 0.2rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* Success message */
    .success-message {
        background: #f0fdf4;
        border: 1px solid #86efac;
        color: #166534;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    /* Info box */
    .info-box {
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        color: #0369a1;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    /* Select box */
    .stSelectbox label {
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    
    .stSelectbox > div > div {
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem;
        color: #64748b;
        font-size: 0.85rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 2rem;
    }
    
    .footer strong {
        color: #010066;
    }
</style>
""", unsafe_allow_html=True)

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
        'show_feedback': False,
        'selected_subject': None
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
            "subject": "Chemistry",
            "question": "What is the pH of a neutral solution?",
            "options": ["0", "7", "14", "1"],
            "correct_option": 1,
            "explanation": "pH 7 is neutral."
        },
        {
            "subject": "Biology",
            "question": "Which organelle is the 'powerhouse'?",
            "options": ["Nucleus", "Ribosome", "Mitochondria", "Golgi"],
            "correct_option": 2,
            "explanation": "Mitochondria produce ATP."
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
    st.markdown("""
    <div class="sidebar-header">
        <h2>🧪 SainsQuiz</h2>
        <p>SPM Science Practice</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Subject selection
    subjects = ["All", "Physics", "Chemistry", "Biology"]
    selected = st.selectbox("📚 Choose Subject", subjects, 
                          index=subjects.index(st.session_state.subject))
    
    if selected != st.session_state.subject:
        st.session_state.subject = selected
        st.session_state.quiz_started = False
        st.rerun()
    
    # New quiz button
    if st.button("🎯 New Quiz", use_container_width=True):
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
        st.metric("🎯 Current Score", 
                 f"{st.session_state.score}/{st.session_state.total_questions}")
        
        # Progress
        progress = st.session_state.q_index / st.session_state.total_questions
        st.progress(progress)
    
    # Leaderboard
    st.markdown("### 🏆 Top Players")
    
    leaderboard = load_leaderboard_from_sheets()
    
    if leaderboard:
        for i, (name, score) in enumerate(leaderboard, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            st.markdown(f"""
            <div class="leaderboard-item">
                <span class="leaderboard-rank">{medal}</span>
                <span class="leaderboard-name">{name}</span>
                <span class="leaderboard-score">{score}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">✨ No scores yet. Be the first!</div>', 
                   unsafe_allow_html=True)

# ---------- MAIN CONTENT ----------
st.markdown("""
<div class="header">
    <h1>🧪 SAINSQUIZ</h1>
    <p>Master SPM Science • Compete with Friends</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.quiz_started:
    # Subject cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="subject-card">
            <div class="subject-icon">📚</div>
            <h3>Physics</h3>
            <p>Forces, Motion, Heat, Light & Waves</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="subject-card">
            <div class="subject-icon">🧪</div>
            <h3>Chemistry</h3>
            <p>Periodic Table, Chemical Bonds, Acids & Bases</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="subject-card">
            <div class="subject-icon">🔬</div>
            <h3>Biology</h3>
            <p>Cells, Human Body, Plants, Ecosystems</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How to play
    with st.expander("ℹ️ How to Play"):
        st.markdown("""
        1. **Choose your subject** from the sidebar
        2. Click **New Quiz** to start
        3. Answer 10 randomly selected questions
        4. Get instant feedback with explanations
        5. Save your score to the global leaderboard
        """)

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
        
        # Options
        answer = st.radio("", q['options'], key=f"q_{st.session_state.q_index}", 
                         index=None, label_visibility="collapsed")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Submit Answer", use_container_width=True):
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
                if st.button("➡️ Next Question", use_container_width=True):
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
                <div class="correct-feedback">
                    ✅ <strong>Correct!</strong><br>
                    {last['explanation']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="wrong-feedback">
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
        <div class="question-box" style="background: #f0fdf4; border-left-color: #22c55e;">
            <h3>🎉 Quiz Complete!</h3>
            <p style="font-size: 2rem; margin: 1rem 0;">{st.session_state.score}/{st.session_state.total_questions}</p>
            <p style="font-size: 1.2rem;">{percentage:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Review
        with st.expander("📋 Review Answers"):
            for i, ans in enumerate(st.session_state.answers):
                if ans['correct']:
                    st.markdown(f"✅ **Q{i+1}:** {ans['question']}")
                else:
                    st.markdown(f"❌ **Q{i+1}:** {ans['question']}")
                    st.markdown(f"*Correct: {ans['correct_answer']}*")
                    st.markdown(f"*{ans['explanation']}*")
                st.markdown("---")
        
        # Save score
        st.markdown("### 🏆 Save Your Score")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            name = st.text_input("", placeholder="Enter your name", 
                                label_visibility="collapsed", key="save_name")
        
        with col2:
            if st.button("💾 Save", use_container_width=True):
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
        
        # New quiz
        if st.button("🔄 Take Another Quiz", use_container_width=True):
            st.session_state.quiz_started = False
            st.rerun()

# ---------- FOOTER ----------
st.markdown("""
<div class="footer">
    <p>🇲🇾 <strong>SainsQuiz</strong> – Helping Malaysian students master SPM Science</p>
    <p>Questions based on SPM syllabus</p>
</div>
""", unsafe_allow_html=True)
