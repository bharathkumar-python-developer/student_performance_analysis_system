# main_app.py - Role-Based Student Performance System
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            roll TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            subject1 INTEGER,
            subject2 INTEGER,
            subject3 INTEGER
        )
    """)
    conn.commit()
    return conn, cursor

conn, cursor = init_db()

# --- GUI App Function ---
def run_main_app(role):
    root = tk.Tk()
    root.title("Student Performance Analysis System")
    root.geometry("900x600")
    root.configure(bg="#f0f2f5")

    def add_student():
        roll = roll_entry.get().strip()
        name = name_entry.get().strip()
        try:
            s1 = int(subject1_entry.get())
            s2 = int(subject2_entry.get())
            s3 = int(subject3_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "All subject marks must be integers.")
            return

        if not roll or not name:
            messagebox.showwarning("Missing Data", "Roll No and Name are required.")
            return

        try:
            cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?)", (roll, name, s1, s2, s3))
            conn.commit()
            messagebox.showinfo("Success", f"Student '{name}' added successfully.")
            clear_fields()
            view_students()
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Entry", "Roll No already exists.")

    def delete_record():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a student to delete.")
            return
        roll = tree.item(selected[0])['values'][0]
        cursor.execute("DELETE FROM students WHERE roll=?", (roll,))
        conn.commit()
        view_students()
        messagebox.showinfo("Deleted", "Student record deleted.")

    def clear_fields():
        for e in [roll_entry, name_entry, subject1_entry, subject2_entry, subject3_entry]:
            e.delete(0, tk.END)

    def view_students():
        tree.delete(*tree.get_children())
        cursor.execute("SELECT * FROM students")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    def plot_performance():
        cursor.execute("SELECT name, subject1 + subject2 + subject3 FROM students")
        data = cursor.fetchall()
        if not data:
            messagebox.showinfo("No Data", "No student records to display.")
            return
        names = [x[0] for x in data]
        totals = [x[1] for x in data]
        plt.figure(figsize=(8, 5))
        plt.bar(names, totals, color="#4B9CD3")
        plt.title("Total Marks of Students")
        plt.xlabel("Name")
        plt.ylabel("Total Marks")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # --- Input Frame ---
    input_frame = tk.LabelFrame(root, text="Student Details", bg="#f0f2f5", font=("Arial", 10, "bold"))
    input_frame.pack(fill="x", padx=20, pady=10)

    tk.Label(input_frame, text="Roll No:", bg="#f0f2f5").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    tk.Label(input_frame, text="Name:", bg="#f0f2f5").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    tk.Label(input_frame, text="Subject 1:", bg="#f0f2f5").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    tk.Label(input_frame, text="Subject 2:", bg="#f0f2f5").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    tk.Label(input_frame, text="Subject 3:", bg="#f0f2f5").grid(row=4, column=0, padx=5, pady=5, sticky="w")

    roll_entry = tk.Entry(input_frame)
    name_entry = tk.Entry(input_frame)
    subject1_entry = tk.Entry(input_frame)
    subject2_entry = tk.Entry(input_frame)
    subject3_entry = tk.Entry(input_frame)

    roll_entry.grid(row=0, column=1, pady=5)
    name_entry.grid(row=1, column=1, pady=5)
    subject1_entry.grid(row=2, column=1, pady=5)
    subject2_entry.grid(row=3, column=1, pady=5)
    subject3_entry.grid(row=4, column=1, pady=5)

    # --- Button Frame ---
    button_frame = tk.Frame(root, bg="#f0f2f5")
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="View Records", command=view_students, bg="#17a2b8", fg="white").grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="Plot Performance", command=plot_performance, bg="#6f42c1", fg="white").grid(row=0, column=1, padx=10)

    if role == "admin":
        tk.Button(button_frame, text="Add Student", command=add_student, bg="#007BFF", fg="white").grid(row=0, column=2, padx=10)
        tk.Button(button_frame, text="Delete Record", command=delete_record, bg="#dc3545", fg="white").grid(row=0, column=3, padx=10)
        tk.Button(button_frame, text="Clear Fields", command=clear_fields, bg="#ffc107").grid(row=0, column=4, padx=10)

    # --- Treeview ---
    tree_frame = tk.Frame(root)
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = ("roll", "name", "s1", "s2", "s3")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, anchor="center", width=100)

    scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll_y.set)
    scroll_y.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)

    # Load Data
    view_students()
    root.mainloop()
