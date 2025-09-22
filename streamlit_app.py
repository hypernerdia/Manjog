import streamlit as st
import json, time
import matplotlib.pyplot as plt
from openai import OpenAI
from db import (
    init_db, add_flashcards, get_due_cards, update_card, get_flashcard_stats,
    save_quiz_result, get_quiz_accuracy,
    add_assignment, get_assignment_history,
    log_activity, get_streaks,
    add_xp, get_xp
)

# ---------------- INIT ----------------
st.set_page_config(page_title="Korean Learning Bot 🇰🇷", layout="wide")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
init_db()

# ---------------- SIDEBAR ----------------
st.sidebar.title("🇰🇷 Korean Learning Bot")
mode = st.sidebar.selectbox(
    "Choose Mode:",
    ["☁️ Chatbot", "📖 Flashcards", "📝 Quizzes", "✍️ Assignments", "📊 Dashboard"]
)

# ---------------- CHATBOT ----------------
if mode == "☁️ Chatbot":
    st.subheader("☁️ Practice Korean with AI")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Say something in Korean (or English):")
    if st.button("Send"):
        if user_input:
            st.session_state.chat_history.append(("You", user_input))
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role":"system","content":"You are a helpful Korean teacher. Correct mistakes and encourage learning."},
                    {"role":"user","content":user_input}
                ]
            )
            bot_reply = response.choices[0].message.content
            st.session_state.chat_history.append(("Bot", bot_reply))
            log_activity()
            add_xp(5)

    for role, msg in st.session_state.chat_history:
        if role == "You":
            st.write(f"🧑 **You:** {msg}")
        else:
            st.write(f"☁️ **ManjogBot:** {msg}")

# ---------------- FLASHCARDS ----------------
elif mode == "📖 Flashcards":
    st.subheader("📖 Flashcards with Spaced Repetition")
    topic = st.text_input("Enter a topic (e.g., food, travel, verbs):")

    if st.button("Generate Flashcards"):
        flash_prompt = f"""
        Create 5 Korean flashcards about {topic}.
        Return them in JSON like this:
        [
          {{"korean":"가다","english":"to go","example":"저는 학교에 가요."}},
          {{"korean":"먹다","english":"to eat","example":"나는 밥을 먹어요."}}
        ]
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are a Korean teacher. Return ONLY valid JSON."},
                {"role":"user","content":flash_prompt}
            ]
        )
        try:
            cards = json.loads(response.choices[0].message.content)
            add_flashcards(topic, cards)
            st.success("✅ Flashcards saved! Refresh to review.")
            log_activity()
            add_xp(20)
        except:
            st.error("⚠️ Could not parse flashcards. Try again.")

    due_cards = get_due_cards()
    if due_cards:
        card = due_cards[0]
        card_id, korean, english, example, interval, next_review = card
        st.write(f"**Front (Korean):** {korean}")

        if st.button("Show Answer", key=f"show{card_id}"):
            st.info(f"**English:** {english}")
            st.write(f"**Example:** {example}")

            st.write("👉 How well did you know this?")
            col1, col2, col3 = st.columns(3)

            def update(difficulty):
                now = time.time()
                if difficulty == "easy":
                    new_interval = interval * 2
                elif difficulty == "hard":
                    new_interval = max(1, interval // 2)
                else:
                    new_interval = 1
                new_review = now + new_interval * 60
                update_card(card_id, new_interval, new_review)
                log_activity()
                add_xp(5)
                st.experimental_rerun()

            with col1:
                if st.button("❌ Again"):
                    update("again")
            with col2:
                if st.button("🤔 Hard"):
                    update("hard")
            with col3:
                if st.button("✅ Easy"):
                    update("easy")
    else:
        st.success("🎉 No cards due now! Come back later.")

# ---------------- QUIZZES ----------------
elif mode == "📝 Quizzes":
    st.subheader("📝 Korean Quizzes")
    topic = st.text_input("Enter a topic for the quiz:")

    if st.button("Start Quiz"):
        quiz_prompt = f"""
        Create a Korean multiple-choice quiz about {topic}.
        Return JSON:
        [
          {{
            "question": "What does '학교' mean?",
            "options": ["School","Teacher","Book","Friend"],
            "answer": "School"
          }}
        ]
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are a Korean teacher. Return ONLY JSON."},
                {"role":"user","content":quiz_prompt}
            ]
        )
        try:
            quiz = json.loads(response.choices[0].message.content)
            q = quiz[0]
            st.write(f"**Q:** {q['question']}")
            choice = st.radio("Choose one:", q["options"])
            if st.button("Submit Answer"):
                correct = choice == q["answer"]
                if correct:
                    st.success("✅ Correct!")
                    add_xp(10)
                else:
                    st.error(f"❌ Wrong. Correct answer: {q['answer']}")
                save_quiz_result(topic, q["question"], q["options"], q["answer"], choice, correct)
                log_activity()
        except:
            st.error("⚠️ Could not parse quiz. Try again.")

# ---------------- ASSIGNMENTS ----------------
elif mode == "✍️ Assignments":
    st.subheader("✍️ Korean Writing Assignments")
    topic = st.text_input("Enter a topic (e.g., hobbies, travel, school):")

    if st.button("Get Assignment"):
        assign_prompt = f"Create a short Korean writing assignment about {topic}."
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":assign_prompt}]
        )
        task = response.choices[0].message.content
        st.session_state["task"] = task
        st.write(f"**Assignment:** {task}")

    if "task" in st.session_state:
        user_response = st.text_area("Write your answer in Korean:")
        if st.button("Submit Assignment"):
            feedback_prompt = f"Student wrote: {user_response}\n\nGive constructive feedback in English + corrections."
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":feedback_prompt}]
            )
            feedback = response.choices[0].message.content
            add_assignment(topic, st.session_state["task"], user_response, feedback)
            st.success("✅ Feedback received:")
            st.write(feedback)
            log_activity()
            add_xp(20)

# ---------------- DASHBOARD ----------------
elif mode == "📊 Dashboard":
    st.subheader("📊 Your Learning Progress")

    # --- XP & Levels ---
    st.write("### 🏆 XP & Levels")
    points, level, xp_into_level = get_xp()
    st.write(f"- Total XP: **{points}**")
    st.write(f"- Level: **{level}**")
    st.progress(xp_into_level / 100)

    # --- Streaks ---
    st.write("### 🔥 Study Streak")
    current, longest = get_streaks()
    st.write(f"- Current streak: **{current} days**")
    st.write(f"- Longest streak: **{longest} days**")
    if current > 0:
        st.success(f"🔥 You're on a {current}-day streak!")
    else:
        st.warning("⚠️ No study today yet. Do one activity to start your streak.")

    # --- Flashcards Stats ---
    st.write("### 📖 Flashcards")
    total, due, interval_data = get_flashcard_stats()
    st.write(f"- Total cards: {total}")
    st.write(f"- Due now: {due}")
    if interval_data:
        labels = [str(iv[0]) for iv in interval_data]
        counts = [iv[1] for iv in interval_data]
        fig, ax = plt.subplots()
        ax.bar(labels, counts)
        ax.set_xlabel("Interval (minutes, demo)")
        ax.set_ylabel("Number of Cards")
        ax.set_title("Flashcards by Interval")
        st.pyplot(fig)

    # --- Quiz Stats ---
    st.write("### 📝 Quizzes")
    total, correct = get_quiz_accuracy()
    if total > 0:
        accuracy = (correct / total) * 100
        st.write(f"- Total questions answered: {total}")
        st.write(f"- Correct: {correct}")
        st.write(f"- Accuracy: {accuracy:.2f}%")
        fig, ax = plt.subplots()
        ax.bar(["Correct","Wrong"], [correct, total-correct], color=["green","red"])
        st.pyplot(fig)
    else:
        st.info("No quizzes taken yet.")

    # --- Assignment History ---
    st.write("### ✍️ Assignments")
    assignments = get_assignment_history()
    if assignments:
        st.write(f"- Total assignments submitted: {len(assignments)}")
        for a in assignments[:5]:
            t, task, resp, fb, ts = a
            st.write(f"- **{t}** | Task: {task}")
            st.write(f"  → Your Answer: {resp}")
            st.write(f"  → Feedback: {fb}")
            st.write("---")
    else:
        st.info("No assignments submitted yet.")
