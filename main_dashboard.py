import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
import subprocess
import os
from datetime import datetime
import csv
import sys
import time

def check_table_exists(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    result = cursor.fetchone()

    if result:
       return True
    else:
        return False

def Ask_data_export_import():
    def import_items_from_csv(db_path, csv_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS items (name TEXT, image BLOB, price REAL, selling_price REAL, quantity INTEGER, location TEXT, stock_date TEXT, notes TEXT)''')
        csv.field_size_limit(int(1e6))  

        with open(csv_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                try:
                    cur.execute('''INSERT INTO items (name, image, price, selling_price, quantity, location, stock_date, notes) VALUES (:name, :image, :price, :selling_price, :quantity, :location, :stock_date, :notes)''', row)
                except sqlite3.IntegrityError as e:
                    print(f"IntegrityError: {e} for row: {row}")

        conn.commit()

    def import_data():
        csv_path = filedialog.askopenfilename(title="Select CSV file to import", filetypes=[("CSV files", "*.csv")])
        if csv_path:
            db_path = './stock.db'  
            try:
                import_items_from_csv(db_path, csv_path)
                messagebox.showinfo("Import Successful", "Data has been successfully imported.\n Please restart the application to see the changes.")
                sys.exit()  
            except Exception as e:
                messagebox.showerror("Import Failed", f"An error occurred: {e}")


    def export_items_to_csv(db_path, csv_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM items")  
        rows = cursor.fetchall()

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([i[0] for i in cursor.description])  
            for row in rows:
                sanitized_row = ['' if item is None else item for item in row]
                writer.writerow(sanitized_row)

    def export_data():
        csv_path = filedialog.asksaveasfilename(title="Save as", defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if csv_path:
            db_path = './stock.db' 
            try:
                export_items_to_csv(db_path, csv_path)
                messagebox.showinfo("Export Successful", "Data has been successfully exported.")
            except Exception as e:
                messagebox.showerror("Export Failed", f"An error occurred: {e}")

    root = tk.Tk()
    root.title("Import or Export Data")

    import_button = tk.Button(root, text="Import Data", command=import_data)
    import_button.pack(fill=tk.X, padx=50, pady=10)

    export_button = tk.Button(root, text="Export Data", command=export_data)
    export_button.pack(fill=tk.X, padx=50, pady=10)

    root.mainloop()





def import_items_from_csv(db_path, csv_path):
    csv.field_size_limit(sys.maxsize)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS items")
    cur.execute('''CREATE TABLE items (name TEXT, image BLOB, price REAL, selling_price REAL, quantity INTEGER, location TEXT, stock_date TEXT, notes TEXT)''')
    with open(csv_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            try:
                cur.execute('''INSERT INTO items (name, image, price, selling_price, quantity, location, stock_date, notes) VALUES (:name, :image, :price, :selling_price, :quantity, :location, :stock_date, :notes)''', row)
            except OverflowError:
                print(f"OverflowError: int too large to convert for row: {row}")

    conn.commit()

def export_items_to_csv(db_path, csv_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT name, image, price, selling_price, quantity, location, stock_date, notes FROM items")
    items_data = cur.fetchall()

    headers = [description[0] for description in cur.description]

    with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers) 
        for item in items_data:  
            csv_writer.writerow(item)  


def fetch_consume_data():
    try:
        conn = sqlite3.connect('stock.db')
        cur = conn.cursor()
        cur.execute("SELECT strftime('%m', date) AS month, SUM(consume) FROM consume GROUP BY month")
        data = cur.fetchall()

        months = []
        sales = []
        for row in data:
            month_num = int(row[0])
            month_name = datetime(1900, month_num, 1).strftime('%b').upper()
            months.append(month_name)
            sales.append(row[1])

        return months, sales
    
    except sqlite3.OperationalError as e:
        if "no such table: consume" in str(e):
            return [], []  
        else:
            raise  

def get_total_consume():
    try:
        conn = sqlite3.connect('stock.db')
        cur = conn.cursor()

        current_month = datetime.now().strftime("%Y-%m")

        cur.execute("SELECT date, consume FROM consume ORDER BY date DESC LIMIT 1")
        latest_record = cur.fetchone()

        total_consumption = 0

        if latest_record:
            latest_date, _ = latest_record
            if datetime.strptime(latest_date, "%Y-%m-%d").strftime("%Y-%m") == current_month:
                cur.execute("SELECT SUM(consume) FROM consume WHERE strftime('%Y-%m', date) = ?", (current_month,))
                result = cur.fetchone()
                total_consumption = result[0] if result[0] is not None else 0

        return total_consumption
    except sqlite3.OperationalError as e:
        if "no such table: consume" in str(e):
            return 0 
        else:
            raise  


def create_consume(db_path='stock.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute('''CREATE TABLE IF NOT EXISTS consume (id INTEGER PRIMARY KEY, date TEXT NOT NULL, consume REAL NOT NULL)''')
    
    conn.commit()
create_consume()







def i_loc():
    global db_path, total_quantity, total_month_quantity, store_items, total_consume
    script_path = os.path.abspath(r".\scripts\location.py")
    loading = subprocess.Popen(["python", script_path])

    while loading.poll() is None:
        time.sleep(0.5)

    total_quantity = total_items(db_path)
    total_month_quantity = get_total_order()
    store_items = get_items(db_path)
    total_consume = get_total_consume()

    update_display()

def i_search():
    global db_path, total_quantity, total_month_quantity, store_items, total_consume
    script_path = os.path.abspath(r".\scripts\search.py")
    loading = subprocess.Popen(["python", script_path])

    while loading.poll() is None:
        time.sleep(0.5)

    total_quantity = total_items(db_path)
    total_month_quantity = get_total_order()
    store_items = get_items(db_path)
    total_consume = get_total_consume()

    update_display()

def i_add():
    global db_path, total_quantity, total_month_quantity, store_items, total_consume
    script_path = os.path.abspath(r".\scripts\Inventory.py")
    loading = subprocess.Popen(["python", script_path])

    while loading.poll() is None:
        time.sleep(0.5)

    total_quantity = total_items(db_path)
    total_month_quantity = get_total_order()
    store_items = get_items(db_path)
    total_consume = get_total_consume()

    update_display()

def i_edit():
    global db_path, total_quantity, total_month_quantity, store_items, total_consume
    script_path = os.path.abspath(r".\scripts\price_edit.py")
    loading = subprocess.Popen(["python", script_path])

    while loading.poll() is None:
        time.sleep(0.5)

    total_quantity = total_items(db_path)
    total_month_quantity = get_total_order()
    store_items = get_items(db_path)
    total_consume = get_total_consume()

    update_display()

def i_coonsume():
    global db_path, total_quantity, total_month_quantity, store_items, total_consume
    script_path = os.path.abspath(r".\scripts\item_use.py")
    loading = subprocess.Popen(["python", script_path])

    while loading.poll() is None:
        time.sleep(0.5)

    total_quantity = total_items(db_path)
    total_month_quantity = get_total_order()
    store_items = get_items(db_path)
    total_consume = get_total_consume()

    update_display()


def get_total_order():
    conn = sqlite3.connect('stock.db')
    cur = conn.cursor()

    cur.execute("SELECT strftime('%Y-%m', stock_date) AS YearMonth FROM items ORDER BY YearMonth DESC LIMIT 1")
    newest_month = cur.fetchone()
    
    if newest_month is None:
        return 0

    cur.execute("SELECT SUM(quantity) FROM items WHERE strftime('%Y-%m', stock_date) = ?", (newest_month[0],))
    total_quantity = cur.fetchone()[0]
    
    return total_quantity if total_quantity is not None else 0

def total_items(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT * FROM items")
    data = cur.fetchall()
    total = 0
    for item in data:
        total += item[4]
    return total

def get_items(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT name, quantity, location FROM items")
    data = cur.fetchall()
    return data













db_path = 'stock.db'
table_name = 'items'
total_quantity = 0
total_month_quantity = 0
store_items = []
total_consume = 0

if check_table_exists(db_path, table_name):
    total_quantity = total_items(db_path)
    total_month_quantity = get_total_order()
    store_items = get_items(db_path)
    total_consume = get_total_consume()
months, sales = fetch_consume_data()



root = tk.Tk()
root.title("Inventory Management System")
root.geometry("1100x600")  
root.configure(bg='white') 

s_menu = tk.Frame(root, bd=2, relief="raised", padx=5, pady=5, bg='#2B2748')
s_menu.pack(side="left", fill="y", padx=2)

style = ttk.Style()
style.theme_use('clam')

style.configure('TButton', background='#2B2748', foreground='white')
style.configure('TButton', borderwidth=0)

s_menu = tk.Frame(root, bd=2, relief="raised", padx=5, pady=5, bg='#2B2748')
s_menu.pack(side="left", fill="y", padx=2)

bts = ["Home", "Search", "Location", "Price Edit", "Consumption", "Item Add"]
for btn_txt in bts:
    if btn_txt == "Item Add":
        button = ttk.Button(s_menu, text=btn_txt, style='TButton', command=i_add)
    elif btn_txt == "Search":
        button = ttk.Button(s_menu, text=btn_txt, style='TButton', command=i_search)
    elif btn_txt == "Location":
        button = ttk.Button(s_menu, text=btn_txt, style='TButton', command=i_loc)
    elif btn_txt == "Price Edit":
        button = ttk.Button(s_menu, text=btn_txt, style='TButton', command=i_edit)
    elif btn_txt == "Consumption":
        button = ttk.Button(s_menu, text=btn_txt, style='TButton', command=i_coonsume)
    else:
        button = ttk.Button(s_menu, text=btn_txt, style='TButton')
    button.pack(fill="x", pady=2)

bot_button = ttk.Button(s_menu, text="Import / Export", style='TButton', command=Ask_data_export_import)
bot_button.pack(fill="x", side="bottom", pady=2)  


numbers_frame = tk.Frame(root, pady=5)
numbers_frame.pack(fill="x")
numbers_frame.configure(bg='white') 


def update_display():
    global total_quantity, total_consume, total_month_quantity

    for widget in numbers_frame.winfo_children():
        widget.destroy()

    number_displays = [
        ("Total Item", str(total_quantity)),
        ("Total Consume", str(total_consume)),
        ("Total Order", str(total_month_quantity)),
    ]

    
    for text, number in number_displays:
        frame = tk.Frame(numbers_frame, bd=2, relief="groove", padx=10, pady=10, bg='white')
        tk.Label(frame, text=text, bg='white').pack()
        tk.Label(frame, text=number, font=("Arial", 24), bg='white').pack()
        tk.Label(frame, text="For this month", bg='white').pack()
        frame.pack(side="left", fill="both", expand=True, padx=5)
update_display()


main_content = tk.Frame(root)
main_content.pack(fill="both", expand=True, pady=5)

graph_width_ratio = 0.8  
table_width_ratio = 0.2 

window_width = root.winfo_screenwidth()
graph_width = int(window_width * graph_width_ratio)
table_width = int(window_width * table_width_ratio)

fig, ax = plt.subplots(figsize=(5, 3)) 
ax.plot(months, sales)
ax.set_title("Produce Sales in Thousands (USD)")
ax.set_xlabel("Month")
ax.set_ylabel("Sales")

canvas = FigureCanvasTkAgg(fig, master=main_content)
canvas.draw()
graph_widget = canvas.get_tk_widget()
graph_widget.pack(side="left", fill="both", expand=True)

table_frame = tk.Frame(main_content, width=table_width)
table_frame.pack(side="left", fill="y", expand=False)

columns = ("item_name", "amount", "location")
tree = ttk.Treeview(table_frame, columns=columns, show="headings")

for col in columns:
    tree.column(col, width=int(table_width / len(columns)), anchor="center")

for col in columns:
    tree.heading(col, text=col.capitalize())

for item in store_items:
    tree.insert("", "end", values=item)

tree.pack(side="top", fill="both", expand=True)

table_frame.pack_propagate(False)

root.mainloop()
