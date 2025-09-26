import streamlit as st
import json
import re
import os
from openai import OpenAI

# ------------------------------
# Helper: render chat messages
# ------------------------------
def render_message(role, content):
    if role == "user":
        st.markdown(
            f"""
            <div style="display:flex; justify-content:flex-end; margin:5px 0;">
                <div style="
                    background-color:#DCF8C6;
                    padding:10px 15px;
                    border-radius:15px;
                    max-width:70%;
                    text-align:right;
                    box-shadow: 0px 2px 4px rgba(0,0,0,0.1);">
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
                    background-color:#E6E6FA;
                    padding:10px 15px;
                    border-radius:15px;
                    max-width:70%;
                    text-align:left;
                    box-shadow: 0px 2px 4px rgba(0,0,0,0.1);">
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
    st.header("🤖 Chatbot")

    # 🎨 Korean flag background + brighter overlay + bubbles
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url('https://upload.wikimedia.org/wikipedia/commons/0/09/Flag_of_South_Korea.svg');
            background-size: contain;       /* Keep flag proportions */
            background-repeat: no-repeat;   /* No tiling */
            background-position: center;    /* Flag centered */
            background-color: white;        /* White base */
        }
        .overlay {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background-color: rgba(255, 255, 255, 0.6); /* Bright transparent layer */
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
        .user-bubble {
            background-color: #ff4c4c; /* Red */
            color: white;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 70%;
            margin-left: auto;
            margin-bottom: 10px;
            text-align: right;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
        }
        .bot-bubble {
            background-color: #4682B4; /* Blue */
            color: white;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 70%;
            margin-right: auto;
            margin-bottom: 10px;
            text-align: left;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
        }
        </style>
        <div class="overlay"></div>
        """,
        unsafe_allow_html=True
    )

    # --- Chat input box ---
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

    # --- Scrollable chat container ---
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
        
# ------------------------------
# Mode: Flashcards
# ------------------------------
elif mode == "📖 Flashcards":
    st.header("📖 Flashcards")
    topic = st.text_input("Enter a topic for flashcards:")

    if st.button("Generate Flashcards") and topic:
        st.session_state.flashcards = generate_flashcards(topic)
        st.session_state.flashcards_topic = topic

    if st.session_state.flashcards:
        st.write(f"### Flashcards on: {st.session_state.flashcards_topic}")
        for i, card in enumerate(st.session_state.flashcards, 1):
            st.write(f"**Card {i}**")
            st.info(f"Front: {card['front']}")
            st.success(f"Back: {card['back']}")
            
# ------------------------------
# Mode: Quizzes
# ------------------------------
elif mode == "📝 Quizzes":
    st.header("📝 Quizzes")
    topic = st.text_input("Enter a topic for quizzes:")

    if st.button("Generate Quiz") and topic:
        st.session_state.quizzes = generate_quiz(topic)
        st.session_state.quiz_topic = topic
        st.session_state.answers = {}

    if st.session_state.quizzes:
        st.write(f"### Quiz on: {st.session_state.quiz_topic}")
        for i, q in enumerate(st.session_state.quizzes, 1):
            st.write(f"**Q{i}. {q['question']}**")

            selected = st.radio(
                f"Choose an answer for Q{i}:",
                q["options"],
                key=f"quiz_{i}"
            )
            st.session_state.answers[i] = selected

        if st.button("Check Answers"):
            correct_count = 0
            for i, q in enumerate(st.session_state.quizzes, 1):
                user_ans = st.session_state.answers.get(i, None)
                if user_ans == q["answer"]:
                    st.success(f"Q{i}: ✅ Correct!")
                    correct_count += 1
                else:
                    st.error(f"Q{i}: ❌ Wrong! Correct: {q['answer']}")

            # 🎯 Update progress
            st.session_state.progress["quizzes_taken"] += 1
            st.session_state.progress["correct_answers"] += correct_count
            st.session_state.progress["xp"] += correct_count * 10
            save_progress(st.session_state.progress)

# ------------------------------
# Mode: Assignments
# ------------------------------
elif mode == "✍️ Assignments":
    st.header("✍️ Assignments")
    topic = st.text_input("Enter a topic for assignments:")

    if st.button("Generate Assignment") and topic:
        st.session_state.assignments = generate_assignment(topic)
        st.session_state.assignment_topic = topic

        # 🎯 Update progress
        st.session_state.progress["assignments_done"] += 1
        st.session_state.progress["xp"] += 20
        save_progress(st.session_state.progress)

    if st.session_state.assignments:
        st.write(f"### Assignments on: {st.session_state.assignment_topic}")
        st.info(st.session_state.assignments)

# ------------------------------
# Mode: Dashboard
# ------------------------------
elif mode == "📊 Dashboard":
    st.header("📊 Dashboard")

    xp = st.session_state.progress["xp"]
    level = xp // 100
    xp_progress = xp % 100

    st.subheader(f"🌟 Level {level} | {xp} XP")
    st.progress(xp_progress / 100)

    st.write("### Stats")
    st.write(f"- 📝 Quizzes taken: {st.session_state.progress['quizzes_taken']}")
    st.write(f"- ✅ Correct answers: {st.session_state.progress['correct_answers']}")
    st.write(f"- ✍️ Assignments completed: {st.session_state.progress['assignments_done']}")

        # 🔄 Reset progress button
    if st.button("Reset Progress"):
        st.session_state.progress = {
            "xp": 0,
            "quizzes_taken": 0,
            "correct_answers": 0,
            "assignments_done": 0
        }
        save_progress(st.session_state.progress)
        st.success("Progress has been reset!")

        # XP Progress Bar (assuming 100 XP = 1 level for example)
    st.subheader("🔥 XP Progress")
    xp = st.session_state.progress.get("xp", 0)
    level = xp // 100
    progress_to_next = xp % 100
    st.write(f"Level {level} — {xp} XP total")
    st.progress(progress_to_next / 100)

    # Key Metrics
    st.subheader("📈 Stats Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Quizzes Taken", st.session_state.progress.get("quizzes_taken", 0))
    col2.metric("Correct Answers", st.session_state.progress.get("correct_answers", 0))
    col3.metric("Assignments Done", st.session_state.progress.get("assignments_done", 0))

    # Simple Chart (XP Growth over time)
    import pandas as pd
    import matplotlib.pyplot as plt

    xp_history = pd.DataFrame({
        "XP": [10, 30, 60, xp],  # you can log these dynamically later
        "Stage": ["Day 1", "Day 2", "Day 3", "Now"]
    })

    st.subheader("📊 XP Growth")
    fig, ax = plt.subplots()
    ax.plot(xp_history["Stage"], xp_history["XP"], marker="o")
    ax.set_ylabel("XP")
    ax.set_xlabel("Progress")
    st.pyplot(fig)

    if st.session_state.quiz_topic:
        st.write(f"- Last quiz topic: {st.session_state.quiz_topic}")
    if st.session_state.flashcards_topic:
        st.write(f"- Last flashcards topic: {st.session_state.flashcards_topic}")
    if st.session_state.assignment_topic:
        st.write(f"- Last assignment topic: {st.session_state.assignment_topic}")
