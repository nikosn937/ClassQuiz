import streamlit as st
import pandas as pd
import pyodbc
import platform

# ==========================================
# 1. DATABASE CONNECTION & INITIALIZATION
# ==========================================
def get_db_connection():
    if "mssql" not in st.secrets:
        st.error("⚠️ Δεν έχουν ρυθμιστεί τα Database Secrets (mssql) στο Streamlit settings.")
        st.stop()
        
    server = st.secrets["mssql"]["server"]
    port = st.secrets["mssql"]["port"]
    database = st.secrets["mssql"]["database"]
    username = st.secrets["mssql"]["username"]
    password = st.secrets["mssql"]["password"]

    if platform.system() == "Windows":
        driver = "{ODBC Driver 17 for SQL Server}"
        conn_str = f"DRIVER={driver};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}"
    else:
        driver = "{FreeTDS}"
        conn_str = f"DRIVER={driver};SERVER={server};PORT={port};DATABASE={database};UID={username};PWD={password};TDS_Version=7.4;ClientCharset=UTF-8;"

    return pyodbc.connect(conn_str)

# ==========================================
# 2. QUIZ DATA STRUCTURE
# ==========================================
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
    ]
    }

# ==========================================
# 3. HELPER: SEED QUIZZES TO DB
# ==========================================
def sync_quizzes_to_db():
    """Διασφαλίζει ότι τα Quizzes του λεξικού υπάρχουν στον πίνακα Quizzes της SQL."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for title in QUIZZES.keys():
        cursor.execute("SELECT QuizID FROM Quizzes WHERE Title = ?", (title,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO Quizzes (Title, Subject) VALUES (?, ?)", (title, "Πληροφορική"))
    
    conn.commit()
    conn.close()

# ==========================================
# 4. PAGE CONFIG & SESSION INITIALIZATION
# ==========================================
st.set_page_config(
    page_title="Informatics League",
    page_icon="🎓",
    layout="wide"
)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'role' not in st.session_state:
    st.session_state['role'] = ''
if 'firstname' not in st.session_state:
    st.session_state['firstname'] = ''

# ==========================================
# 5. LOGIN SCREEN
# ==========================================
def login_screen():
    st.title("🔐 Σύνδεση στην Πλατφόρμα")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username_input = st.text_input("Όνομα Χρήστη (Username)")
        password_input = st.text_input("Κωδικός Πρόσβασης (Password)", type="password")
        
        if st.button("Σύνδεση", type="primary", use_container_width=True):
            conn = get_db_connection()
            query = "SELECT Username, FirstName, LastName, Role, Password FROM Students WHERE Username = ?"
            df_user = pd.read_sql(query, conn, params=[username_input])
            conn.close()

            if not df_user.empty:
                user_row = df_user.iloc[0]
                if user_row['Password'] == password_input:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user_row['Username']
                    st.session_state['role'] = user_row['Role']
                    st.session_state['firstname'] = user_row['FirstName']
                    
                    # Συγχρονισμός Quizzes στη βάση κατά τη σύνδεση
                    sync_quizzes_to_db()
                    st.success("Επιτυχής σύνδεση!")
                    st.rerun()
                else:
                    st.error("Λανθασμένος κωδικός πρόσβασης.")
            else:
                st.error("Το όνομα χρήστη δεν βρέθηκε.")

# ==========================================
# 6. STUDENT DASHBOARD
# ==========================================
def student_dashboard():
    username = st.session_state['username']
    st.title(f"🎓 Καλωσόρισες, {st.session_state['firstname']}!")
    
    conn = get_db_connection()
    
    # 1. Θέση & Μέσος Όρος από Views
    rank_query = """
        SELECT c.AvgScore, c.ClassRank, c.TotalInClass, o.OverallRank, o.TotalStudents
        FROM vw_ClassRankings c
        JOIN vw_OverallRankings o ON c.Username = o.Username
        WHERE c.Username = ?
    """
    df_rank = pd.read_sql(rank_query, conn, params=[username])
    
    # 2. Ιστορικό Αποτελεσμάτων
    results_query = """
        SELECT q.Title AS [Διαγώνισμα], qr.Score AS [Βαθμός], qr.CompletedAt AS [Ημερομηνία]
        FROM QuizResults qr
        JOIN Quizzes q ON qr.QuizID = q.QuizID
        WHERE qr.Username = ?
        ORDER BY qr.CompletedAt DESC
    """
    df_results = pd.read_sql(results_query, conn, params=[username])
    conn.close()

    # Εμφάνιση Cards
    if not df_rank.empty:
        avg_score = df_rank.iloc[0]['AvgScore']
        class_rank = df_rank.iloc[0]['ClassRank']
        total_class = df_rank.iloc[0]['TotalInClass']
        overall_rank = df_rank.iloc[0]['OverallRank']
        total_overall = df_rank.iloc[0]['TotalStudents']

        col1, col2, col3 = st.columns(3)
        col1.metric("Ο Μέσος Όρος σου", f"{avg_score:.1f} / 100")
        col2.metric("Θέση στο Τμήμα", f"{class_rank}ος", f"σε {total_class} μαθητές")
        col3.metric("Θέση στη Σειρά", f"{overall_rank}ος", f"σε {total_overall} μαθητές")

    tab1, tab2 = st.tabs(["📝 Επίλυση Quiz", "📜 Ιστορικό Βαθμολογιών"])
with tab1:
        st.subheader("Επίλεξε Διαγώνισμα για Επίλυση")
        selected_quiz_title = st.selectbox("Διαθέσιμα Quizzes:", list(QUIZZES.keys()))
        questions = QUIZZES[selected_quiz_title]
        
        # 🔍 Έλεγχος πόσες προσπάθειες έχει κάνει ο μαθητής για το συγκεκριμένο Quiz
        conn = get_db_connection()
        attempts_query = """
            SELECT COUNT(*) AS AttemptCount, ISNULL(MAX(Score), 0) AS BestScore
            FROM QuizResults qr
            JOIN Quizzes q ON qr.QuizID = q.QuizID
            WHERE qr.Username = ? AND q.Title = ?
        """
        df_attempts = pd.read_sql(attempts_query, conn, params=[username, selected_quiz_title])
        conn.close()
        
        attempts_count = df_attempts.iloc[0]['AttemptCount'] if not df_attempts.empty else 0
        best_score = df_attempts.iloc[0]['BestScore'] if not df_attempts.empty else 0

        # Ενημερωτικό μήνυμα για τις προσπάθειες
        if attempts_count == 0:
            st.info("ℹ️ Έχεις **2 διαθέσιμες προσπάθειες** για αυτό το διαγώνισμα. Στον Μέσο Όρο σου θα προσμετρηθεί ο καλύτερος βαθμός.")
        elif attempts_count == 1:
            st.warning(f"⚠️ Έχεις κάνει **1 προσπάθεια** (Βαθμός: **{best_score:.1f}/100**). Έχεις ακόμα **1 τελευταία προσπάθεια**!")
        else:
            st.error(f"🚫 Έχεις συμπληρώσει το όριο των **2 προσπαθειών** για αυτό το Quiz! Ο καλύτερος βαθμός σου είναι **{best_score:.1f}/100**.")

        # 🔒 Εμφάνιση φόρμας ΜΟΝΟ αν οι προσπάθειες είναι λιγότερες από 2
        if attempts_count < 2:
            with st.form("quiz_form"):
                user_answers = {}
                for i, q in enumerate(questions):
                    st.markdown(f"**{q['question']}**")
                    user_answers[i] = st.radio(f"Επιλογή για την ερώτηση {i+1}:", q['options'], key=f"q_{selected_quiz_title}_{i}")
                    st.write("---")
                
                submit_quiz = st.form_submit_button("🚀 Υποβολή Απαντήσεων", type="primary")
                
                if submit_quiz:
                    correct_count = 0
                    for i, q in enumerate(questions):
                        if user_answers[i] == q['answer']:
                            correct_count += 1
                    
                    final_score = (correct_count / len(questions)) * 100
                    st.success(f"Το Quiz ολοκληρώθηκε! Η βαθμολογία σου σε αυτή την προσπάθεια: **{final_score:.1f} / 100** ({correct_count}/{len(questions)} σωστά)")
                    
                    # Αποθήκευση της προσπάθειας στη βάση
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT QuizID FROM Quizzes WHERE Title = ?", (selected_quiz_title,))
                    quiz_row = cursor.fetchone()
                    
                    if quiz_row:
                        quiz_id = quiz_row[0]
                        cursor.execute(
                            "INSERT INTO QuizResults (Username, QuizID, Score) VALUES (?, ?, ?)",
                            (username, quiz_id, final_score)
                        )
                        conn.commit()
                    conn.close()
                    st.info("Η προσπάθεια αποθηκεύτηκε επιτυχώς!")
                    st.rerun()
    
    with tab2:
        st.subheader("Ιστορικό Διαγωνισμάτων")
        if not df_results.empty:
            st.dataframe(df_results, use_container_width=True)
        else:
            st.info("Δεν έχεις υποβάλει ακόμη κάποιο διαγώνισμα.")

# ==========================================
# 7. TEACHER DASHBOARD
# ==========================================
def teacher_dashboard():
    st.title("👨‍🏫 Dashboard Καθηγητή")
    st.write("Πλήρης εικόνα επιδόσεων και κατατάξεων μαθητών.")
    
    conn = get_db_connection()
    
    all_ranks_query = """
        SELECT 
            c.ClassGroup AS [Τμήμα],
            c.LastName AS [Επώνυμο],
            c.FirstName AS [Όνομα],
            c.AvgScore AS [Μέσος Όρος],
            c.ClassRank AS [Θέση Τμήματος],
            o.OverallRank AS [Θέση Σειράς]
        FROM vw_ClassRankings c
        JOIN vw_OverallRankings o ON c.Username = o.Username
        ORDER BY c.ClassGroup, c.ClassRank
    """
    df_all_ranks = pd.read_sql(all_ranks_query, conn)
    
    all_results_query = """
        SELECT 
            s.ClassGroup AS [Τμήμα],
            s.LastName + ' ' + s.FirstName AS [Μαθητής],
            q.Title AS [Διαγώνισμα],
            qr.Score AS [Βαθμός],
            qr.CompletedAt AS [Ημερομηνία]
        FROM QuizResults qr
        JOIN Students s ON qr.Username = s.Username
        JOIN Quizzes q ON qr.QuizID = q.QuizID
        ORDER BY qr.CompletedAt DESC
    """
    df_all_results = pd.read_sql(all_results_query, conn)
    conn.close()

    # Sidebar Filter
    st.sidebar.header("🔍 Φίλτρα")
    class_list = ["Όλα τα Τμήματα"] + sorted(df_all_ranks['Τμήμα'].unique().tolist()) if not df_all_ranks.empty else ["Όλα τα Τμήματα"]
    selected_class = st.sidebar.selectbox("Επιλογή Τμήματος", class_list)

    if selected_class != "Όλα τα Τμήματα":
        filtered_ranks = df_all_ranks[df_all_ranks['Τμήμα'] == selected_class]
        filtered_results = df_all_results[df_all_results['Τμήμα'] == selected_class]
    else:
        filtered_ranks = df_all_ranks
        filtered_results = df_all_results

    tab1, tab2 = st.tabs(["🏆 Γενική Κατάταξη & Μ.Ο.", "📝 Αναλυτικά Αποτελέσματα Quiz"])

    with tab1:
        st.subheader(f"Πίνακας Κατάταξης ({selected_class})")
        st.dataframe(filtered_ranks, use_container_width=True)
        
        csv = filtered_ranks.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Εξαγωγή Κατάταξης σε CSV",
            data=csv,
            file_name=f'rankings_{selected_class}.csv',
            mime='text/csv',
        )

    with tab2:
        st.subheader(f"Αποτελέσματα Διαγωνισμάτων ({selected_class})")
        st.dataframe(filtered_results, use_container_width=True)

# ==========================================
# 8. MAIN ROUTER & LOGOUT
# ==========================================
if not st.session_state['logged_in']:
    login_screen()
else:
    st.sidebar.title("👤 Στοιχεία Χρήστη")
    st.sidebar.write(f"**Χρήστης:** {st.session_state['username']}")
    st.sidebar.write(f"**Ρόλος:** {st.session_state['role']}")
    
    if st.sidebar.button("Αποσύνδεση"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.session_state['role'] = ''
        st.session_state['firstname'] = ''
        st.rerun()

    if st.session_state['role'] == 'TEACHER':
        teacher_dashboard()
    else:
        student_dashboard()
