import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
from datetime import datetime

# إعدادات الألوان
COLOR_BG = "#f4f7f6"
COLOR_PRIMARY = "#2c3e50"
COLOR_ACCENT = "#3498db"
COLOR_SUCCESS = "#27ae60"
COLOR_DANGER = "#e74c3c"

class HotelManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("سستم إدارة - عجيبة جاردن")
        self.root.geometry("1150x850")
        self.root.configure(bg=COLOR_BG)
        
        # مسار الداتابيز
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, 'AgibaSystem_New.db')
        
        self.init_database()
        self.create_widgets()
        self.update_ui_data()

    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS transactions 
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          type TEXT, name TEXT, phone TEXT, apt_num TEXT, 
                          nights INTEGER, amount REAL, date TEXT)''')
            c.execute('CREATE TABLE IF NOT EXISTS v_vault (shift_total REAL, manager_total REAL)')
            c.execute('SELECT * FROM v_vault')
            if not c.fetchone():
                c.execute('INSERT INTO v_vault VALUES (0, 0)')
            conn.commit()

    def create_widgets(self):
        header = tk.Frame(self.root, bg=COLOR_PRIMARY, height=100)
        header.pack(fill="x")
        tk.Label(header, text="نظام إدارة شقق عجيبة جاردن", fg="white", 
                 bg=COLOR_PRIMARY, font=("Arial", 22, "bold")).pack(pady=20)

        input_frame = tk.LabelFrame(self.root, text=" تسجيل بيانات العملية ", bg="white", 
                                    font=("Arial", 12, "bold"), padx=15, pady=20)
        input_frame.pack(padx=20, pady=20, fill="x")

        labels = ["اسم العميل:", "رقم الهاتف:", "رقم الشقة:", "عدد الليالي:", "المبلغ المدفوع:"]
        keys = ["name", "phone", "apt_num", "nights", "amount"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(input_frame, text=label, bg="white", font=("Arial", 10)).grid(row=0, column=i*2, padx=5, sticky="e")
            ent = tk.Entry(input_frame, width=12, font=("Arial", 10))
            ent.grid(row=0, column=i*2+1, padx=5, pady=10)
            self.entries[keys[i]] = ent

        btn_frame = tk.Frame(self.root, bg=COLOR_BG)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="تسكين وتحصيل (In)", bg=COLOR_SUCCESS, fg="white", 
                  font=("Arial", 11, "bold"), width=25, height=2, command=self.process_checkin).pack(side="left", padx=10)
        
        # زر الإخلاء المطور
        tk.Button(btn_frame, text="إخلاء المختار (Out)", bg=COLOR_DANGER, fg="white", 
                  font=("Arial", 11, "bold"), width=25, height=2, command=self.process_checkout_selected).pack(side="left", padx=10)

        vault_frame = tk.Frame(self.root, bg=COLOR_BG)
        vault_frame.pack(pady=20, fill="x", padx=50)

        shift_box = tk.Frame(vault_frame, bg="white", bd=2, relief="groove")
        shift_box.pack(side="left", expand=True, fill="both", padx=10)
        self.lbl_shift = tk.Label(shift_box, text="خزنة الشفت: 0 ج.م", font=("Arial", 14, "bold"), fg=COLOR_PRIMARY, bg="white", pady=10)
        self.lbl_shift.pack()
        tk.Button(shift_box, text="تصفير الشفت 🔄", bg=COLOR_ACCENT, fg="white", command=self.reset_shift).pack(pady=5)

        manager_box = tk.Frame(vault_frame, bg="white", bd=2, relief="groove")
        manager_box.pack(side="right", expand=True, fill="both", padx=10)
        self.lbl_manager = tk.Label(manager_box, text="خزنة المدير (الإجمالي): 0 ج.م", font=("Arial", 14, "bold"), fg="#c0392b", bg="white", pady=18)
        self.lbl_manager.pack()

        table_frame = tk.Frame(self.root)
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tree = ttk.Treeview(table_frame, columns=("1", "2", "3", "4", "5", "6", "7"), show="headings")
        cols = [("1", "التاريخ"), ("2", "المبلغ"), ("3", "الليالي"), ("4", "الشقة"), ("5", "الهاتف"), ("6", "الاسم"), ("7", "النوع")]
        for id, name in cols:
            self.tree.heading(id, text=name)
            self.tree.column(id, anchor="center", width=110)
        self.tree.pack(fill="both", expand=True)

    def process_checkin(self):
        try:
            name = self.entries['name'].get()
            phone = self.entries['phone'].get()
            apt_num = self.entries['apt_num'].get()
            nights = int(self.entries['nights'].get() or 0)
            amount = float(self.entries['amount'].get() or 0)
            dt = datetime.now().strftime("%Y-%m-%d %H:%M")

            if not (name and apt_num): 
                messagebox.showwarning("تنبيه", "برجاء إدخال الاسم ورقم الشقة")
                return

            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO transactions (type, name, phone, apt_num, nights, amount, date) VALUES (?,?,?,?,?,?,?)",
                          ("تسكين 📥", name, phone, apt_num, nights, amount, dt))
                c.execute("UPDATE v_vault SET shift_total = shift_total + ?, manager_total = manager_total + ?", (amount, amount))
                conn.commit()

            self.clear_entries()
            self.update_ui_data()
            messagebox.showinfo("نجاح", f"تم تسكين شقة {apt_num}")
        except Exception as e:
            messagebox.showerror("خطأ", "تأكد من كتابة الأرقام بشكل صحيح")

    def process_checkout_selected(self):
        # 1. تحديد الصف المختار
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("تنبيه", "برجاء اختيار (تحديد) عملية من الجدول أولاً بالماوس")
            return
        
        # 2. استخراج البيانات من الصف المختار
        item_data = self.tree.item(selected_item)['values']
        # ترتيب القيم في الجدول: تاريخ، مبلغ، ليالي، شقة، هاتف، اسم، نوع
        apt_num = item_data[3]
        name = item_data[5]
        
        # 3. تنفيذ عملية الإخلاء
        dt = datetime.now().strftime("%Y-%m-%d %H:%M")
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO transactions (type, name, phone, apt_num, nights, amount, date) VALUES (?,?,?,?,?,?,?)",
                      ("مغادرة 📤", name, "-", apt_num, 0, 0, dt))
            conn.commit()
        
        self.update_ui_data()
        messagebox.showinfo("مغادرة", f"تم إخلاء شقة {apt_num} بنجاح")

    def reset_shift(self):
        if messagebox.askyesno("تصفير الشفت", "هل تريد تصفير خزنة الشفت؟"):
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("UPDATE v_vault SET shift_total = 0")
                conn.commit()
            self.update_ui_data()

    def update_ui_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT date, amount, nights, apt_num, phone, name, type FROM transactions ORDER BY id DESC LIMIT 50")
            for row in c.fetchall():
                self.tree.insert("", "end", values=row)
            
            c.execute("SELECT shift_total, manager_total FROM v_vault")
            res = c.fetchone()
            if res:
                self.lbl_shift.config(text=f"خزنة الشفت: {res[0]:,.2f} ج.م")
                self.lbl_manager.config(text=f"خزنة المدير (الإجمالي): {res[1]:,.2f} ج.م")

    def clear_entries(self):
        for ent in self.entries.values():
            ent.delete(0, 'end')

if __name__ == "__main__":
    root = tk.Tk()
    app = HotelManagementSystem(root)
    root.mainloop()
