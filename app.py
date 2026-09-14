import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# 1. Ρυθμίσεις Σελίδας
st.set_page_config(page_title="Πρωτάθλημα Πληροφορικής", page_icon="🏆", layout="wide")

# 2. Σύνδεση με τον SQL Server (nikosn_1QUIZ) μέσω st.secrets
@st.cache_resource
def get_db_connection():
    try:
        db_user = st.secrets["sql"]["user"]        # TEACHER
        db_password = st.secrets["sql"]["password"]    # Audirs7!!!
        db_host = st.secrets["sql"]["host"]        # IP / Domain του Arvixe Server
        db_port = st.secrets["sql"]["port"]        # 1433
        db_name = st.secrets["sql"]["database"]    # nikosn_1QUIZ

        # Σύνδεση μέσω SQLAlchemy με pymssql
        connection_string = f"mssql+pymssql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        return create_engine(connection_string, pool_pre_ping=True)
    except Exception as e:
        st.error(f"❌ Σφάλμα σύνδεσης με τη βάση δεδομένων: {e}")
        st.stop()

engine = get_db_connection()

# 3. Βάση Δεδομένων Quiz (Νέες Παρόμοιες Ασκήσεις - Χωρίς τα δοκιμαστικά quiz)
QUIZZES = {
    "Γ.7.Μ1: Εισαγωγή στους Αλγορίθμους & Χαρακτηριστικά (Νέες Ασκήσεις)": [
        {
            "question": "1. Ποια από τις παρακάτω οδηγίες περιέχει ΑΣΑΦΕΙΑ (δεν ικανοποιεί το κριτήριο της Σαφήνειας);",
            "options": [
                "Πρόσθεσε 200 γραμμάρια αλεύρι στο μίγμα.",
                "Ψήσε το γλυκό στο φούρνο για λίγη ώρα.",
                "Ανακάτεψε το μίγμα για 3 λεπτά.",
                "Πρόσθεσε 2 αβγά."
            ],
            "answer": "Ψήσε το γλυκό στο φούρνο για λίγη ώρα."
        },
        {
            "question": "2. Ένας αλγόριθμος εκτελεί μια διαδικασία που δεν τελειώνει ποτέ (μπαίνει σε ατέρμονα βρόχο). Ποιο χαρακτηριστικό παραβιάζεται;",
            "options": [
                "Η Σαφήνεια / Καθοριστικότητα",
                "Η Είσοδος δεδομένων",
                "Η Περατότητα",
                "Η Αποτελεσματικότητα"
            ],
            "answer": "Η Περατότητα"
        },
        {
            "question": "3. Ποια είναι η σωστή σειρά εντολών για τον αλγόριθμο «Υπολογισμός Μέσου Όρου 3 Βαθμών»;\n1. Τύπωσε τον Μέσο Όρο\n2. Διάβασε τους βαθμούς Β1, Β2, Β3\n3. Υπολόγισε MO = (Β1 + Β2 + Β3) / 3",
            "options": [
                "1, 2, 3",
                "2, 3, 1",
                "3, 2, 1",
                "2, 1, 3"
            ],
            "answer": "2, 3, 1"
        },
        {
            "question": "4. Δίνεται ο αλγόριθμος για τη σχεδίαση ισόπλευρου τριγώνου πλευράς 10 cm:\n1. Σχεδίασε ευθύγραμμο τμήμα 10 cm\n2. Στρίψε δεξιά 120°\n3. Σχεδίασε ευθύγραμμο τμήμα 10 cm\n4. Στρίψε αριστερά 90°\n5. Σχεδίασε ευθύγραμμο τμήμα 10 cm\nΠοια εντολή περιέχει λάθος;",
            "options": [
                "Η εντολή 2",
                "Η εντολή 4 (πρέπει να στρίψει δεξιά 120°)",
                "Η εντολή 5",
                "Ο αλγόριθμος είναι πλήρως σωστός"
            ],
            "answer": "Η εντολή 4 (πρέπει να στρίψει δεξιά 120°)"
        },
        {
            "question": "5. Ποια είναι η σωστή σειρά εντολών για την αποστολή ενός μηνύματος e-mail;\n1. Πληκτρολογούμε το κείμενο του μηνύματος\n2. Πατάμε το κουμπί «Αποστολή»\n3. Ανοίγουμε την εφαρμογή ηλεκτρονικού ταχυδρομείου\n4. Γράφουμε τη διεύθυνση του παραλήπτη\n5. Πατάμε «Νέο Μήνυμα»",
            "options": [
                "3, 5, 4, 1, 2",
                "3, 4, 5, 1, 2",
                "5, 3, 4, 1, 2",
                "3, 1, 4, 5, 2"
            ],
            "answer": "3, 5, 4, 1, 2"
        },
        {
            "question": "6. Όταν λέμε ότι κάθε εντολή ενός αλγορίθμου πρέπει να είναι απλή και υλοποιήσιμη, αναφερόμαστε στο χαρακτηριστικό της:",
            "options": [
                "Σαφήνειας",
                "Περατότητας",
                "Αποτελεσματικότητας",
                "Εισόδου"
            ],
            "answer": "Αποτελεσματικότητας"
        },
        {
            "question": "7. Ποιο από τα παρακάτω ΣΤΑΔΙΑ ΔΕΝ ανήκει στον κύκλο ανάπτυξης ενός προγράμματος;",
            "options": [
                "Ανάλυση προβλήματος",
                "Σχεδιασμός αλγορίθμου",
                "Προγραμματισμός / Κωδικοποίηση",
                "Αγορά νέου υπολογιστή"
            ],
            "answer": "Αγορά νέου υπολογιστή"
        },
        {
            "question": "8. Ποια είναι η σωστή σειρά για τον υπολογισμό του κόστους περιφράξεως ενός οικοπέδου;\n1. Μετράμε το μήκος και το πλάτος του οικοπέδου\n2. Υπολογίζουμε την περίμετρο: 2 * μήκος + 2 * πλάτος\n3. Μαθαίνουμε την τιμή του συρματοπλέγματος ανά μέτρο\n4. Πολλαπλασιάζουμε την περίμετρο με την τιμή ανά μέτρο",
            "options": [
                "1, 3, 2, 4",
                "1, 2, 3, 4",
                "3, 1, 4, 2",
                "2, 1, 3, 4"
            ],
            "answer": "1, 3, 2, 4"
        }
    ]
}

# 4. Συναρτήσεις Βάσης Δεδομένων
def verify_student(username, password):
    query = text("SELECT Username, FirstName, LastName, ClassGroup FROM Students WHERE Username = :u AND Password = :p")
    with engine.connect() as conn:
        result = conn.execute(query, {"u": username, "p": password}).fetchone()
        if result:
            return {
                "username": result[0],
                "full_name": f"{result[1]} {result[2]}",
                "class": result[3]
            }
        return None

def save_or_update_score(username, lesson_name, new_score):
    with engine.begin() as conn:
        check_query = text("SELECT Score, Attempts FROM Leaderboard WHERE Username = :u AND LessonName = :l")
        existing = conn.execute(check_query, {"u": username, "l": lesson_name}).fetchone()

        if existing:
            current_best = existing[0]
            attempts = existing[1] + 1
            best_score = max(current_best, new_score)
            
            update_query = text("""
                UPDATE Leaderboard 
                SET Score = :score, Attempts = :attempts, LastUpdated = GETDATE()
                WHERE Username = :u AND LessonName = :l
            """)
            conn.execute(update_query, {"score": best_score, "attempts": attempts, "u": username, "l": lesson_name})
        else:
            insert_query = text("""
                INSERT INTO Leaderboard (Username, LessonName, Score, Attempts) 
                VALUES (:u, :l, :score, 1)
            """)
            conn.execute(insert_query, {"u": username, "l": lesson_name, "score": new_score})

def load_leaderboard(selected_lesson=None, selected_class=None):
    base_query = """
        SELECT 
            s.FirstName + ' ' + s.LastName AS [Μαθητής],
            s.ClassGroup AS [Τμήμα],
            l.LessonName AS [Μάθημα],
            l.Score AS [Βαθμολογία (%)],
            l.Attempts AS [Προσπάθειες]
        FROM Leaderboard l
        JOIN Students s ON l.Username = s.Username
    """
    
    conditions = []
    params = {}

    if selected_lesson and selected_lesson != "Όλα τα Μαθήματα":
        conditions.append("l.LessonName = :lesson")
        params["lesson"] = selected_lesson
        
    if selected_class and selected_class != "Όλα τα Τμήματα":
        conditions.append("s.ClassGroup = :cls")
        params["cls"] = selected_class

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += " ORDER BY l.Score DESC, l.Attempts ASC"
    
    return pd.read_sql(text(base_query), engine, params=params)

# 5. Session State για διατήρηση σύνδεσης
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "student_data" not in st.session_state:
    st.session_state.student_data = {}

# --- ΟΘΟΝΗ ΣΥΝΔΕΣΗΣ ---
if not st.session_state.logged_in:
    st.title("🔐 Είσοδος στο Πρωτάθλημα Πληροφορικής")
    
    with st.form("login_form"):
        username = st.text_input("Username Μαθητή")
        password = st.text_input("Κωδικός Πρόσβασης", type="password")
        submit = st.form_submit_button("Σύνδεση")
        
        if submit:
            student_info = verify_student(username, password)
            if student_info:
                st.session_state.logged_in = True
                st.session_state.student_data = student_info
                st.success(f"Καλώς ήρθες, {student_info['full_name']}!")
                st.rerun()
            else:
                st.error("Λανθασμένο Username ή Κωδικός.")

# --- ΚΥΡΙΩΣ ΕΦΑΡΜΟΓΗ ---
else:
    st.sidebar.title(f"👤 {st.session_state.student_data['full_name']}")
    st.sidebar.caption(f"Τμήμα: {st.session_state.student_data['class']}")
    
    if st.sidebar.button("Αποσύνδεση"):
        st.session_state.logged_in = False
        st.session_state.student_data = {}
        st.rerun()

    menu = st.sidebar.radio("Πλοήγηση", ["📝 Ασκήσεις / Quiz", "🏆 Πίνακας Κατάταξης (Leaderboard)"])

    # --- ΕΝΟΤΗΤΑ ΑΣΚΗΣΕΩΝ ---
    if menu == "📝 Ασκήσεις / Quiz":
        st.title("🎯 Ασκήσεις Πληροφορικής")
        
        selected_lesson = st.selectbox("Επίλεξε Μάθημα:", list(QUIZZES.keys()))
        questions = QUIZZES[selected_lesson]

        st.info(f"Επίλεξες: **{selected_lesson}** ({len(questions)} ερωτήσεις)")

        with st.form("quiz_form"):
            user_answers = {}
            for i, q in enumerate(questions):
                st.subheader(q["question"])
                user_answers[i] = st.radio(
                    "Επίλεξε απάντηση:",
                    q["options"],
                    key=f"{selected_lesson}_q_{i}",
                    index=None
                )
                st.divider()

            submit_quiz = st.form_submit_button("Υποβολή Απαντήσεων")

        if submit_quiz:
            score = 0
            total = len(questions)
            
            for i, q in enumerate(questions):
                if user_answers[i] == q["answer"]:
                    score += 1
            
            final_score = int((score / total) * 100)
            st.balloons()
            st.success(f"Ολοκλήρωσες το quiz! Το σκορ σου: **{final_score} / 100** ({score}/{total} σωστές).")
            
            # Αποθήκευση στον SQL Server
            save_or_update_score(st.session_state.student_data["username"], selected_lesson, final_score)
            st.info("Η βαθμολογία σου ενημερώθηκε στη βάση δεδομένων του Πρωταθλήματος!")

    # --- ΕΝΟΤΗΤΑ LEADERBOARD ---
    elif menu == "🏆 Πίνακας Κατάταξης (Leaderboard)":
        st.title("🏆 Πρωτάθλημα Πληροφορικής")
        
        col1, col2 = st.columns(2)
        with col1:
            filter_lesson = st.selectbox("Φιλτράρισμα ανά Μάθημα:", ["Όλα τα Μαθήματα"] + list(QUIZZES.keys()))
        with col2:
            filter_class = st.selectbox("Φιλτράρισμα ανά Τμήμα:", ["Όλα τα Τμήματα", "Γ1", "Γ2", "Γ3"])
        
        df_scores = load_leaderboard(filter_lesson, filter_class)
        
        if not df_scores.empty:
            df_scores.index += 1
            st.dataframe(
                df_scores,
                use_container_width=True,
                column_config={
                    "Βαθμολογία (%)": st.column_config.ProgressColumn(
                        "Βαθμολογία (%)",
                        format="%d%%",
                        min_value=0,
                        max_value=100,
                    )
                }
            )
        else:
            st.info("Δεν υπάρχουν ακόμη καταχωρημένες βαθμολογίες για τα επιλεγμένα φίλτρα.")
