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

# 3. Βάση Δεδομένων Quiz (Ενσωμάτωση Φύλλου Εργασίας Γ.7.Μ1)
QUIZZES = {
    "Γ.7.Μ1: Αλγόριθμοι - Χαρακτηριστικά": [
        {
            "question": "1. Ποια από τις πιο κάτω εντολές ΔΕΝ είναι σαφής (περιέχει ασάφεια);",
            "options": [
                "Πρόσθεσε 0.5 λίτρα νερού.",
                "Βάλε λίγη ζάχαρη.",
                "Πρόσθεσε τον χυμό ενός πορτοκαλιού.",
                "Ανακάτεψε τα πιο πάνω υλικά για 6 λεπτά."
            ],
            "answer": "Βάλε λίγη ζάχαρη."
        },
        {
            "question": "2. Ο Αλγόριθμος είναι μια σειρά από βήματα που:",
            "options": [
                "Τοποθετούνται σε λογική σειρά και περιγράφουν τον τρόπο επίλυσης ενός προβλήματος",
                "Μπορούν να εκτελεστούν μόνο από έναν υπολογιστή",
                "Περιγράφουν μια διαδικασία ετοιμασίας φαγητού",
                "Περιγράφουν τη λύση μιας μαθηματικής εξίσωσης"
            ],
            "answer": "Τοποθετούνται σε λογική σειρά και περιγράφουν τον τρόπο επίλυσης ενός προβλήματος"
        },
        {
            "question": "3. Η Σαφήνεια είναι χαρακτηριστικό του Αλγόριθμου το οποίο καθορίζει ότι:",
            "options": [
                "Κάθε εντολή/οδηγία πρέπει να είναι απλή",
                "Κάθε εντολή/οδηγία πρέπει να καθορίζεται χωρίς καμία αμφιβολία για τον τρόπο εκτέλεσής της",
                "Οι εντολές / οδηγίες που δίνονται πρέπει να έχουν σχόλια",
                "Κάθε εντολή/οδηγία πρέπει να μην έχει ορθογραφικά λάθη"
            ],
            "answer": "Κάθε εντολή/οδηγία πρέπει να καθορίζεται χωρίς καμία αμφιβολία για τον τρόπο εκτέλεσής της"
        },
        {
            "question": "4. Η Περατότητα είναι χαρακτηριστικό του Αλγόριθμου το οποίο καθορίζει ότι:",
            "options": [
                "Ο Αλγόριθμος είναι αποτελεσματικός",
                "Ο Αλγόριθμος μπορεί να λειτουργήσει",
                "Κάθε εκτέλεση είναι πεπερασμένη, δηλαδή τελειώνει ύστερα από έναν πεπερασμένο αριθμό διεργασιών ή βημάτων",
                "Ο Αλγόριθμος είναι ταχύς"
            ],
            "answer": "Κάθε εκτέλεση είναι πεπερασμένη, δηλαδή τελειώνει ύστερα από έναν πεπερασμένο αριθμό διεργασιών ή βημάτων"
        },
        {
            "question": "5. Η Αποτελεσματικότητα είναι χαρακτηριστικό του Αλγόριθμου το οποίο καθορίζει ότι:",
            "options": [
                "Ο Αλγόριθμος δίνει ένα μόνο αποτέλεσμα",
                "Ο Αλγόριθμος μπορεί να εκτελεστεί από έναν υπολογιστή",
                "Ο Αλγόριθμος είναι οικονομικός",
                "Ένας αλγόριθμος θα πρέπει να δίνει ένα αποτέλεσμα σε πεπερασμένο χρονικό διάστημα"
            ],
            "answer": "Ένας αλγόριθμος θα πρέπει να δίνει ένα αποτέλεσμα σε πεπερασμένο χρονικό διάστημα"
        },
        {
            "question": "6. Ποια είναι η σωστή σειρά ώστε οι παρακάτω εντολές να αποτελέσουν αλγόριθμο υπολογισμού εμβαδού τριγώνου;\n1. Δώσε τη βάση τριγώνου\n2. Υπολόγισε το εμβαδόν (Β x Υ/2)\n3. Τύπωσε το εμβαδόν\n4. Δώσε το ύψος",
            "options": [
                "1, 2, 3, 4",
                "1, 3, 4, 2",
                "1, 4, 2, 3",
                "4, 1, 2, 3"
            ],
            "answer": "1, 4, 2, 3"
        },
        {
            "question": "7. Ποια είναι η σωστή σειρά για την αντιγραφή μέρους κειμένου στο Word;\n1. Μετακίνησε τον δρομέα στο σημείο που θα γίνει η αντιγραφή\n2. Επίλεξε το μέρος του κειμένου που θα αντιγράψεις\n3. Επίλεξε την εντολή Copy\n4. Επίλεξε την εντολή Paste\n5. Τοποθέτησε τον δρομέα στην αρχή του κειμένου που θα αντιγράψεις",
            "options": [
                "5, 2, 3, 1, 4",
                "5, 2, 3, 4, 1",
                "5, 1, 2, 3, 4",
                "Κανένα από τα πιο πάνω"
            ],
            "answer": "5, 2, 3, 1, 4"
        },
        {
            "question": "8. Ο αλγόριθμος σχεδίασης τετραγώνου πλευράς 20 cm περιλαμβάνει τα βήματα:\n1. Σχεδίασε ευθ. τμήμα 20cm | 2. Στρίψε δεξιά 90° | 3. Σχεδίασε ευθ. τμήμα 20cm | 4. Στρίψε δεξιά 90° | 5. Σχεδίασε ευθ. τμήμα 20cm | 6. Στρίψε αριστερά 90° | 7. Σχεδίασε ευθ. τμήμα 20cm.\nΠοιο είναι το σφάλμα;",
            "options": [
                "Η εντολή 4 είναι λανθασμένη",
                "Υπάρχει πρόβλημα σαφήνειας σε μια από τις εντολές",
                "Η εντολή 6 είναι λανθασμένη (πρέπει να στρίψει δεξιά 90°)",
                "Ο αλγόριθμος είναι σωστός"
            ],
            "answer": "Η εντολή 6 είναι λανθασμένη (πρέπει να στρίψει δεξιά 90°)"
        }
    ],
    "Μάθημα 1: Εισαγωγή στην Πληροφορική": [
        {
            "question": "1. Ποια από τις παρακάτω είναι γλώσσα προγραμματισμού υψηλού επιπέδου;",
            "options": ["Assembly", "Python", "Machine Code", "HTML"],
            "answer": "Python"
        },
        {
            "question": "2. Τι σημαίνει ο όρος CPU;",
            "options": ["Central Processing Unit", "Central Power Unit", "Computer Personal Unit", "Control Processing Unit"],
            "answer": "Central Processing Unit"
        }
    ],
    "Μάθημα 2: Δομές Δεδομένων": [
        {
            "question": "1. Ποια δομή δεδομένων ακολουθεί την αρχή LIFO (Last In, First Out);",
            "options": ["Ουρά (Queue)", "Στοίβα (Stack)", "Δέντρο (Tree)", "Γράφος (Graph)"],
            "answer": "Στοίβα (Stack)"
        },
        {
            "question": "2. Στον πίνακα `a = [10, 20, 30]`, ποιο είναι το στοιχείο `a[0]`;",
            "options": ["10", "20", "30", "0"],
            "answer": "10"
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
