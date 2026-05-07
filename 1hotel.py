import streamlit as st
import sqlite3
import os
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="سستم عجيبة جاردن", layout="wide")

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

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🏨 نظام إدارة شقق عجيبة جاردن</h1>", unsafe_allow_html=True)
st.divider()

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
            dt = datetime.now().strftime("%Y-%m-%d %H:%M")
            with sqlite3.connect(db_path) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO transactions (type, name, phone, apt_num, nights, amount, date) VALUES (?,?,?,?,?,?,?)", 
                         ("تسكين 📥", name, phone, apt_num, nights, amount, dt))
                c.execute("UPDATE v_vault SET shift_total = shift_total + ?, manager_total = manager_total + ?", (amount, amount))
            st.success(f"تم تسكين {name} بنجاح!")
            st.rerun()

st.divider()

with sqlite3.connect(db_path) as conn:
    res = pd.read_sql_query("SELECT * FROM v_vault", conn)
    shift_val = res['shift_total'].iloc[0]
    manager_val = res['manager_total'].iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric("💰 خزنة الشفت", f"{shift_val:,.2f} ج.م")
c2.metric("🏦 خزنة المدير", f"{manager_val:,.2f} ج.م")
with c3:
    if st.button("🔄 تصفير الشفت"):
        with sqlite3.connect(db_path) as conn:
            conn.execute("UPDATE v_vault SET shift_total = 0")
        st.rerun()

st.divider()
st.subheader("📋 سجل آخر العمليات")
with sqlite3.connect(db_path) as conn:
    df = pd.read_sql_query("SELECT type, name, phone, apt_num, nights, amount, date FROM transactions ORDER BY id DESC LIMIT 50", conn)
    st.dataframe(df, use_container_width=True)
