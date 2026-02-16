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

# ---------- CUSTOM CSS FOR MODERN MALAYSIA THEME ----------
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Main container styling */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 30px;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        margin: 1rem 0;
    }
    
    /* Header with Malaysia flag colors */
    .main-header {
        background: linear-gradient(135deg, #cc0000 0%, #010066 50%, #ffcc00 100%);
        padding: 2rem;
        border-radius: 25px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        animation: slideIn 0.5s ease-out;
    }
    
    .main-header h1 {
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        letter-spacing: 2px;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.95;
        margin: 0.5rem 0 0;
        font-weight: 300;
    }
    
    /* Subject cards */
    .subject-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        cursor: pointer;
        height: 100%;
        border: 2px solid transparent;
    }
    
    .subject-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        border-color: #667eea;
    }
    
    .subject-card h3 {
        color: #333;
        font-size: 1.8rem;
        margin: 1rem 0 0.5rem;
        font-weight: 600;
    }
    
    .subject-card p {
        color: #666;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .subject-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    /* Question box */
    .question-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 25px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        animation: fadeIn 0.5s ease-out;
    }
    
    .question-box h3 {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .question-box p {
        font-size: 1.5rem;
        font-weight: 600;
        line-height: 1.6;
        margin: 1rem 0;
    }
    
    /* Answer feedback */
    .correct-answer {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 1.5rem;
        border-radius: 20px;
        color: #1a4731;
        font-weight: 500;
        margin: 1.5rem 0;
        animation: slideUp 0.4s ease-out;
        box-shadow: 0 10px 30px rgba(132, 250, 176, 0.3);
    }
    
    .wrong-answer {
        background: linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%);
        padding: 1.5rem;
        border-radius: 20px;
        color: #721c24;
        font-weight: 500;
        margin: 1.5rem 0;
        animation: slideUp 0.4s ease-out;
        box-shadow: 0 10px 30px rgba(250, 208, 196, 0.3);
    }
    
    /* Leaderboard styling */
    .leaderboard-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .leaderboard-item {
        background: #f8f9fa;
        padding: 0.8rem 1.2rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .leaderboard-item:hover {
        transform: translateX(5px);
        border-color: #667eea;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
    
    .leaderboard-rank {
        font-size: 1.2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .leaderboard-name {
        font-weight: 600;
        color: #333;
    }
    
    .leaderboard-score {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 0.3rem 1rem;
        border-radius: 20px;
        color: #1a4731;
        font-weight: 700;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 15px;
        padding: 0.8rem 2rem;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5);
    }
    
    /* Sidebar styling */
    div[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2rem 1.5rem;
        box-shadow: -5px 0 20px rgba(0,0,0,0.1);
    }
    
    .sidebar-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .sidebar-header h2 {
        color: #333;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .sidebar-header p {
        color: #667eea;
        font-weight: 500;
    }
    
    /* Success message */
    .success-message {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 1rem;
        border-radius: 15px;
        color: #1a4731;
        text-align: center;
        font-weight: 600;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }
    
    /* Animations */
    @keyframes slideIn {
        from {
            transform: translateY(-30px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    @keyframes slideUp {
        from {
            transform: translateY(20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes pulse {
        0% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.02);
        }
        100% {
            transform: scale(1);
        }
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    
    .stRadio label {
        font-size: 1.1rem;
        padding: 0.8rem;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .stRadio label:hover {
        background: #f0f2f6;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        border-radius: 10px;
    }
    
    /* Metric styling */
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    
    .stMetric label {
        color: #667eea;
        font-weight: 600;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 15px;
        font-weight: 600;
        color: #667eea;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: rgba(255,255,255,0.9);
        font-size: 0.9rem;
    }
    
    .footer strong {
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ---------- INITIALIZE SESSION STATE ----------
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        'score': 0,
        'q_index': 0,
        'answers': [],
        'quiz_started': False,
        'subject': "All",
        'feedback': None,
        'selected_option': None,
        'leaderboard': [],
        'questions': [],
        'total_questions': 0,
        'show_feedback': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ---------- LOAD QUESTIONS FROM JSON ----------
@st.cache_data(ttl=3600)
def load_questions():
    """Load questions from JSON file with fallback defaults."""
    try:
        with open("questions.json", "r") as f:
            questions = json.load(f)
            if questions:
                return questions
    except:
        pass
    
    # Default questions if file not found
    return [
        {
            "subject": "Physics",
            "question": "What is the SI unit of force?",
            "options": ["Joule", "Newton", "Watt", "Pascal"],
            "correct_option": 1,
            "explanation": "Newton (N) is the SI unit of force. 1 N = 1 kg·m/s²."
        },
        {
            "subject": "Physics",
            "question": "Which of the following is a scalar quantity?",
            "options": ["Velocity", "Acceleration", "Mass", "Force"],
            "correct_option": 2,
            "explanation": "Mass is scalar (only magnitude). The others are vectors (magnitude + direction)."
        },
        {
            "subject": "Chemistry",
            "question": "What is the pH of a neutral solution at 25°C?",
            "options": ["0", "7", "14", "1"],
            "correct_option": 1,
            "explanation": "pH 7 is neutral. Below 7 is acidic, above 7 is alkaline."
        },
        {
            "subject": "Chemistry",
            "question": "Which element has the symbol 'Na'?",
            "options": ["Nitrogen", "Neon", "Sodium", "Nickel"],
            "correct_option": 2,
            "explanation": "Na comes from the Latin 'natrium', meaning sodium."
        },
        {
            "subject": "Biology",
            "question": "What is the main function of red blood cells?",
            "options": ["Fight infection", "Carry oxygen", "Clot blood", "Produce antibodies"],
            "correct_option": 1,
            "explanation": "Red blood cells contain hemoglobin, which binds oxygen and transports it."
        },
        {
            "subject": "Biology",
            "question": "Which organelle is known as the 'powerhouse' of the cell?",
            "options": ["Nucleus", "Ribosome", "Mitochondria", "Golgi apparatus"],
            "correct_option": 2,
            "explanation": "Mitochondria generate ATP, the cell's energy currency."
        }
    ]

questions_db = load_questions()

# ---------- GOOGLE SHEETS CONNECTION ----------
@st.cache_resource
def get_google_sheets_connection():
    """Establish connection to Google Sheets."""
    try:
        if "gcp_service_account" not in st.secrets:
            return None
            
        scope = ["https://spreadsheets.google.com/feeds", 
                 "https://www.googleapis.com/auth/drive"]
        
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Open the sheet
        sheet = client.open("SainsQuiz Leaderboard").sheet1
        
        # Ensure headers exist
        headers = sheet.row_values(1)
        if headers != ['Name', 'Score', 'Date']:
            sheet.clear()
            sheet.append_row(['Name', 'Score', 'Date'])
        
        return sheet
    except Exception as e:
        return None

def save_score_to_sheets(name, score):
    """Save a score to Google Sheets."""
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
    """Load top scores from Google Sheets."""
    try:
        sheet = get_google_sheets_connection()
        if sheet:
            records = sheet.get_all_records()
            
            # Convert to list of (name, score)
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
            
            # Sort and return top 10
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
    selected_subject = st.selectbox("📚 Choose Subject", subjects, 
                                   index=subjects.index(st.session_state.subject))
    
    if selected_subject != st.session_state.subject:
        st.session_state.subject = selected_subject
        st.session_state.quiz_started = False
        st.rerun()
    
    # New quiz button
    if st.button("🎯 New Quiz", use_container_width=True):
        st.session_state.quiz_started = True
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.answers = []
        st.session_state.feedback = None
        
        # Filter and shuffle questions
        if st.session_state.subject == "All":
            st.session_state.questions = random.sample(questions_db, min(10, len(questions_db)))
        else:
            filtered = [q for q in questions_db if q['subject'] == st.session_state.subject]
            st.session_state.questions = random.sample(filtered, min(10, len(filtered)))
        
        st.session_state.total_questions = len(st.session_state.questions)
        st.rerun()
    
    st.markdown("---")
    
    # Score during quiz
    if st.session_state.quiz_started and st.session_state.total_questions > 0:
        st.metric("📊 Current Score", 
                 f"{st.session_state.score}/{st.session_state.total_questions}")
        
        # Progress bar
        progress = st.session_state.q_index / st.session_state.total_questions
        st.progress(progress)
    
    # Leaderboard
    st.markdown("### 🏆 Top Players")
    
    leaderboard_data = load_leaderboard_from_sheets()
    
    if leaderboard_data:
        for i, (name, score) in enumerate(leaderboard_data, 1):
            if i == 1:
                st.markdown(f"""
                <div class="leaderboard-item">
                    <span class="leaderboard-rank">🥇</span>
                    <span class="leaderboard-name">{name}</span>
                    <span class="leaderboard-score">{score}</span>
                </div>
                """, unsafe_allow_html=True)
            elif i == 2:
                st.markdown(f"""
                <div class="leaderboard-item">
                    <span class="leaderboard-rank">🥈</span>
                    <span class="leaderboard-name">{name}</span>
                    <span class="leaderboard-score">{score}</span>
                </div>
                """, unsafe_allow_html=True)
            elif i == 3:
                st.markdown(f"""
                <div class="leaderboard-item">
                    <span class="leaderboard-rank">🥉</span>
                    <span class="leaderboard-name">{name}</span>
                    <span class="leaderboard-score">{score}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="leaderboard-item">
                    <span class="leaderboard-rank">#{i}</span>
                    <span class="leaderboard-name">{name}</span>
                    <span class="leaderboard-score">{score}</span>
                </div>
                """, unsafe_allow_html=True)
    elif st.session_state.leaderboard:
        for i, (name, score) in enumerate(st.session_state.leaderboard[:5], 1):
            st.markdown(f"""
            <div class="leaderboard-item">
                <span class="leaderboard-rank">#{i}</span>
                <span class="leaderboard-name">{name}</span>
                <span class="leaderboard-score">{score}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("✨ No scores yet. Be the first!")

# ---------- MAIN CONTENT ----------
st.markdown("""
<div class="main-header">
    <h1>🧪 SAINSQUIZ</h1>
    <p>Master SPM Science • Compete with Friends • Top the Leaderboard</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.quiz_started:
    # Welcome screen with subject cards
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
    
    st.markdown("---")
    
    with st.expander("ℹ️ How to Play", expanded=True):
        st.markdown("""
        <div style="padding:1rem;">
            <p>✨ <strong>Choose your subject</strong> from the sidebar</p>
            <p>🎯 Click <strong>"New Quiz"</strong> to start</p>
            <p>📝 Answer 10 randomly selected questions</p>
            <p>💡 Get instant feedback with explanations</p>
            <p>🏆 Save your score to the global leaderboard</p>
            <p>👥 Challenge friends to beat your score!</p>
            <p style="margin-top:1rem; color:#667eea;"><em>Questions are based on actual SPM syllabus.</em></p>
        </div>
        """, unsafe_allow_html=True)

else:
    # Quiz active
    if st.session_state.q_index < st.session_state.total_questions:
        q = st.session_state.questions[st.session_state.q_index]
        
        # Question box
        st.markdown(f"""
        <div class="question-box">
            <h3>Question {st.session_state.q_index + 1} of {st.session_state.total_questions}</h3>
            <p>{q['question']}</p>
            <p style="font-size:0.9rem; opacity:0.8;">📚 {q['subject']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Answer options
        answer = st.radio("Select your answer:", q['options'], 
                         key=f"q_{st.session_state.q_index}", 
                         index=None)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("✅ Submit Answer", use_container_width=True):
                if answer is None:
                    st.warning("Please select an answer!")
                else:
                    correct = q['options'][q['correct_option']]
                    is_correct = (answer == correct)
                    
                    # Store answer
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
                if st.button("➡️ Next Question", use_container_width=True, type="primary"):
                    st.session_state.q_index += 1
                    st.session_state.show_feedback = False
                    st.session_state.feedback = None
                    st.rerun()
        
        # Show feedback
        if st.session_state.show_feedback and st.session_state.feedback:
            last_answer = st.session_state.answers[-1]
            
            if last_answer['correct']:
                st.markdown(f"""
                <div class="correct-answer">
                    ✅ <strong>Correct!</strong><br>
                    {last_answer['explanation']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="wrong-answer">
                    ❌ <strong>Not quite!</strong><br>
                    Correct answer: <strong>{last_answer['correct_answer']}</strong><br>
                    {last_answer['explanation']}
                </div>
                """, unsafe_allow_html=True)
    
    else:
        # Quiz completed
        st.balloons()
        
        percentage = (st.session_state.score / st.session_state.total_questions) * 100
        
        st.markdown(f"""
        <div class="question-box" style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); color: #1a4731;">
            <h1>🎉 Quiz Complete!</h1>
            <h2>Your Score: {st.session_state.score}/{st.session_state.total_questions}</h2>
            <h3>{percentage:.1f}%</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Review answers
        with st.expander("📋 Review Your Answers", expanded=True):
            for i, ans in enumerate(st.session_state.answers):
                if ans['correct']:
                    st.markdown(f"**Q{i+1}:** ✅ {ans['question']}")
                else:
                    st.markdown(f"**Q{i+1}:** ❌ {ans['question']}")
                    st.markdown(f"*Correct: {ans['correct_answer']}*")
                    st.markdown(f"*{ans['explanation']}*")
                st.markdown("---")
        
        # Save score section
        st.markdown("### 🏆 Save to Leaderboard")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            player_name = st.text_input("Your name:", max_chars=20, 
                                       placeholder="Enter your name")
        
        with col2:
            if st.button("💾 Save", type="primary", use_container_width=True):
                if player_name:
                    if save_score_to_sheets(player_name, st.session_state.score):
                        st.markdown('<div class="success-message">✅ Score saved to global leaderboard!</div>', 
                                  unsafe_allow_html=True)
                        st.cache_data.clear()
                    else:
                        st.session_state.leaderboard.append((player_name, st.session_state.score))
                        st.session_state.leaderboard.sort(key=lambda x: x[1], reverse=True)
                        st.session_state.leaderboard = st.session_state.leaderboard[:10]
                        st.markdown('<div class="success-message">✅ Score saved locally!</div>', 
                                  unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.warning("Please enter your name!")
        
        # New quiz button
        if st.button("🔄 Take Another Quiz", use_container_width=True):
            st.session_state.quiz_started = False
            st.rerun()

# ---------- FOOTER ----------
st.markdown("""
<div class="footer">
    <p>🇲🇾 <strong>SainsQuiz</strong> – Helping Malaysian students master SPM Science</p>
    <p style="font-size:0.8rem; opacity:0.8;">Questions based on SPM syllabus • Not affiliated with MOE</p>
</div>
""", unsafe_allow_html=True)
