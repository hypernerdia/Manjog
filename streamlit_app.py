import streamlit as st
import json
import re
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# ------------------------------
# Load A.X 4.0 model & tokenizer
# ------------------------------
@st.cache_resource
def load_ax_model():
    model_name = "skt/A.X-4.0"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )
    return tokenizer, model

tokenizer, ax_model = load_ax_model()

def ax_chat_completion(messages, max_new_tokens=300):
    prompt = ""
    for m in messages:
        if m["role"] == "system":
            prompt += f"System: {m['content']}\n"
        elif m["role"] == "user":
            prompt += f"User: {m['content']}\n"
        elif m["role"] == "assistant":
            prompt += f"Assistant: {m['content']}\n"
    prompt += "Assistant:"

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True).to(ax_model.device)
    with torch.no_grad():
        outputs = ax_model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.8,
            top_p=0.9
        )
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract assistant’s reply
    response_text = result.split("Assistant:")[-1].strip()
    return response_text

# ------------------------------
# Global Fonts & Background
# ------------------------------
st.markdown(
    """
    <style>
    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Calligraffitti&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo&display=swap');

    /* Apply English font (Calligraffitti) and Korean font (Nanum Myeongjo) */
    html, body, [class*="css"]  {
        font-family: 'Calligraffitti', 'Nanum Myeongjo', sans-serif;
    }

    /* Force Korean characters to use Nanum Myeongjo */
    body, div, p, span, input, textarea {
        font-family: 'Calligraffitti', sans-serif;
    }
    :lang(ko), .korean-text {
        font-family: 'Nanum Myeongjo', serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    /* Set background for the whole app */
    .stApp {
        background-color: #E6ECF8; /* Light navy blue */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------
# Helper: Font Formatting
# ------------------------------
def format_text(text):
    """Detect Korean vs English and wrap in appropriate font spans."""
    if re.search(r"[\u3131-\uD79D]", text):  # Korean range
        return f"<span style='font-family: Nanum Myeongjo;'>{text}</span>"
    else:
        return f"<span style='font-family: Calligraffitti;'>{text}</span>"

st.markdown(
    """
    <style>
    /* Sidebar radio button styling */
    .stRadio div[role="radiogroup"] label {
        display: block;
        background-color: #ffcccc; /* light red */
        color: black;
        padding: 10px 15px;
        margin-bottom: 10px;
        border-radius: 10px; /* rounded corners */
        cursor: pointer;
        border: 2px solid transparent; /* default border */
        font-family: 'Calligraffitti', sans-serif;
    }

    /* Selected option */
    .stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
        border: 2px solid #003366; /* dark blue border */
    }

    /* Hover effect */
    .stRadio div[role="radiogroup"] label:hover {
        background-color: #ffb3b3;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
        raw = ax_chat_completion([
            {"role": "system", "content": "You are a JSON-only flashcard generator."},
            {"role": "user", "content": prompt}
        ])
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
        raw = ax_chat_completion([
            {"role": "system", "content": "You are a JSON-only quiz generator."},
            {"role": "user", "content": prompt}
        ])
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
        raw = ax_chat_completion([
            {"role": "user", "content": prompt}
        ])
        return raw
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
    "🤖 Chatbot", "📖 Flashcards", "📝 Quizzes", "✍️ Assignments", "💖 Wellness", "📊 Dashboard"
])

# ------------------------------
# Mode: Chatbot
# ------------------------------
if mode == "🤖 Chatbot":
    st.markdown(f"<h2>{format_text('🤖 Chatbot')}</h2>", unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        .stApp { background-color: white; }
        .flag-overlay {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background-image: url('https://lh3.googleusercontent.com/gg-dl/AJfQ9KTdPmW50RZdroUTFHXooYhr5VKSMioWsOO7VrMQb4O6yeYvBsoEVl2ZI0OFv21WIwyH40qiMfT0UfLm6oDNHcKBE2E_vof-P39PurGiwApoik9LLaSfs0Xf2Rg_fOxesDVfl7ojyRVuyo3V6-oBleTGW_6lsut4iP3Qp09NA6sYD0unBg=s1024');
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
        .user-bubble {
            background-color: #ff4c4c;
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
            background-color: #4682B4;
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
        raw = ax_chat_completion(
            [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.chat_history]
        )
        bot_reply = raw.strip()
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        st.rerun()

    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div class='user-bubble'>{format_text(msg['content'])}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-bubble'>{format_text(msg['content'])}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------
# Mode: Flashcards (fixed visual + flipping)
# ------------------------------
elif mode == "📖 Flashcards":
    st.markdown(f"<h2>{format_text('📖 Flashcards')}</h2>", unsafe_allow_html=True)

    topic = st.text_input("Enter a topic for flashcards:")

    if st.button("Generate Flashcards") and topic:
        st.session_state.flashcards = generate_flashcards(topic)
        st.session_state.flashcards_topic = topic

    if st.session_state.flashcards:
        st.markdown(
            f"### {format_text('Flashcards on: ' + st.session_state.flashcards_topic)}",
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <style>
            .flashcards-grid {
                display: flex;
                flex-wrap: wrap;
                gap: 16px;
                align-items: flex-start;
            }
            .card {
                display: inline-block;
                perspective: 1000px;
                cursor: pointer;
                -webkit-tap-highlight-color: transparent;
            }
            .card input[type="checkbox"] {
                position: absolute;
                opacity: 0;
                pointer-events: none;
                height: 0; width: 0;
            }
            .card-inner {
                width: 260px;
                height: 150px;
                position: relative;
                transform-style: preserve-3d;
                transition: transform 0.6s cubic-bezier(.2,.8,.2,1);
                border-radius: 12px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.12);
                user-select: none;
            }
            .card input[type="checkbox"]:checked + .card-inner {
                transform: rotateY(180deg);
            }
            .card-face {
                position: absolute;
                inset: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                -webkit-backface-visibility: hidden;
                backface-visibility: hidden;
                border-radius: 12px;
                color: #ffffff;
                font-size: 28px;
                font-weight: 700;
                padding: 12px;
                text-align: center;
                word-break: break-word;
            }
            .card-front {
                background: #173a69;
            }
            .card-back {
                background: #8B0000;
                transform: rotateY(180deg);
            }
            @media (max-width: 600px) {
                .card-inner { width: 90vw; height: 140px; }
                .card-face { font-size: 22px; }
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown('<div class="flashcards-grid">', unsafe_allow_html=True)
        for i, card in enumerate(st.session_state.flashcards, 1):
            front_html = format_text(card.get("front", ""))
            back_html = format_text(card.get("back", ""))
            card_html = f"""
                <label class="card">
                    <input type="checkbox" />
                    <div class="card-inner">
                        <div class="card-face card-front">{front_html}</div>
                        <div class="card-face card-back">{back_html}</div>
                    </div>
                </label>
            """
            st.markdown(card_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------
# Mode: Quizzes
# ------------------------------
elif mode == "📝 Quizzes":
    st.markdown(f"<h2>{format_text('📚 Quizzes')}</h2>", unsafe_allow_html=True)
    st.markdown(format_text("Enter a topic for quizzes:"), unsafe_allow_html=True)
    topic = st.text_input("", key="quiz_topic")

    if st.button("Generate Quiz") and topic:
        st.session_state.quizzes = generate_quiz(topic)
        st.session_state.answers = {}

    if st.session_state.quizzes:
        st.write(f"### Quiz on: {st.session_state['quiz_topic']}")
        for i, q in enumerate(st.session_state.quizzes, 1):
            st.write(f"**Q{i}. {q['question']}**")
            selected = st.radio(f"Choose an answer for Q{i}:", q["options"], key=f"quiz_{i}")
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
            st.session_state.progress["quizzes_taken"] += 1
            st.session_state.progress["correct_answers"] += correct_count
            st.session_state.progress["xp"] += correct_count * 10
            save_progress(st.session_state.progress)

# ------------------------------
# Mode: Assignments
# ------------------------------
elif mode == "✍️ Assignments":
    st.markdown(f"<h2>{format_text('✍️ Assignments')}</h2>", unsafe_allow_html=True)
    topic = st.text_input("Enter a topic for assignments:")
    if st.button("Generate Assignment") and topic:
        st.session_state.assignments = generate_assignment(topic)
        st.session_state.assignment_topic = topic
        st.session_state.progress["assignments_done"] += 1
        st.session_state.progress["xp"] += 20
        save_progress(st.session_state.progress)
    if st.session_state.assignments:
        st.write(f"### Assignments on: {st.session_state.assignment_topic}")
        st.info(st.session_state.assignments)

# ------------------------------
# Mode: Wellness
# ------------------------------
elif mode == "💖 Wellness":
    st.markdown(f"<h2>{format_text('💖 Wellness Check')}</h2>", unsafe_allow_html=True)
    feeling = st.text_input("How are you feeling today?", key="wellness_feeling")
    if st.button("Get Motivation") and feeling:
        try:
            prompt = f"""
            Generate a funny, uplifting, and emoji-rich motivational message for someone who is feeling '{feeling}'.
            Include a newly created Korean quote with English translation that matches the mood.
            Respond ONLY in JSON format like this:
            {{
              "motivation": "Your funny motivational message with emojis",
              "korean_quote": "Unique Korean quote",
              "english_translation": "English translation"
            }}
            """
            raw = ax_chat_completion([
                {"role": "system", "content": "You are a creative, playful, funny wellness coach. Use emojis freely."},
                {"role": "user", "content": prompt}
            ])
            match = re.search(r"\{.*\}", raw, re.S)
            if match:
                data = json.loads(match.group(0))
                motivation = data.get("motivation", "💪 Keep going, you're awesome! 😎")
                korean_quote = data.get("korean_quote", "천 리 길도 한 걸음부터다")
                english_translation = data.get("english_translation", "A journey of a thousand miles begins with a single step.")
            else:
                motivation = "💪 Keep going, you're awesome! 😎"
                korean_quote = "천 리 길도 한 걸음부터다"
                english_translation = "A journey of a thousand miles begins with a single step."
            st.session_state.latest_wellness = {
                "feeling": feeling,
                "motivation": motivation,
                "korean_quote": korean_quote,
                "english_translation": english_translation
            }
        except Exception as e:
            st.error(f"⚠️ Failed to generate wellness content: {e}")

    # Render wellness only if in Wellness mode
    if "latest_wellness" in st.session_state:
        card_html = f"""
        <style>
        .wellness-card {{
            display: inline-block;
            perspective: 1200px;
            cursor: pointer;
            margin: 15px 0;
        }}
        .wellness-card-inner {{
            width: 400px;
            height: 220px;
            position: relative;
            transform-style: preserve-3d;
            transition: transform 0.8s cubic-bezier(.25,.8,.25,1);
            border-radius: 12px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.12);
            padding: 12px;
        }}
        .wellness-card input[type="checkbox"] {{
            position: absolute;
            opacity: 0;
            pointer-events: none;
            height: 0; width: 0;
        }}
        .wellness-card-front, .wellness-card-back {{
            position: absolute;
            inset: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            -webkit-backface-visibility: hidden;
            backface-visibility: hidden;
            border-radius: 12px;
            padding: 12px;
            text-align: center;
            word-break: break-word;
            overflow-wrap: break-word;
        }}
        .wellness-card-front {{
            background-color: #4C6EB1;
            color: white;
            font-family: 'Calligraffitti', sans-serif;
            font-size: 22px;
            font-weight: 700;
            transition: box-shadow 0.3s ease-in-out;
        }}
        .wellness-card-front:hover {{
            box-shadow: 0 0 25px 5px rgba(255,255,255,0.5);
        }}
        .wellness-card-back {{
            background-color: #FF6F61;
            color: white;
            transform: rotateY(180deg);
            font-size: 18px;
            font-weight: 600;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            overflow-y: auto;
            padding: 15px;
        }}
        .wellness-card-back span.korean-text {{
            font-family: 'Nanum Myeongjo', serif;
        }}
        .wellness-card input[type="checkbox"]:checked + .wellness-card-inner {{
            transform: rotateY(180deg);
        }}
        @media (max-width: 600px) {{
            .wellness-card-inner {{
                width: 90vw;
                height: auto;
            }}
        }}
        </style>

        <label class="wellness-card">
            <input type="checkbox" />
            <div class="wellness-card-inner">
                <div class="wellness-card-front">
                    {format_text("💖 Click to see your motivation!")}
                </div>
                <div class="wellness-card-back">
                    <b>Feeling:</b> {format_text(st.session_state.latest_wellness['feeling'])}<br><br>
                    <b>Motivation:</b> {format_text(st.session_state.latest_wellness['motivation'])}<br><br>
                    <b>Korean Quote:</b> <span class="korean-text">{st.session_state.latest_wellness['korean_quote']}</span><br>
                    <i>{format_text(st.session_state.latest_wellness['english_translation'])}</i>
                </div>
            </div>
        </label>
        """
        st.markdown(card_html, unsafe_allow_html=True)

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

    if st.button("Reset Progress"):
        st.session_state.progress = {"xp": 0, "quizzes_taken": 0, "correct_answers": 0, "assignments_done": 0}
        save_progress(st.session_state.progress)
        st.success("Progress has been reset!")

    st.subheader("🔥 XP Progress")
    progress_to_next = xp % 100
    st.write(f"Level {level} — {xp} XP total")
    st.progress(progress_to_next / 100)

    st.subheader("📈 Stats Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Quizzes Taken", st.session_state.progress.get("quizzes_taken", 0))
    col2.metric("Correct Answers", st.session_state.progress.get("correct_answers", 0))
    col3.metric("Assignments Done", st.session_state.progress.get("assignments_done", 0))

    import pandas as pd
    import matplotlib.pyplot as plt
    xp_history = pd.DataFrame({"XP": [10, 30, 60, xp], "Stage": ["Day 1", "Day 2", "Day 3", "Now"]})
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
