import streamlit as st
import sqlite3
import os
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="سستم المصروفات - عجيبة جاردن", layout="wide")

# إعدادات قاعدة البيانات (نفس المسار لربط الملفين)
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'AgibaSystem_New.db')

st.markdown("<h1 style='text-align: center; color: #e74c3c;'>💸 إدارة مصروفات عجيبة جاردن</h1>", unsafe_allow_html=True)
st.divider()

# --- قسم إدخال المصروفات ---
with st.container():
    col1, col2 = st.columns([2, 1])
    with col1:
        reason = st.text_input("بيان المصروف (مثلاً: سباكة، كهرباء، منظفات)")
    with col2:
        amount = st.number_input("المبلغ (ج.م)", min_value=0.0, step=10.0)

    if st.button("تسجيل المصروف وخصمه من الخزنة ⬇️", use_container_width=True):
        if reason and amount > 0:
            with sqlite3.connect(db_path) as conn:
                dt = datetime.now().strftime("%Y-%m-%d %H:%M")
                # 1. تسجيل العملية في الجدول العام كـ "مصروف"
                conn.execute("""INSERT INTO transactions (type, name, phone, apt_num, nights, amount, date) 
                                VALUES (?,?,?,?,?,?,?)""", 
                             ("مصروفات 🚫", reason, "-", "نثريات", 0, -amount, dt))
                
                # 2. الخصم من الخزنة (الشفت والمدير)
                conn.execute("UPDATE v_vault SET shift_total = shift_total - ?, manager_total = manager_total - ?", 
                             (amount, amount))
                conn.commit()
                st.success(f"تم تسجيل {amount} ج.م بنجاح")
                st.rerun()
        else:
            st.error("من فضلك ادخل البيان والمبلغ")

st.divider()

# --- قسم عرض وفلترة المصروفات ---
st.subheader("🔍 سجل المصروفات السابقة")

with sqlite3.connect(db_path) as conn:
    # هنجيب فقط العمليات اللي نوعها "مصروفات"
    df_ex = pd.read_sql_query("SELECT date, name as 'البيان', amount as 'المبلغ' FROM transactions WHERE type LIKE '%مصروفات%' ORDER BY id DESC", conn)

if not df_ex.empty:
    # تحويل المبلغ لقيمة موجبة للعرض فقط بشكل أشيك
    df_display = df_ex.copy()
    df_display['المبلغ'] = df_display['المبلغ'].abs()
    
    # إحصائية سريعة
    total_spent = df_display['المبلغ'].sum()
    st.info(f"إجمالي ما تم صرفه المسجل في القائمة: {total_spent:,.2f} ج.م")
    
    # عرض الجدول
    st.table(df_display)
else:
    st.write("لا توجد مصروفات مسجلة حتى الآن.")

# --- زر للعودة أو التذكير ---
st.sidebar.info("💡 ملاحظة: أي مبلغ بيتم تسجيله هنا بيخصم فوراً من خزنة السيستم الرئيسي.")
