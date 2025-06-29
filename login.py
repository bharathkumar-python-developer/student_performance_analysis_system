# login.py - Enhanced Login System with Passlib, Registration, and Role-Based Access
import tkinter as tk
from tkinter import messagebox
import sqlite3
from passlib.hash import pbkdf2_sha256
import main_app

# Initialize DB and users table
conn = sqlite3.connect("student.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
""")
conn.commit()

# Insert default admin if not exists
try:
    cursor.execute("INSERT INTO users VALUES (?, ?, ?)", ("admin", pbkdf2_sha256.hash("admin123"), "admin"))
    conn.commit()
except sqlite3.IntegrityError:
    pass

# --- Login Window ---
login_win = tk.Tk()
login_win.title("Login - Student System")
login_win.geometry("400x300")
login_win.configure(bg="#f0f2f5")

# --- Register Window ---
def open_register():
    reg_win = tk.Toplevel(login_win)
    reg_win.title("Register New User")
    reg_win.geometry("350x300")

    def register_user():
        uname = reg_user.get().strip()
        pwd = reg_pass.get().strip()
        role = role_var.get()
        if not uname or not pwd:
            messagebox.showwarning("Error", "All fields required.", parent=reg_win)
            return
        try:
            hashed_pwd = pbkdf2_sha256.hash(pwd)
            cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (uname, hashed_pwd, role))
            conn.commit()
            messagebox.showinfo("Success", "User registered.", parent=reg_win)
            reg_win.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Exists", "Username already taken.", parent=reg_win)

    tk.Label(reg_win, text="Register", font=("Arial", 14, "bold")).pack(pady=10)
    tk.Label(reg_win, text="Username:").pack()
    reg_user = tk.Entry(reg_win)
    reg_user.pack(pady=5)
    tk.Label(reg_win, text="Password:").pack()
    reg_pass = tk.Entry(reg_win, show="*")
    reg_pass.pack(pady=5)
    tk.Label(reg_win, text="Role (admin/user):").pack()
    role_var = tk.StringVar(value="user")
    tk.OptionMenu(reg_win, role_var, "admin", "user").pack(pady=5)
    tk.Button(reg_win, text="Register", command=register_user).pack(pady=10)

# --- Perform Login ---
def login():
    uname = username_entry.get().strip()
    pwd = password_entry.get().strip()
    if not uname or not pwd:
        messagebox.showwarning("Input Error", "Enter username & password.")
        return

    cursor.execute("SELECT password, role FROM users WHERE username=?", (uname,))
    result = cursor.fetchone()

    if result and pbkdf2_sha256.verify(pwd, result[0]):
        role = result[1]
        login_win.destroy()
        main_app.run_main_app(role)
    else:
        messagebox.showerror("Access Denied", "Invalid credentials.")

# --- GUI Layout ---
tk.Label(login_win, text="Login", font=("Arial", 16, "bold"), bg="#f0f2f5").pack(pady=20)
tk.Label(login_win, text="Username:", bg="#f0f2f5").pack()
username_entry = tk.Entry(login_win, width=30)
username_entry.pack(pady=5)
tk.Label(login_win, text="Password:", bg="#f0f2f5").pack()
password_entry = tk.Entry(login_win, show="*", width=30)
password_entry.pack(pady=5)
tk.Button(login_win, text="Login", command=login, bg="#007BFF", fg="white", width=15).pack(pady=10)
tk.Button(login_win, text="Register", command=open_register, bg="#28a745", fg="white", width=15).pack()

login_win.mainloop()
