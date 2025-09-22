import sqlite3, time, datetime

DB_NAME = "flashcards.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Flashcards
    c.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            korean TEXT,
            english TEXT,
            example TEXT,
            interval INTEGER,
            next_review REAL
        )
    ''')

    # Quizzes
    c.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            question TEXT,
            options TEXT,
            answer TEXT,
            user_answer TEXT,
            correct INTEGER,
            timestamp REAL
        )
    ''')

    # Assignments
    c.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            task TEXT,
            user_response TEXT,
            feedback TEXT,
            timestamp REAL
        )
    ''')

    # Streaks
    c.execute('''
        CREATE TABLE IF NOT EXISTS streaks (
            date TEXT PRIMARY KEY
        )
    ''')

    # XP system
    c.execute('''
        CREATE TABLE IF NOT EXISTS xp (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            points INTEGER DEFAULT 0
        )
    ''')
    c.execute("INSERT OR IGNORE INTO xp (id, points) VALUES (1, 0)")

    conn.commit()
    conn.close()

# ---------------- FLASHCARDS ----------------
def add_flashcards(topic, cards):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for card in cards:
        c.execute('''
            INSERT INTO flashcards (topic, korean, english, example, interval, next_review)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (topic, card["korean"], card["english"], card["example"], 1, time.time()))
    conn.commit()
    conn.close()

def get_due_cards():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = time.time()
    c.execute("SELECT id, korean, english, example, interval, next_review FROM flashcards WHERE next_review <= ?", (now,))
    cards = c.fetchall()
    conn.close()
    return cards

def update_card(card_id, interval, next_review):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE flashcards SET interval=?, next_review=? WHERE id=?", (interval, next_review, card_id))
    conn.commit()
    conn.close()

def get_flashcard_stats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM flashcards")
    total = c.fetchone()[0]

    now = time.time()
    c.execute("SELECT COUNT(*) FROM flashcards WHERE next_review <= ?", (now,))
    due = c.fetchone()[0]

    c.execute("SELECT interval, COUNT(*) FROM flashcards GROUP BY interval")
    interval_data = c.fetchall()

    conn.close()
    return total, due, interval_data

# ---------------- QUIZZES ----------------
def save_quiz_result(topic, question, options, answer, user_answer, correct):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO quizzes (topic, question, options, answer, user_answer, correct, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (topic, question, str(options), answer, user_answer, int(correct), time.time()))
    conn.commit()
    conn.close()

def get_quiz_accuracy():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(correct) FROM quizzes")
    total, correct = c.fetchone()
    conn.close()
    return total, correct if correct else 0

# ---------------- ASSIGNMENTS ----------------
def add_assignment(topic, task, user_response, feedback):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO assignments (topic, task, user_response, feedback, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (topic, task, user_response, feedback, time.time()))
    conn.commit()
    conn.close()

def get_assignment_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT topic, task, user_response, feedback, timestamp FROM assignments ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# ---------------- STREAKS ----------------
def log_activity():
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO streaks (date) VALUES (?)", (today,))
    conn.commit()
    conn.close()

def get_streaks():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date FROM streaks ORDER BY date ASC")
    dates = [datetime.date.fromisoformat(row[0]) for row in c.fetchall()]
    conn.close()

    if not dates:
        return 0, 0

    longest, current = 1, 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days == 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    if (datetime.date.today() - dates[-1]).days == 0:
        return current, longest
    else:
        return 0, longest

# ---------------- XP ----------------
def add_xp(amount: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE xp SET points = points + ? WHERE id = 1", (amount,))
    conn.commit()
    conn.close()

def get_xp():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT points FROM xp WHERE id = 1")
    points = c.fetchone()[0]
    conn.close()

    level = points // 100 + 1
    xp_into_level = points % 100
    return points, level, xp_into_level
