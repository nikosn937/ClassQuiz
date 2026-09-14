import streamlit as st
import pandas as pd
import pyodbc
import platform

# ==========================================
# 1. DATABASE CONNECTION
# ==========================================
def get_db_connection():
    # Ανάκτηση στοιχείων από τα Secrets
    server = st.secrets["mssql"]["server"]
    port = st.secrets["mssql"]["port"]
    database = st.secrets["mssql"]["database"]
    username = st.secrets["mssql"]["username"]
    password = st.secrets["mssql"]["password"]

    # Έλεγχος Λειτουργικού Συστήματος (Windows vs Linux/Cloud)
    if platform.system() == "Windows":
        # Driver για τοπική εκτέλεση σε Windows
        driver = "{ODBC Driver 17 for SQL Server}"
        conn_str = f"DRIVER={driver};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}"
    else:
        # Driver για Streamlit Cloud (Linux / FreeTDS)
        driver = "{FreeTDS}"
        conn_str = f"DRIVER={driver};SERVER={server};PORT={port};DATABASE={database};UID={username};PWD={password};TDS_Version=7.4;ClientCharset=UTF-8;"

    return pyodbc.connect(conn_str)

# ==========================================
# 2. PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Εκπαιδευτική Πλατφόρμα Quiz",
    page_icon="🎓",
    layout="wide"
)

# Initialize Session States
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'role' not in st.session_state:
    st.session_state['role'] = ''
if 'firstname' not in st.session_state:
    st.session_state['firstname'] = ''

# ==========================================
# 3. LOGIN FORM
# ==========================================
def login_screen():
    st.title("🔐 Σύνδεση στην Πλατφόρμα")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username_input = st.text_input("Όνομα Χρήστη (Username)")
        password_input = st.text_input("Κωδικός Πρόσβασης (Password)", type="password")
        
        if st.button("Σύνδεση", type="primary", use_container_width=True):
            conn = get_db_connection()
            query = """
                SELECT Username, FirstName, LastName, Role, Password 
                FROM Students 
                WHERE Username = ?
            """
            df_user = pd.read_sql(query, conn, params=[username_input])
            conn.close()

            if not df_user.empty:
                user_row = df_user.iloc[0]
                # Έλεγχος κωδικού (μπορεί να γίνει και με hashing αν χρησιμοποιείτε bcrypt)
                if user_row['Password'] == password_input:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user_row['Username']
                    st.session_state['role'] = user_row['Role']
                    st.session_state['firstname'] = user_row['FirstName']
                    st.success("Επιτυχής σύνδεση!")
                    st.rerun()
                else:
                    st.error("Λανθασμένος κωδικός πρόσβασης.")
            else:
                st.error("Το όνομα χρήστη δεν βρέθηκε.")

# ==========================================
# 4. STUDENT DASHBOARD
# ==========================================
def student_dashboard():
    username = st.session_state['username']
    st.title(f"🎓 Καλωσόρισες, {st.session_state['firstname']}!")
    
    conn = get_db_connection()
    
    # 1. Ανάκτηση Θέσης & Μέσου Όρου από τα Views (Μόνο για τον συνδεδεμένο μαθητή)
    rank_query = """
        SELECT c.AvgScore, c.ClassRank, c.TotalInClass, o.OverallRank, o.TotalStudents
        FROM vw_ClassRankings c
        JOIN vw_OverallRankings o ON c.Username = o.Username
        WHERE c.Username = ?
    """
    df_rank = pd.read_sql(rank_query, conn, params=[username])
    
    # 2. Ανάκτηση Ατομικού Ιστορικού Quiz
    results_query = """
        SELECT q.Title AS [Διαγώνισμα], q.Subject AS [Μάθημα], qr.Score AS [Βαθμός], qr.CompletedAt AS [Ημερομηνία]
        FROM QuizResults qr
        JOIN Quizzes q ON qr.QuizID = q.QuizID
        WHERE qr.Username = ?
        ORDER BY qr.CompletedAt DESC
    """
    df_results = pd.read_sql(results_query, conn, params=[username])
    conn.close()

    # Εμφάνιση Μετρικών Cards
    if not df_rank.empty:
        avg_score = df_rank.iloc[0]['AvgScore']
        class_rank = df_rank.iloc[0]['ClassRank']
        total_class = df_rank.iloc[0]['TotalInClass']
        overall_rank = df_rank.iloc[0]['OverallRank']
        total_overall = df_rank.iloc[0]['TotalStudents']

        col1, col2, col3 = st.columns(3)
        col1.metric("Ο Μέσος Όρος σου", f"{avg_score:.1f} / 100")
        col2.metric("Θέση στο Τμήμα", f"{class_rank}ος", f"σε {total_class} μαθητές")
        col3.metric("Θέση στη Σειρά (Όλες οι τάξεις)", f"{overall_rank}ος", f"σε {total_overall} μαθητές")

    st.divider()
    
    # Πίνακας με τα προσωπικά αποτελέσματα
    st.subheader("📜 Το Ιστορικό των Διαγωνισμάτων σου")
    if not df_results.empty:
        st.dataframe(df_results, use_container_width=True)
    else:
        st.info("Δεν έχεις ολοκληρώσει ακόμη κάποιο διαγώνισμα.")

# ==========================================
# 5. TEACHER DASHBOARD
# ==========================================
def teacher_dashboard():
    st.title("👨‍🏫 Dashboard Καθηγητή")
    st.write("Πλήρης εικόνα επιδόσεων και κατατάξεων μαθητών.")
    
    conn = get_db_connection()
    
    # 1. Ανάκτηση όλων των κατατάξεων
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
    
    # 2. Ανάκτηση αναλυτικών αποτελεσμάτων
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

    # Φίλτρα
    st.sidebar.header("🔍 Φίλτρα Αναζήτησης")
    class_list = ["Όλα τα Τμήματα"] + sorted(df_all_ranks['Τμήμα'].unique().tolist())
    selected_class = st.sidebar.selectbox("Επιλογή Τμήματος", class_list)

    if selected_class != "Όλα τα Τμήματα":
        filtered_ranks = df_all_ranks[df_all_ranks['Τμήμα'] == selected_class]
        filtered_results = df_all_results[df_all_results['Τμήμα'] == selected_class]
    else:
        filtered_ranks = df_all_ranks
        filtered_results = df_all_results

    # Tabs για οργάνωση των πληροφοριών
    tab1, tab2 = st.tabs(["🏆 Γενική Κατάταξη & Μ.Ο.", "📝 Αναλυτικά Αποτελέσματα Quiz"])

    with tab1:
        st.subheader(f"Πίνακας Κατάταξης ({selected_class})")
        st.dataframe(filtered_ranks, use_container_width=True)
        
        # Εξαγωγή σε CSV
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
# 6. MAIN ROUTER & SIDEBAR LOGOUT
# ==========================================
if not st.session_state['logged_in']:
    login_screen()
else:
    # Sidebar
    st.sidebar.title("👤 Στοιχεία Χρήστη")
    st.sidebar.write(f"**Χρήστης:** {st.session_state['username']}")
    st.sidebar.write(f"**Ρόλος:** {st.session_state['role']}")
    
    if st.sidebar.button("Αποσύνδεση"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.session_state['role'] = ''
        st.session_state['firstname'] = ''
        st.rerun()

    # Routing βάσει ρόλου
    if st.session_state['role'] == 'TEACHER':
        teacher_dashboard()
    else:
        student_dashboard()
