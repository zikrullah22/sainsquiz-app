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

# ---------- FINAL CSS (FIXED FOR DARK/LIGHT MODE) ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Global Reset to force visibility */
    * { font-family: 'Inter', sans-serif; }
    
    .stApp { background-color: #f3f4f6; }

    /* Force all text inside our white boxes to be DEEP BLACK */
    .header h1, .header p, .question-box h3, .question-box p, 
    div.row-widget.stRadio label p, .leaderboard-item span {
        color: #000000 !important;
    }

    /* Header */
    .header {
        background: white !important;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 0px #000000;
        text-align: center;
        margin-bottom: 2rem;
        border: 3px solid #000000;
    }

    /* Subject Cards */
    .subject-card {
        background: white !important;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        border: 3px solid #000000;
        box-shadow: 0 4px 0px #000000;
        color: #000000 !important;
    }
    .subject-card h3 { color: #000000 !important; }

    /* Question Box */
    .question-box {
        background: white !important;
        padding: 1.8rem;
        border-radius: 16px;
        border: 3px solid #000000;
        margin-bottom: 1.8rem;
        box-shadow: 0 6px 0px #000000;
    }

    .subject-tag {
        background: #2563eb !important;
        color: white !important;
        padding: 0.3rem 1.2rem;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 10px;
    }

    /* ===== RADIO BUTTONS – FORCED VISIBILITY ===== */
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
        box-shadow: 0 4px 0px #000000 !important;
        transition: all 0.2s ease !important;
    }

    /* Selection Circle Color */
    div.row-widget.stRadio [data-baseweb="radio"] > div:first-child {
        border-color: #000000 !important;
        background-color: white !important;
    }

    /* Hover effect */
    div.row-widget.stRadio label:hover {
        background-color: #f0f7ff !important;
        border-color: #2563eb !important;
        box-shadow: 0 6px 0px #2563eb !important;
    }

    /* THE TEXT INSIDE THE OPTIONS */
    div.row-widget.stRadio label p {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
    }

    /* When selected */
    div.row-widget.stRadio label:has(input:checked) {
        background-color: #eff6ff !important;
        border-color: #2563eb !important;
    }

    /* ===== BUTTONS ===== */
    .stButton button {
        background: #000000 !important;
        color: white !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        padding: 0.7rem 1.5rem !important;
        border: 2px solid #000000 !important;
        box-shadow: 0 4px 0px #2563eb !important;
        width: 100%;
    }

    /* Leaderboard */
    .leaderboard-item {
        background: white !important;
        padding: 0.7rem 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        border: 2px solid #000000;
    }
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
def init_session_state():
    if 'score' not in st.session_state:
        st.session_state.update({
            'score': 0, 'q_index': 0, 'answers': [], 'quiz_started': False,
            'subject': "All", 'questions': [], 'total_questions': 0, 'show_feedback': False
        })

init_session_state()

# ---------- DATA LOADING ----------
@st.cache_data
def load_questions():
    try:
        with open("questions.json", "r") as f: return json.load(f)
    except:
        return [
            {"subject": "Chemistry", "question": "What is the chemical symbol for gold?", "options": ["Go", "Gd", "Au", "Ag"], "correct_option": 2, "explanation": "Au comes from the Latin word 'Aurum'."},
            {"subject": "Physics", "question": "Which law states that F = ma?", "options": ["Newton's 1st", "Newton's 2nd", "Newton's 3rd", "Hooke's Law"], "correct_option": 1, "explanation": "Newton's Second Law relates force, mass, and acceleration."},
            {"subject": "Biology", "question": "What is the primary function of red blood cells?", "options": ["Clotting", "Immunity", "Oxygen Transport", "Digestion"], "correct_option": 2, "explanation": "Haemoglobin in RBCs carries oxygen."}
        ]

questions_db = load_questions()

# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("🧪 SainsQuiz")
    st.divider()
    
    subj_list = ["All", "Physics", "Chemistry", "Biology"]
    selected = st.selectbox("Choose Subject", subj_list, index=subj_list.index(st.session_state.subject))
    
    if selected != st.session_state.subject:
        st.session_state.subject = selected
        st.session_state.quiz_started = False

    if st.button("New Quiz 🚀"):
        st.session_state.quiz_started = True
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.show_feedback = False
        st.session_state.answers = []
        
        pool = questions_db if selected == "All" else [q for q in questions_db if q['subject'] == selected]
        st.session_state.questions = random.sample(pool, min(10, len(pool)))
        st.session_state.total_questions = len(st.session_state.questions)
        st.rerun()

    if st.session_state.quiz_started:
        st.divider()
        st.metric("Progress", f"{st.session_state.q_index}/{st.session_state.total_questions}")
        st.progress(st.session_state.q_index / st.session_state.total_questions if st.session_state.total_questions > 0 else 0)

# ---------- MAIN CONTENT ----------
if not st.session_state.quiz_started:
    st.markdown('<div class="header"><h1>🧪 SainsQuiz</h1><p>Master SPM Science with Ease</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown('<div class="subject-card"><h3>Physics</h3></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="subject-card"><h3>Chemistry</h3></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="subject-card"><h3>Biology</h3></div>', unsafe_allow_html=True)
else:
    if st.session_state.q_index < st.session_state.total_questions:
        q = st.session_state.questions[st.session_state.q_index]
        
        st.markdown(f"""
        <div class="question-box">
            <span class="subject-tag">{q['subject']}</span>
            <h3>Question {st.session_state.q_index + 1} of {st.session_state.total_questions}</h3>
            <p>{q['question']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Radio Selection
        user_choice = st.radio("Options", q['options'], key=f"q_{st.session_state.q_index}", index=None, label_visibility="collapsed")

        col_a, col_b = st.columns(2)
        
        if not st.session_state.show_feedback:
            with col_a:
                if st.button("Submit Answer"):
                    if user_choice:
                        correct_val = q['options'][q['correct_option']]
                        is_correct = (user_choice == correct_val)
                        if is_correct: st.session_state.score += 1
                        st.session_state.answers.append({'correct': is_correct, 'exp': q['explanation'], 'val': correct_val})
                        st.session_state.show_feedback = True
                        st.rerun()
                    else:
                        st.error("Please pick an option!")
        else:
            feedback = st.session_state.answers[-1]
            color = "#dcfce7" if feedback['correct'] else "#fee2e2"
            txt_color = "#166534" if feedback['correct'] else "#991b1b"
            
            st.markdown(f"""
            <div style="background:{color}; border:3px solid #000000; padding:1.2rem; border-radius:12px; margin-bottom:1rem; color:{txt_color}; font-weight:700;">
                {"✅ Correct!" if feedback['correct'] else "❌ Wrong. Correct: " + feedback['val']}<br>
                <small style="color:black;">{feedback['exp']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            with col_b:
                if st.button("Next Question ➡️"):
                    st.session_state.q_index += 1
                    st.session_state.show_feedback = False
                    st.rerun()
    else:
        st.balloons()
        st.markdown(f'<div class="header"><h1>🎉 Quiz Complete!</h1><p style="font-size:2rem; font-weight:800;">Score: {st.session_state.score}/{st.session_state.total_questions}</p></div>', unsafe_allow_html=True)
        if st.button("Try Another Quiz"):
            st.session_state.quiz_started = False
            st.rerun()

st.markdown('<div style="text-align:center; color:#6b7280; padding:20px;">SainsQuiz 🇲🇾</div>', unsafe_allow_html=True)
