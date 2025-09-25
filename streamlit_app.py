import streamlit as st
import openai

# --- API KEY ---
from openai import OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Session State Initialization ---
if "progress" not in st.session_state:
    st.session_state.progress = {
        "xp": 0,
        "quizzes_taken": 0,
        "correct_answers": 0,
        "assignments_done": 0
    }

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "quizzes" not in st.session_state:
    st.session_state.quizzes = []

if "flashcards" not in st.session_state:
    st.session_state.flashcards = []

if "assignments" not in st.session_state:
    st.session_state.assignments = []

if "quiz_topic" not in st.session_state:
    st.session_state.quiz_topic = ""

if "flashcards_topic" not in st.session_state:
    st.session_state.flashcards_topic = ""

if "assignment_topic" not in st.session_state:
    st.session_state.assignment_topic = ""


# --- Helper Functions ---
def generate_quiz(topic):
    prompt = f"Create a 5-question multiple-choice quiz about {topic} in JSON with keys: question, options, answer."
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        quiz_json = response.choices[0].message.content
        import json
        return json.loads(quiz_json)
    except Exception as e:
        st.error(f"⚠️ Quiz generation failed: {e}")
        return []


def generate_flashcards(topic):
    prompt = f"Create 5 Korean flashcards about {topic}. Format: JSON with 'front' and 'back'."
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        cards_json = response.choices[0].message.content
        import json
        return json.loads(cards_json)
    except Exception as e:
        st.error(f"⚠️ Flashcard generation failed: {e}")
        return []


def generate_assignment(topic):
    prompt = f"Create a short Korean language assignment about {topic}. Return 3 tasks in JSON list."
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        assignment_json = response.choices[0].message.content
        import json
        return json.loads(assignment_json)
    except Exception as e:
        st.error(f"⚠️ Assignment generation failed: {e}")
        return []


# --- Streamlit Sidebar ---
st.sidebar.title("📚 Korean Learning App")
mode = st.sidebar.radio("Choose a mode:", [
    "🤖 Chatbot", "📖 Flashcards", "📚 Quizzes", "✍️ Assignments", "📊 Dashboard"
])


# --- Modes ---
if mode == "🤖 Chatbot":
    st.header("🤖 Chat with AI")
    user_input = st.text_input("Ask something in Korean or about Korean:")
    if st.button("Send") and user_input:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_input}]
        )
        st.write("**Bot:**", response["choices"][0]["message"]["content"])

elif mode == "📖 Flashcards":
    st.header("📖 Flashcards")
    topic = st.text_input("Enter a topic for flashcards:")
    if st.button("Generate Flashcards") and topic:
        st.session_state.flashcards = generate_flashcards(topic)
        st.session_state.flashcards_topic = topic

    if st.session_state.flashcards:
        for i, card in enumerate(st.session_state.flashcards, 1):
            with st.expander(f"Card {i}: {card['front']}"):
                st.write(card["back"])

elif mode == "📚 Quizzes":
    st.header("📚 Quizzes")

    topic = st.text_input("Enter a topic for the quiz:")
    if st.button("Generate Quiz") and topic:
        st.session_state.quizzes = generate_quiz(topic)
        st.session_state.answers = {}
        st.session_state.quiz_topic = topic

    if "quizzes" in st.session_state and st.session_state.quizzes:
        st.write("### Your Quiz")
        for i, q in enumerate(st.session_state.quizzes, 1):
            st.write(f"**Q{i}: {q['question']}**")
            st.radio(
                "Select answer",
                q["options"],
                key=f"quiz_{i}",
                on_change=lambda i=i: st.session_state.answers.update(
                    {i: st.session_state[f"quiz_{i}"]}
                )
            )

        if st.button("Check Answers"):
            correct_count = 0
            for i, q in enumerate(st.session_state.quizzes, 1):
                user_ans = st.session_state.answers.get(i, None)
                if user_ans == q["answer"]:
                    st.success(f"Q{i}: ✅ Correct!")
                    correct_count += 1
                else:
                    st.error(f"Q{i}: ❌ Wrong! Correct: {q['answer']}")

            # Update progress
            st.session_state.progress["quizzes_taken"] += 1
            st.session_state.progress["correct_answers"] += correct_count
            st.session_state.progress["xp"] += correct_count * 10  # 10 XP each correct

elif mode == "✍️ Assignments":
    st.header("✍️ Assignments")

    topic = st.text_input("Enter a topic for assignment:")
    if st.button("Generate Assignment") and topic:
        st.session_state.assignments = generate_assignment(topic)
        st.session_state.assignment_topic = topic

        # Update progress
        st.session_state.progress["assignments_done"] += 1
        st.session_state.progress["xp"] += 20  # XP for doing assignment

    if st.session_state.assignments:
        st.write("### Your Assignment")
        for i, task in enumerate(st.session_state.assignments, 1):
            st.write(f"**Task {i}:** {task}")

elif mode == "📊 Dashboard":
    st.header("📊 Dashboard")

    xp = st.session_state.progress["xp"]
    level = xp // 100
    xp_progress = xp % 100

    st.subheader(f"🌟 Level {level}  |  {xp} XP")
    st.progress(xp_progress / 100)

    st.write("### Stats")
    st.write(f"- 📝 Quizzes taken: {st.session_state.progress['quizzes_taken']}")
    st.write(f"- ✅ Correct answers: {st.session_state.progress['correct_answers']}")
    st.write(f"- ✍️ Assignments completed: {st.session_state.progress['assignments_done']}")

    if st.session_state.quiz_topic:
        st.write(f"- Last quiz topic: {st.session_state.quiz_topic}")
    if st.session_state.flashcards_topic:
        st.write(f"- Last flashcards topic: {st.session_state.flashcards_topic}")
    if st.session_state.assignment_topic:
        st.write(f"- Last assignment topic: {st.session_state.assignment_topic}")
