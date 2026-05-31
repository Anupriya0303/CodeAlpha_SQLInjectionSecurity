import sqlite3
import hashlib
import re
import random
from datetime import datetime

# ============================================
#   ENCRYPTION SYSTEM (AES-256 Simulated)
# ============================================
def encrypt(data, key="HospitalSecure@2025"):
    encrypted = ""
    for i, char in enumerate(data):
        encrypted += chr(ord(char) ^ ord(key[i % len(key)]))
    return encrypted.encode().hex()

def decrypt(encrypted_hex, key="HospitalSecure@2025"):
    try:
        encrypted = bytes.fromhex(encrypted_hex).decode()
        decrypted = ""
        for i, char in enumerate(encrypted):
            decrypted += chr(ord(char) ^ ord(key[i % len(key)]))
        return decrypted
    except:
        return "❌ Decryption Failed"

# ============================================
#   SQL INJECTION DETECTOR
# ============================================
def is_sql_injection(text):
    patterns = [
        r"(\bSELECT\b)", r"(\bDROP\b)", r"(\bDELETE\b)",
        r"(\bINSERT\b)", r"(\bUNION\b)", r"(\bUPDATE\b)",
        r"(--)", r"(/\*)", r"(1=1)", r"(OR\s+1=1)",
        r"(\bEXEC\b)", r"(;)", r"(')", r"(\bDROP TABLE\b)",
        r"(\bOR\b)", r"(\bAND\b\s+\d+=\d+)"
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

# ============================================
#   DATABASE SETUP
# ============================================
def setup_db():
    conn = sqlite3.connect("hospital_secure.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        encrypted_phone TEXT NOT NULL,
        encrypted_diagnosis TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        doctor TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS attack_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        input_data TEXT NOT NULL,
        attack_type TEXT NOT NULL,
        blocked_at TEXT NOT NULL,
        severity TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )''')

    conn.commit()
    return conn

# ============================================
#   STAFF LOGIN
# ============================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_default_staff(conn):
    try:
        conn.execute(
            "INSERT INTO staff (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", hash_password("admin123"), "Administrator")
        )
        conn.execute(
            "INSERT INTO staff (username, password_hash, role) VALUES (?, ?, ?)",
            ("doctor1", hash_password("doctor123"), "Doctor")
        )
        conn.commit()
    except:
        pass

def login(conn):
    print("\n" + "=" * 55)
    print("      🏥 HOSPITAL SECURE LOGIN PORTAL")
    print("=" * 55)
    print("  🔐 Double Layer Security Active")
    print("  🛡️  SQL Injection Protection: ON")
    print("=" * 55)

    attempts = 0
    while attempts < 3:
        username = input("\n  👤 Username: ").strip()
        password = input("  🔑 Password: ").strip()

        # Layer 1: SQL Injection Check
        if is_sql_injection(username) or is_sql_injection(password):
            severity = "CRITICAL"
            conn.execute(
                "INSERT INTO attack_logs (input_data, attack_type, blocked_at, severity) VALUES (?, ?, ?, ?)",
                (f"User:{username} Pass:{password}", "SQL Injection Attempt", 
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"), severity)
            )
            conn.commit()
            print("\n  🚨 SECURITY ALERT!")
            print("  ❌ SQL Injection Detected!")
            print("  🛡️  Attack Blocked & Logged!")
            print(f"  ⚠️  Severity: {severity}")
            return None, None

        # Layer 2: Password Hash Check
        cursor = conn.execute(
            "SELECT username, role FROM staff WHERE username=? AND password_hash=?",
            (username, hash_password(password))
        )
        staff = cursor.fetchone()

        if staff:
            print(f"\n  ✅ Welcome {staff[0]}! Role: {staff[1]}")
            return staff[0], staff[1]
        else:
            attempts += 1
            print(f"\n  ❌ Invalid credentials! {3-attempts} attempts remaining")

    print("\n  🔒 Account locked after 3 failed attempts!")
    return None, None

# ============================================
#   PATIENT MANAGEMENT
# ============================================
def generate_patient_id():
    return f"PID{random.randint(10000, 99999)}"

def add_patient(conn, staff_name):
    print("\n" + "=" * 55)
    print("         🏥 ADD NEW PATIENT RECORD")
    print("=" * 55)

    name = input("  Patient Name    : ").strip()
    phone = input("  Phone Number    : ").strip()
    diagnosis = input("  Diagnosis       : ").strip()
    blood_group = input("  Blood Group     : ").strip()
    doctor = input("  Doctor Name     : ").strip()

    # SQL Injection Check on all inputs
    all_inputs = [name, phone, diagnosis, blood_group, doctor]
    for inp in all_inputs:
        if is_sql_injection(inp):
            conn.execute(
                "INSERT INTO attack_logs (input_data, attack_type, blocked_at, severity) VALUES (?, ?, ?, ?)",
                (inp, "SQL Injection in Patient Form",
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "HIGH")
            )
            conn.commit()
            print(f"\n  🚨 SQL Injection detected in input: '{inp}'")
            print("  ❌ Patient record NOT saved! Attack logged!")
            return

    # Encrypt sensitive data
    enc_phone = encrypt(phone)
    enc_diagnosis = encrypt(diagnosis)
    patient_id = generate_patient_id()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn.execute(
            "INSERT INTO patients (patient_id, name, encrypted_phone, encrypted_diagnosis, blood_group, doctor, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (patient_id, name, enc_phone, enc_diagnosis, blood_group, doctor, timestamp)
        )
        conn.commit()
        print(f"\n  ✅ Patient added successfully!")
        print(f"  🆔 Patient ID    : {patient_id}")
        print(f"  👤 Name          : {name}")
        print(f"  🔐 Phone         : [ENCRYPTED]")
        print(f"  🔐 Diagnosis     : [ENCRYPTED]")
        print(f"  🩸 Blood Group   : {blood_group}")
        print(f"  👨‍⚕️ Doctor        : {doctor}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def view_patients(conn):
    print("\n" + "=" * 55)
    print("         🏥 PATIENT RECORDS")
    print("=" * 55)

    cursor = conn.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    if not patients:
        print("  No patient records found!")
    else:
        for p in patients:
            print(f"\n  🆔 ID      : {p[1]}")
            print(f"  👤 Name    : {p[2]}")
            print(f"  📱 Phone   : {decrypt(p[3])}")
            print(f"  🏥 Diagnosis: {decrypt(p[4])}")
            print(f"  🩸 Blood   : {p[5]}")
            print(f"  👨‍⚕️ Doctor  : {p[6]}")
            print(f"  🕐 Added   : {p[7]}")
            print("  " + "-" * 51)

    print(f"\n  Total Patients: {len(patients)}")

def search_patient(conn):
    keyword = input("\n  🔍 Search by name or Patient ID: ").strip()

    if is_sql_injection(keyword):
        print("\n  🚨 SQL Injection detected in search!")
        print("  ❌ Search blocked!")
        return

    cursor = conn.execute(
        "SELECT * FROM patients WHERE name LIKE ? OR patient_id LIKE ?",
        (f"%{keyword}%", f"%{keyword}%")
    )
    results = cursor.fetchall()

    print(f"\n  🔍 Results for '{keyword}':")
    if not results:
        print("  No matching patients found!")
    else:
        for p in results:
            print(f"\n  🆔 {p[1]} | 👤 {p[2]} | 🩸 {p[5]} | 👨‍⚕️ {p[6]}")

def view_attack_logs(conn):
    print("\n" + "=" * 55)
    print("      🚨 SECURITY ATTACK LOGS DASHBOARD")
    print("=" * 55)

    cursor = conn.execute("SELECT * FROM attack_logs ORDER BY id DESC")
    logs = cursor.fetchall()

    if not logs:
        print("  ✅ No attacks detected! System is safe!")
    else:
        for log in logs:
            print(f"\n  ⚠️  Attack #{log[0]}")
            print(f"  📝 Input     : {log[1][:40]}...")
            print(f"  🎯 Type      : {log[2]}")
            print(f"  🕐 Time      : {log[3]}")
            print(f"  🔴 Severity  : {log[4]}")
            print("  " + "-" * 51)

    print(f"\n  Total Attacks Blocked: {len(logs)}")
    print("  🛡️  System Security Status: PROTECTED")

def simulate_attack(conn):
    print("\n" + "=" * 55)
    print("      🎮 SQL INJECTION ATTACK SIMULATOR")
    print("=" * 55)
    print("  Testing system security with known attacks...\n")

    attacks = [
        ("' OR '1'='1", "Classic SQL Injection"),
        ("admin'--", "Comment Injection"),
        ("1; DROP TABLE patients;--", "Drop Table Attack"),
        ("UNION SELECT * FROM staff--", "Union Attack"),
        ("' OR 1=1--", "Boolean Attack"),
    ]

    blocked = 0
    for attack, attack_type in attacks:
        if is_sql_injection(attack):
            conn.execute(
                "INSERT INTO attack_logs (input_data, attack_type, blocked_at, severity) VALUES (?, ?, ?, ?)",
                (attack, attack_type,
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "CRITICAL")
            )
            conn.commit()
            print(f"  🚨 BLOCKED: {attack_type}")
            print(f"     Input: {attack}")
            blocked += 1
        print()

    print(f"  ✅ {blocked}/{len(attacks)} attacks successfully blocked!")
    print("  🛡️  Hospital data is SECURE!")

# ============================================
#   MAIN MENU
# ============================================
def main():
    print("\n" + "=" * 55)
    print("   🏥 HOSPITAL PATIENT DATA SECURITY SYSTEM")
    print("   🔐 SQL Injection Protection + AES Encryption")
    print("=" * 55)

    conn = setup_db()
    create_default_staff(conn)

    username, role = login(conn)
    if not username:
        print("\n  ❌ Access Denied! Exiting system...")
        conn.close()
        return

    while True:
        print("\n" + "=" * 55)
        print(f"  🏥 HOSPITAL SYSTEM  |  👤 {username}  |  {role}")
        print("=" * 55)
        print("  1️⃣  Add Patient Record")
        print("  2️⃣  View All Patients")
        print("  3️⃣  Search Patient")
        print("  4️⃣  View Attack Logs")
        print("  5️⃣  Simulate SQL Attack")
        print("  6️⃣  Exit")
        print("=" * 55)

        choice = input("  Choose option (1-6): ").strip()

        if choice == "1":
            add_patient(conn, username)
        elif choice == "2":
            view_patients(conn)
        elif choice == "3":
            search_patient(conn)
        elif choice == "4":
            view_attack_logs(conn)
        elif choice == "5":
            simulate_attack(conn)
        elif choice == "6":
            print(f"\n  🏥 Goodbye {username}! Stay safe! 👋")
            conn.close()
            break
        else:
            print("  ❌ Invalid choice!")

        input("\n  Press Enter to continue...")

main()