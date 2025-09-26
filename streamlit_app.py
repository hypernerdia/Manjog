import streamlit as st
import json
import re
import os
from openai import OpenAI

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

def generate_image(prompt):
    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="512x512"
        )
        return response.data[0].url
    except Exception as e:
        st.error(f"⚠️ Image generation failed: {e}")
        return None

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
    user_input = st.text_input("Ask something in Korean or English:")

    if st.button("Send") and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.chat_history]
        )
        bot_reply = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

    # Show conversation
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.write(f"🧑: {msg['content']}")
        else:
            st.success(f"🤖: {msg['content']}")

# ------------------------------
# Mode: Flashcards
# ------------------------------
elif mode == "📖 Flashcards":
    st.header("📖 Flashcards")
    topic = st.text_input("Enter a topic for flashcards:")

    if st.button("Generate Flashcards") and topic:
        st.session_state.flashcards = generate_flashcards(topic)
        st.session_state.flashcards_topic = topic

        # Reset flip states when generating new flashcards
        for i in range(len(st.session_state.flashcards)):
            st.session_state[f"flip_{i}"] = False

    if st.session_state.flashcards:
        st.write(f"### Flashcards on: {st.session_state.flashcards_topic}")
        for i, card in enumerate(st.session_state.flashcards, 1):
            st.write(f"**Card {i}**")

            # Ensure each card has a flip state
            if f"flip_{i}" not in st.session_state:
                st.session_state[f"flip_{i}"] = False

            if not st.session_state[f"flip_{i}"]:
                # Front: AI image with Korean text
                img_url = generate_image(
                    f"An educational illustration of {card['front']} with the Korean word '{card['front']}' written on the picture"
                )
                if img_url:
                    st.image(img_url, caption=f"Front (Korean: {card['front']})")
            else:
                # Back: English meaning
                st.success(f"Back: {card['back']}")

                # Download flashcard as PNG with Korean + English
                img_url = generate_image(
                    f"An educational illustration of {card['front']} with the Korean word '{card['front']}' written on the picture"
                )
                buffer = create_flashcard_image(card['front'], card['back'], img_url)
                if buffer:
                    st.download_button(
                        label=f"📥 Download Flashcard {i}",
                        data=buffer,
                        file_name=f"flashcard_{i}.png",
                        mime="image/png"
                    )

            # Flip button
            if st.button(f"Flip Card {i}", key=f"btn_{i}"):
                st.session_state[f"flip_{i}"] = not st.session_state[f"flip_{i}"]

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

    if st.session_state.quiz_topic:
        st.write(f"- Last quiz topic: {st.session_state.quiz_topic}")
    if st.session_state.flashcards_topic:
        st.write(f"- Last flashcards topic: {st.session_state.flashcards_topic}")
    if st.session_state.assignment_topic:
        st.write(f"- Last assignment topic: {st.session_state.assignment_topic}")
