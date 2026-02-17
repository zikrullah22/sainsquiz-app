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

# ---------- FINAL CSS WITH NEUBRUTALISM STYLE ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f3f4f6; }

    /* Header & Cards */
    .header {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 0px #000000;
        text-align: center;
        margin-bottom: 2rem;
        border: 3px solid #000000;
    }
    .subject-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        border: 3px solid #000000;
        transition: 0.2s;
        height: 100%;
        box-shadow: 0 4px 0px #000000;
    }
    .question-box {
        background: white;
        padding: 1.8rem;
        border-radius: 16px;
        border: 3px solid #000000;
        margin-bottom: 1.8rem;
        box-shadow: 0 6px 0px #000000;
    }
    .subject-tag {
        background: #2563eb;
        color: white;
        padding: 0.3rem 1.2rem;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
    }

    /* ===== RADIO BUTTONS – MAXIMUM VISIBILITY ===== */
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
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 0px #000000 !important;
    }

    div.row-widget.stRadio label:hover {
        background-color: #f8fafc !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 0px #2563eb !important;
        border-color: #2563eb !important;
    }

    /* Target the text inside radio labels */
    div.row-widget.stRadio label p {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }

    /* Highlight selected option */
    div.row-widget.stRadio label:has(input:checked) {
        background-color: #eff6ff !important;
        border-color: #2563eb !important;
    }

    /* Big custom radio circles */
    div.row-widget.stRadio [data-baseweb="radio"] > div:first-child {
        border: 2px solid black !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* Buttons */
    .stButton button {
        background: #000000 !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        padding: 0.7rem 1.5rem !important;
        border: 2px solid #000000 !important;
        box-shadow: 0 4px 0px #2563eb !important;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 0px #2563eb !important;
    }

    /* Success/Error Feedback */
    .feedback-box {
        padding: 1.2rem;
        border-radius: 12px;
        border: 3px solid #000000;
        margin: 1rem 0;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
def init_session_state():
    if 'score' not in st.session_state:
        st.session_state.update({
            'score': 0, 'q_index': 0, 'answers': [], 
            'quiz_started': False, 'subject': "All", 
            'questions': [], 'total_questions': 0, 'show_feedback': False
        })

init_session_state()

# ---------- QUESTIONS DB ----------
@st.cache_data
def load_questions():
    # Attempt to load from JSON, else use defaults
    try:
        with open("questions.json", "r") as f: return json.load(f)
    except:
        return [
            {"subject": "Physics", "question": "What is the SI unit of force?", "options": ["Joule", "Newton", "Watt", "Pascal"], "correct_option": 1, "explanation": "Newton (N) is the unit named after Isaac Newton."},
            {"subject": "Chemistry", "question": "What is the pH of a neutral solution?", "options": ["0", "7", "14", "1"], "correct_option": 1, "explanation": "pH 7 is neutral; below 7 is acidic and above 7 is alkaline."},
            {"subject": "Biology", "question": "Which organelle is the 'powerhouse' of the cell?", "options": ["Nucleus", "Ribosome", "Mitochondria", "Golgi"], "correct_option": 2, "explanation": "Mitochondria generate most of the cell's supply of ATP."}
        ]

questions_db = load_questions()

# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("🧪 SainsQuiz")
    selected = st.selectbox("Select Subject", ["All", "Physics", "Chemistry", "Biology"])
    if selected != st.session_state.subject:
        st.session_state.subject = selected
        st.session_state.quiz_started = False

    if st.button("🚀 Start New Quiz", use_container_width=True):
        st.session_state.quiz_started = True
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.show_feedback = False
        st.session_state.answers = []
        
        filtered = questions_db if selected == "All" else [q for q in questions_db if q['subject'] == selected]
        st.session_state.questions = random.sample(filtered, min(5, len(filtered)))
        st.session_state.total_questions = len(st.session_state.questions)
        st.rerun()

    if st.session_state.quiz_started:
        st.divider()
        st.metric("Score", f"{st.session_state.score}/{st.session_state.total_questions}")
        st.progress(st.session_state.q_index / st.session_state.total_questions if st.session_state.total_questions > 0 else 0)

# ---------- MAIN CONTENT ----------
if not st.session_state.quiz_started:
    st.markdown('<div class="header"><h1>SPM Science Mastery</h1><p>Select a subject and click "Start New Quiz" to begin!</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown('<div class="subject-card">📚<br>Physics</div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="subject-card">🧪<br>Chemistry</div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="subject-card">🔬<br>Biology</div>', unsafe_allow_html=True)
else:
    if st.session_state.q_index < st.session_state.total_questions:
        q = st.session_state.questions[st.session_state.q_index]
        
        st.markdown(f"""
        <div class="question-box">
            <span class="subject-tag">{q['subject']}</span>
            <h3>Question {st.session_state.q_index + 1}</h3>
            <p style="font-size:1.3rem;">{q['question']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Radio Selection
        ans = st.radio("Choose one:", q['options'], key=f"q_{st.session_state.q_index}", index=None, label_visibility="collapsed")

        if not st.session_state.show_feedback:
            if st.button("Submit Answer", use_container_width=True):
                if ans:
                    is_correct = (ans == q['options'][q['correct_option']])
                    if is_correct: st.session_state.score += 1
                    st.session_state.answers.append(is_correct)
                    st.session_state.show_feedback = True
                    st.rerun()
                else:
                    st.warning("Please select an option!")
        else:
            # Show Feedback
            correct_answer = q['options'][q['correct_option']]
            is_right = (ans == correct_answer)
            
            bg = "#dcfce7" if is_right else "#fee2e2"
            icon = "✅ Correct!" if is_right else f"❌ Incorrect (Correct: {correct_answer})"
            
            st.markdown(f"""
            <div class="feedback-box" style="background:{bg};">
                {icon}<br>
                <small style="font-weight:400;">{q['explanation']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Next Question ➡️", use_container_width=True):
                st.session_state.q_index += 1
                st.session_state.show_feedback = False
                st.rerun()
    else:
        # Results
        st.balloons()
        st.markdown(f"""
        <div class="header" style="background:#f0f9ff;">
            <h1>🎉 Quiz Complete!</h1>
            <p style="font-size:3rem; font-weight:800; color:#2563eb;">{st.session_state.score} / {st.session_state.total_questions}</p>
            <p>Great job! Ready to try another subject?</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Back to Home"):
            st.session_state.quiz_started = False
            st.rerun()

st.markdown('<div style="text-align:center; color:#6b7280; margin-top:50px;">Made for SPM Students 🇲🇾</div>', unsafe_allow_html=True)
