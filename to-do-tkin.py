import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# Connect to SQLite DB
conn = sqlite3.connect('todo_advanced.db')
c = conn.cursor()

# Create tasks table
c.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        due_date TEXT,
        priority TEXT,
        status TEXT DEFAULT 'Pending'
    )
''')
conn.commit()

# Add task
def add_task():
    task = entry_task.get()
    due_date = entry_due.get()
    priority = combo_priority.get()

    if task and priority:
        c.execute("INSERT INTO tasks (task, due_date, priority) VALUES (?, ?, ?)",
                  (task, due_date, priority))
        conn.commit()
        clear_inputs()
        load_tasks()
    else:
        messagebox.showwarning("Input Error", "Please enter task and priority.")

# Load tasks with filters
def load_tasks(filter_status=None, search_query=None):
    listbox_tasks.delete(0, tk.END)
    query = "SELECT id, task, due_date, priority, status FROM tasks"
    params = []

    if filter_status and filter_status != "All":
        query += " WHERE status = ?"
        params.append(filter_status)
    if search_query:
        if "WHERE" in query:
            query += " AND task LIKE ?"
        else:
            query += " WHERE task LIKE ?"
        params.append(f"%{search_query}%")

    c.execute(query, params)
    for row in c.fetchall():
        task_str = f"{row[0]}. {row[1]} | Due: {row[2]} | Priority: {row[3]} | [{row[4]}]"
        color = "black"
        if row[3] == "High":
            color = "red"
        elif row[3] == "Medium":
            color = "orange"
        elif row[3] == "Low":
            color = "green"
        listbox_tasks.insert(tk.END, task_str)
        listbox_tasks.itemconfig(tk.END, {'fg': color})

def clear_inputs():
    entry_task.delete(0, tk.END)
    entry_due.delete(0, tk.END)
    combo_priority.set("")

def delete_task():
    selected = listbox_tasks.curselection()
    if selected:
        task_id = listbox_tasks.get(selected[0]).split(".")[0]
        c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        load_tasks()
    else:
        messagebox.showwarning("Select Task", "Please select a task to delete.")

def mark_done():
    selected = listbox_tasks.curselection()
    if selected:
        task_id = listbox_tasks.get(selected[0]).split(".")[0]
        c.execute("UPDATE tasks SET status='Done' WHERE id=?", (task_id,))
        conn.commit()
        load_tasks()
    else:
        messagebox.showwarning("Select Task", "Please select a task to mark as done.")

def apply_filter():
    status = combo_filter.get()
    search_text = entry_search.get()
    load_tasks(status, search_text)

# GUI Setup
root = tk.Tk()
root.title("To-Do List")
root.geometry("700x600")
root.configure(bg="#f0f4f8")

font_title = ("Helvetica", 18, "bold")
font_label = ("Arial", 12)
font_entry = ("Arial", 11)

# Header
tk.Label(root, text="My To-Do List", font=font_title, bg="#f0f4f8", fg="#333").pack(pady=10)

# Input Frame
frame_input = tk.Frame(root, bg="#f0f4f8")
frame_input.pack(pady=10)

tk.Label(frame_input, text="Task:", font=font_label, bg="#f0f4f8").grid(row=0, column=0, sticky="e")
entry_task = tk.Entry(frame_input, width=40, font=font_entry)
entry_task.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame_input, text="Due Date:", font=font_label, bg="#f0f4f8").grid(row=1, column=0, sticky="e")
entry_due = tk.Entry(frame_input, width=40, font=font_entry)
entry_due.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame_input, text="Priority:", font=font_label, bg="#f0f4f8").grid(row=2, column=0, sticky="e")
combo_priority = ttk.Combobox(frame_input, values=["Low", "Medium", "High"], state="readonly", font=font_entry)
combo_priority.grid(row=2, column=1, padx=10, pady=5)

tk.Button(frame_input, text="Add Task", command=add_task, bg="#4CAF50", fg="white", font=font_label, padx=10).grid(row=3, column=0, columnspan=2, pady=10)

# Filter/Search
frame_filter = tk.Frame(root, bg="#f0f4f8")
frame_filter.pack(pady=5)

tk.Label(frame_filter, text="Search:", font=font_label, bg="#f0f4f8").grid(row=0, column=0, padx=5)
entry_search = tk.Entry(frame_filter, font=font_entry)
entry_search.grid(row=0, column=1, padx=5)

tk.Label(frame_filter, text="Status Filter:", font=font_label, bg="#f0f4f8").grid(row=0, column=2, padx=5)
combo_filter = ttk.Combobox(frame_filter, values=["All", "Pending", "Done"], state="readonly", font=font_entry)
combo_filter.set("All")
combo_filter.grid(row=0, column=3, padx=5)

tk.Button(frame_filter, text="Apply Filter", command=apply_filter, bg="#2196F3", fg="white", font=font_label, padx=8).grid(row=0, column=4, padx=10)

# Task Listbox
listbox_tasks = tk.Listbox(root, width=80, height=15, font=("Courier New", 10), selectbackground="#cceeff")
listbox_tasks.pack(pady=10)

# Action Buttons
frame_actions = tk.Frame(root, bg="#f0f4f8")
frame_actions.pack(pady=10)

tk.Button(frame_actions, text="Mark as Done", command=mark_done, bg="#FF9800", fg="white", font=font_label, padx=10).grid(row=0, column=0, padx=10)
tk.Button(frame_actions, text="Delete Task", command=delete_task, bg="#F44336", fg="white", font=font_label, padx=10).grid(row=0, column=1, padx=10)

# Load tasks
load_tasks()

root.mainloop()
conn.close()
