import streamlit as st
import sqlite3
import os
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="سستم عجيبة جاردن", layout="wide")

# إعدادات قاعدة البيانات
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'AgibaSystem_New.db')

def init_db():
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, name TEXT, phone TEXT, apt_num TEXT, nights INTEGER, amount REAL, date TEXT)''')
        c.execute('CREATE TABLE IF NOT EXISTS v_vault (shift_total REAL, manager_total REAL)')
        c.execute('SELECT * FROM v_vault')
        if not c.fetchone():
            c.execute('INSERT INTO v_vault VALUES (0, 0)')
        conn.commit()

init_db()

# جلب بيانات الخزنة
with sqlite3.connect(db_path) as conn:
    res = pd.read_sql_query("SELECT * FROM v_vault", conn)
    shift_val = res['shift_total'].iloc[0]
    manager_val = res['manager_total'].iloc[0]

# --- لوحة تحكم المدير (في الجنب) ---
with st.sidebar:
    st.header("🔐 لوحة المدير")
    admin_pass = st.text_input("أدخل الباسورد لرؤية الخزنة", type="password")
    if admin_pass == "161980": # <--- الرقم السري الجديد الخاص بك
        st.success("أهلاً يا سلطان")
        st.metric("🏦 خزنة المدير (الإجمالي)", f"{manager_val:,.2f} ج.م")
        st.divider()
        if st.button("🗑️ مسح كل سجل العمليات"):
            with sqlite3.connect(db_path) as conn:
                conn.execute("DELETE FROM transactions")
            st.rerun()
        if st.button("💰 تصفير خزنة المدير"):
            with sqlite3.connect(db_path) as conn:
                conn.execute("UPDATE v_vault SET manager_total = 0")
            st.rerun()
    elif admin_pass != "":
        st.error("الباسورد خطأ")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🏨 نظام إدارة شقق عجيبة جاردن</h1>", unsafe_allow_html=True)
st.divider()

# --- قسم الإدخال ---
with st.container():
    st.subheader("➕ تسجيل عملية تسكين جديدة")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("اسم العميل")
        phone = st.text_input("رقم الهاتف")
    with col2:
        apt_num = st.text_input("رقم الشقة")
        nights = st.number_input("عدد الليالي", min_value=1, step=1)
    with col3:
        amount = st.number_input("المبلغ المدفوع", min_value=0.0)
        
    if st.button("حفظ التسكين وتحصيل المبلغ 📥", use_container_width=True):
        if name and apt_num:
            with sqlite3.connect(db_path) as conn:
                check = pd.read_sql_query(f"SELECT type FROM transactions WHERE apt_num='{apt_num}' ORDER BY id DESC LIMIT 1", conn)
                if not check.empty and "تسكين" in check['type'].iloc[0]:
                    st.error(f"❌ شقة {apt_num} مشغولة حالياً!")
                else:
                    dt = datetime.now().strftime("%Y-%m-%d %H:%M")
                    conn.execute("INSERT INTO transactions (type, name, phone, apt_num, nights, amount, date) VALUES (?,?,?,?,?,?,?)", 
                             ("تسكين 📥", name, phone, apt_num, nights, amount, dt))
                    conn.execute("UPDATE v_vault SET shift_total = shift_total + ?, manager_total = manager_total + ?", (amount, amount))
                    conn.commit()
                    st.success(f"تم تسكين {name} بنجاح!")
                    st.rerun()

st.divider()

# --- عرض خزنة الشفت فقط في الشاشة الرئيسية ---
c1, c2 = st.columns(2)
c1.metric("💰 خزنة الشفت (الحالية)", f"{shift_val:,.2f} ج.م")
with c2:
    if st.button("🔄 تصفير الشفت"):
        with sqlite3.connect(db_path) as conn:
            conn.execute("UPDATE v_vault SET shift_total = 0")
        st.rerun()

st.divider()

# --- سجل العمليات والإخلاء ---
st.subheader("📋 سجل العمليات")
with sqlite3.connect(db_path) as conn:
    df = pd.read_sql_query("SELECT id, type, name, apt_num, date FROM transactions ORDER BY id DESC LIMIT 10", conn)

for index, row in df.iterrows():
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.write(f"🏠 {row['apt_num']}")
    col_b.write(f"👤 {row['name']}")
    col_c.write(f"📅 {row['date']}")
    if "تسكين" in row['type']:
        if col_d.button(f"إخلاء 📤", key=f"btn_{row['id']}"):
            dt_now = datetime.now().strftime("%Y-%m-%d %H:%M")
            with sqlite3.connect(db_path) as conn:
                conn.execute("INSERT INTO transactions (type, name, phone, apt_num, nights, amount, date) VALUES (?,?,?,?,?,?,?)", 
                         ("مغادرة 📤", row['name'], "-", row['apt_num'], 0, 0, dt_now))
                conn.commit()
            st.rerun()
    else:
        col_d.write("✅ تم")
    st.divider()
