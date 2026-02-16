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

# ---------- CUSTOM CSS FOR MALAYSIA THEME ----------
st.markdown("""
<style>
    /* Malaysia flag colors theme */
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    }
    .main-header {
        background: linear-gradient(90deg, #cc0000 0%, #010066 50%, #ffcc00 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 2.5rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .question-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .correct-answer {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 1rem;
        border-radius: 15px;
        color: #1a4731;
        font-weight: bold;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .wrong-answer {
        background: linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%);
        padding: 1rem;
        border-radius: 15px;
        color: #721c24;
        font-weight: bold;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
    }
    .leaderboard-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        text-align: center;
    }
    .stButton button {
        background: linear-gradient(90deg, #cc0000 0%, #010066 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .success-message {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 1rem;
        border-radius: 10px;
        color: #1a4731;
        text-align: center;
        font-weight: bold;
    }
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem 1rem;
    }
    .status-badge {
        padding: 0.5rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        text-align: center;
        margin: 0.5rem 0;
    }
    .status-connected {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #1a4731;
    }
    .status-disconnected {
        background: linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%);
        color: #721c24;
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
        st.sidebar.error(f"❌ Sheets error: {str(e)}")
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
    st.markdown("## 🧪 **SainsQuiz**")
    st.markdown("### *SPM Science Practice*")
    st.markdown("---")
    
    # Connection status
    sheet = get_google_sheets_connection()
    if sheet:
        st.markdown('<div class="status-badge status-connected">✅ Connected to Global Leaderboard</div>', 
                   unsafe_allow_html=True)
        client_email = st.secrets["gcp_service_account"].get("client_email", "")
        if client_email:
            st.caption(f"📧 {client_email[:30]}...")
    else:
        st.markdown('<div class="status-badge status-disconnected">⚠️ Local Mode Only</div>', 
                   unsafe_allow_html=True)
    
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
    st.markdown("### 🏆 **Top Players**")
    
    leaderboard_data = load_leaderboard_from_sheets()
    
    if leaderboard_data:
        for i, (name, score) in enumerate(leaderboard_data, 1):
            if i == 1:
                st.markdown(f"🥇 **{name}** – {score} pts")
            elif i == 2:
                st.markdown(f"🥈 **{name}** – {score} pts")
            elif i == 3:
                st.markdown(f"🥉 **{name}** – {score} pts")
            else:
                st.markdown(f"{i}. **{name}** – {score} pts")
    elif st.session_state.leaderboard:
        st.caption("📱 Local scores only")
        for i, (name, score) in enumerate(st.session_state.leaderboard[:5], 1):
            st.markdown(f"{i}. **{name}** – {score} pts")
    else:
        st.info("No scores yet. Be the first!")

# ---------- MAIN CONTENT ----------
st.markdown('<div class="main-header">🧪 SAINSQUIZ</div>', unsafe_allow_html=True)
st.markdown("### *Master SPM Science • Compete with Friends • Top the Leaderboard*")

if not st.session_state.quiz_started:
    # Welcome screen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align:center; padding:1rem;">
            <h3>📚 Physics</h3>
            <p>Forces, Motion, Heat, Light & Waves</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align:center; padding:1rem;">
            <h3>🧪 Chemistry</h3>
            <p>Periodic Table, Chemical Bonds, Acids & Bases</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align:center; padding:1rem;">
            <h3>🔬 Biology</h3>
            <p>Cells, Human Body, Plants, Ecosystems</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    with st.expander("ℹ️ How to Play", expanded=True):
        st.markdown("""
        1. **Choose your subject** from the sidebar
        2. Click **"New Quiz"** to start
        3. Answer 10 randomly selected questions
        4. Get instant feedback with explanations
        5. Save your score to the global leaderboard
        6. Challenge friends to beat your score!
        
        *Questions are based on actual SPM syllabus.*
        """)

else:
    # Quiz active
    if st.session_state.q_index < st.session_state.total_questions:
        q = st.session_state.questions[st.session_state.q_index]
        
        # Question box
        st.markdown(f"""
        <div class="question-box">
            <h3>Question {st.session_state.q_index + 1} of {st.session_state.total_questions}</h3>
            <p style="font-size:1.2rem;">{q['question']}</p>
            <p style="font-size:0.9rem; opacity:0.8;">Subject: {q['subject']}</p>
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
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            player_name = st.text_input("Your name:", max_chars=20, 
                                       placeholder="Enter your name")
        
        with col2:
            if st.button("💾 Save My Score", type="primary", use_container_width=True):
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
        
        with col3:
            st.markdown(" ")
        
        # Share buttons
        st.markdown("### 📱 Share Your Achievement")
        
        share_text = f"I scored {st.session_state.score}/{st.session_state.total_questions} on SainsQuiz! Can you beat me?"
        app_url = "https://sainsquiz.streamlit.app"
        
        col1, col2 = st.columns(2)
        
        with col1:
            wa_link = f"https://wa.me/?text={share_text} {app_url}".replace(' ', '%20')
            st.markdown(f"""
            <a href="{wa_link}" target="_blank">
                <button style="background-color:#25D366; color:white; border:none; padding:10px; border-radius:10px; width:100%;">
                📱 WhatsApp
                </button>
            </a>
            """, unsafe_allow_html=True)
        
        with col2:
            tg_link = f"https://t.me/share/url?url={app_url}&text={share_text}".replace(' ', '%20')
            st.markdown(f"""
            <a href="{tg_link}" target="_blank">
                <button style="background-color:#0088cc; color:white; border:none; padding:10px; border-radius:10px; width:100%;">
                📨 Telegram
                </button>
            </a>
            """, unsafe_allow_html=True)
        
        # New quiz button
        if st.button("🔄 Take Another Quiz", use_container_width=True):
            st.session_state.quiz_started = False
            st.rerun()

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#666; padding:1rem;">
    <p>🇲🇾 <strong>SainsQuiz</strong> – Helping Malaysian students master SPM Science</p>
    <p style="font-size:0.8rem;">Questions based on SPM syllabus • Not affiliated with MOE • Data crowdsourced from students</p>
</div>
""", unsafe_allow_html=True)
