import streamlit as st
import json
import re
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ------------------------------
# Helper functions
# ------------------------------

def generate_flashcards(topic):
    """Generate flashcards in JSON format"""
    prompt = f"""
    Create 3 Korean flashcards about "{topic}".
    Respond ONLY with valid JSON, nothing else.
    Format:
    [
      {{
        "front": "학교",
        "back": "School"
      }}
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
        cards = json.loads(raw)
        return cards
    except Exception as e:
        st.error(f"⚠️ Flashcard generation failed: {e}")
        return [{"front": "학교", "back": "School"}]


def generate_quiz(topic):
    """Generate quizzes in JSON format"""
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
        quizzes = json.loads(raw)
        return quizzes
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
    """Generate assignment tasks"""
    prompt = f"""
    Create 2 Korean learning assignments about "{topic}".
    Keep them short and clear. Respond as plain text.
    """
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
    if user_input:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful Korean learning assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        st.success(response.choices[0].message.content)

# ------------------------------
# Mode: Flashcards
# ------------------------------
elif mode == "📖 Flashcards":
    st.header("📖 Flashcards")
    topic = st.text_input("Enter a topic for flashcards:")
    if st.button("Generate Flashcards") and topic:
        cards = generate_flashcards(topic)
        for i, card in enumerate(cards, 1):
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
        quizzes = generate_quiz(topic)
        for i, q in enumerate(quizzes, 1):
            st.write(f"**Q{i}. {q['question']}**")
            choice = st.radio("Choose an answer:", q["options"], key=f"quiz_{i}")
            if st.button(f"Check Answer {i}"):
                if choice == q["answer"]:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Wrong! Correct answer: {q['answer']}")

# ------------------------------
# Mode: Assignments
# ------------------------------
elif mode == "✍️ Assignments":
    st.header("✍️ Assignments")
    topic = st.text_input("Enter a topic for assignments:")
    if st.button("Generate Assignment") and topic:
        tasks = generate_assignment(topic)
        st.write("### Your Assignments:")
        st.info(tasks)

# ------------------------------
# Mode: Dashboard
# ------------------------------
elif mode == "📊 Dashboard":
    st.header("📊 Dashboard")
    st.write("📈 Learning progress will be displayed here (to be implemented).")
