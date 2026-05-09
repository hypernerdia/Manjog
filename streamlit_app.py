import streamlit as st
import json
import re
import os
from groq import Groq

# ── Must be FIRST Streamlit call ──────────────────
st.set_page_config(
    page_title="한국어 배우기 · Korean Learning",
    page_icon="🌸",
    layout="wide"
)

# ══════════════════════════════════════════════════
# GLOBAL CSS  —  Old Korea Aesthetic
# Fonts: Times New Roman (English) · Nanum Myeongjo (Korean)
# ══════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&family=Black+Han+Sans&display=swap');

/* ── Root palette ── */
:root {
    --hanji:        #F5EDD8;
    --ink:          #1C1208;
    --dancheong:    #C0392B;
    --dancheong2:   #8B1A1A;
    --celadon:      #6B8E7B;
    --gold:         #B8973A;
    --cloud:        #EDE0CC;
    --hanbok-blue:  #3B5E8C;
    --brush-gray:   #6E5E4A;
    --petal:        #E8B4B8;
    --petal-deep:   #C97B8A;
}

/* ── Base font rules ── */
html, body, [class*="css"] {
    font-family: 'Times New Roman', Times, serif !important;
    color: var(--ink) !important;
}
.korean-text, :lang(ko) {
    font-family: 'Nanum Myeongjo', serif !important;
}

/* ── App background ── */
.stApp {
    background-color: var(--hanji) !important;
    background-image:
        radial-gradient(ellipse at 10% 20%, rgba(232,180,184,0.18) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 80%, rgba(107,142,123,0.12) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(184,151,58,0.06) 0%, transparent 70%);
    background-attachment: fixed;
}

/* ── Dancheong top bar ── */
.stApp::before {
    content: '';
    display: block;
    height: 6px;
    background: repeating-linear-gradient(
        90deg,
        var(--dancheong)   0px,  var(--dancheong)   40px,
        var(--gold)        40px, var(--gold)         80px,
        var(--celadon)     80px, var(--celadon)      120px,
        var(--hanbok-blue) 120px,var(--hanbok-blue)  160px,
        var(--gold)        160px,var(--gold)         200px
    );
    position: fixed;
    top: 0; left: 0; width: 100%; z-index: 9999;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--dancheong2) !important;
    background-image: repeating-linear-gradient(
        0deg, transparent, transparent 38px,
        rgba(255,255,255,0.04) 38px, rgba(255,255,255,0.04) 40px
    ) !important;
    border-right: 3px solid var(--gold) !important;
}
[data-testid="stSidebar"] * {
    color: var(--hanji) !important;
    font-family: 'Times New Roman', Times, serif !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2 {
    color: var(--gold) !important;
    font-family: 'Black Han Sans', sans-serif !important;
    letter-spacing: 2px;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.4);
}

/* Sidebar radio */
.stRadio div[role="radiogroup"] label {
    display: block;
    background-color: rgba(245,237,216,0.10) !important;
    color: var(--hanji) !important;
    padding: 10px 16px;
    margin-bottom: 8px;
    border-radius: 4px;
    cursor: pointer;
    border: 1px solid rgba(184,151,58,0.35);
    font-family: 'Times New Roman', Times, serif !important;
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

/* ── Headings ── */
h1, h2, h3 {
    font-family: 'Black Han Sans', sans-serif !important;
    color: var(--dancheong2) !important;
    letter-spacing: 1px;
}
h2 { border-bottom: 2px solid var(--gold); padding-bottom: 6px; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background-color: rgba(255,255,255,0.65) !important;
    border: 1.5px solid var(--gold) !important;
    border-radius: 4px !important;
    color: var(--ink) !important;
    font-family: 'Times New Roman', Times, serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--dancheong) !important;
    box-shadow: 0 0 0 2px rgba(192,57,43,0.2) !important;
}

/* ── Buttons ── */
.stButton > button {
    background-color: var(--dancheong2) !important;
    color: var(--hanji) !important;
    border: 2px solid var(--gold) !important;
    border-radius: 4px !important;
    font-family: 'Times New Roman', Times, serif !important;
    font-size: 15px;
    letter-spacing: 1px;
    padding: 8px 22px;
    transition: background 0.2s, transform 0.1s;
    box-shadow: 2px 3px 8px rgba(0,0,0,0.18);
}
.stButton > button:hover {
    background-color: var(--dancheong) !important;
    transform: translateY(-1px);
}
.stButton > button:active { transform: translateY(0); }

/* ── Progress bar ── */
.stProgress > div > div > div { background-color: var(--dancheong) !important; }
.stProgress > div > div      { background-color: rgba(184,151,58,0.25) !important; }

/* ── Metric cards ── */
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

/* ── Alerts ── */
.stSuccess { border-left: 4px solid var(--celadon) !important; border-radius: 6px; }
.stError   { border-left: 4px solid var(--dancheong) !important; border-radius: 6px; }
.stInfo    { border-left: 4px solid var(--gold) !important; border-radius: 6px; }

/* ── Chat bubbles ── */
.user-bubble {
    background: linear-gradient(135deg, var(--hanbok-blue), #2c4a6e);
    color: var(--hanji) !important;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    max-width: 68%;
    margin-left: auto;
    margin-bottom: 12px;
    font-family: 'Times New Roman', Times, serif;
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
    font-family: 'Times New Roman', Times, serif;
    box-shadow: 2px 3px 10px rgba(0,0,0,0.12);
}

/* ── Chat scroll container ── */
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

/* ── Flashcard grid ── */
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
    font-size: 24px; font-weight: 700;
    padding: 14px; text-align: center; word-break: break-word;
}
.card-front {
    background: linear-gradient(145deg, var(--dancheong2), #6B1010);
    color: var(--hanji);
    border: 2px solid var(--gold);
    font-family: 'Nanum Myeongjo', serif;
}
.card-back {
    background: linear-gradient(145deg, var(--celadon), #4a6b5a);
    color: #fff;
    transform: rotateY(180deg);
    border: 2px solid var(--gold);
    font-family: 'Times New Roman', Times, serif;
}

/* ── Wellness flip card ── */
.wellness-card {
    display: inline-block; perspective: 1200px;
    cursor: pointer; width: 100%; margin: 15px 0;
}
.wellness-card input[type="checkbox"] {
    position: absolute; opacity: 0; pointer-events: none; height: 0; width: 0;
}
.wellness-card-inner {
    width: 100%; min-height: 480px; position: relative;
    transform-style: preserve-3d;
    transition: transform 0.8s cubic-bezier(.25,.8,.25,1);
    border-radius: 12px;
    box-shadow: 0 8px 28px rgba(0,0,0,0.18);
}
.wellness-card input[type="checkbox"]:checked + .wellness-card-inner {
    transform: rotateY(180deg);
}
.wellness-card-front, .wellness-card-back {
    position: absolute; inset: 0;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    -webkit-backface-visibility: hidden; backface-visibility: hidden;
    border-radius: 12px; padding: 24px;
    text-align: center; word-break: break-word;
}
.wellness-card-front {
    background: linear-gradient(145deg, var(--hanbok-blue), #2c3e6b);
    color: var(--hanji);
    font-family: 'Times New Roman', Times, serif;
    font-size: 20px;
    border: 3px solid var(--gold);
}
.wellness-card-back {
    background: linear-gradient(145deg, #1a3a2a, #2e5c42);
    color: #F5EDD8;
    transform: rotateY(180deg);
    font-size: 16px;
    font-family: 'Times New Roman', Times, serif;
    border: 3px solid var(--gold);
    overflow-y: auto;
    box-shadow: inset 0 0 30px rgba(0,0,0,0.25);
}

/* ── Story card ── */
.story-card {
    background: linear-gradient(145deg, #2a1a0e, #4a2a18);
    border-radius: 14px;
    padding: 28px 32px;
    margin-top: 16px;
    color: var(--hanji);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    border: 2px solid var(--gold);
    max-width: 820px;
    line-height: 1.9;
    font-family: 'Times New Roman', Times, serif;
}
.story-card h3 {
    font-family: 'Black Han Sans', sans-serif !important;
    color: var(--gold) !important;
    font-size: 22px; margin-bottom: 14px; letter-spacing: 2px;
}
.story-card p { font-size: 16px; margin-bottom: 10px; }
.story-card .moral { font-style: italic; color: var(--petal); margin-top: 14px; font-size: 15px; }

/* ── Blossom deco ── */
.blossom-deco { text-align: center; padding: 8px 0 16px; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--cloud); }
::-webkit-scrollbar-thumb { background: var(--gold); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# SVG GRAPHICS
# ══════════════════════════════════════════════════
def blossom_svg():
    return """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 60" width="180" height="55">
      <path d="M10,55 Q60,30 100,28 Q140,26 190,10"
            stroke="#6B3A2A" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      <g opacity="0.9">
        <g transform="translate(38,38)">
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#E8B4B8" transform="rotate(0)"/>
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#E8B4B8" transform="rotate(72)"/>
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#E8B4B8" transform="rotate(144)"/>
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#EDCFD1" transform="rotate(216)"/>
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#EDCFD1" transform="rotate(288)"/>
          <circle cx="0" cy="0" r="3" fill="#F5D5A0"/>
        </g>
        <g transform="translate(75,30)">
          <ellipse cx="0" cy="-6" rx="3.5" ry="6" fill="#C97B8A" transform="rotate(0)"/>
          <ellipse cx="0" cy="-6" rx="3.5" ry="6" fill="#C97B8A" transform="rotate(72)"/>
          <ellipse cx="0" cy="-6" rx="3.5" ry="6" fill="#E8B4B8" transform="rotate(144)"/>
          <ellipse cx="0" cy="-6" rx="3.5" ry="6" fill="#E8B4B8" transform="rotate(216)"/>
          <ellipse cx="0" cy="-6" rx="3.5" ry="6" fill="#C97B8A" transform="rotate(288)"/>
          <circle cx="0" cy="0" r="2.5" fill="#F5D5A0"/>
        </g>
        <g transform="translate(115,27)">
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#EDCFD1" transform="rotate(0)"/>
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#E8B4B8" transform="rotate(72)"/>
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#EDCFD1" transform="rotate(144)"/>
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#E8B4B8" transform="rotate(216)"/>
          <ellipse cx="0" cy="-7" rx="4" ry="7" fill="#EDCFD1" transform="rotate(288)"/>
          <circle cx="0" cy="0" r="3" fill="#F5D5A0"/>
        </g>
        <g transform="translate(158,17)">
          <ellipse cx="0" cy="-5.5" rx="3" ry="5.5" fill="#E8B4B8" transform="rotate(0)"/>
          <ellipse cx="0" cy="-5.5" rx="3" ry="5.5" fill="#C97B8A" transform="rotate(72)"/>
          <ellipse cx="0" cy="-5.5" rx="3" ry="5.5" fill="#E8B4B8" transform="rotate(144)"/>
          <ellipse cx="0" cy="-5.5" rx="3" ry="5.5" fill="#EDCFD1" transform="rotate(216)"/>
          <ellipse cx="0" cy="-5.5" rx="3" ry="5.5" fill="#C97B8A" transform="rotate(288)"/>
          <circle cx="0" cy="0" r="2" fill="#F5D5A0"/>
        </g>
        <ellipse cx="55" cy="50" rx="3" ry="5" fill="#E8B4B8" transform="rotate(-30,55,50)" opacity="0.7"/>
        <ellipse cx="95" cy="48" rx="2.5" ry="4.5" fill="#C97B8A" transform="rotate(20,95,48)" opacity="0.6"/>
        <ellipse cx="140" cy="44" rx="2" ry="4" fill="#EDCFD1" transform="rotate(-15,140,44)" opacity="0.7"/>
      </g>
    </svg>
    """

def dancheong_divider():
    return """
    <div style="margin:16px 0;">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 12" width="100%" height="12">
      <rect x="0"   width="40" height="12" fill="#C0392B"/>
      <rect x="40"  width="40" height="12" fill="#B8973A"/>
      <rect x="80"  width="40" height="12" fill="#6B8E7B"/>
      <rect x="120" width="40" height="12" fill="#3B5E8C"/>
      <rect x="160" width="40" height="12" fill="#B8973A"/>
      <rect x="200" width="40" height="12" fill="#C0392B"/>
      <rect x="240" width="40" height="12" fill="#B8973A"/>
      <rect x="280" width="40" height="12" fill="#6B8E7B"/>
      <rect x="320" width="40" height="12" fill="#3B5E8C"/>
      <rect x="360" width="40" height="12" fill="#B8973A"/>
      <rect x="400" width="40" height="12" fill="#C0392B"/>
      <rect x="440" width="40" height="12" fill="#B8973A"/>
      <rect x="480" width="40" height="12" fill="#6B8E7B"/>
      <rect x="520" width="40" height="12" fill="#3B5E8C"/>
      <rect x="560" width="40" height="12" fill="#B8973A"/>
      <polygon points="20,0 26,6 20,12 14,6"    fill="rgba(255,255,255,0.25)"/>
      <polygon points="60,0 66,6 60,12 54,6"    fill="rgba(255,255,255,0.25)"/>
      <polygon points="100,0 106,6 100,12 94,6"  fill="rgba(255,255,255,0.25)"/>
      <polygon points="140,0 146,6 140,12 134,6" fill="rgba(255,255,255,0.25)"/>
      <polygon points="180,0 186,6 180,12 174,6" fill="rgba(255,255,255,0.25)"/>
      <polygon points="220,0 226,6 220,12 214,6" fill="rgba(255,255,255,0.25)"/>
      <polygon points="260,0 266,6 260,12 254,6" fill="rgba(255,255,255,0.25)"/>
      <polygon points="300,0 306,6 300,12 294,6" fill="rgba(255,255,255,0.25)"/>
      <polygon points="340,0 346,6 340,12 334,6" fill="rgba(255,255,255,0.25)"/>
      <polygon points="380,0 386,6 380,12 374,6" fill="rgba(255,255,255,0.25)"/>
      <polygon points="420,0 426,6 420,12 414,6" fill="rgba(255,255,255,0.25)"/>
      <polygon points="460,0 466,6 460,12 454,6" fill="rgba(255,255,255,0.25)"/>
      <polygon points="500,0 506,6 500,12 494,6" fill="rgba(255,255,255,0.25)"/>
      <polygon points="540,0 546,6 540,12 534,6" fill="rgba(255,255,255,0.25)"/>
      <polygon points="580,0 586,6 580,12 574,6" fill="rgba(255,255,255,0.25)"/>
    </svg>
    </div>
    """

def page_header(title, subtitle=""):
    sub_html = (
        f'<p style="font-family:Times New Roman,Times,serif;color:#6E5E4A;'
        f'margin-top:-6px;font-size:15px;">{subtitle}</p>'
    ) if subtitle else ""
    return (
        f'<div style="margin-bottom:4px;">'
        f'<h2 style="font-family:Black Han Sans,sans-serif;color:#8B1A1A;'
        f'letter-spacing:2px;margin-bottom:4px;">{title}</h2>'
        f'{sub_html}</div>'
    ) + dancheong_divider()


# ══════════════════════════════════════════════════
# FONT HELPER
# ══════════════════════════════════════════════════
def fmt(text):
    """Wrap text in the correct font span."""
    if re.search(r"[\u3131-\uD79D]", str(text)):
        return f"<span style='font-family:Nanum Myeongjo,serif;'>{text}</span>"
    return f"<span style='font-family:Times New Roman,Times,serif;'>{text}</span>"


# ══════════════════════════════════════════════════
# GROQ CLIENT  —  cached, initialised once
# ══════════════════════════════════════════════════
@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

client = get_client()
MODEL  = "llama3-8b-8192"


# ══════════════════════════════════════════════════
# PROGRESS HELPERS
# ══════════════════════════════════════════════════
PROGRESS_FILE = "progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"xp": 0, "quizzes_taken": 0, "correct_answers": 0, "assignments_done": 0}

def save_progress(p):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(p, f)


# ══════════════════════════════════════════════════
# AI HELPERS
# ══════════════════════════════════════════════════
def groq_chat(messages, system=None, max_tokens=1500):
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.extend(messages)
    resp = client.chat.completions.create(model=MODEL, messages=msgs, max_tokens=max_tokens)
    return resp.choices[0].message.content.strip()

def clean_raw(raw):
    """Strip markdown fences, leading/trailing backticks."""
    raw = re.sub(r"```[a-zA-Z]*", "", raw)
    return raw.strip().strip("`").strip()

def extract_json_list(raw):
    raw = clean_raw(raw)
    # Try direct parse first
    try:
        return json.loads(raw)
    except Exception:
        pass
    # Try extracting array
    m = re.search(r"\[.*\]", raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            # Try encoding fix for escaped unicode
            try:
                return json.loads(m.group(0).encode().decode("unicode_escape").encode("latin-1").decode("utf-8"))
            except Exception:
                pass
    return None

def extract_json_obj(raw):
    raw = clean_raw(raw)
    # Try direct parse first
    try:
        return json.loads(raw)
    except Exception:
        pass
    # Try extracting object — use a greedy match from first { to last }
    start = raw.find("{")
    end   = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = raw[start:end+1]
        try:
            return json.loads(candidate)
        except Exception:
            # Attempt to fix common LLM issues: unescaped newlines inside strings
            try:
                fixed = re.sub(r'(?<!\\)\n', ' ', candidate)
                return json.loads(fixed)
            except Exception:
                pass
    return None

def generate_flashcards(topic):
    prompt = (
        f'Create 5 Korean flashcards about "{topic}". '
        f'Each side max 5 words. Front = Korean, Back = English. '
        f'Output ONLY a JSON array: [{{"front":"학교","back":"School"}}]'
    )
    try:
        raw = groq_chat([{"role": "user", "content": prompt}],
                        system="Output only a valid JSON array, no other text.")
        data = extract_json_list(raw)
        if data:
            return data
    except Exception as e:
        st.error(f"⚠️ Flashcard error: {e}")
    return [{"front": "학교", "back": "School"}]

def generate_quiz(topic_prompt):
    prompt = (
        f'{topic_prompt} '
        f'Create exactly 10 multiple-choice questions. '
        f'CRITICAL RULE: The "answer" field MUST be copied EXACTLY (same spelling, same capitalisation, '
        f'same punctuation) from one of the 4 options in the "options" array. '
        f'Output ONLY a JSON array, no markdown, no extra text: '
        f'[{{"question":"...","options":["Option A","Option B","Option C","Option D"],"answer":"Option A"}}]'
    )
    try:
        raw = groq_chat([{"role": "user", "content": prompt}],
                        system=(
                            "You are a JSON-only quiz generator. "
                            "Output only a valid JSON array. "
                            "The answer field must be an exact copy of one of the options strings."
                        ))
        data = extract_json_list(raw)
        if data:
            # Normalise: ensure answer matches an option exactly (case-insensitive fallback)
            for q in data:
                ans = q.get("answer", "")
                opts = q.get("options", [])
                if ans not in opts:
                    # Try to find the closest matching option
                    for opt in opts:
                        if opt.strip().lower() == ans.strip().lower():
                            q["answer"] = opt  # replace with exact option text
                            break
            return data
    except Exception as e:
        st.error(f"⚠️ Quiz error: {e}")
    return [{"question": "What does '학교' mean?",
             "options": ["School", "Book", "Friend", "Teacher"],
             "answer": "School"}]

def generate_assignment(topic):
    prompt = f"Create 2 practical Korean learning assignments about '{topic}'."
    try:
        return groq_chat([{"role": "user", "content": prompt}])
    except Exception as e:
        st.error(f"⚠️ Assignment error: {e}")
    return "Write 5 sentences using the word '학교'."

def generate_wellness(feeling):
    prompt = (
        f"Motivational message (~35 words) for someone feeling '{feeling}'. "
        f"Exactly 3 emojis. Include Korean quote + English translation. "
        f'Output ONLY JSON: {{"motivation":"...","korean_quote":"...","english_translation":"..."}}'
    )
    try:
        raw = groq_chat([{"role": "user", "content": prompt}],
                        system="Output only valid JSON, no other text.")
        data = extract_json_obj(raw)
        if data:
            return data
    except Exception as e:
        st.error(f"⚠️ Wellness error: {e}")
    return {
        "motivation": "💪 You've got this! Keep going! 😊",
        "korean_quote": "천 리 길도 한 걸음부터다",
        "english_translation": "A journey of a thousand miles begins with a single step."
    }

# Fallback stories so the section never shows empty
_FALLBACK_STORIES = [
    {
        "name_korean": "유관순",
        "name_english": "Yu Gwan-sun",
        "korean_story": "유관순은 1902년 충청남도에서 태어났습니다. 일제강점기 시절, 그녀는 조국의 독립을 위해 싸웠습니다. 1919년 3.1 운동 당시 고향에서 만세운동을 이끌다 체포되어 서대문 형무소에 갇혔습니다. 모진 고문에도 굴하지 않고 옥중에서도 대한독립만세를 외쳤으며, 18세의 나이로 순국하였습니다. 그녀의 용기와 희생은 오늘날에도 많은 이들에게 감동을 줍니다.",
        "english_story": "Yu Gwan-sun was born in 1902 in South Chungcheong Province. During the Japanese occupation, she fought bravely for Korean independence. During the March 1st Movement of 1919, she led a protest in her hometown and was arrested. Even under brutal torture in Seodaemun Prison, she never stopped crying out for independence. She died at just 18 years old. Her courage and sacrifice continue to inspire generations of Koreans.",
        "moral_korean": "진정한 용기는 두려움이 없는 것이 아니라, 두려움보다 더 중요한 것을 위해 싸우는 것이다.",
        "moral_english": "True courage is not the absence of fear, but fighting for something more important than fear."
    },
    {
        "name_korean": "세종대왕",
        "name_english": "King Sejong the Great",
        "korean_story": "세종대왕은 조선의 네 번째 왕으로, 1397년에 태어났습니다. 그는 백성들이 글을 읽고 쓸 수 있도록 1443년에 한글을 창제하였습니다. 당시 한자는 배우기 어려워 일반 백성들은 문자를 사용하지 못했습니다. 세종은 과학, 음악, 농업 등 다양한 분야에서도 큰 업적을 남겼으며, 측우기와 같은 과학 기구를 발명하게 했습니다. 그의 업적은 오늘날까지 한국 문화의 근간이 되고 있습니다.",
        "english_story": "King Sejong was the fourth king of the Joseon Dynasty, born in 1397. Seeing that ordinary people could not read because Chinese characters were too difficult, he created Hangeul in 1443 — a simple, scientific alphabet designed for everyone. He also made great achievements in science, music, and agriculture, commissioning inventions like the rain gauge. His legacy remains the foundation of Korean culture and identity to this day.",
        "moral_korean": "지식은 모든 사람의 것이어야 한다. 배움의 문은 누구에게나 열려 있어야 한다.",
        "moral_english": "Knowledge belongs to everyone. The door to learning must be open to all."
    },
    {
        "name_korean": "이순신",
        "name_english": "Admiral Yi Sun-sin",
        "korean_story": "이순신 장군은 1545년에 태어나 조선 최고의 해군 장수가 되었습니다. 임진왜란 당시 그는 거북선을 이용해 일본 수군을 연이어 격파하였습니다. 부하들의 신뢰를 받으며 단 한 번도 패전하지 않은 그는 명량 해전에서 단 12척의 배로 133척의 적선을 물리치는 기적을 이루었습니다. 1598년 노량 해전에서 전사하였지만, 그의 나라 사랑과 불굴의 의지는 영원히 기억됩니다.",
        "english_story": "Admiral Yi Sun-sin was born in 1545 and became Korea's greatest naval commander. During the Japanese invasions, he used the famous Turtle Ship to defeat enemy fleets repeatedly. Beloved by his soldiers and never defeated in battle, he achieved the miracle of the Battle of Myeongnyang — defeating 133 enemy ships with only 12. He died in battle in 1598, but his patriotism and indomitable spirit are remembered forever.",
        "moral_korean": "한 번도 포기하지 않는 사람은 절대 패배하지 않는다.",
        "moral_english": "A person who never gives up can never truly be defeated."
    }
]

def generate_story():
    import random
    # Pick a random person to avoid always getting Sejong
    subjects = [
        ("유관순", "Yu Gwan-sun", "a young female independence activist during Japanese occupation"),
        ("안창호", "Ahn Chang-ho", "an educator and independence movement leader"),
        ("김구", "Kim Gu", "a prominent independence activist and politician"),
        ("신사임당", "Shin Saimdang", "a renowned artist, poet and scholar of the Joseon era"),
        ("장영실", "Jang Yeong-sil", "a low-born inventor who rose to greatness under King Sejong"),
        ("허준", "Heo Jun", "a royal physician who wrote the Dongui Bogam medical encyclopedia"),
    ]
    name_ko, name_en, desc = random.choice(subjects)

    prompt = (
        f"Write an inspiring story about the Korean historical figure {name_en} ({name_ko}), "
        f"who was {desc}. "
        f"Include their struggles, key turning point, and greatest achievement. "
        f"Keep each section to 3-4 sentences. "
        f"Use this EXACT format with these EXACT field names, nothing else:\n"
        f"NAME_KOREAN: {name_ko}\n"
        f"NAME_ENGLISH: {name_en}\n"
        f"KOREAN_STORY: <write 3-4 sentences in Korean here>\n"
        f"ENGLISH_STORY: <write 3-4 sentences in English here>\n"
        f"MORAL_KOREAN: <one sentence moral in Korean>\n"
        f"MORAL_ENGLISH: <one sentence moral in English>"
    )
    try:
        raw = groq_chat(
            [{"role": "user", "content": prompt}],
            system=(
                "You are a bilingual Korean storyteller. "
                "Follow the format exactly. "
                "Write Korean as real Korean characters. "
                "Do not use JSON. Do not add extra commentary."
            ),
            max_tokens=800
        )
        # Parse the plain-text labelled format — much more reliable than JSON
        def extract_field(label, text):
            pattern = rf"{label}:\s*(.+?)(?=\n[A-Z_]+:|$)"
            m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            return m.group(1).strip() if m else ""

        result = {
            "name_korean":   extract_field("NAME_KOREAN",   raw),
            "name_english":  extract_field("NAME_ENGLISH",  raw),
            "korean_story":  extract_field("KOREAN_STORY",  raw),
            "english_story": extract_field("ENGLISH_STORY", raw),
            "moral_korean":  extract_field("MORAL_KOREAN",  raw),
            "moral_english": extract_field("MORAL_ENGLISH", raw),
        }
        # If we got at least english_story, it worked
        if result["english_story"]:
            return result
    except Exception as e:
        st.error(f"⚠️ Story generation error: {e}")

    # Return a random fallback story rather than None
    return random.choice(_FALLBACK_STORIES)


# ══════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════
_defaults = {
    "chat_history":     [],
    "flashcards":       [],
    "flashcards_topic": "",
    "quizzes":          [],
    "quiz_topic":       "",
    "answers":          {},
    "assignments":      "",
    "assignment_topic": "",
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
if "progress" not in st.session_state:
    st.session_state.progress = load_progress()


# ══════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        f'<div style="text-align:center;padding:12px 0 10px;">{blossom_svg()}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='text-align:center;padding:4px 0 6px;'>"
        "<h2 style='margin:0;letter-spacing:3px;font-family:Nanum Myeongjo,serif;"
        "color:#F5D5A0;font-size:22px;'>한국어 배우기</h2>"
        "<p style='margin:4px 0 0;font-size:13px;opacity:0.8;"
        "font-family:Times New Roman,Times,serif;color:#EDE0CC;'>Korean Learning</p>"
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='height:2px;background:linear-gradient(90deg,transparent,#B8973A,transparent);"
        "margin:10px 16px 14px;'></div>",
        unsafe_allow_html=True
    )
    mode = st.radio("", [
        "🤖 Chatbot",
        "📖 Flashcards",
        "📝 Quizzes",
        "✍️ Assignments",
        "💖 Wellness",
        "🎤 Korean Inspiration",
        "📊 Dashboard",
    ], label_visibility="collapsed")

    xp    = st.session_state.progress["xp"]
    level = xp // 100
    st.markdown("---")
    st.markdown(
        f"<div style='text-align:center;padding:10px;"
        f"background:rgba(184,151,58,0.2);border-radius:6px;"
        f"border:1px solid rgba(184,151,58,0.5);'>"
        f"<span style='font-size:22px;'>🌸</span><br>"
        f"<b style='color:#F5D5A0;font-size:18px;"
        f"font-family:Black Han Sans,sans-serif;'>Lv. {level}</b><br>"
        f"<span style='font-size:12px;color:#e0cfa8;"
        f"font-family:Times New Roman,Times,serif;'>{xp} XP</span>"
        f"</div>",
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════
# MODE: CHATBOT
# ══════════════════════════════════════════════════
if mode == "🤖 Chatbot":
    st.markdown(page_header("🤖 Chatbot",
                            "Ask me anything about Korean language & culture"),
                unsafe_allow_html=True)

    col1, col2 = st.columns([8, 1])
    with col1:
        user_input = st.text_input("Message", key="chat_box",
                                   label_visibility="collapsed",
                                   placeholder="💬 Type your message here…")
    with col2:
        send = st.button("전송")

    if send and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        try:
            reply = groq_chat(st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"⚠️ Chat error: {e}")
        st.rerun()

    st.markdown('<div class="chat-scroll">', unsafe_allow_html=True)
    if not st.session_state.chat_history:
        st.markdown(
            "<p style='text-align:center;color:#9E8C78;font-style:italic;"
            "padding-top:40px;font-family:Times New Roman,Times,serif;'>"
            "안녕하세요! · Begin your conversation below 🌸</p>",
            unsafe_allow_html=True
        )
    for msg in st.session_state.chat_history:
        css  = "user-bubble" if msg["role"] == "user" else "bot-bubble"
        lbl  = "🧑 You"      if msg["role"] == "user" else "🤖 Bot"
        st.markdown(
            f"<div class='{css}'><b>{lbl}</b><br>{fmt(msg['content'])}</div>",
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# MODE: FLASHCARDS
# ══════════════════════════════════════════════════
elif mode == "📖 Flashcards":
    st.markdown(page_header("📖 Flashcards",
                            "Click a card to flip and reveal the translation"),
                unsafe_allow_html=True)

    topic = st.text_input("Topic", placeholder="e.g. animals, food, K-drama phrases…",
                          label_visibility="collapsed")
    if st.button("Generate Flashcards 🌸") and topic:
        with st.spinner("Generating cards…"):
            st.session_state.flashcards       = generate_flashcards(topic)
            st.session_state.flashcards_topic = topic

    if st.session_state.flashcards:
        st.markdown(
            f"<p style='color:#6E5E4A;font-style:italic;"
            f"font-family:Times New Roman,Times,serif;'>"
            f"Cards for: <b>{st.session_state.flashcards_topic}</b> — click to flip</p>",
            unsafe_allow_html=True
        )
        st.markdown('<div class="flashcards-grid">', unsafe_allow_html=True)
        for card in st.session_state.flashcards:
            front = fmt(card.get("front", ""))
            back  = fmt(card.get("back",  ""))
            st.markdown(f"""
            <label class="card">
                <input type="checkbox"/>
                <div class="card-inner">
                    <div class="card-face card-front">{front}</div>
                    <div class="card-face card-back">{back}</div>
                </div>
            </label>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# MODE: QUIZZES
# ══════════════════════════════════════════════════
elif mode == "📝 Quizzes":
    st.markdown(page_header("📝 Quizzes", "Test your Korean knowledge"),
                unsafe_allow_html=True)

    quiz_type = st.radio("Quiz type:", ["Vocabulary", "Grammar", "General"],
                         key="quiz_type", horizontal=True)

    if quiz_type == "Vocabulary":
        vocab_topic = st.text_input("Vocabulary topic:",
                                    placeholder="e.g. food, family, travel")
        if st.button("Generate Vocabulary Quiz 🌸") and vocab_topic:
            with st.spinner("Generating quiz…"):
                st.session_state.quizzes = generate_quiz(
                    f"Korean vocabulary quiz on '{vocab_topic}'. "
                    f"Give English words, Korean-related answer options. All questions in English."
                )
                st.session_state.answers = {}

    elif quiz_type == "Grammar":
        grammar_topic = st.selectbox("Grammar focus:", [
            "Sentence formation (Subject-Object-Verb)",
            "Particles and markers (이/가, 을/를, 은/는)",
            "Honorifics and politeness levels",
            "Verb conjugations",
            "Connectives (-고, -지만, -서)",
            "Tenses and aspect",
        ], key="grammar_topic")
        if st.button("Generate Grammar Quiz 🌸"):
            with st.spinner("Generating quiz…"):
                st.session_state.quizzes = generate_quiz(
                    f"Korean grammar quiz about '{grammar_topic}'. All questions in English."
                )
                st.session_state.answers = {}

    elif quiz_type == "General":
        general_topic = st.text_input("General topic:",
                                      placeholder="e.g. K-pop, Joseon Dynasty, Korean food")
        if st.button("Generate General Quiz 🌸") and general_topic:
            with st.spinner("Generating quiz…"):
                st.session_state.quizzes = generate_quiz(
                    f"General knowledge quiz about '{general_topic}' "
                    f"related to Korean culture. All in English."
                )
                st.session_state.answers = {}

    if st.session_state.get("quizzes"):
        st.markdown(dancheong_divider(), unsafe_allow_html=True)
        for i, q in enumerate(st.session_state.quizzes, 1):
            st.markdown(f"**Q{i}. {q['question']}**")
            sel = st.radio("", q["options"],
                           key=f"q_{i}_{quiz_type}",
                           label_visibility="collapsed")
            st.session_state.answers[i] = sel

        if st.button("Check Answers ✅"):
            def answers_match(user_ans, correct_ans, options):
                if user_ans is None:
                    return False
                if user_ans == correct_ans:
                    return True
                u = user_ans.strip().lower()
                c = correct_ans.strip().lower()
                if u == c:
                    return True
                if u in c or c in u:
                    return True
                # Find closest option to the stated answer key
                best_option = min(options, key=lambda o: abs(len(o) - len(correct_ans)))
                if best_option.strip().lower() == u:
                    return True
                return False

            correct = 0
            for i, q in enumerate(st.session_state.quizzes, 1):
                user_ans    = st.session_state.answers.get(i)
                correct_ans = q["answer"]
                options     = q.get("options", [])
                if answers_match(user_ans, correct_ans, options):
                    st.success(f"Q{i}: ✅ Correct!")
                    correct += 1
                else:
                    st.error(f"Q{i}: ❌ Wrong — correct answer: **{correct_ans}**")
            st.session_state.progress["quizzes_taken"]   += 1
            st.session_state.progress["correct_answers"] += correct
            st.session_state.progress["xp"]              += correct * 10
            save_progress(st.session_state.progress)
            st.info(f"🌸 Score: {correct}/{len(st.session_state.quizzes)}  ·  +{correct * 10} XP")


# ══════════════════════════════════════════════════
# MODE: ASSIGNMENTS
# ══════════════════════════════════════════════════
elif mode == "✍️ Assignments":
    st.markdown(page_header("✍️ Assignments", "Practice makes perfect"),
                unsafe_allow_html=True)

    topic = st.text_input("Assignment topic:",
                          placeholder="e.g. greetings, shopping, school life")
    if st.button("Generate Assignment 🌸") and topic:
        with st.spinner("Generating assignment…"):
            st.session_state.assignments      = generate_assignment(topic)
            st.session_state.assignment_topic = topic
            st.session_state.progress["assignments_done"] += 1
            st.session_state.progress["xp"]               += 20
            save_progress(st.session_state.progress)
        st.info("🌸 +20 XP earned!")

    if st.session_state.assignments:
        st.markdown(
            f"<h3 style='color:#8B1A1A;font-family:Black Han Sans,sans-serif;'>"
            f"Assignments on: {st.session_state.assignment_topic}</h3>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='background:rgba(255,255,255,0.55);"
            f"border:1.5px solid #B8973A;border-radius:8px;"
            f"padding:20px 24px;font-family:Times New Roman,Times,serif;"
            f"font-size:16px;line-height:1.9;'>"
            f"{st.session_state.assignments}</div>",
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════
# MODE: WELLNESS
# ══════════════════════════════════════════════════
elif mode == "💖 Wellness":
    st.markdown(page_header("💖 Wellness Check",
                            "마음 건강 · Take care of your heart"),
                unsafe_allow_html=True)

    feeling = st.text_input("How are you feeling today?",
                            placeholder="e.g. tired, excited, overwhelmed…",
                            key="wellness_feeling")
    if st.button("Get Motivation 🌸") and feeling:
        with st.spinner("Preparing your message…"):
            data = generate_wellness(feeling)
            st.session_state.latest_wellness = {
                "feeling":             feeling,
                "motivation":          data.get("motivation", "💪 Keep going!"),
                "korean_quote":        data.get("korean_quote", "천 리 길도 한 걸음부터다"),
                "english_translation": data.get("english_translation",
                    "A journey of a thousand miles begins with a single step.")
            }

    if "latest_wellness" in st.session_state:
        w = st.session_state.latest_wellness
        st.markdown(f"""
        <label class="wellness-card">
            <input type="checkbox"/>
            <div class="wellness-card-inner">
                <div class="wellness-card-front">
                    🌸<br><br>
                    <span style='font-size:18px;font-family:Times New Roman,Times,serif;'>
                        Click to reveal your<br>daily motivation
                    </span><br><br>
                    <span style='font-size:13px;opacity:0.75;
                        font-family:Nanum Myeongjo,serif;'>마음을 담아</span>
                </div>
                <div class="wellness-card-back">
                    <b style='color:#F5D5A0;font-size:15px;'>Feeling:</b><br>
                    <span style='font-family:Times New Roman,Times,serif;color:#F5EDD8;'>{w['feeling']}</span>
                    <br><br>
                    <b style='color:#F5D5A0;font-size:15px;'>Motivation:</b><br>
                    <span style='font-family:Times New Roman,Times,serif;color:#F5EDD8;'>{w['motivation']}</span>
                    <br><br>
                    <b style='color:#F5D5A0;font-size:15px;'>Korean Quote:</b><br>
                    <span style='font-family:Nanum Myeongjo,serif;font-size:20px;color:#E8B4B8;'>
                        {w['korean_quote']}
                    </span><br>
                    <i style='color:#c8dfc8;font-family:Times New Roman,Times,serif;font-size:14px;'>
                        {w['english_translation']}
                    </i>
                </div>
            </div>
        </label>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# MODE: KOREAN INSPIRATION
# ══════════════════════════════════════════════════
elif mode == "🎤 Korean Inspiration":
    st.markdown(page_header("🎤 Inspiring Korean Stories",
                            "영감을 주는 이야기 · Stories that move the soul"),
                unsafe_allow_html=True)

    if "latest_story" not in st.session_state:
        with st.spinner("Loading a story…"):
            st.session_state.latest_story = generate_story()

    if st.button("✨ New Story"):
        with st.spinner("Generating story…"):
            st.session_state.latest_story = generate_story()

    if st.session_state.latest_story:
        s = st.session_state.latest_story
        st.markdown(f"""
        <div class="story-card">
            <h3>🌸
                <span style='font-family:Nanum Myeongjo,serif;'>{s['name_korean']}</span>
                · <span style='font-family:Times New Roman,Times,serif;'>{s['name_english']}</span>
            </h3>
            <p><b style='color:#B8973A;'>Korean Story:</b><br>
               <span style='font-family:Nanum Myeongjo,serif;'>{s['korean_story']}</span></p>
            <p><b style='color:#B8973A;'>English Story:</b><br>
               <span style='font-family:Times New Roman,Times,serif;'>{s['english_story']}</span></p>
            <p class="moral">
               🌸 <span style='font-family:Nanum Myeongjo,serif;'>{s['moral_korean']}</span><br>
               <i style='font-family:Times New Roman,Times,serif;'>({s['moral_english']})</i>
            </p>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# MODE: DASHBOARD
# ══════════════════════════════════════════════════
elif mode == "📊 Dashboard":
    st.markdown(page_header("📊 Dashboard",
                            "나의 여정 · Track your learning journey"),
                unsafe_allow_html=True)

    prog        = st.session_state.progress
    xp          = prog["xp"]
    level       = xp // 100
    xp_progress = xp % 100

    st.markdown(
        f"<div style='background:rgba(139,26,26,0.08);border:2px solid #B8973A;"
        f"border-radius:10px;padding:16px 22px;margin-bottom:16px;'>"
        f"<span style='font-family:Black Han Sans,sans-serif;font-size:26px;"
        f"color:#8B1A1A;'>🌸 Level {level}</span>"
        f"<span style='font-family:Times New Roman,Times,serif;color:#6E5E4A;"
        f"font-size:15px;'> · {xp} XP total</span></div>",
        unsafe_allow_html=True
    )
    st.progress(xp_progress / 100)
    st.caption(f"{xp_progress} / 100 XP to next level")

    st.markdown(dancheong_divider(), unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("📝 Quizzes Taken",    prog.get("quizzes_taken", 0))
    c2.metric("✅ Correct Answers",   prog.get("correct_answers", 0))
    c3.metric("✍️ Assignments Done",  prog.get("assignments_done", 0))

    import pandas as pd
    import matplotlib.pyplot as plt

    st.markdown("<h3 style='margin-top:20px;'>📊 XP Growth</h3>", unsafe_allow_html=True)
    xp_df = pd.DataFrame({
        "XP":    [10, 30, 60, max(xp, 60)],
        "Stage": ["Day 1", "Day 2", "Day 3", "Now"]
    })
    fig, ax = plt.subplots(figsize=(7, 3))
    fig.patch.set_facecolor("#F5EDD8")
    ax.set_facecolor("#F5EDD8")
    ax.plot(xp_df["Stage"], xp_df["XP"],
            marker="o", color="#8B1A1A", linewidth=2.5,
            markerfacecolor="#B8973A", markersize=9)
    ax.fill_between(xp_df["Stage"], xp_df["XP"], alpha=0.15, color="#C0392B")
    ax.set_ylabel("XP", color="#4a2a18")
    ax.set_xlabel("Progress", color="#4a2a18")
    ax.tick_params(colors="#4a2a18")
    for spine in ax.spines.values():
        spine.set_edgecolor("#B8973A")
    st.pyplot(fig)

    st.markdown(dancheong_divider(), unsafe_allow_html=True)

    recent = [
        ("📝 Last quiz topic",       st.session_state.quiz_topic),
        ("📖 Last flashcards topic", st.session_state.flashcards_topic),
        ("✍️ Last assignment topic", st.session_state.assignment_topic),
    ]
    shown = [(lbl, val) for lbl, val in recent if val]
    if shown:
        st.markdown("<h3>🗂 Recent Topics</h3>", unsafe_allow_html=True)
        for lbl, val in shown:
            st.write(f"{lbl}: **{val}**")

    if st.button("🔄 Reset Progress"):
        st.session_state.progress = {
            "xp": 0, "quizzes_taken": 0,
            "correct_answers": 0, "assignments_done": 0
        }
        save_progress(st.session_state.progress)
        st.success("Progress reset! 새로 시작합니다 🌸")
        st.rerun()
