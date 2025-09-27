import streamlit as st
import json
import re
import os
from openai import OpenAI

# ------------------------------
# Global Fonts & Background
# ------------------------------
st.markdown(
    """
    <style>
    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Calligraffitti&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo&display=swap');

    /* Default English font */
    html, body, [class*="css"] {
        font-family: 'Calligraffitti', sans-serif;
    }

    /* Korean text uses Nanum Myeongjo */
    :lang(ko), .korean-text {
        font-family: 'Nanum Myeongjo', serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------
# Helper: format text by language
# ------------------------------
def format_text(text: str) -> str:
    """Wrap Korean text in Nanum Myeongjo, English in Calligraffitti."""
    korean_re = re.compile(r"[\uac00-\ud7a3]+")
    parts = korean_re.split(text)
    korean_parts = korean_re.findall(text)

    result = []
    for i, part in enumerate(parts):
        if part.strip():
            result.append(f"<span style='font-family: Calligraffitti;'>{part}</span>")
        if i < len(korean_parts):
            result.append(f"<span style='font-family: Nanum Myeongjo;' lang='ko'>{korean_parts[i]}</span>")
    return "".join(result)

# ------------------------------
# Helper: render chat messages
# ------------------------------
def render_message(role, content):
    content = format_text(content)
    if role == "user":
        st.markdown(
            f"""
            <div style="display:flex; justify-content:flex-end; margin:5px 0;">
                <div style="
                    background-color:#ff4c4c;
                    color: white;
                    padding:10px 15px;
                    border-radius:15px;
                    max-width:70%;
                    text-align:right;
                    box-shadow: 0px 2px 5px rgba(0,0,0,0.2);">
                    <b>🧑 You:</b><br>{content}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="display:flex; justify-content:flex-start; margin:5px 0;">
                <div style="
                    background-color:#4682B4;
                    color: white;
                    padding:10px 15px;
                    border-radius:15px;
                    max-width:70%;
                    text-align:left;
                    box-shadow: 0px 2px 5px rgba(0,0,0,0.2);">
                    <b>🤖 Bot:</b><br>{content}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ------------------------------
# Progress Persistence Helpers
# ------------------------------

PROGRESS_FILE = "progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except:
            return {"xp": 0, "quizzes_taken": 0, "correct_answers": 0, "assignments_done": 0}
    else:
        return {"xp": 0, "quizzes_taken": 0, "correct_answers": 0, "assignments_done": 0}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

# ------------------------------
# Helper functions
# ------------------------------

def generate_flashcards(topic):
    prompt = f"""
    Create 3 Korean flashcards about "{topic}".
    Respond ONLY with valid JSON, nothing else.
    Format:
    [
      {{"front": "학교", "back": "School"}}
    ]
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a JSON-only flashcard generator."},
                {"role": "user", "content": prompt}
            ]
        )
        raw = response.choices[0].message.content.strip()
        match = re.search(r"\[.*\]", raw, re.S)
        if match:
            raw = match.group(0)
        return json.loads(raw)
    except Exception as e:
        st.error(f"⚠️ Flashcard generation failed: {e}")
        return [{"front": "학교", "back": "School"}]

def generate_quiz(topic):
    prompt = f"""
    Create 3 Korean multiple-choice quizzes about "{topic}".
    Respond ONLY with valid JSON, nothing else.
    Format:
    [
      {{
        "question": "What does '학교' mean?",
        "options": ["School", "Teacher", "Book", "Friend"],
        "answer": "School"
      }}
    ]
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a JSON-only quiz generator."},
                {"role": "user", "content": prompt}
            ]
        )
        raw = response.choices[0].message.content.strip()
        match = re.search(r"\[.*\]", raw, re.S)
        if match:
            raw = match.group(0)
        return json.loads(raw)
    except Exception as e:
        st.error(f"⚠️ Quiz generation failed: {e}")
        return [
            {
                "question": "What does '학교' mean?",
                "options": ["School", "Book", "Friend", "Teacher"],
                "answer": "School"
            }
        ]

def generate_assignment(topic):
    prompt = f"Create 2 Korean learning assignments about '{topic}'."
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"⚠️ Assignment generation failed: {e}")
        return "Write 5 sentences using the word '학교'."

# ------------------------------
# Initialize session state
# ------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "flashcards" not in st.session_state:
    st.session_state.flashcards = []
if "flashcards_topic" not in st.session_state:
    st.session_state.flashcards_topic = ""

if "quizzes" not in st.session_state:
    st.session_state.quizzes = []
if "quiz_topic" not in st.session_state:
    st.session_state.quiz_topic = ""
if "answers" not in st.session_state:
    st.session_state.answers = {}

if "assignments" not in st.session_state:
    st.session_state.assignments = ""
if "assignment_topic" not in st.session_state:
    st.session_state.assignment_topic = ""

# 🎯 Progress Tracker (persistent)
if "progress" not in st.session_state:
    st.session_state.progress = load_progress()

# ------------------------------
# Streamlit UI
# ------------------------------
st.set_page_config(page_title="Korean Learning Chatbot", page_icon="🇰🇷", layout="wide")

st.sidebar.title("📚 Korean Learning Chatbot")
mode = st.sidebar.radio("Choose a mode:", [
    "🤖 Chatbot", "📖 Flashcards", "📝 Quizzes", "✍️ Assignments", "📊 Dashboard"
])

# ------------------------------
# Mode: Chatbot
# ------------------------------
if mode == "🤖 Chatbot":
    st.header(format_text("🤖 Chatbot"), unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        .stApp { background-color: white; }
        .flag-overlay {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background-image: url('https://upload.wikimedia.org/wikipedia/commons/0/09/Flag_of_South_Korea.svg');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            opacity: 0.5;
            z-index: -1;
        }
        .chat-container {
            max-height: 500px;
            overflow-y: auto;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 20px;
            background-color: rgba(255, 255, 255, 0.85);
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        </style>
        <div class="flag-overlay"></div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([8,1])
    with col1:
        user_input = st.text_input("💬 Type your message...", key="chat_box", label_visibility="collapsed")
    with col2:
        send = st.button("📩 Send")

    if send and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.chat_history]
        )
        bot_reply = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        st.rerun()

    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        render_message(msg["role"], msg["content"])
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------
# Mode: Flashcards
# ------------------------------
elif mode == "📖 Flashcards":
    st.header(format_text("📖 Flashcards"), unsafe_allow_html=True)
    topic = st.text_input("Enter a topic for flashcards:")

    if st.button("Generate Flashcards") and topic:
        st.session_state.flashcards = generate_flashcards(topic)
        st.session_state.flashcards_topic = topic

    if st.session_state.flashcards:
        st.markdown(f"### Flashcards on: {format_text(st.session_state.flashcards_topic)}", unsafe_allow_html=True)
        for i, card in enumerate(st.session_state.flashcards, 1):
            st.markdown(f"**Card {i}**", unsafe_allow_html=True)
            st.markdown(f"Front: {format_text(card['front'])}", unsafe_allow_html=True)
            st.markdown(f"Back: {format_text(card['back'])}", unsafe_allow_html=True)

# ------------------------------
# Mode: Quizzes
# ------------------------------
elif mode == "📝 Quizzes":
    st.header(format_text("📝 Quizzes"), unsafe_allow_html=True)
    topic = st.text_input("Enter a topic for quizzes:")

    if st.button("Generate Quiz") and topic:
        st.session_state.quizzes = generate_quiz(topic)
        st.session_state.quiz_topic = topic
        st.session_state.answers = {}

    if st.session_state.quizzes:
        st.markdown(f"### Quiz on: {format_text(st.session_state.quiz_topic)}", unsafe_allow_html=True)
        for i, q in enumerate(st.session_state.quizzes, 1):
            st.markdown(f"**Q{i}. {format_text(q['question'])}**", unsafe_allow_html=True)
            selected = st.radio(
                f"Choose an answer for Q{i}:",
                [format_text(opt) for opt in q["options"]],
                key=f"quiz_{i}"
            )
            st.session_state.answers[i] = re.sub(r"<.*?>", "", selected)

        if st.button("Check Answers"):
            correct_count = 0
            for i, q in enumerate(st.session_state.quizzes, 1):
                user_ans = st.session_state.answers.get(i, None)
                if user_ans == q["answer"]:
                    st.success(format_text(f"Q{i}: ✅ Correct!"))
                    correct_count += 1
                else:
                    st.error(format_text(f"Q{i}: ❌ Wrong! Correct: {q['answer']}"))

            st.session_state.progress["quizzes_taken"] += 1
            st.session_state.progress["correct_answers"] += correct_count
            st.session_state.progress["xp"] += correct_count * 10
            save_progress(st.session_state.progress)

# ------------------------------
# Mode: Assignments
# ------------------------------
elif mode == "✍️ Assignments":
    st.header(format_text("✍️ Assignments"), unsafe_allow_html=True)
    topic = st.text_input("Enter a topic for assignments:")

    if st.button("Generate Assignment") and topic:
        st.session_state.assignments = generate_assignment(topic)
        st.session_state.assignment_topic = topic
        st.session_state.progress["assignments_done"] += 1
        st.session_state.progress["xp"] += 20
        save_progress(st.session_state.progress)

    if st.session_state.assignments:
        st.markdown(f"### Assignments on: {format_text(st.session_state.assignment_topic)}", unsafe_allow_html=True)
        st.markdown(format_text(st.session_state.assignments), unsafe_allow_html=True)

# ------------------------------
# Mode: Dashboard
# ------------------------------
elif mode == "📊 Dashboard":
    st.header(format_text("📊 Dashboard"), unsafe_allow_html=True)

    xp = st.session_state.progress["xp"]
    level = xp // 100
    xp_progress = xp % 100

    st.subheader(format_text(f"🌟 Level {level} | {xp} XP"), unsafe_allow_html=True)
    st.progress(xp_progress / 100)

    st.markdown("### Stats", unsafe_allow_html=True)
    st.markdown(format_text(f"- 📝 Quizzes taken: {st.session_state.progress['quizzes_taken']}"), unsafe_allow_html=True)
    st.markdown(format_text(f"- ✅ Correct answers: {st.session_state.progress['correct_answers']}"), unsafe_allow_html=True)
    st.markdown(format_text(f"- ✍️ Assignments completed: {st.session_state.progress['assignments_done']}"), unsafe_allow_html=True)

    if st.button("Reset Progress"):
        st.session_state.progress = {"xp": 0, "quizzes_taken": 0, "correct_answers": 0, "assignments_done": 0}
        save_progress(st.session_state.progress)
        st.success("Progress has been reset!")

    st.subheader(format_text("🔥 XP Progress"), unsafe_allow_html=True)
    xp = st.session_state.progress.get("xp", 0)
    level = xp // 100
    progress_to_next = xp % 100
    st.markdown(format_text(f"Level {level} — {xp} XP total"), unsafe_allow_html=True)
    st.progress(progress_to_next / 100)

    st.subheader(format_text("📈 Stats Overview"), unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Quizzes Taken", st.session_state.progress.get("quizzes_taken", 0))
    col2.metric("Correct Answers", st.session_state.progress.get("correct_answers", 0))
    col3.metric("Assignments Done", st.session_state.progress.get("assignments_done", 0))

    import pandas as pd
    import matplotlib.pyplot as plt
    xp_history = pd.DataFrame({"XP": [10, 30, 60, xp], "Stage": ["Day 1", "Day 2", "Day 3", "Now"]})

    st.subheader(format_text("📊 XP Growth"), unsafe_allow_html=True)
    fig, ax = plt.subplots()
    ax.plot(xp_history["Stage"], xp_history["XP"], marker="o")
    ax.set_ylabel("XP")
    ax.set_xlabel("Progress")
    st.pyplot(fig)

    if st.session_state.quiz_topic:
        st.markdown(format_text(f"- Last quiz topic: {st.session_state.quiz_topic}"), unsafe_allow_html=True)
    if st.session_state.flashcards_topic:
        st.markdown(format_text(f"- Last flashcards topic: {st.session_state.flashcards_topic}"), unsafe_allow_html=True)
    if st.session_state.assignment_topic:
        st.markdown(format_text(f"- Last assignment topic: {st.session_state.assignment_topic}"), unsafe_allow_html=True)
