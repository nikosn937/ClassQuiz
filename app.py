import platform
import pandas as pd
import pyodbc
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh



# ==========================================
# 1. DATABASE CONNECTION & INITIALIZATION
# ==========================================
def get_db_connection():
    if "mssql" not in st.secrets:
        st.error(
            "⚠️ Δεν έχουν ρυθμιστεί τα Database Secrets (mssql) στο Streamlit"
            " settings."
        )
        st.stop()

    server = st.secrets["mssql"]["server"]
    port = st.secrets["mssql"]["port"]
    database = st.secrets["mssql"]["database"]
    username = st.secrets["mssql"]["username"]
    password = st.secrets["mssql"]["password"]

    if platform.system() == "Windows":
        driver = "{ODBC Driver 17 for SQL Server}"
        conn_str = (
            f"DRIVER={driver};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}"
        )
    else:
        driver = "{FreeTDS}"
        conn_str = (
            f"DRIVER={driver};SERVER={server};PORT={port};DATABASE={database};UID={username};PWD={password};TDS_Version=7.4;ClientCharset=UTF-8;"
        )

    return pyodbc.connect(conn_str)


# ==========================================
# 2. QUIZ DATA STRUCTURE
# ==========================================
QUIZZES = {
    "Γ.7.Μ1: Αλγόριθμοι - Χαρακτηριστικά": [
        {
            "question": (
                "1. Ποια από τις πιο κάτω εντολές ΔΕΝ είναι σαφής (περιέχει"
                " ασάφεια);"
            ),
            "options": [
                "Πρόσθεσε 200 ml γάλα.",
                "Ψήσε το κέικ σε μέτριο φούρνο.",
                "Ζέστανε το νερό στους 80°C.",
                "Ανακάτεψε τα υλικά για 3 λεπτά.",
            ],
            "answer": "Ψήσε το κέικ σε μέτριο φούρνο.",
        },
        {
            "question": (
                "2. Ποια από τις παρακάτω προτάσεις περιγράφει σωστά την έννοια"
                " του Αλγόριθμου;"
            ),
            "options": [
                (
                    "Μια αυστηρά καθορισμένη αλληλουχία βημάτων που οδηγεί στην"
                    " επίλυση ενός προβλήματος"
                ),
                "Ένα πρόγραμμα γραμμένο αποκλειστικά σε γλώσσα Python",
                "Μια λίστα με τυχαίες οδηγίες χωρίς συγκεκριμένη σειρά",
                "Ένα μαθηματικό πρόβλημα που δεν έχει λύση",
            ],
            "answer": (
                "Μια αυστηρά καθορισμένη αλληλουχία βημάτων που οδηγεί στην"
                " επίλυση ενός προβλήματος"
            ),
        },
        {
            "question": (
                "3. Όταν λέμε ότι ένας Αλγόριθμος πρέπει να διακρίνεται από"
                " Σαφήνεια, εννοούμε ότι:"
            ),
            "options": [
                "Κάθε εντολή πρέπει να είναι σύντομη",
                "Κάθε εντολή πρέπει να επιδέχεται μία μόνο μονοσήμαντη ερμηνεία",
                "Ο αλγόριθμος πρέπει να εκτελείται χωρίς τη χρήση υπολογιστή",
                "Οι εντολές πρέπει να είναι γραμμένες στα ελληνικά",
            ],
            "answer": (
                "Κάθε εντολή πρέπει να επιδέχεται μία μόνο μονοσήμαντη ερμηνεία"
            ),
        },
        {
            "question": (
                "4. Το χαρακτηριστικό της Περατότητας εξασφαλίζει ότι ο"
                " Αλγόριθμος:"
            ),
            "options": [
                (
                    "Δεν θα κολλήσει σε ατέρμονα βρόγχο (εκτέλεση χωρίς τέλος)"
                    " και θα τερματίσει μετά από πεπερασμένο αριθμό βημάτων"
                ),
                "Θα δίνει πάντα το ίδιο αποτέλεσμα",
                "Θα αποτελείται το πολύ από 10 βήματα",
                "Θα εκτελεστεί στον ταχύτερο δυνατό χρόνο",
            ],
            "answer": (
                "Δεν θα κολλήσει σε ατέρμονα βρόγχο (εκτέλεση χωρίς τέλος) και"
                " θα τερματίσει μετά από πεπερασμένο αριθμό βημάτων"
            ),
        },
        {
            "question": (
                "5. Η Αποτελεσματικότητα ως χαρακτηριστικό ενός Αλγόριθμου"
                " σημαίνει ότι:"
            ),
            "options": [
                (
                    "Κάθε εντολή είναι αρκετά απλή ώστε να μπορεί να εκτελεστεί"
                    " μηχανικά σε πεπερασμένο χρόνο"
                ),
                "Ο αλγόριθμος είναι ο συντομότερος δυνατός",
                "Ο αλγόριθμος λύνει όλα τα προβλήματα Πληροφορικής",
                "Ο αλγόριθμος χρησιμοποιεί ελάχιστη μνήμη",
            ],
            "answer": (
                "Κάθε εντολή είναι αρκετά απλή ώστε να μπορεί να εκτελεστεί"
                " μηχανικά σε πεπερασμένο χρόνο"
            ),
        },
        {
            "question": (
                "6. Ποια είναι η σωστή σειρά εντολών για τον αλγόριθμο"
                " υπολογισμού του Μέσου Όρου δύο αριθμών;\n1. Διάβασε τον"
                " δεύτερο αριθμό (Β)\n2. Τύπωσε το αποτέλεσμα (ΜΟ)\n3."
                " Υπολόγισε ΜΟ = (Α + Β) / 2\n4. Διάβασε τον πρώτο αριθμό (Α)"
            ),
            "options": ["4, 1, 3, 2", "1, 4, 2, 3", "4, 3, 1, 2", "1, 2, 3, 4"],
            "answer": "4, 1, 3, 2",
        },
        {
            "question": (
                "7. Ποια είναι η σωστή σειρά βημάτων για τη διαγραφή μιας"
                " παραγράφου σε έναν Επεξεργαστή Κειμένου (Word);\n1. Πίεσε το"
                " πλήκτρο Delete\n2. Επίλεξε (μάρκαρε) την παράγραφο με το"
                " ποντίκι\n3. Τοποθέτησε τον δρομέα στην αρχή της παραγράφου"
            ),
            "options": ["3, 2, 1", "2, 3, 1", "1, 2, 3", "3, 1, 2"],
            "answer": "3, 2, 1",
        },
        {
            "question": (
                "8. Ένας μαθητής έγραψε αλγόριθμο για να σχεδιάσει ένα"
                " ισόπλευρο τρίγωνο:\n1. Σχεδίασε ευθύγραμμο τμήμα 10 cm\n2."
                " Στρίψε δεξιά 120°\n3. Σχεδίασε ευθύγραμμο τμήμα 10 cm\n4."
                " Στρίψε αριστερά 120°\n5. Σχεδίασε ευθύγραμμο τμήμα 10 cm\nΠού"
                " υπάρχει το λογικό σφάλμα;"
            ),
            "options": [
                "Στην εντολή 4 (πρέπει να στρίψει δεξιά 120°)",
                "Στην εντολή 2 (πρέπει να στρίψει 90°)",
                "Στην εντολή 5 (το μήκος πρέπει να είναι 5 cm)",
                "Ο αλγόριθμος είναι απόλυτα σωστός",
            ],
            "answer": "Στην εντολή 4 (πρέπει να στρίψει δεξιά 120°)",
        },
    ],
 
}

# ==========================================
# 3. HELPER: SEED QUIZZES TO DB
# ==========================================
def sync_quizzes_to_db():
    """Διασφαλίζει ότι τα Quizzes του λεξικού υπάρχουν στον πίνακα Quizzes της SQL."""
    conn = get_db_connection()
    cursor = conn.cursor()

    for title in QUIZZES.keys():
        cursor.execute(
            "SELECT QuizID FROM Quizzes WHERE Title = ?", (title,)
        )
        row = cursor.fetchone()
        if not row:
            cursor.execute(
                "INSERT INTO Quizzes (Title, Subject) VALUES (?, ?)",
                (title, "Πληροφορική"),
            )

    conn.commit()
    conn.close()


# ==========================================
# 4. PAGE CONFIG & SESSION INITIALIZATION
# ==========================================
st.set_page_config(
    page_title="Informatics League", page_icon="🎓", layout="wide"
)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "role" not in st.session_state:
    st.session_state["role"] = ""
if "firstname" not in st.session_state:
    st.session_state["firstname"] = ""


# ==========================================
# 5. LOGIN SCREEN
# ==========================================
def login_screen():
    st.title("🔐 Σύνδεση στην Πλατφόρμα")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username_input = st.text_input("Όνομα Χρήστη (Username)")
        password_input = st.text_input(
            "Κωδικός Πρόσβασης (Password)", type="password"
        )

        if st.button("Σύνδεση", type="primary", use_container_width=True):
            conn = get_db_connection()
            query = (
                "SELECT Username, FirstName, LastName, Role, Password FROM"
                " Students WHERE Username = ?"
            )
            df_user = pd.read_sql(query, conn, params=[username_input])
            conn.close()

            if not df_user.empty:
                user_row = df_user.iloc[0]
                if user_row["Password"] == password_input:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = user_row["Username"]
                    st.session_state["role"] = user_row["Role"]
                    st.session_state["firstname"] = user_row["FirstName"]

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
    if "last_quiz_result" not in st.session_state:
        st.session_state["last_quiz_result"] = None

    username = st.session_state["username"]
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
        avg_score = df_rank.iloc[0]["AvgScore"]
        class_rank = df_rank.iloc[0]["ClassRank"]
        total_class = df_rank.iloc[0]["TotalInClass"]
        overall_rank = df_rank.iloc[0]["OverallRank"]
        total_overall = df_rank.iloc[0]["TotalStudents"]

        col1, col2, col3 = st.columns(3)
        col1.metric("Ο Μέσος Όρος σου", f"{avg_score:.1f} / 100")
        col2.metric(
            "Θέση στο Τμήμα", f"{class_rank}ος", f"σε {total_class} μαθητές"
        )
        col3.metric(
            "Θέση στην Τάξη (A/Β/Γ)",
            f"{overall_rank}ος",
            f"σε {total_overall} μαθητές",
        )

    tab1, tab2 = st.tabs(["📝 Επίλυση Quiz", "📜 Ιστορικό Βαθμολογιών"])

    with tab1:
        if st.session_state["last_quiz_result"] is not None:
            res = st.session_state["last_quiz_result"]
            st.success(
                f"🎉 **Το Διαγώνισμα '{res['quiz_title']}' ολοκληρώθηκε!**"
            )
            st.metric(
                label="Βαθμολογία Προσπάθειας",
                value=f"{res['score']:.1f} / 100",
                delta=f"{res['correct']}/{res['total']} σωστές απαντήσεις",
            )
            st.divider()

        st.subheader("Επίλεξε Διαγώνισμα για Επίλυση")
        selected_quiz_title = st.selectbox(
            "Διαθέσιμα Quizzes:", list(QUIZZES.keys())
        )
        questions = QUIZZES[selected_quiz_title]

        # 🔍 Έλεγχος προσπαθειών
        conn = get_db_connection()
        attempts_query = """
            SELECT COUNT(*) AS AttemptCount, ISNULL(MAX(Score), 0) AS BestScore
            FROM QuizResults qr
            JOIN Quizzes q ON qr.QuizID = q.QuizID
            WHERE qr.Username = ? AND q.Title = ?
        """
        df_attempts = pd.read_sql(
            attempts_query, conn, params=[username, selected_quiz_title]
        )
        conn.close()

        attempts_count = (
            df_attempts.iloc[0]["AttemptCount"] if not df_attempts.empty else 0
        )
        best_score = (
            df_attempts.iloc[0]["BestScore"] if not df_attempts.empty else 0
        )

        if attempts_count == 0:
            st.info(
                "ℹ️ Έχεις **2 διαθέσιμες προσπάθειες** για αυτό το διαγώνισμα."
                " Στον Μέσο Όρο σου θα προσμετρηθεί ο καλύτερος βαθμός."
            )
        elif attempts_count == 1:
            st.warning(
                f"⚠️ Έχεις κάνει **1 προσπάθεια** (Βαθμός:"
                f" **{best_score:.1f}/100**). Έχεις ακόμα **1 τελευταία"
                " προσπάθεια**!"
            )
        else:
            st.error(
                "🚫 Έχεις συμπληρώσει το όριο των **2 προσπαθειών** για αυτό το"
                f" Quiz! Ο καλύτερος βαθμός σου είναι **{best_score:.1f}/100**."
            )

        if attempts_count < 2:
            with st.form("quiz_form"):
                user_answers = {}
                for i, q in enumerate(questions):
                    st.markdown(f"**{q['question']}**")
                    user_answers[i] = st.radio(
                        f"Επιλογή για την ερώτηση {i+1}:",
                        q["options"],
                        index=None,
                        key=f"q_{selected_quiz_title}_{i}",
                    )
                    st.write("---")

                submit_quiz = st.form_submit_button(
                    "🚀 Υποβολή Απαντήσεων", type="primary"
                )

            if submit_quiz:
                if None in user_answers.values():
                    st.warning(
                        "⚠️ Παρακαλώ απάντησε σε όλες τις ερωτήσεις πριν την"
                        " υποβολή!"
                    )
                else:
                    correct_count = 0
                    conn = get_db_connection()
                    cursor = conn.cursor()

                    cursor.execute(
                        "SELECT QuizID FROM Quizzes WHERE Title = ?",
                        (selected_quiz_title,),
                    )
                    quiz_row = cursor.fetchone()

                    if quiz_row:
                        quiz_id = quiz_row[0]

                        for i, q in enumerate(questions):
                            is_correct = user_answers[i] == q["answer"]
                            if is_correct:
                                correct_count += 1

                            cursor.execute(
                                """
                                INSERT INTO StudentAnswers (Username, QuizID, QuestionIndex, IsCorrect)
                                VALUES (?, ?, ?, ?)
                            """,
                                (username, quiz_id, i, 1 if is_correct else 0),
                            )

                        final_score = (correct_count / len(questions)) * 100
                        cursor.execute(
                            "INSERT INTO QuizResults (Username, QuizID, Score)"
                            " VALUES (?, ?, ?)",
                            (username, quiz_id, final_score),
                        )
                        conn.commit()

                    conn.close()

                    st.session_state["last_quiz_result"] = {
                        "quiz_title": selected_quiz_title,
                        "score": final_score,
                        "correct": correct_count,
                        "total": len(questions),
                    }
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
    st_autorefresh(interval=10000, key="teacher_dashboard_autorefresh")

    st.title("👨‍🏫 Dashboard Καθηγητή")
    st.write(
        "Πλήρης εικόνα επιδόσεων, κατατάξεων και διαχείρισης μαθητών (Ζωντανή"
        " Ενημέρωση 🔄)."
    )

    conn = get_db_connection()

    # 1. Γενική Κατάταξη
    all_ranks_query = """
        SELECT 
            c.ClassGroup AS [Τμήμα],
            c.LastName AS [Επώνυμο],
            c.FirstName AS [Όνομα],
            c.AvgScore AS [Μέσος Όρος],
            c.ClassRank AS [Θέση Τμήματος],
            o.OverallRank AS [Θέση Τάξης]
        FROM vw_ClassRankings c
        JOIN vw_OverallRankings o ON c.Username = o.Username
        ORDER BY c.ClassGroup, c.ClassRank
    """
    df_all_ranks = pd.read_sql(all_ranks_query, conn)

    # 2. Αναλυτικά Αποτελέσματα Quizzes
    all_results_query = """
        SELECT 
            qr.ResultID,
            s.ClassGroup AS [Τμήμα],
            s.Username,
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

    # 3. Στοιχεία Σύνδεσης Μαθητών
    credentials_query = """
        SELECT 
            ClassGroup AS [Τμήμα],
            LastName AS [Επώνυμο],
            FirstName AS [Όνομα],
            Username AS [Όνομα Χρήστη],
            Password AS [Κωδικός Πρόσβασης]
        FROM Students
        WHERE Role = 'STUDENT'
        ORDER BY ClassGroup, LastName, FirstName
    """
    df_credentials = pd.read_sql(credentials_query, conn)

    # 4. Αναφορά Αδυναμιών
    weakness_query = """
        SELECT 
            s.LastName + ' ' + s.FirstName AS [Μαθητής],
            q.Title AS [Διαγώνισμα],
            sa.QuestionIndex AS [Αριθμός Ερώτησης],
            COUNT(*) AS [Συνολικές Λάθος Απαντήσεις]
        FROM StudentAnswers sa
        JOIN Students s ON sa.Username = s.Username
        JOIN Quizzes q ON sa.QuizID = q.QuizID
        WHERE sa.IsCorrect = 0
        GROUP BY s.LastName, s.FirstName, q.Title, sa.QuestionIndex
        ORDER BY [Συνολικές Λάθος Απαντήσεις] DESC
    """
    df_weakness = pd.read_sql(weakness_query, conn)
    conn.close()

    # Sidebar Filter
    st.sidebar.header("🔍 Φίλτρα")
    class_list = (
        ["Όλα τα Τμήματα"] + sorted(df_credentials["Τμήμα"].unique().tolist())
        if not df_credentials.empty
        else ["Όλα τα Τμήματα"]
    )
    selected_class = st.sidebar.selectbox("Επιλογή Τμήματος", class_list)

    # Φιλτράρισμα Δεδομένων
    if selected_class != "Όλα τα Τμήματα":
        filtered_ranks = (
            df_all_ranks[df_all_ranks["Τμήμα"] == selected_class]
            if not df_all_ranks.empty
            else df_all_ranks
        )
        filtered_results = (
            df_all_results[df_all_results["Τμήμα"] == selected_class]
            if not df_all_results.empty
            else df_all_results
        )
        filtered_credentials = (
            df_credentials[df_credentials["Τμήμα"] == selected_class]
            if not df_credentials.empty
            else df_credentials
        )
    else:
        filtered_ranks = df_all_ranks
        filtered_results = df_all_results
        filtered_credentials = df_credentials

    # 5 Ορισμένα Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 Γενική Κατάταξη & Μ.Ο.",
        "📝 Αναλυτικά Αποτελέσματα Quiz",
        "📊 Αναφορά Αδυναμιών",
        "🔑 Στοιχεία Σύνδεσης",
        "🗑️ Επανυποβολή / Διαγραφή Quiz",
    ])

    with tab1:
        st.subheader(f"Πίνακας Κατάταξης ({selected_class})")
        st.dataframe(filtered_ranks, use_container_width=True)

        if not filtered_ranks.empty:
            csv = filtered_ranks.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 Εξαγωγή Κατάταξης σε CSV",
                data=csv,
                file_name=f"rankings_{selected_class}.csv",
                mime="text/csv",
            )

    with tab2:
        st.subheader(f"Αποτελέσματα Διαγωνισμάτων ({selected_class})")
        display_results = filtered_results.drop(
            columns=["ResultID", "Username"], errors="ignore"
        )
        st.dataframe(display_results, use_container_width=True)

    with tab3:
        st.subheader("📊 Αναφορά Αδυναμιών & Λανθασμένων Απαντήσεων")
        if not df_weakness.empty:
            selected_student = st.selectbox(
                "Επιλογή Μαθητή για Διαγνωστικό Έλεγχο:",
                df_weakness["Μαθητής"].unique(),
            )
            student_issues = df_weakness[
                df_weakness["Μαθητής"] == selected_student
            ]

            st.write(
                f"**Σημεία που χρειάζεται ενίσχυση ο/η {selected_student}:**"
            )
            for idx, row in student_issues.iterrows():
                q_title = row["Διαγώνισμα"]
                q_idx = row["Αριθμός Ερώτησης"]
                if (
                    q_title in QUIZZES
                    and q_idx < len(QUIZZES[q_title])
                ):
                    q_text = QUIZZES[q_title][q_idx]["question"]
                    st.error(
                        f"❌ **{q_title}** — *Ερώτηση {q_idx + 1}:* {q_text}"
                        " (Λάθος προσπάθειες:"
                        f" {row['Συνολικές Λάθος Απαντήσεις']})"
                    )
        else:
            st.success(
                "🎉 Δεν υπάρχουν καταγεγραμμένες αδυναμίες ή δεν έχουν"
                " υποβληθεί ακόμη απαντήσεις!"
            )

    with tab4:
        st.subheader(f"🔑 Στοιχεία Σύνδεσης Μαθητών ({selected_class})")
        st.info(
            "ℹ️ Χρησιμοποίησε αυτόν τον πίνακα για να δώσεις τα Usernames και"
            " τους Κωδικούς στους μαθητές."
        )
        st.dataframe(filtered_credentials, use_container_width=True)

        if not filtered_credentials.empty:
            csv_creds = filtered_credentials.to_csv(index=False).encode(
                "utf-8-sig"
            )
            st.download_button(
                label="📥 Εξαγωγή Στοιχείων Σύνδεσης σε CSV",
                data=csv_creds,
                file_name=f"passwords_{selected_class}.csv",
                mime="text/csv",
            )

    with tab5:
        st.subheader("🗑️ Διαγραφή Προσπάθειας Μαθητή (Επανεξέταση)")
        st.warning(
            "⚠️ Η διαγραφή προσπάθειας θα επιτρέψει στον μαθητή να ξανακάνει"
            " το συγκεκριμένο Quiz."
        )

        if not filtered_results.empty:
            students_list = sorted(
                filtered_results["Μαθητής"].unique().tolist()
            )
            selected_student_name = st.selectbox(
                "Επιλογή Μαθητή:", students_list
            )
            student_attempts = filtered_results[
                filtered_results["Μαθητής"] == selected_student_name
            ]

            if not student_attempts.empty:
                quizzes_list = sorted(
                    student_attempts["Διαγώνισμα"].unique().tolist()
                )
                selected_quiz = st.selectbox(
                    "Επιλογή Διαγωνίσματος για Διαγραφή:", quizzes_list
                )
                target_attempts = student_attempts[
                    student_attempts["Διαγώνισμα"] == selected_quiz
                ]

                st.write("**Καταγεγραμμένες Προσπάθειες:**")
                st.dataframe(
                    target_attempts[
                        ["Μαθητής", "Διαγώνισμα", "Βαθμός", "Ημερομηνία"]
                    ],
                    use_container_width=True,
                )

                if st.button(
                    "❌ Διαγραφή Όλων των Προσπαθειών για αυτό το Quiz",
                    type="primary",
                ):
                    conn = get_db_connection()
                    cursor = conn.cursor()

                    cursor.execute(
                        "SELECT QuizID FROM Quizzes WHERE Title = ?",
                        (selected_quiz,),
                    )
                    quiz_id = cursor.fetchone()[0]
                    username_to_del = target_attempts.iloc[0]["Username"]

                    cursor.execute(
                        "DELETE FROM QuizResults WHERE Username = ? AND QuizID"
                        " = ?",
                        (username_to_del, quiz_id),
                    )
                    cursor.execute(
                        "DELETE FROM StudentAnswers WHERE Username = ? AND"
                        " QuizID = ?",
                        (username_to_del, quiz_id),
                    )
                    conn.commit()
                    conn.close()

                    st.success(
                        f"Οι προσπάθειες του μαθητή {selected_student_name} για"
                        f" το '{selected_quiz}' διαγράφηκαν!"
                    )
                    st.rerun()
            else:
                st.info(
                    "Ο μαθητής δεν έχει υποβάλει ακόμη κάποιο διαγώνισμα."
                )
        else:
            st.info("Δεν υπάρχουν υποβληθέντα διαγωνίσματα για διαγραφή.")


# ==========================================
# 8. MAIN ROUTER & LOGOUT
# ==========================================
if not st.session_state["logged_in"]:
    login_screen()
else:
    st.sidebar.title("👤 Στοιχεία Χρήστη")
    st.sidebar.write(f"**Χρήστης:** {st.session_state['username']}")
    st.sidebar.write(f"**Ρόλος:** {st.session_state['role']}")

    if st.sidebar.button("Αποσύνδεση"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = ""
        st.session_state["firstname"] = ""
        st.rerun()

    if st.session_state["role"] == "TEACHER":
        teacher_dashboard()
    else:
        student_dashboard()
