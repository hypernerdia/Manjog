import streamlit as st
import json
import re
import os
from openai import OpenAI

# Must be first Streamlit call
st.set_page_config(page_title="한국어 배우기 · Korean Learning", page_icon="🌸", layout="wide")

# ------------------------------
# OLD KOREA AESTHETIC — Global CSS
# Traditional colors: hanji-cream, dancheong-red, deep ink, celadon green, gold
# ------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&family=Gowun+Batang&family=Black+Han+Sans&display=swap');

:root {
    --hanji:     #F5EDD8;       /* aged paper cream */
    --ink:       #1C1208;       /* deep brush ink */
    --dancheong: #C0392B;       /* traditional red */
    --dancheong2:#8B1A1A;       /* deep red */
    --celadon:   #6B8E7B;       /* celadon jade */
    --gold:      #B8973A;       /* muted gold */
    --cloud:     #EDE0CC;       /* warm off-white */
    --hanbok-blue: #3B5E8C;     /* deep hanbok blue */
    --brush-gray:#6E5E4A;       /* warm gray */
    --petal:     #E8B4B8;       /* blossom pink */
    --petal-deep:#C97B8A;       /* deep blossom */
}

/* Reset */
html, body, [class*="css"] {
    font-family: 'Gowun Batang', 'Nanum Myeongjo', serif !important;
    color: var(--ink) !important;
}

/* App background — aged hanji with subtle blossom texture */
.stApp {
    background-color: var(--hanji) !important;
    background-image:
        radial-gradient(ellipse at 10% 20%, rgba(232,180,184,0.18) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 80%, rgba(107,142,123,0.12) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(184,151,58,0.06) 0%, transparent 70%);
    background-attachment: fixed;
}

/* Decorative top border — dancheong stripe */
.stApp::before {
    content: '';
    display: block;
    height: 6px;
    background: repeating-linear-gradient(
        90deg,
        var(--dancheong) 0px, var(--dancheong) 40px,
        var(--gold) 40px, var(--gold) 80px,
        var(--celadon) 80px, var(--celadon) 120px,
        var(--hanbok-blue) 120px, var(--hanbok-blue) 160px,
        var(--gold) 160px, var(--gold) 200px
    );
    position: fixed;
    top: 0; left: 0; width: 100%; z-index: 9999;
}

/* ─── SIDEBAR ─────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: var(--dancheong2) !important;
    background-image:
        repeating-linear-gradient(
            0deg,
            transparent,
            transparent 38px,
            rgba(255,255,255,0.04) 38px,
            rgba(255,255,255,0.04) 40px
        ) !important;
    border-right: 3px solid var(--gold) !important;
}

[data-testid="stSidebar"] * {
    color: var(--hanji) !important;
    font-family: 'Nanum Myeongjo', serif !important;
}

[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2 {
    color: var(--gold) !important;
    font-family: 'Black Han Sans', sans-serif !important;
    letter-spacing: 2px;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.4);
}

/* Sidebar radio buttons */
.stRadio div[role="radiogroup"] label {
    display: block;
    background-color: rgba(245,237,216,0.10) !important;
    color: var(--hanji) !important;
    padding: 10px 16px;
    margin-bottom: 8px;
    border-radius: 4px;
    cursor: pointer;
    border: 1px solid rgba(184,151,58,0.35);
    font-family: 'Nanum Myeongjo', serif !important;
    font-size: 15px;
    transition: background 0.2s, border-color 0.2s;
}
.stRadio div[role="radiogroup"] label:hover {
    background-color: rgba(184,151,58,0.25) !important;
    border-color: var(--gold) !important;
}
.stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
    background-color: rgba(184,151,58,0.30) !important;
    border: 2px solid var(--gold) !important;
    font-weight: 700;
}

/* ─── HEADINGS ─────────────────────────────────── */
h1, h2, h3 {
    font-family: 'Black Han Sans', sans-serif !important;
    color: var(--dancheong2) !important;
    letter-spacing: 1px;
}
h2 { border-bottom: 2px solid var(--gold); padding-bottom: 6px; }

/* ─── INPUTS ─────────────────────────────────── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background-color: rgba(255,255,255,0.65) !important;
    border: 1.5px solid var(--gold) !important;
    border-radius: 4px !important;
    color: var(--ink) !important;
    font-family: 'Gowun Batang', serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--dancheong) !important;
    box-shadow: 0 0 0 2px rgba(192,57,43,0.2) !important;
}

/* ─── BUTTONS ─────────────────────────────────── */
.stButton > button {
    background-color: var(--dancheong2) !important;
    color: var(--hanji) !important;
    border: 2px solid var(--gold) !important;
    border-radius: 4px !important;
    font-family: 'Black Han Sans', sans-serif !important;
    letter-spacing: 1px;
    padding: 8px 22px;
    transition: background 0.2s, transform 0.1s;
    box-shadow: 2px 3px 8px rgba(0,0,0,0.18);
}
.stButton > button:hover {
    background-color: var(--dancheong) !important;
    transform: translateY(-1px);
    box-shadow: 3px 5px 12px rgba(0,0,0,0.22);
}
.stButton > button:active { transform: translateY(0); }

/* ─── PROGRESS BAR ─────────────────────────────── */
.stProgress > div > div > div {
    background-color: var(--dancheong) !important;
}
.stProgress > div > div {
    background-color: rgba(184,151,58,0.25) !important;
}

/* ─── METRIC CARDS ─────────────────────────────── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.5);
    border: 1px solid var(--gold);
    border-radius: 6px;
    padding: 12px !important;
}
[data-testid="stMetricValue"] {
    color: var(--dancheong2) !important;
    font-family: 'Black Han Sans', sans-serif !important;
}

/* ─── SUCCESS / ERROR / INFO ────────────────────── */
.stSuccess, .stInfo { border-radius: 6px; }
.stSuccess { border-left: 4px solid var(--celadon) !important; }
.stError   { border-left: 4px solid var(--dancheong) !important; }
.stInfo    { border-left: 4px solid var(--gold) !important; }

/* ─── CHAT BUBBLES ──────────────────────────────── */
.user-bubble {
    background: linear-gradient(135deg, var(--hanbok-blue), #2c4a6e);
    color: var(--hanji) !important;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    max-width: 68%;
    margin-left: auto;
    margin-bottom: 12px;
    font-family: 'Gowun Batang', serif;
    box-shadow: 2px 3px 10px rgba(0,0,0,0.2);
}
.bot-bubble {
    background: linear-gradient(135deg, #f0e8d5, #e8dcc8);
    color: var(--ink) !important;
    padding: 12px 18px;
    border-radius: 18px 18px 18px 4px;
    max-width: 68%;
    margin-right: auto;
    margin-bottom: 12px;
    border: 1px solid rgba(184,151,58,0.4);
    font-family: 'Gowun Batang', serif;
    box-shadow: 2px 3px 10px rgba(0,0,0,0.12);
}

/* ─── CHAT CONTAINER ────────────────────────────── */
.chat-scroll {
    max-height: 480px;
    overflow-y: auto;
    padding: 18px;
    border: 2px solid var(--gold);
    border-radius: 10px;
    background: rgba(255,255,255,0.45);
    backdrop-filter: blur(4px);
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.06);
}

/* ─── FLASHCARD GRID ────────────────────────────── */
.flashcards-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 18px;
    align-items: flex-start;
    margin-top: 12px;
}
.card {
    display: inline-block;
    perspective: 1200px;
    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
}
.card input[type="checkbox"] {
    position: absolute; opacity: 0; pointer-events: none; height: 0; width: 0;
}
.card-inner {
    width: 240px; height: 160px;
    position: relative;
    transform-style: preserve-3d;
    transition: transform 0.65s cubic-bezier(.2,.8,.2,1);
    border-radius: 10px;
    box-shadow: 3px 5px 18px rgba(0,0,0,0.18);
    user-select: none;
}
.card input[type="checkbox"]:checked + .card-inner { transform: rotateY(180deg); }
.card-face {
    position: absolute; inset: 0;
    display: flex; align-items: center; justify-content: center;
    -webkit-backface-visibility: hidden; backface-visibility: hidden;
    border-radius: 10px;
    font-size: 26px; font-weight: 700;
    padding: 14px; text-align: center; word-break: break-word;
}
.card-front {
    background: linear-gradient(145deg, var(--dancheong2), #6B1010);
    color: var(--hanji);
    border: 2px solid var(--gold);
}
.card-back {
    background: linear-gradient(145deg, var(--celadon), #4a6b5a);
    color: #fff;
    transform: rotateY(180deg);
    border: 2px solid var(--gold);
}

/* ─── WELLNESS + STORY CARD ─────────────────────── */
.wellness-card { display:inline-block; perspective:1200px; cursor:pointer; width:100%; margin:15px 0; }
.wellness-card input[type="checkbox"] { position:absolute;opacity:0;pointer-events:none;height:0;width:0; }
.wellness-card-inner {
    width:100%; min-height:500px; position:relative;
    transform-style:preserve-3d;
    transition:transform 0.8s cubic-bezier(.25,.8,.25,1);
    border-radius:12px;
    box-shadow:0 8px 28px rgba(0,0,0,0.18);
}
.wellness-card input[type="checkbox"]:checked + .wellness-card-inner { transform:rotateY(180deg); }
.wellness-card-front, .wellness-card-back {
    position:absolute; inset:0;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    -webkit-backface-visibility:hidden; backface-visibility:hidden;
    border-radius:12px; padding:20px; text-align:center; word-break:break-word;
}
.wellness-card-front {
    background: linear-gradient(145deg, var(--hanbok-blue), #2c3e6b);
    color: var(--hanji);
    font-family:'Black Han Sans',sans-serif; font-size:22px;
    border: 3px solid var(--gold);
}
.wellness-card-back {
    background: linear-gradient(145deg, #f5e6d0, #ecdcc8);
    color: var(--ink);
    transform:rotateY(180deg);
    font-size:17px; font-family:'Gowun Batang',serif;
    border: 3px solid var(--gold);
}

/* ─── STORY CARD ────────────────────────────────── */
.story-card {
    background: linear-gradient(145deg, #2a1a0e, #4a2a18);
    border-radius: 14px;
    padding: 28px 32px;
    margin-top: 16px;
    color: var(--hanji);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    border: 2px solid var(--gold);
    font-family: 'Nanum Myeongjo', serif;
    max-width: 820px;
    line-height: 1.8;
}
.story-card h3 {
    font-family: 'Black Han Sans', sans-serif !important;
    color: var(--gold) !important;
    font-size: 24px; margin-bottom: 14px;
    letter-spacing: 2px;
}
.story-card p { font-size: 17px; margin-bottom: 10px; }
.story-card .moral { font-style: italic; color: var(--petal); margin-top: 14px; font-size: 16px; }

/* ─── BLOSSOM SVG DECORATION (sidebar top) ──────── */
.blossom-deco { text-align:center; padding: 8px 0 16px; }

/* ─── DIVIDER ───────────────────────────────────── */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
    margin: 20px 0;
}

/* ─── SCROLLBAR ─────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--cloud); }
::-webkit-scrollbar-thumb { background: var(--gold); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ------------------------------
# SVG Graphics Helpers
# ------------------------------

def blossom_svg():
    return """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 60" width="180" height="55">
      <!-- Branch -->
      <path d="M10,55 Q60,30 100,28 Q140,26 190,10" stroke="#6B3A2A" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      <!-- Petals scattered along branch -->
      <g opacity="0.9">
        <!-- Blossom 1 -->
        <g transform="translate(38,38)">
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#E8B4B8" transform="rotate(0)"/>
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#E8B4B8" transform="rotate(72)"/>
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#E8B4B8" transform="rotate(144)"/>
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#EDCFD1" transform="rotate(216)"/>
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#EDCFD1" transform="rotate(288)"/>
          <circle cx="0" cy="0" r="3" fill="#F5D5A0"/>
        </g>
        <!-- Blossom 2 -->
        <g transform="translate(75,30)">
          <ellipse cx="0" cy="-6" rx="3.5" ry="6" fill="#C97B8A" transform="rotate(0)"/>
          <ellipse cx="0" cy="-6" rx="3.5" ry="6" fill="#C97B8A" transform="rotate(72)"/>
          <ellipse cx="0" cy="-6" rx="3.5" ry="6" fill="#E8B4B8" transform="rotate(144)"/>
          <ellipse cx="0" cy="-6" rx="3.5" ry="6" fill="#E8B4B8" transform="rotate(216)"/>
          <ellipse cx="0" cy="-6" rx="3.5" ry="6" fill="#C97B8A" transform="rotate(288)"/>
          <circle cx="0" cy="0" r="2.5" fill="#F5D5A0"/>
        </g>
        <!-- Blossom 3 -->
        <g transform="translate(115,27)">
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#EDCFD1" transform="rotate(0)"/>
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#E8B4B8" transform="rotate(72)"/>
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#EDCFD1" transform="rotate(144)"/>
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#E8B4B8" transform="rotate(216)"/>
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#EDCFD1" transform="rotate(288)"/>
          <circle cx="0" cy="0" r="3" fill="#F5D5A0"/>
        </g>
        <!-- Blossom 4 -->
        <g transform="translate(158,17)">
          <ellipse cx="0" cy="-5.5" rx="3" ry="5.5" fill="#E8B4B8" transform="rotate(0)"/>
          <ellipse cx="0" cy="-5.5" rx="3" ry="5.5" fill="#C97B8A" transform="rotate(72)"/>
          <ellipse cx="0" cy="-5.5" rx="3" ry="5.5" fill="#E8B4B8" transform="rotate(144)"/>
          <ellipse cx="0" cy="-5.5" rx="3" ry="5.5" fill="#EDCFD1" transform="rotate(216)"/>
          <ellipse cx="0" cy="-5.5" rx="3" ry="5.5" fill="#C97B8A" transform="rotate(288)"/>
          <circle cx="0" cy="0" r="2" fill="#F5D5A0"/>
        </g>
        <!-- Falling petals -->
        <ellipse cx="55" cy="50" rx="3" ry="5" fill="#E8B4B8" transform="rotate(-30,55,50)" opacity="0.7"/>
        <ellipse cx="95" cy="48" rx="2.5" ry="4.5" fill="#C97B8A" transform="rotate(20,95,48)" opacity="0.6"/>
        <ellipse cx="140" cy="44" rx="2" ry="4" fill="#EDCFD1" transform="rotate(-15,140,44)" opacity="0.7"/>
      </g>
    </svg>
    """

def dancheong_divider():
    return """
    <div style="margin:18px 0;">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 14" width="100%" height="14">
      <rect width="600" height="14" fill="#F5EDD8"/>
      <!-- repeating dancheong pattern -->
      <rect x="0"   width="40" height="14" fill="#C0392B"/>
      <rect x="40"  width="40" height="14" fill="#B8973A"/>
      <rect x="80"  width="40" height="14" fill="#6B8E7B"/>
      <rect x="120" width="40" height="14" fill="#3B5E8C"/>
      <rect x="160" width="40" height="14" fill="#B8973A"/>
      <rect x="200" width="40" height="14" fill="#C0392B"/>
      <rect x="240" width="40" height="14" fill="#B8973A"/>
      <rect x="280" width="40" height="14" fill="#6B8E7B"/>
      <rect x="320" width="40" height="14" fill="#3B5E8C"/>
      <rect x="360" width="40" height="14" fill="#B8973A"/>
      <rect x="400" width="40" height="14" fill="#C0392B"/>
      <rect x="440" width="40" height="14" fill="#B8973A"/>
      <rect x="480" width="40" height="14" fill="#6B8E7B"/>
      <rect x="520" width="40" height="14" fill="#3B5E8C"/>
      <rect x="560" width="40" height="14" fill="#B8973A"/>
      <!-- white diamond overlays for decoration -->
      <polygon points="20,0 26,7 20,14 14,7" fill="rgba(255,255,255,0.25)"/>
      <polygon points="60,0 66,7 60,14 54,7" fill="rgba(255,255,255,0.25)"/>
      <polygon points="100,0 106,7 100,14 94,7" fill="rgba(255,255,255,0.25)"/>
      <polygon points="140,0 146,7 140,14 134,7" fill="rgba(255,255,255,0.25)"/>
      <polygon points="180,0 186,7 180,14 174,7" fill="rgba(255,255,255,0.25)"/>
      <polygon points="220,0 226,7 220,14 214,7" fill="rgba(255,255,255,0.25)"/>
      <polygon points="260,0 266,7 260,14 254,7" fill="rgba(255,255,255,0.25)"/>
      <polygon points="300,0 306,7 300,14 294,7" fill="rgba(255,255,255,0.25)"/>
      <polygon points="340,0 346,7 340,14 334,7" fill="rgba(255,255,255,0.25)"/>
      <polygon points="380,0 386,7 380,14 374,7" fill="rgba(255,255,255,0.25)"/>
      <polygon points="420,0 426,7 420,14 414,7" fill="rgba(255,255,255,0.25)"/>
      <polygon points="460,0 466,7 460,14 454,7" fill="rgba(255,255,255,0.25)"/>
      <polygon points="500,0 506,7 500,14 494,7" fill="rgba(255,255,255,0.25)"/>
      <polygon points="540,0 546,7 540,14 534,7" fill="rgba(255,255,255,0.25)"/>
      <polygon points="580,0 586,7 580,14 574,7" fill="rgba(255,255,255,0.25)"/>
    </svg>
    </div>
    """

def page_header(title, subtitle=""):
    sub_html = f'<p style="font-family:\'Gowun Batang\',serif;color:#6E5E4A;margin-top:-8px;font-size:16px;">{subtitle}</p>' if subtitle else ""
    return f"""
    <div style="margin-bottom:6px;">
      <h2 style="font-family:\'Black Han Sans\',sans-serif;color:#8B1A1A;letter-spacing:2px;margin-bottom:4px;">{title}</h2>
      {sub_html}
    </div>
    """ + dancheong_divider()

# ------------------------------
# Helper: Korean/English font spans
# ------------------------------
def format_text(text):
    if re.search(r"[\u3131-\uD79D]", text):
        return f"<span style='font-family:Nanum Myeongjo,serif;'>{text}</span>"
    return f"<span style='font-family:Gowun Batang,serif;'>{text}</span>"

# ------------------------------
# OpenAI client
# ------------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ------------------------------
# Progress persistence
# ------------------------------
PROGRESS_FILE = "progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"xp": 0, "quizzes_taken": 0, "correct_answers": 0, "assignments_done": 0}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

# ------------------------------
# AI helpers
# ------------------------------
def generate_flashcards(topic):
    prompt = f"""
    Create 5 Korean flashcards about "{topic}". Either side of each flashcard should have no more than 5 words.
    The front side must be in Korean; the back side must be in English.
    Respond ONLY with valid JSON, nothing else.
    Format: [{{"front": "학교", "back": "School"}}]
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
            return json.loads(match.group(0))
    except Exception as e:
        st.error(f"⚠️ Flashcard generation failed: {e}")
    return [{"front": "학교", "back": "School"}]

def generate_quiz(topic):
    prompt = f"""
    Create 10 Korean multiple-choice quizzes in ENGLISH LANGUAGE ONLY about "{topic}".
    All questions must be linked to Korea and its culture.
    Respond ONLY with valid JSON, nothing else.
    Format:
    [{{"question": "What does '학교' mean?", "options": ["School","Teacher","Book","Friend"], "answer": "School"}}]
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
            return json.loads(match.group(0))
    except Exception as e:
        st.error(f"⚠️ Quiz generation failed: {e}")
    return [{"question": "What does '학교' mean?", "options": ["School","Book","Friend","Teacher"], "answer": "School"}]

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
# Session state init
# ------------------------------
defaults = {
    "chat_history": [],
    "flashcards": [], "flashcards_topic": "",
    "quizzes": [], "quiz_topic": "", "answers": {},
    "assignments": "", "assignment_topic": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
if "progress" not in st.session_state:
    st.session_state.progress = load_progress()

# ------------------------------
# SIDEBAR
# ------------------------------
with st.sidebar:
    st.markdown(
        f'<div class="blossom-deco">{blossom_svg()}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        "<h2 style='text-align:center;letter-spacing:3px;'>한국어 배우기</h2>"
        "<p style='text-align:center;font-size:13px;opacity:0.8;margin-top:-12px;'>Korean Learning</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    mode = st.radio("", [
        "🤖 Chatbot",
        "📖 Flashcards",
        "📝 Quizzes",
        "✍️ Assignments",
        "💖 Wellness",
        "🎤 Korean Inspiration",
        "📊 Dashboard",
    ], label_visibility="collapsed")

    # XP badge in sidebar
    xp = st.session_state.progress["xp"]
    level = xp // 100
    st.markdown("---")
    st.markdown(
        f"<div style='text-align:center;padding:8px;"
        f"background:rgba(184,151,58,0.2);border-radius:6px;"
        f"border:1px solid rgba(184,151,58,0.5);'>"
        f"<span style='font-size:22px;'>🌸</span><br>"
        f"<b style='color:#F5D5A0;font-size:18px;'>Lv. {level}</b><br>"
        f"<span style='font-size:12px;color:#e0cfa8;'>{xp} XP</span>"
        f"</div>",
        unsafe_allow_html=True
    )

# ══════════════════════════════════════════════════
# MODE: CHATBOT
# ══════════════════════════════════════════════════
if mode == "🤖 Chatbot":
    st.markdown(page_header("🤖 Chatbot", "Ask me anything about Korean language & culture"), unsafe_allow_html=True)

    col1, col2 = st.columns([8, 1])
    with col1:
        user_input = st.text_input("💬 Type your message...", key="chat_box", label_visibility="collapsed")
    with col2:
        send = st.button("전송")

    if send and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history]
        )
        bot_reply = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        st.rerun()

    st.markdown('<div class="chat-scroll">', unsafe_allow_html=True)
    if not st.session_state.chat_history:
        st.markdown(
            "<p style='text-align:center;color:#9E8C78;font-style:italic;padding-top:40px;'>"
            "안녕하세요! · Begin your conversation below 🌸</p>",
            unsafe_allow_html=True
        )
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f"<div class='user-bubble'><b>🧑 You</b><br>{format_text(msg['content'])}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='bot-bubble'><b>🤖 Bot</b><br>{format_text(msg['content'])}</div>",
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# MODE: FLASHCARDS
# ══════════════════════════════════════════════════
elif mode == "📖 Flashcards":
    st.markdown(page_header("📖 Flashcards", "Click a card to reveal the translation"), unsafe_allow_html=True)

    topic = st.text_input("Enter a topic for flashcards:", placeholder="e.g. animals, food, K-drama phrases…")

    if st.button("Generate Flashcards 🌸") and topic:
        st.session_state.flashcards = generate_flashcards(topic)
        st.session_state.flashcards_topic = topic

    if st.session_state.flashcards:
        st.markdown(
            f"<p style='color:#6E5E4A;font-style:italic;'>Cards for: <b>{st.session_state.flashcards_topic}</b> — click to flip</p>",
            unsafe_allow_html=True
        )
        st.markdown('<div class="flashcards-grid">', unsafe_allow_html=True)
        for card in st.session_state.flashcards:
            front_html = format_text(card.get("front", ""))
            back_html  = format_text(card.get("back", ""))
            st.markdown(f"""
            <label class="card">
                <input type="checkbox"/>
                <div class="card-inner">
                    <div class="card-face card-front">{front_html}</div>
                    <div class="card-face card-back">{back_html}</div>
                </div>
            </label>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# MODE: QUIZZES
# ══════════════════════════════════════════════════
elif mode == "📝 Quizzes":
    st.markdown(page_header("📝 Quizzes", "Test your Korean knowledge"), unsafe_allow_html=True)

    quiz_type = st.radio("Select quiz type:", ["Vocabulary", "Grammar", "General"], key="quiz_type", horizontal=True)

    if quiz_type == "Vocabulary":
        vocab_topic = st.text_input("Enter a vocabulary topic:", placeholder="e.g. food, family, travel")
        if st.button("Generate Vocabulary Quiz 🌸") and vocab_topic:
            st.session_state.quizzes = generate_quiz(
                f"Korean vocabulary quiz on '{vocab_topic}'. Give English words, provide Korean translations as options. Always in English."
            )
            st.session_state.answers = {}

    elif quiz_type == "Grammar":
        grammar_topic = st.selectbox("Choose grammar focus:", [
            "Sentence formation (Subject-Object-Verb)",
            "Particles and markers (이/가, 을/를, 은/는)",
            "Honorifics and politeness levels",
            "Verb conjugations",
            "Connectives (-고, -지만, -서)",
            "Tenses and aspect"
        ], key="grammar_topic")
        if st.button("Generate Grammar Quiz 🌸") and grammar_topic:
            st.session_state.quizzes = generate_quiz(
                f"Korean grammar quiz about '{grammar_topic}'. All questions and answers in English."
            )
            st.session_state.answers = {}

    elif quiz_type == "General":
        general_topic = st.text_input("Enter a general topic:", placeholder="e.g. K-pop, Joseon Dynasty, Korean food")
        if st.button("Generate General Quiz 🌸") and general_topic:
            st.session_state.quizzes = generate_quiz(
                f"General knowledge quiz about '{general_topic}' related to Korean culture. All in English."
            )
            st.session_state.answers = {}

    if st.session_state.get("quizzes"):
        st.markdown(dancheong_divider(), unsafe_allow_html=True)
        for i, q in enumerate(st.session_state.quizzes, 1):
            st.markdown(f"**Q{i}. {q['question']}**")
            selected = st.radio(f"", q["options"], key=f"quiz_{i}_{quiz_type}", label_visibility="collapsed")
            st.session_state.answers[i] = selected

        if st.button("Check Answers ✅"):
            correct_count = 0
            for i, q in enumerate(st.session_state.quizzes, 1):
                user_ans = st.session_state.answers.get(i)
                if user_ans == q["answer"]:
                    st.success(f"Q{i}: ✅ Correct!")
                    correct_count += 1
                else:
                    st.error(f"Q{i}: ❌ Wrong! Correct answer: **{q['answer']}**")

            st.session_state.progress["quizzes_taken"] += 1
            st.session_state.progress["correct_answers"] += correct_count
            st.session_state.progress["xp"] += correct_count * 10
            save_progress(st.session_state.progress)
            st.info(f"🌸 Score: {correct_count}/{len(st.session_state.quizzes)}  |  +{correct_count * 10} XP earned")

# ══════════════════════════════════════════════════
# MODE: ASSIGNMENTS
# ══════════════════════════════════════════════════
elif mode == "✍️ Assignments":
    st.markdown(page_header("✍️ Assignments", "Practice makes perfect"), unsafe_allow_html=True)

    topic = st.text_input("Enter a topic for your assignment:", placeholder="e.g. greetings, shopping, school life")

    if st.button("Generate Assignment 🌸") and topic:
        st.session_state.assignments = generate_assignment(topic)
        st.session_state.assignment_topic = topic
        st.session_state.progress["assignments_done"] += 1
        st.session_state.progress["xp"] += 20
        save_progress(st.session_state.progress)
        st.info("🌸 +20 XP earned for completing an assignment!")

    if st.session_state.assignments:
        st.markdown(
            f"<h3 style='color:#8B1A1A;'>Assignments on: {st.session_state.assignment_topic}</h3>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='background:rgba(255,255,255,0.55);border:1.5px solid #B8973A;"
            f"border-radius:8px;padding:20px 24px;"
            f"font-family:Gowun Batang,serif;font-size:16px;line-height:1.8;'>"
            f"{st.session_state.assignments}</div>",
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════════
# MODE: WELLNESS
# ══════════════════════════════════════════════════
elif mode == "💖 Wellness":
    st.markdown(page_header("💖 Wellness Check", "마음 건강 · Take care of your heart"), unsafe_allow_html=True)

    feeling = st.text_input("How are you feeling today?", key="wellness_feeling", placeholder="e.g. tired, excited, overwhelmed…")

    if st.button("Get Motivation 🌸") and feeling:
        try:
            prompt = f"""
            Generate a funny, uplifting, emoji-rich motivational message (~35 words) for someone feeling '{feeling}'. Add only 3 emojis total.
            Include a newly created Korean quote with English translation matching the mood.
            Respond ONLY in JSON:
            {{"motivation":"...","korean_quote":"...","english_translation":"..."}}
            """
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Creative, playful wellness coach."},
                    {"role": "user", "content": prompt}
                ]
            )
            raw = response.choices[0].message.content.strip()
            match = re.search(r"\{.*\}", raw, re.S)
            if match:
                data = json.loads(match.group(0))
                st.session_state.latest_wellness = {
                    "feeling": feeling,
                    "motivation": data.get("motivation", "💪 Keep going!"),
                    "korean_quote": data.get("korean_quote", "천 리 길도 한 걸음부터다"),
                    "english_translation": data.get("english_translation", "A journey of a thousand miles begins with a single step.")
                }
        except Exception as e:
            st.error(f"⚠️ Failed: {e}")

    if "latest_wellness" in st.session_state:
        w = st.session_state.latest_wellness
        st.markdown(f"""
        <label class="wellness-card">
            <input type="checkbox"/>
            <div class="wellness-card-inner">
                <div class="wellness-card-front">
                    🌸<br><br>
                    <span style='font-size:18px;'>Click to reveal your<br>daily motivation</span><br><br>
                    <span style='font-size:13px;opacity:0.75;'>마음을 담아</span>
                </div>
                <div class="wellness-card-back">
                    <b style='color:#8B1A1A;font-size:16px;'>Feeling:</b><br>
                    {format_text(w['feeling'])}<br><br>
                    <b style='color:#8B1A1A;'>Motivation:</b><br>
                    {format_text(w['motivation'])}<br><br>
                    <b style='color:#8B1A1A;'>Korean Quote:</b><br>
                    <span style='font-family:Nanum Myeongjo,serif;font-size:18px;color:#3B5E8C;'>{w['korean_quote']}</span><br>
                    <i style='color:#6E5E4A;'>{format_text(w['english_translation'])}</i>
                </div>
            </div>
        </label>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# MODE: KOREAN INSPIRATION
# ══════════════════════════════════════════════════
elif mode == "🎤 Korean Inspiration":
    st.markdown(page_header("🎤 Inspiring Korean Stories", "영감을 주는 이야기 · Stories that move the soul"), unsafe_allow_html=True)

    def generate_korean_story():
        try:
            prompt = """
            Generate a detailed, emotionally rich story about a Korean person (historical or modern) who inspires others.
            Include struggles, values, turning points, achievements in both Korean and English (~100 words).
            Include: name_korean, name_english, korean_story, english_story, moral_korean, moral_english.
            Respond ONLY in JSON.
            """
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Warm Korean bilingual storyteller."},
                    {"role": "user", "content": prompt}
                ]
            )
            raw = response.choices[0].message.content.strip()
            match = re.search(r"\{.*\}", raw, re.S)
            if match:
                d = json.loads(match.group(0))
                return {
                    "name_korean": d.get("name_korean", "이름 없음"),
                    "name_english": d.get("name_english", "Unknown Hero"),
                    "korean_story": d.get("korean_story", ""),
                    "english_story": d.get("english_story", ""),
                    "moral_korean": d.get("moral_korean", ""),
                    "moral_english": d.get("moral_english", ""),
                }
        except Exception as e:
            st.error(f"⚠️ Failed: {e}")
        return None

    if "latest_story" not in st.session_state:
        st.session_state.latest_story = generate_korean_story()

    if st.button("✨ New Story"):
        st.session_state.latest_story = generate_korean_story()

    if st.session_state.latest_story:
        s = st.session_state.latest_story
        st.markdown(f"""
        <div class="story-card">
            <h3>🌸 {s['name_korean']} · {s['name_english']}</h3>
            <p><b style='color:#B8973A;'>Korean Story:</b><br>
            <span style='font-family:Nanum Myeongjo,serif;'>{s['korean_story']}</span></p>
            <p><b style='color:#B8973A;'>English Story:</b><br>{s['english_story']}</p>
            <p class="moral">🌸 {s['moral_korean']}<br><i>({s['moral_english']})</i></p>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# MODE: DASHBOARD
# ══════════════════════════════════════════════════
elif mode == "📊 Dashboard":
    st.markdown(page_header("📊 Dashboard", "나의 여정 · Track your learning journey"), unsafe_allow_html=True)

    prog = st.session_state.progress
    xp   = prog["xp"]
    level = xp // 100
    xp_progress = xp % 100

    # Level display
    st.markdown(
        f"<div style='background:rgba(139,26,26,0.08);border:2px solid #B8973A;"
        f"border-radius:10px;padding:18px 24px;margin-bottom:18px;'>"
        f"<span style='font-family:Black Han Sans,sans-serif;font-size:28px;color:#8B1A1A;'>🌸 Level {level}</span>"
        f"<span style='font-family:Gowun Batang,serif;color:#6E5E4A;font-size:16px;'> · {xp} XP total</span>"
        f"</div>",
        unsafe_allow_html=True
    )
    st.progress(xp_progress / 100)
    st.caption(f"{xp_progress} / 100 XP to next level")

    st.markdown(dancheong_divider(), unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("📝 Quizzes Taken",   prog.get("quizzes_taken", 0))
    col2.metric("✅ Correct Answers",  prog.get("correct_answers", 0))
    col3.metric("✍️ Assignments Done", prog.get("assignments_done", 0))

    # XP chart
    import pandas as pd, matplotlib.pyplot as plt, matplotlib as mpl
    st.markdown("<h3 style='margin-top:20px;'>📊 XP Growth</h3>", unsafe_allow_html=True)
    xp_history = pd.DataFrame({
        "XP":    [10, 30, 60, xp],
        "Stage": ["Day 1", "Day 2", "Day 3", "Now"]
    })
    fig, ax = plt.subplots(figsize=(7, 3))
    fig.patch.set_facecolor("#F5EDD8")
    ax.set_facecolor("#F5EDD8")
    ax.plot(xp_history["Stage"], xp_history["XP"],
            marker="o", color="#8B1A1A", linewidth=2.5,
            markerfacecolor="#B8973A", markersize=9)
    ax.fill_between(xp_history["Stage"], xp_history["XP"],
                    alpha=0.15, color="#C0392B")
    ax.set_ylabel("XP", color="#4a2a18")
    ax.set_xlabel("Progress", color="#4a2a18")
    ax.tick_params(colors="#4a2a18")
    for spine in ax.spines.values():
        spine.set_edgecolor("#B8973A")
    st.pyplot(fig)

    st.markdown(dancheong_divider(), unsafe_allow_html=True)

    # Last topics
    if any([st.session_state.quiz_topic, st.session_state.flashcards_topic, st.session_state.assignment_topic]):
        st.markdown("<h3>🗂 Recent Topics</h3>", unsafe_allow_html=True)
        if st.session_state.quiz_topic:
            st.write(f"📝 Last quiz topic: **{st.session_state.quiz_topic}**")
        if st.session_state.flashcards_topic:
            st.write(f"📖 Last flashcards topic: **{st.session_state.flashcards_topic}**")
        if st.session_state.assignment_topic:
            st.write(f"✍️ Last assignment topic: **{st.session_state.assignment_topic}**")

    if st.button("🔄 Reset Progress"):
        st.session_state.progress = {"xp": 0, "quizzes_taken": 0, "correct_answers": 0, "assignments_done": 0}
        save_progress(st.session_state.progress)
        st.success("Progress has been reset! 새로 시작합니다 🌸")
        st.rerun()
