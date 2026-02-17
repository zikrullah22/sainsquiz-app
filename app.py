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
        background-color: #f8fafc;
    }
    
    /* Header */
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .header p {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
    }
    
    /* Subject cards */
    .subject-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
    }
    
    .subject-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    .subject-card h3 {
        color: #1f2937;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 0.75rem 0 0.25rem;
    }
    
    .subject-card p {
        color: #6b7280;
        font-size: 0.85rem;
    }
    
    .subject-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Question box */
    .question-box {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }
    
    .question-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .question-number {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 30px;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 2px 5px rgba(102, 126, 234, 0.3);
    }
    
    .question-progress {
        background: #f1f5f9;
        color: #475569;
        padding: 0.5rem 1rem;
        border-radius: 30px;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    .question-box h3 {
        color: #667eea;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.75rem;
    }
    
    .question-text {
        color: #1e293b;
        font-size: 1.3rem;
        font-weight: 600;
        line-height: 1.6;
        margin: 1rem 0;
    }
    
    .subject-tag {
        display: inline-block;
        background: #f1f5f9;
        color: #475569;
        padding: 0.3rem 1.2rem;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    /* Options styling */
    div.row-widget.stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
        padding: 0.5rem 0;
    }
    
    div.row-widget.stRadio label {
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 1rem 1.5rem !important;
        color: #1e293b !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }
    
    div.row-widget.stRadio label:hover {
        border-color: #667eea !important;
        background: #f8fafc !important;
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1) !important;
    }
    
    div.row-widget.stRadio label[data-baseweb="radio"] input:checked + div {
        background-color: #667eea !important;
        border-color: #667eea !important;
    }
    
    /* Button container */
    .button-container {
        display: flex;
        gap: 1rem;
        margin-top: 1.5rem;
    }
    
    /* Primary button */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.5rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    
    /* Secondary button */
    .secondary-button button {
        background: white !important;
        color: #667eea !important;
        border: 2px solid #667eea !important;
        box-shadow: none !important;
    }
    
    .secondary-button button:hover {
        background: #f8fafc !important;
        transform: translateY(-2px) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 1px solid #e2e8f0;
        padding: 2rem 1rem;
    }
    
    .sidebar-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .sidebar-header h2 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: white;
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    [data-testid="stMetric"] label {
        color: #64748b !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Leaderboard */
    .leaderboard-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    
    .leaderboard-item {
        background: white;
        padding: 0.8rem 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease;
    }
    
    .leaderboard-item:hover {
        transform: translateX(5px);
        border-color: #667eea;
    }
    
    .leaderboard-rank {
        font-weight: 700;
        min-width: 40px;
        text-align: center;
    }
    
    .rank-1 { color: #FFD700; font-size: 1.2rem; }
    .rank-2 { color: #C0C0C0; font-size: 1.1rem; }
    .rank-3 { color: #CD7F32; font-size: 1.1rem; }
    
    .leaderboard-name {
        color: #1e293b;
        font-weight: 500;
        flex: 1;
        margin: 0 0.5rem;
    }
    
    .leaderboard-score {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 0.3rem 0.8rem;
        border-radius: 30px;
        font-size: 0.85rem;
        min-width: 45px;
        text-align: center;
    }
    
    .leaderboard-empty {
        background: #f8fafc;
        border: 2px dashed #cbd5e1;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        color: #64748b;
    }
    
    /* Feedback messages */
    .feedback-correct {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
    }
    
    .feedback-wrong {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2);
    }
    
    /* Score card */
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .score-number {
        font-size: 4rem;
        font-weight: 700;
        line-height: 1;
        margin: 1rem 0;
    }
    
    .score-percentage {
        font-size: 1.5rem;
        opacity: 0.9;
    }
    
    /* Review section */
    .review-item {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    
    .review-correct { border-left-color: #10b981; }
    .review-wrong { border-left-color: #ef4444; }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem;
        color: #94a3b8;
        font-size: 0.85rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------- SIMPLE ICONS ----------
PHYSICS_ICON = "⚡"
CHEMISTRY_ICON = "🧪"
BIOLOGY_ICON = "🧬"
LOGO_ICON = "🎓"

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
        'current_answer': None,
        'answer_submitted': False
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
            "explanation": "Newton (N) is the SI unit of force. It's named after Sir Isaac Newton for his work in classical mechanics."
        },
        {
            "subject": "Physics",
            "question": "Which of the following is a scalar quantity?",
            "options": ["Velocity", "Acceleration", "Mass", "Force"],
            "correct_option": 2,
            "explanation": "Mass is scalar (only magnitude). Velocity, acceleration, and force are vectors (have both magnitude and direction)."
        },
        {
            "subject": "Chemistry",
            "question": "What is the pH of a neutral solution?",
            "options": ["0", "7", "14", "1"],
            "correct_option": 1,
            "explanation": "pH 7 is neutral. Values below 7 are acidic, above 7 are alkaline/basic."
        },
        {
            "subject": "Biology",
            "question": "Which organelle is the 'powerhouse' of the cell?",
            "options": ["Nucleus", "Ribosome", "Mitochondria", "Golgi apparatus"],
            "correct_option": 2,
            "explanation": "Mitochondria produce ATP (energy) through cellular respiration, making them the cell's powerhouse."
        },
        {
            "subject": "Chemistry",
            "question": "What is the most abundant element in the universe?",
            "options": ["Oxygen", "Carbon", "Helium", "Hydrogen"],
            "correct_option": 3,
            "explanation": "Hydrogen makes up about 75% of the universe's elemental mass. Helium is second at about 23%."
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
    </div>
    """, unsafe_allow_html=True)
    
    # Subject selection with icons
  # Subject selection with icons
subjects = ["All", "Physics ⚡", "Chemistry 🧪", "Biology 🧬"]
subject_map = {"All": "All", "Physics ⚡": "Physics", 
               "Chemistry 🧪": "Chemistry", "Biology 🧬": "Biology"}

# Fix: Map current subject to display version
if st.session_state.subject == "All":
    default_display = "All"
elif st.session_state.subject == "Physics":
    default_display = "Physics ⚡"
elif st.session_state.subject == "Chemistry":
    default_display = "Chemistry 🧪"
elif st.session_state.subject == "Biology":
    default_display = "Biology 🧬"

selected_display = st.selectbox("📚 Choose Subject", subjects, 
                              index=subjects.index(default_display))

selected = subject_map[selected_display]
    
    if selected != st.session_state.subject:
        st.session_state.subject = selected
        st.session_state.quiz_started = False
        st.rerun()
    
    st.markdown("---")
    
    # New quiz button with icon
    if st.button("🎯 New Quiz", use_container_width=True):
        st.session_state.quiz_started = True
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.answers = []
        st.session_state.feedback = None
        st.session_state.answer_submitted = False
        st.session_state.current_answer = None
        
        if st.session_state.subject == "All":
            st.session_state.questions = random.sample(questions_db, min(10, len(questions_db)))
        else:
            filtered = [q for q in questions_db if q['subject'] == st.session_state.subject]
            st.session_state.questions = random.sample(filtered, min(10, len(filtered)))
        
        st.session_state.total_questions = len(st.session_state.questions)
        st.rerun()
    
    # Current progress in sidebar (if quiz started)
    if st.session_state.quiz_started and st.session_state.total_questions > 0:
        st.markdown("---")
        st.markdown("### 📊 Your Progress")
        
        # Metric
        st.metric("Current Score", 
                 f"{st.session_state.score}/{st.session_state.total_questions}")
        
        # Progress with emoji
        progress = st.session_state.q_index / st.session_state.total_questions
        st.progress(progress)
        
        questions_left = st.session_state.total_questions - st.session_state.q_index
        st.caption(f"🎯 {questions_left} questions remaining")
    
    # Leaderboard with motivational design
    st.markdown("---")
    st.markdown("""
    <div class="leaderboard-title">
        🏆 TOP PLAYERS 🏆
    </div>
    """, unsafe_allow_html=True)
    
    leaderboard = load_leaderboard_from_sheets()
    
    if leaderboard:
        for i, (name, score) in enumerate(leaderboard, 1):
            if i == 1:
                rank_emoji = "👑"
                rank_class = "rank-1"
            elif i == 2:
                rank_emoji = "⭐"
                rank_class = "rank-2"
            elif i == 3:
                rank_emoji = "🌟"
                rank_class = "rank-3"
            else:
                rank_emoji = f"{i}"
                rank_class = ""
            
            st.markdown(f"""
            <div class="leaderboard-item">
                <span class="leaderboard-rank {rank_class}">{rank_emoji}</span>
                <span class="leaderboard-name">{name}</span>
                <span class="leaderboard-score">{score}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="leaderboard-empty">
            🎯 Be the first champion!<br>
            <small>Complete a quiz to claim your spot</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Motivational quote
    st.markdown("---")
    quotes = [
        "✨ Science is magic that works!",
        "🚀 Dream it. Science it. Do it.",
        "💡 Stay curious, keep learning!",
        "🎓 Your future is bright!",
        "⭐ Every expert was once a beginner."
    ]
    st.caption(random.choice(quotes))

# ---------- MAIN CONTENT ----------
st.markdown("""
<div class="header">
    <h1>🎓 SainsQuiz</h1>
    <p>Master SPM Science • Challenge Friends • Be a Champion</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.quiz_started:
    # Welcome message
    st.markdown("### 🌟 Ready to test your knowledge?")
    
    # Subject cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="subject-card">
            <div class="subject-icon">{PHYSICS_ICON}</div>
            <h3>Physics</h3>
            <p>Forces, Motion, Energy, Waves</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="subject-card">
            <div class="subject-icon">{CHEMISTRY_ICON}</div>
            <h3>Chemistry</h3>
            <p>Periodic Table, Reactions, Acids</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="subject-card">
            <div class="subject-icon">{BIOLOGY_ICON}</div>
            <h3>Biology</h3>
            <p>Cells, Systems, Genetics, Ecology</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How to play
    with st.expander("📖 How to Play"):
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 12px;">
            <p style="margin: 0.5rem 0;">✨ <strong>Step 1:</strong> Choose your favorite subject from the sidebar</p>
            <p style="margin: 0.5rem 0;">✨ <strong>Step 2:</strong> Click "New Quiz" to start your journey</p>
            <p style="margin: 0.5rem 0;">✨ <strong>Step 3:</strong> Answer 10 exciting questions</p>
            <p style="margin: 0.5rem 0;">✨ <strong>Step 4:</strong> Learn from instant explanations</p>
            <p style="margin: 0.5rem 0;">✨ <strong>Step 5:</strong> Save your score and climb the leaderboard</p>
        </div>
        """, unsafe_allow_html=True)

else:
    if st.session_state.q_index < st.session_state.total_questions:
        q = st.session_state.questions[st.session_state.q_index]
        
        # Question header with clear progress
        st.markdown(f"""
        <div class="question-box">
            <div class="question-header">
                <span class="question-number">📝 Question {st.session_state.q_index + 1}</span>
                <span class="question-progress">{st.session_state.q_index + 1}/{st.session_state.total_questions}</span>
            </div>
            <div class="question-text">
                {q['question']}
            </div>
            <span class="subject-tag">{q['subject']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Options
        answer = st.radio("", q['options'], key=f"q_{st.session_state.q_index}", 
                         index=None, label_visibility="collapsed",
                         disabled=st.session_state.answer_submitted)
        
        # Button container
        col1, col2 = st.columns(2)
        
        with col1:
            button_label = "✅ Check Answer" if not st.session_state.answer_submitted else "✅ Answer Submitted"
            if st.button(button_label, use_container_width=True, disabled=st.session_state.answer_submitted):
                if answer is None:
                    st.warning("🎯 Please select an answer first!")
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
                    
                    st.session_state.answer_submitted = True
                    st.session_state.current_answer = answer
                    st.rerun()
        
        with col2:
            if st.session_state.answer_submitted:
                if st.button("➡️ Next Question", use_container_width=True, type="primary"):
                    st.session_state.q_index += 1
                    st.session_state.answer_submitted = False
                    st.session_state.current_answer = None
                    st.rerun()
        
        # Feedback
        if st.session_state.answer_submitted and st.session_state.answers:
            last = st.session_state.answers[-1]
            if last['correct']:
                st.markdown(f"""
                <div class="feedback-correct">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🎉 Correct!</div>
                    <div>{last['explanation']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="feedback-wrong">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📚 Keep Learning!</div>
                    <div><strong>Correct answer:</strong> {last['correct_answer']}</div>
                    <div style="margin-top: 0.5rem;">{last['explanation']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        # Quiz complete - Celebratory screen
        st.balloons()
        
        percentage = (st.session_state.score / st.session_state.total_questions) * 100
        
        # Motivational message based on score
        if percentage >= 80:
            msg = "🏆 Excellent! You're a Science Champion!"
            emoji = "🌟"
        elif percentage >= 60:
            msg = "🎯 Good job! You're on the right track!"
            emoji = "📚"
        else:
            msg = "💪 Keep practicing! Every attempt makes you stronger!"
            emoji = "🌱"
        
        st.markdown(f"""
        <div class="score-card">
            <div style="font-size: 1.5rem;">{emoji} {msg}</div>
            <div class="score-number">{st.session_state.score}/{st.session_state.total_questions}</div>
            <div class="score-percentage">{percentage:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Review answers
        with st.expander("📋 Review Your Answers"):
            for i, ans in enumerate(st.session_state.answers):
                if ans['correct']:
                    st.markdown(f"""
                    <div class="review-item review-correct">
                        <strong>✅ Question {i+1}:</strong> {ans['question']}<br>
                        <small>✨ {ans['explanation']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="review-item review-wrong">
                        <strong>📚 Question {i+1}:</strong> {ans['question']}<br>
                        <strong>Correct answer:</strong> {ans['correct_answer']}<br>
                        <small>💡 {ans['explanation']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Save score with motivation
        st.markdown("### 🏆 Save Your Achievement")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            name = st.text_input("", placeholder="Enter your name to join the leaderboard", 
                                label_visibility="collapsed")
        
        with col2:
            if st.button("💾 Save Score", use_container_width=True):
                if name:
                    if save_score_to_sheets(name, st.session_state.score):
                        st.success("✨ Congratulations! You're on the leaderboard!")
                        st.balloons()
                        st.cache_data.clear()
                    else:
                        st.session_state.leaderboard.append((name, st.session_state.score))
                        st.session_state.leaderboard.sort(key=lambda x: x[1], reverse=True)
                        st.session_state.leaderboard = st.session_state.leaderboard[:10]
                        st.success("✨ Saved successfully!")
                    st.rerun()
                else:
                    st.warning("Please enter your name to save your score!")
        
        # Play again
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Take Another Quiz", use_container_width=True):
                st.session_state.quiz_started = False
                st.session_state.answer_submitted = False
                st.rerun()

# ---------- FOOTER ----------
st.markdown("""
<div class="footer">
    <p>🇲🇾 SainsQuiz – Empowering Malaysian students to excel in SPM Science</p>
    <p style="margin-top: 0.5rem;">✨ Keep learning, keep growing! ✨</p>
</div>
""", unsafe_allow_html=True)

