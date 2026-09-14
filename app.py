import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# 1. Ρυθμίσεις Σελίδας
st.set_page_config(page_title="Πρωτάθλημα Πληροφορικής", page_icon="🏆", layout="wide")

# 2. Σύνδεση με τον SQL Server (nikosn_1QUIZ) μέσω st.secrets
@st.cache_resource
def get_db_connection():
    try:
        db_user = st.secrets["sql"]["user"]
        db_password = st.secrets["sql"]["password"]
        db_host = st.secrets["sql"]["host"]
        db_port = st.secrets["sql"]["port"]
        db_name = st.secrets["sql"]["database"]

        connection_string = f"mssql+pymssql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        return create_engine(connection_string, pool_pre_ping=True)
    except Exception as e:
        st.error(f"❌ Σφάλμα σύνδεσης με τη βάση δεδομένων: {e}")
        st.stop()

engine = get_db_connection()

# 3. Βάση Δεδομένων Quiz
QUIZZES = {
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

def get_user_attempts(username, lesson_name):
    """ Επιστρέφει τις προσπάθειες που έχει κάνει ο μαθητής στο συγκεκριμένο μάθημα """
    query = text("SELECT Attempts, Score FROM Leaderboard WHERE Username = :u AND LessonName = :l")
    with engine.connect() as conn:
        res = conn.execute(query, {"u": username, "l": lesson_name}).fetchone()
        if res:
            return res[0], res[1]  # (Attempts, Current Best Score)
        return 0, 0

def save_or_update_score(username, lesson_name, new_score):
    """ Αποθηκεύει τη βαθμολογία και αυξάνει τις προσπάθειες κατά 1 """
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

def load_overall_leaderboard(selected_class=None):
    """ Υπολογίζει το Άθροισμα και τον Μέσο Όρο για κάθε μαθητή """
    base_query = """
        SELECT 
            s.FirstName + ' ' + s.LastName AS [Μαθητής],
            s.ClassGroup AS [Τμήμα],
            SUM(l.Score) AS [Συνολικοί Πόντοι],
            ROUND(AVG(CAST(l.Score AS FLOAT)), 1) AS [Μέσος Όρος (%)],
            COUNT(l.LessonName) AS [Ολοκληρωμένα Quiz]
        FROM Leaderboard l
        JOIN Students s ON l.Username = s.Username
    """
    params = {}
    if selected_class and selected_class != "Όλα τα Τμήματα":
        base_query += " WHERE s.ClassGroup = :cls"
        params["cls"] = selected_class

    base_query += " GROUP BY s.FirstName, s.LastName, s.ClassGroup ORDER BY [Συνολικοί Πόντοι] DESC, [Μέσος Όρος (%)] DESC"
    return pd.read_sql(text(base_query), engine, params=params)

def load_lesson_leaderboard(selected_lesson=None, selected_class=None):
    """ Αναλυτικός πίνακας ανά Μάθημα """
    base_query = """
        SELECT 
            s.FirstName + ' ' + s.LastName AS [Μαθητής],
            s.ClassGroup AS [Τμήμα],
            l.LessonName AS [Μάθημα],
            l.Score AS [Καλύτερη Βαθμολογία (%)],
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

# 5. Session State
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

        # Έλεγχος Προσπαθειών Μαθητή
        attempts, best_score = get_user_attempts(st.session_state.student_data["username"], selected_lesson)
        
        col_info1, col_info2 = st.columns(2)
        col_info1.info(f"📌 **Προσπάθειες:** {attempts} / 2")
        if attempts > 0:
            col_info2.success(f"⭐ **Καλύτερο Σκορ:** {best_score}%")

        # Αν ο μαθητής έχει συμπληρώσει 2 προσπάθειες
        if attempts >= 2:
            st.warning("⚠️ Έχεις εξαντλήσει το όριο των 2 προσπαθειών για αυτό το quiz!")
        else:
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
                st.success(f"Ολοκλήρωσες το quiz! Το σκορ σου σε αυτή την προσπάθεια: **{final_score} / 100** ({score}/{total} σωστές).")
                
                # Αποθήκευση στον SQL Server
                save_or_update_score(st.session_state.student_data["username"], selected_lesson, final_score)
                st.rerun()

    # --- ΕΝΟΤΗΤΑ LEADERBOARD ---
    elif menu == "🏆 Πίνακας Κατάταξης (Leaderboard)":
        st.title("🏆 Πρωτάθλημα Πληροφορικής")
        
        tab1, tab2 = st.tabs(["🥇 Γενική Κατάταξη (Άθροισμα & Μ.Ο.)", "📊 Αναλυτικά ανά Μάθημα"])

        # TAB 1: ΓΕΝΙΚΗ ΚΑΤΑΤΑΞΗ
        with tab1:
            st.subheader("Συνολική Βαθμολογία Πρωταθλήματος")
            filter_class = st.selectbox("Φιλτράρισμα ανά Τμήμα:", ["Όλα τα Τμήματα", "Γ1", "Γ2", "Γ3"], key="overall_class")
            
            df_overall = load_overall_leaderboard(filter_class)
            if not df_overall.empty:
                df_overall.index += 1
                st.dataframe(
                    df_overall,
                    use_container_width=True,
                    column_config={
                        "Μέσος Όρος (%)": st.column_config.ProgressColumn(
                            "Μέσος Όρος (%)",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100,
                        )
                    }
                )
            else:
                st.info("Δεν υπάρχουν ακόμη καταχωρημένες βαθμολογίες.")

        # TAB 2: ΑΝΑΛΥΤΙΚΑ ΑΝΑ ΜΑΘΗΜΑ
        with tab2:
            st.subheader("Βαθμολογίες ανά Μάθημα")
            col1, col2 = st.columns(2)
            with col1:
                filter_lesson = st.selectbox("Φιλτράρισμα ανά Μάθημα:", ["Όλα τα Μαθήματα"] + list(QUIZZES.keys()), key="lesson_filter")
            with col2:
                filter_class_lesson = st.selectbox("Φιλτράρισμα ανά Τμήμα:", ["Όλα τα Τμήματα", "Γ1", "Γ2", "Γ3"], key="lesson_class_filter")
            
            df_lesson = load_lesson_leaderboard(filter_lesson, filter_class_lesson)
            if not df_lesson.empty:
                df_lesson.index += 1
                st.dataframe(
                    df_lesson,
                    use_container_width=True,
                    column_config={
                        "Καλύτερη Βαθμολογία (%)": st.column_config.ProgressColumn(
                            "Καλύτερη Βαθμολογία (%)",
                            format="%d%%",
                            min_value=0,
                            max_value=100,
                        )
                    }
                )
            else:
                st.info("Δεν υπάρχουν ακόμη καταχωρημένες βαθμολογίες για τα επιλεγμένα φίλτρα.")
