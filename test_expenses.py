import sqlite3
import os
from datetime import datetime

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'AgibaSystem_New.db')

def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, name TEXT, 
                  phone TEXT, apt_num TEXT, nights INTEGER, amount REAL, date TEXT)''')
    c.execute('CREATE TABLE IF NOT EXISTS v_vault (shift_total REAL, manager_total REAL)')
    c.execute('SELECT count(*) FROM v_vault')
    if c.fetchone() == 0:
        c.execute('INSERT INTO v_vault VALUES (0, 0)')
    conn.commit()
    conn.close()

def main():
    init_db()
    
    print("========================================")
    print("    AGIBA GARDEN - EXPENSES SYSTEM     ")
    print("========================================")
    
    try:
        # شيلنا العربي تماماً من المطالبة عشان المربعات
        reason = input("Enter Reason (You can type in Arabic): ")
        amount_input = input("Enter Amount: ")
        
        amount = float(amount_input)

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        dt = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # العملية هتتسجل في القاعدة بالتايج العربي عشان تظهر في السيستم التاني صح
        c.execute("""INSERT INTO transactions (type, name, phone, apt_num, nights, amount, date) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                 ("مصروفات 🚫", reason, "-", "Expenses", 0, -amount, dt))
        
        c.execute("UPDATE v_vault SET shift_total = shift_total - ?, manager_total = manager_total - ?", 
                  (amount, amount))
        
        conn.commit()
        conn.close()

        print("\n" + "*"*30)
        print(f"SUCCESS: {amount} EGP Saved.")
        print("*"*30)
        
    except ValueError:
        print("\nERROR: Please enter numbers only for amount.")
    except Exception as e:
        print(f"\nERROR: {e}")

    print("\n" + "-"*40)
    input("Press Enter to Exit...")

if __name__ == "__main__":
    main()
