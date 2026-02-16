import streamlit as st
import pandas as pd
import random
import json
from datetime import date
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

# ---------- GOOGLE SHEETS SETUP (FREE) ----------
# Instructions: Create a Google Sheet, share with a service account email, and download JSON key.
# For now, we'll use a local file for leaderboard (session state) – but to make it real across all users,
# uncomment the Google Sheets code and follow the setup guide at the end.

# Simpler: Use session state leaderboard (per user) – but for multi-user, we need Sheets.
# Let's implement both: if Sheets fails, fallback to session state.

def init_google_sheets():
    """Connect to Google Sheets for persistent leaderboard."""
    try:
        # Use secrets from Streamlit Cloud (safer)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gcp_service_account"])  # Store in Streamlit secrets
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("SainsQuiz Leaderboard").sheet1  # Create this sheet first
        return sheet
    except:
        return None

# ---------- LOAD QUESTIONS ----------
@st.cache_data
def load_questions():
    with open("questions.json", "r") as f:
        return json.load(f)

questions_db = load_questions()

# ---------- SESSION STATE INIT ----------
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'q_index' not in st.session_state:
    st.session_state.q_index = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []  # store user answers for review
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'subject' not in st.session_state:
    st.session_state.subject = "All"
if 'feedback' not in st.session_state:
    st.session_state.feedback = None
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None
if 'leaderboard' not in st.session_state:
    st.session_state.leaderboard = []  # fallback local leaderboard

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
    
    # Leaderboard preview
    st.markdown("### 🏆 Top Players")
    # For simplicity, show local leaderboard; later we'll integrate Sheets
    if st.session_state.leaderboard:
        for i, (name, score) in enumerate(st.session_state.leaderboard[:5], 1):
            st.write(f"{i}. {name} – {score}")
    else:
        st.write("No scores yet. Be the first!")

# ---------- MAIN QUIZ AREA ----------
st.title("🧪 SainsQuiz – SPM Science")
st.caption("Test your knowledge with SPM-style questions!")

if not st.session_state.quiz_started:
    st.info("👋 Click **New Quiz** in the sidebar to begin!")
    
    # Show some instructions
    with st.expander("ℹ️ How to Play"):
        st.write("""
        - Choose a subject from the sidebar.
        - Click 'New Quiz' to start.
        - You'll get 10 random questions.
        - Each correct answer = 1 point.
        - After finishing, you can review your answers.
        - Add your name to the leaderboard!
        """)
else:
    # Filter questions by subject
    if st.session_state.subject == "All":
        questions = questions_db
    else:
        questions = [q for q in questions_db if q['subject'] == st.session_state.subject]
    
    if not questions:
        st.error("No questions for this subject yet. Add some in questions.json!")
        st.stop()
    
    # Randomize if starting new quiz
    if st.session_state.q_index == 0 and not st.session_state.answers:
        random.shuffle(questions)
        st.session_state.quiz_questions = questions[:10]  # take 10 random
    
    # Check if quiz finished
    if st.session_state.q_index >= len(st.session_state.quiz_questions):
        st.success(f"🎉 Quiz Complete! Your final score: {st.session_state.score}/10")
        
        # Review answers
        with st.expander("📋 Review Your Answers"):
            for i, ans in enumerate(st.session_state.answers):
                q = st.session_state.quiz_questions[i]
                if ans['correct']:
                    st.markdown(f"**Q{i+1}:** ✅ {q['question']} – You got it right!")
                else:
                    st.markdown(f"**Q{i+1}:** ❌ {q['question']}")
                    st.markdown(f"*Your answer:* {ans['user_answer']}")
                    st.markdown(f"*Correct answer:* {q['options'][q['correct_option']]}")
                    st.markdown(f"*Explanation:* {q['explanation']}")
                st.markdown("---")
        
        # Save to leaderboard
        player_name = st.text_input("Enter your name for leaderboard:", max_chars=20)
        if st.button("🏆 Save Score", type="primary"):
            if player_name:
                # Add to local leaderboard
                st.session_state.leaderboard.append((player_name, st.session_state.score))
                st.session_state.leaderboard.sort(key=lambda x: x[1], reverse=True)
                st.session_state.leaderboard = st.session_state.leaderboard[:10]  # keep top 10
                st.success("Score saved!")
                st.rerun()
            else:
                st.warning("Please enter a name.")
        
        # Share on WhatsApp
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
            
            options = q['options']
            # Radio buttons for answer
            choice = st.radio("Select your answer:", options, key=f"q_{st.session_state.q_index}", index=None)
            
            col1, col2 = st.columns([1, 5])
            with col1:
                submit = st.button("✅ Submit")
            with col2:
                if st.session_state.feedback:
                    st.markdown(st.session_state.feedback)
            
            if submit:
                if choice is None:
                    st.warning("Please select an answer.")
                else:
                    # Check answer
                    correct_option = q['correct_option']  # index 0-3
                    correct_text = options[correct_option]
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
                        feedback = f"❌ Incorrect. The correct answer is: **{correct_text}**. {q['explanation']}"
                    
                    st.session_state.feedback = feedback
                    
                    # Move to next question after a short delay? Better to let user click next.
                    # We'll add a "Next" button.
                    st.rerun()
            
            # Next button (appears after answering)
            if st.session_state.feedback and st.button("➡️ Next Question", type="primary"):
                st.session_state.q_index += 1
                st.session_state.feedback = None
                st.rerun()

# ---------- FOOTER ----------
st.markdown("---")
st.caption("© 2025 SainsQuiz – Data sourced from SPM past papers. Not affiliated with MOE.")