import streamlit as st
import json
import matplotlib.pyplot as plt
from openai import OpenAI
from db import (
    init_db, add_flashcards, get_due_cards, update_card, get_flashcard_stats,
    save_quiz_result, get_quiz_accuracy,
    add_assignment, get_assignment_history,
    log_activity, get_streaks,
    add_xp, get_xp
)

# ---------------- SETUP ----------------
st.set_page_config(page_title="🇰🇷 Korean Learning Bot", layout="wide")
init_db()

# OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🇰🇷 Korean Learning Bot")

# Sidebar menu
mode = st.sidebar.radio("Choose a mode:", [
    "🤖 Chatbot",
    "📖 Flashcards",
    "📝 Quizzes",
    "✍️ Assignments",
    "📊 Dashboard"
])

# ---------------- CHATBOT ----------------
if mode == "🤖 Chatbot":
    st.subheader("Practice Korean with the AI Tutor")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for role, msg in st.session_state.chat_history:
        st.chat_message(role).markdown(msg)

    if prompt := st.chat_input("Write in Korean or English..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.chat_history.append(("user", prompt))

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful Korean tutor."},
                    *[{"role": role, "content": msg} for role, msg in st.session_state.chat_history]
                ]
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"⚠️ Error: {e}"

        st.chat_message("assistant").markdown(reply)
        st.session_state.chat_history.append(("assistant", reply))

        log_activity()
        add_xp(5)

# ---------------- FLASHCARDS ----------------
elif mode == "📖 Flashcards":
    st.subheader("Spaced Repetition Flashcards")

    topic = st.text_input("Enter a topic (e.g., Food, Travel, Verbs)")
    if st.button("Generate Flashcards"):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Create Korean flashcards as JSON."},
                    {"role": "user", "content": f"Generate 5 flashcards for topic '{topic}' in JSON: "
                                                "[{{'korean':'...', 'english':'...', 'example':'...'}}]"}
                ]
            )
            raw = response.choices[0].message.content
            cards = json.loads(raw)
            add_flashcards(topic, cards)
            st.success("✅ Flashcards added!")
        except Exception as e:
            st.error(f"⚠️ Could not generate flashcards: {e}")

    st.markdown("### Review Due Flashcards")
    cards = get_due_cards()
    for card in cards:
        card_id, korean, english, example, interval, _ = card
        st.write(f"**{korean}** — {example}")
        if st.button("Show Answer", key=f"ans_{card_id}"):
            st.info(f"👉 {english}")

        col1, col2 = st.columns(2)
        if col1.button("✅ I knew it", key=f"yes_{card_id}"):
            update_card(card_id, interval * 2, st.session_state.get("time", 0) + interval * 86400)
            add_xp(10)
        if col2.button("❌ I forgot", key=f"no_{card_id}"):
            update_card(card_id, 1, st.session_state.get("time", 0) + 86400)

# ---------------- QUIZZES ---------------
import re

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

        # Extract JSON only (removes text before/after)
        match = re.search(r"\[.*\]", raw, re.S)
        if match:
            raw = match.group(0)

        quizzes = json.loads(raw)
        return quizzes

    except Exception as e:
        st.error(f"⚠️ Quiz generation failed: {e}")
        return [
            {"question": "What does '학교' mean?",
             "options": ["School", "Book", "Friend", "Teacher"],
             "answer": "School"}
        ]

# ---------------- ASSIGNMENTS ----------------
elif mode == "✍️ Assignments":
    st.subheader("Assignments")

    topic = st.text_input("Assignment topic")
    task = st.text_area("Enter your writing prompt (e.g., 'Write 3 sentences about your family.')")

    if st.button("Get Feedback"):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a Korean teacher. Give constructive feedback."},
                    {"role": "user", "content": task}
                ]
            )
            feedback = response.choices[0].message.content
            st.info(feedback)
            add_assignment(topic, task, task, feedback)
            add_xp(20)
        except Exception as e:
            st.error(f"⚠️ Could not get feedback: {e}")

    st.markdown("### Assignment History")
    for row in get_assignment_history():
        t, q, resp, fb, ts = row
        st.write(f"**{t}** — {q}")
        st.write(f"✍️ Your response: {resp}")
        st.write(f"📌 Feedback: {fb}")
        st.markdown("---")

# ---------------- DASHBOARD ----------------
elif mode == "📊 Dashboard":
    st.subheader("Your Progress Dashboard")

    total, due, interval_data = get_flashcard_stats()
    st.metric("📖 Total Flashcards", total)
    st.metric("⏰ Due for Review", due)

    total_q, correct_q = get_quiz_accuracy()
    st.metric("📝 Quizzes Taken", total_q)
    st.metric("✅ Correct Answers", correct_q)

    current_streak, longest_streak = get_streaks()
    st.metric("🔥 Current Streak", current_streak)
    st.metric("🏆 Longest Streak", longest_streak)

    points, level, xp_into_level = get_xp()
    st.metric("⭐ XP Points", points)
    st.metric("🎯 Level", level)

    st.markdown("### Flashcard Progress")
    if interval_data:
        labels = [f"Interval {iv}" for iv, _ in interval_data]
        values = [count for _, count in interval_data]
        fig, ax = plt.subplots()
        ax.bar(labels, values)
        st.pyplot(fig)
