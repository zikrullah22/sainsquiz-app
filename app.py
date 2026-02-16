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
    layout="centered"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
    .question-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
    }
    .correct {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
    }
    .incorrect {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
    }
    .stButton button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ---------- INIT SESSION STATE ----------
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'q_index' not in st.session_state:
    st.session_state.q_index = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'subject' not in st.session_state:
    st.session_state.subject = "All"
if 'feedback' not in st.session_state:
    st.session_state.feedback = None
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None
if 'leaderboard' not in st.session_state:
    st.session_state.leaderboard = []  # local fallback

# ---------- LOAD QUESTIONS ----------
@st.cache_data
def load_questions():
    try:
        with open("questions.json", "r") as f:
            return json.load(f)
    except:
        # Default questions if file not found
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
                "question": "Which organelle is the 'powerhouse' of the cell?",
                "options": ["Nucleus", "Ribosome", "Mitochondria", "Golgi"],
                "correct_option": 2,
                "explanation": "Mitochondria produce ATP."
            }
        ]

questions_db = load_questions()

# ---------- GOOGLE SHEETS CONNECTION ----------
def init_google_sheets():
    """Connect to Google Sheets for persistent leaderboard."""
    try:
        # Check if secrets exist
        if "gcp_service_account" not in st.secrets:
            st.sidebar.warning("⚠️ Google Sheets credentials not found in secrets")
            return None
            
        scope = ["https://spreadsheets.google.com/feeds", 
                 "https://www.googleapis.com/auth/drive"]
        
        # Get credentials from secrets
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        # Debug: show which email we're using
        client_email = creds_dict.get("client_email", "Not found")
        st.sidebar.info(f"🔑 Using account: {client_email}")
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Try to open the sheet
        sheet = client.open("SainsQuiz Leaderboard").sheet1
        st.sidebar.success("✅ Connected to Google Sheets!")
        return sheet
    except Exception as e:
        st.sidebar.error(f"❌ Sheets connection failed: {str(e)}")
        return None

def save_score_to_sheets(name, score):
    """Save a score to Google Sheets."""
    sheet = init_google_sheets()
    if sheet:
        try:
            today = datetime.now().strftime("%Y-%m-%d %H:%M")
            sheet.append_row([name, score, today])
            return True
        except Exception as e:
            st.error(f"Failed to save to leaderboard: {e}")
            return False
    return False

@st.cache_data(ttl=30)  # Refresh every 30 seconds
def load_leaderboard_from_sheets():
    """Load top scores from Google Sheets."""
    sheet = init_google_sheets()
    if sheet:
        try:
            # Get all records
            records = sheet.get_all_records()
            
            # Convert to list of (name, score)
            leaderboard = []
            for r in records:
                if 'Name' in r and 'Score' in r:
                    try:
                        score = int(r['Score'])
                        leaderboard.append((r['Name'], score))
                    except:
                        pass
            
            # Sort by score descending, take top 10
            leaderboard.sort(key=lambda x: x[1], reverse=True)
            return leaderboard[:10]
        except Exception as e:
            st.warning(f"Could not load leaderboard: {e}")
            return None
    return None

# ---------- SIDEBAR ----------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/6/66/Flag_of_Malaysia.svg", width=100)
    st.title("🧪 SainsQuiz")
    st.caption("SPM Science Practice")
    
    st.markdown("---")
    
    # Subject selection
    subject = st.selectbox("Choose subject", ["All", "Physics", "Chemistry", "Biology"])
    st.session_state.subject = subject
    
    # New quiz button
    if st.button("🔄 New Quiz", use_container_width=True):
        st.session_state.score = 0
        st.session_state.q_index = 0
        st.session_state.answers = []
        st.session_state.quiz_started = True
        st.session_state.feedback = None
        st.rerun()
    
    st.markdown("---")
    
    # Show score during quiz
    if st.session_state.quiz_started:
        st.metric("Current Score", f"{st.session_state.score}")
    
    # Leaderboard display
    st.markdown("### 🏆 Top Players")
    
    # Try to load from Google Sheets first
    leaderboard_data = load_leaderboard_from_sheets()
    
    if leaderboard_data:
        for i, (name, score) in enumerate(leaderboard_data, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            st.write(f"{medal} **{name}** – {score} pts")
    elif st.session_state.leaderboard:
        st.caption("(Local scores - not shared)")
        for i, (name, score) in enumerate(st.session_state.leaderboard[:5], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            st.write(f"{medal} **{name}** – {score} pts")
    else:
        st.write("No scores yet. Be the first!")

# ---------- MAIN QUIZ AREA ----------
st.title("🧪 SainsQuiz – SPM Science")
st.caption("Test your knowledge with SPM-style questions!")

if not st.session_state.quiz_started:
    st.info("👋 Click **New Quiz** in the sidebar to begin!")
    
    with st.expander("ℹ️ How to Play"):
        st.write("""
        - Choose a subject from the sidebar
        - Click 'New Quiz' to start
        - You'll get 10 random questions
        - Each correct answer = 1 point
        - After finishing, add your name to the leaderboard!
        """)
else:
    # Filter questions by subject
    if st.session_state.subject == "All":
        questions = questions_db
    else:
        questions = [q for q in questions_db if q['subject'] == st.session_state.subject]
    
    if not questions:
        st.error("No questions for this subject yet!")
        st.stop()
    
    # Initialize quiz questions if starting
    if st.session_state.q_index == 0 and not st.session_state.answers:
        random.shuffle(questions)
        st.session_state.quiz_questions = questions[:min(10, len(questions))]
    
    # Check if quiz finished
    if st.session_state.q_index >= len(st.session_state.quiz_questions):
        st.success(f"🎉 Quiz Complete! Your final score: {st.session_state.score}/{len(st.session_state.quiz_questions)}")
        
        # Review answers
        with st.expander("📋 Review Your Answers"):
            for i, ans in enumerate(st.session_state.answers):
                q = st.session_state.quiz_questions[i]
                if ans['correct']:
                    st.markdown(f"**Q{i+1}:** ✅ {q['question']}")
                else:
                    st.markdown(f"**Q{i+1}:** ❌ {q['question']}")
                    st.markdown(f"*Correct answer:* {q['options'][q['correct_option']]}")
                    st.markdown(f"*Explanation:* {q['explanation']}")
                st.markdown("---")
        
        # Save score section
        st.markdown("### 🏆 Save Your Score")
        col1, col2 = st.columns(2)
        
        with col1:
            player_name = st.text_input("Enter your name:", max_chars=20, key="player_name")
        
        with col2:
            if st.button("💾 Save Score", type="primary", use_container_width=True):
                if player_name:
                    # Try Google Sheets first
                    if save_score_to_sheets(player_name, st.session_state.score):
                        st.success("✅ Score saved to global leaderboard!")
                        st.cache_data.clear()
                    else:
                        # Fallback to local
                        st.session_state.leaderboard.append((player_name, st.session_state.score))
                        st.session_state.leaderboard.sort(key=lambda x: x[1], reverse=True)
                        st.session_state.leaderboard = st.session_state.leaderboard[:10]
                        st.success("✅ Score saved locally!")
                    st.rerun()
                else:
                    st.warning("Please enter a name.")
        
        # Share on WhatsApp
        st.markdown("### 📱 Share Your Score")
        share_text = f"I scored {st.session_state.score}/10 on SainsQuiz SPM Science! Can you beat me? https://sainsquiz.streamlit.app"
        wa_link = f"https://wa.me/?text={share_text.replace(' ', '%20')}"
        st.markdown(f"""
        <a href="{wa_link}" target="_blank">
            <button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:10px; font-size:16px; width:100%;">
            📱 Share on WhatsApp
            </button>
        </a>
        """, unsafe_allow_html=True)
        
    else:
        # Display current question
        q = st.session_state.quiz_questions[st.session_state.q_index]
        
        with st.container():
            st.markdown(f"### Question {st.session_state.q_index+1} of {len(st.session_state.quiz_questions)}")
            st.markdown(f"**{q['question']}**")
            
            # Radio buttons for answer
            choice = st.radio("Select your answer:", q['options'], key=f"q_{st.session_state.q_index}", index=None)
            
            col1, col2 = st.columns([1, 5])
            with col1:
                submit = st.button("✅ Submit")
            
            if submit:
                if choice is None:
                    st.warning("Please select an answer.")
                else:
                    # Check answer
                    correct_option = q['correct_option']
                    correct_text = q['options'][correct_option]
                    is_correct = (choice == correct_text)
                    
                    # Store answer
                    st.session_state.answers.append({
                        'question': q['question'],
                        'user_answer': choice,
                        'correct': is_correct
                    })
                    
                    # Update score
                    if is_correct:
                        st.session_state.score += 1
                        feedback = f"✅ Correct! {q['explanation']}"
                    else:
                        feedback = f"❌ Incorrect. Correct answer: **{correct_text}**. {q['explanation']}"
                    
                    st.session_state.feedback = feedback
                    st.rerun()
            
            # Show feedback and next button
            if st.session_state.feedback:
                st.markdown(st.session_state.feedback)
                if st.button("➡️ Next Question", type="primary"):
                    st.session_state.q_index += 1
                    st.session_state.feedback = None
                    st.rerun()

# ---------- FOOTER ----------
st.markdown("---")
st.caption("© 2025 SainsQuiz – For SPM students. Not affiliated with MOE.")
