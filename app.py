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

# ---------- AMAZING CSS WITH ONLINE IMAGES ----------
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Poppins', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Animated Gradient Background */
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        min-height: 100vh;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Floating Animation for Cards */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    /* Pulse Animation */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* Glow Animation */
    @keyframes glow {
        0% { box-shadow: 0 0 5px rgba(255, 255, 255, 0.5); }
        50% { box-shadow: 0 0 20px rgba(255, 255, 255, 0.8); }
        100% { box-shadow: 0 0 5px rgba(255, 255, 255, 0.5); }
    }
    
    /* Main Header with Online Image */
    .main-header {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.2) 100%);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255,255,255,0.3);
        border-radius: 30px;
        padding: 2rem;
        margin: 1rem 0 2rem 0;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        animation: float 3s ease-in-out infinite;
    }
    
    .main-header h1 {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #fff 0%, #ffd700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: white;
        font-size: 1.2rem;
        font-weight: 500;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Cool Subject Cards with Images */
    .subject-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 30px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        border: 2px solid rgba(255,255,255,0.5);
        height: 100%;
        animation: float 4s ease-in-out infinite;
    }
    
    .subject-card:hover {
        transform: scale(1.05) translateY(-10px);
        box-shadow: 0 30px 60px rgba(0,0,0,0.3);
        border-color: #ffd700;
        animation: pulse 1s ease-in-out;
    }
    
    .subject-card img {
        width: 100px;
        height: 100px;
        margin-bottom: 1rem;
        border-radius: 50%;
        border: 4px solid #ffd700;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    
    .subject-card h3 {
        color: #333;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .subject-card p {
        color: #666;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Question Box with Glass Effect */
    .question-box {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 40px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        border: 2px solid rgba(255,255,255,0.5);
        animation: glow 2s ease-in-out infinite;
    }
    
    .question-box h3 {
        color: #e73c7e;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 1rem;
    }
    
    .question-box p {
        color: #333;
        font-size: 1.5rem;
        font-weight: 600;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    .subject-tag {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 2rem;
        border-radius: 50px;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 5px 10px rgba(0,0,0,0.1);
    }
    
    /* Cool Radio Buttons */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 30px;
        padding: 1.5rem;
        border: 2px solid rgba(255,255,255,0.5);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .stRadio label {
        background: white !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 20px !important;
        padding: 1rem 1.5rem !important;
        margin: 0.5rem 0 !important;
        color: #333 !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 5px 10px rgba(0,0,0,0.05) !important;
    }
    
    .stRadio label:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-color: transparent !important;
        transform: translateX(10px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stRadio [data-testid="StyledFullScreenButton"] {
        display: none;
    }
    
    /* Awesome Buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 1rem 2rem !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4) !important;
        border: 2px solid rgba(255,255,255,0.2) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 20px 30px rgba(102, 126, 234, 0.6) !important;
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    }
    
    .stButton button:active {
        transform: translateY(0);
    }
    
    /* Secondary Button */
    .secondary-button button {
        background: linear-gradient(135deg, #ffd700 0%, #ffa500 100%) !important;
        box-shadow: 0 10px 20px rgba(255, 215, 0, 0.4) !important;
    }
    
    /* Sidebar with Glass Effect */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-right: 2px solid rgba(255,255,255,0.2);
        padding: 2rem;
    }
    
    .sidebar-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .sidebar-header h2 {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .sidebar-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
    }
    
    /* Score Card */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(5px);
        border: 2px solid rgba(255,255,255,0.3);
        border-radius: 30px;
        padding: 1.5rem;
        text-align: center;
    }
    
    [data-testid="stMetric"] label {
        color: white !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffd700 !important;
        font-size: 3rem !important;
        font-weight: 800 !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #ffd700, #ffa500);
        border-radius: 20px;
        height: 15px !important;
    }
    
    .stProgress > div {
        background: rgba(255,255,255,0.2);
        border-radius: 20px;
    }
    
    /* Leaderboard Items */
    .leaderboard-item {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(5px);
        border: 2px solid rgba(255,255,255,0.3);
        border-radius: 50px;
        padding: 0.8rem 1.2rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.3s ease;
    }
    
    .leaderboard-item:hover {
        transform: translateX(10px);
        background: rgba(255, 255, 255, 0.3);
        border-color: #ffd700;
    }
    
    .leaderboard-rank {
        font-size: 1.5rem;
        font-weight: 800;
        color: #ffd700;
        min-width: 50px;
    }
    
    .leaderboard-name {
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        flex: 1;
    }
    
    .leaderboard-score {
        background: linear-gradient(135deg, #ffd700 0%, #ffa500 100%);
        color: #333;
        font-weight: 800;
        padding: 0.3rem 1.2rem;
        border-radius: 50px;
        font-size: 1rem;
    }
    
    /* Success Message */
    .success-message {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #1a4731;
        padding: 1.5rem;
        border-radius: 30px;
        text-align: center;
        font-weight: 700;
        margin: 1rem 0;
        animation: pulse 2s infinite;
        border: 2px solid white;
    }
    
    /* Info Box */
    .info-box {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(5px);
        border: 2px solid rgba(255,255,255,0.3);
        color: white;
        padding: 1.5rem;
        border-radius: 30px;
        text-align: center;
        font-weight: 500;
    }
    
    /* Select Box */
    .stSelectbox label {
        color: white !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(5px) !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        border-radius: 30px !important;
        color: white !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        color: white;
        font-size: 0.9rem;
        border-top: 2px solid rgba(255,255,255,0.2);
    }
    
    .footer strong {
        color: #ffd700;
    }
</style>
""", unsafe_allow_html=True)

# ---------- ONLINE IMAGES FOR SUBJECTS ----------
PHYSICS_IMG = "https://cdn-icons-png.flaticon.com/512/2917/2917996.png"
CHEMISTRY_IMG = "https://cdn-icons-png.flaticon.com/512/2917/2917995.png"
BIOLOGY_IMG = "https://cdn-icons-png.flaticon.com/512/2917/2917990.png"
LOGO_IMG = "https://cdn-icons-png.flaticon.com/512/2810/2810051.png"

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
    st.markdown(f"""
    <div class="sidebar-header">
        <img src="{LOGO_IMG}" style="width: 80px; height: 80px; margin-bottom: 1rem;">
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
            if i == 1:
                rank = "🥇"
            elif i == 2:
                rank = "🥈"
            elif i == 3:
                rank = "🥉"
            else:
                rank = f"#{i}"
                
            st.markdown(f"""
            <div class="leaderboard-item">
                <span class="leaderboard-rank">{rank}</span>
                <span class="leaderboard-name">{name}</span>
                <span class="leaderboard-score">{score}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">✨ No scores yet. Be the first!</div>', 
                   unsafe_allow_html=True)

# ---------- MAIN CONTENT ----------
st.markdown("""
<div class="main-header">
    <h1>🧪 SAINSQUIZ</h1>
    <p>Master SPM Science • Compete with Friends • Win the Leaderboard</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.quiz_started:
    # Subject cards with online images
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="subject-card">
            <img src="{PHYSICS_IMG}" alt="Physics">
            <h3>Physics</h3>
            <p>Forces, Motion, Heat, Light & Waves</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="subject-card">
            <img src="{CHEMISTRY_IMG}" alt="Chemistry">
            <h3>Chemistry</h3>
            <p>Periodic Table, Chemical Bonds, Acids & Bases</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="subject-card">
            <img src="{BIOLOGY_IMG}" alt="Biology">
            <h3>Biology</h3>
            <p>Cells, Human Body, Plants, Ecosystems</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How to play
    with st.expander("ℹ️ How to Play", expanded=True):
        st.markdown("""
        <div class="info-box">
            ✨ Choose your subject from the sidebar<br>
            🎯 Click New Quiz to start<br>
            📝 Answer 10 randomly selected questions<br>
            💡 Get instant feedback with explanations<br>
            🏆 Save your score to the global leaderboard<br>
            👥 Challenge friends to beat your score!
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
                <div class="success-message">
                    ✅ <strong>Correct!</strong><br>
                    {last['explanation']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="info-box" style="background: rgba(239, 68, 68, 0.2);">
                    ❌ <strong>Not quite!</strong><br>
                    Correct answer: <strong>{last['correct_answer']}</strong><br>
                    {last['explanation']}
                </div>
                """, unsafe_allow_html=True)
    
    else:
        # Quiz complete
        st.balloons()
        st.snow()
        
        percentage = (st.session_state.score / st.session_state.total_questions) * 100
        
        st.markdown(f"""
        <div class="question-box" style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);">
            <h3 style="color: #1a4731;">🎉 QUIZ COMPLETE! 🎉</h3>
            <p style="font-size: 4rem; color: #1a4731;">{st.session_state.score}/{st.session_state.total_questions}</p>
            <p style="font-size: 2rem; color: #1a4731;">{percentage:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Review
        with st.expander("📋 Review Your Answers"):
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
    <p>Made with ❤️ for SPM students • Questions based on SPM syllabus</p>
</div>
""", unsafe_allow_html=True)
