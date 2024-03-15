import tkinter as tk
from tkinter import ttk
import sqlite3
from PIL import Image, ImageTk
import io
import base64

def debug_sql(query, params):
    return query.replace("?", "{}").format(*params)

def item_detail(event=None):
    selected_item = table.selection()
    name = table.item(selected_item[0], 'values')[0]

    try:
        conn = sqlite3.connect('stock.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM items WHERE name = ?", (str(name),))
        rows = cur.fetchall()

        if rows:
            details_text[0].set(f"Item name: {rows[0][0]}")
            details_text[1].set(f"Quantity: {rows[0][4]}")
            details_text[2].set(f"Location: {rows[0][5]}")
            details_text[3].set(f"Price: {rows[0][2]}")
            details_text[4].set(f"Selling Price: {rows[0][3]}")
            details_text[5].set(f"Note: {rows[0][7]}")
            details_text[6].set(f"Stock Date: {rows[0][6]}")


            print(rows[0][0])
            print(rows[0][1])

            image_data = base64.b64decode(rows[0][1])
            image = Image.open(io.BytesIO(image_data))
            image = image.resize((300, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            img_label.config(image=photo)
            img_label.image = photo  
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()



def load_items(search=''):
    conn = sqlite3.connect('stock.db')
    cur = conn.cursor()
    cur.execute("SELECT name, quantity, location FROM items WHERE name LIKE ?", ('%' + search + '%',))
    rows = cur.fetchall()

    return rows

def refresh_item_list(event=None):
    search = search_var.get()
    for i in table.get_children():
        table.delete(i)

    for item in load_items(search):
        table.insert('', 'end', values=item)

















root = tk.Tk()
root.geometry("600x450") 
root.title("Item Quantity")
root.configure(bg="white")

search_frame = tk.Frame(root)
search_frame.pack(padx=10, pady=12)
search_frame.configure(bg="white")


search_var = tk.StringVar()
search_label = tk.Label(search_frame, text="Search Bar", bg="white")
search_entry = tk.Entry(search_frame, textvariable=search_var, bg="light gray", width=50)
search_label.pack(side=tk.LEFT, padx=(10, 2))
root.configure(bg="white")

search_entry.pack(side=tk.LEFT, padx=(2, 10))
search_frame.pack(fill=tk.X)

search_entry.bind('<KeyRelease>', refresh_item_list)

details_frame = tk.Frame(root)
details_frame.configure(bg="white")

img_label = tk.Label(details_frame, text="IMG", bg="grey")
img_label.pack()
 
details_labels = ["Item name:                                                                                 ", "Quantity:", "Location:", "Price:", "Selling Price:", "Note:", "Stock Date:"]
details_text = [tk.StringVar(value=lbl) for lbl in details_labels]

for i in range(len(details_labels)):
    tk.Label(details_frame, textvariable=details_text[i], bg="white").pack(anchor='w')

details_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

list_frame = tk.Frame(root)
table = ttk.Treeview(list_frame, columns=('Item Name', 'Amount', 'Location'), show='headings')

table.heading('Item Name', text='Item Name')
table.heading('Amount', text='Amount')
table.heading('Location', text='Location')
table.column('Item Name', width=100, stretch=False)
table.column('Amount', width=60, stretch=False)
table.column('Location', width=100, stretch=False)
table.bind('<<TreeviewSelect>>', item_detail) 

scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=table.yview)
table.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

table.pack(expand=True, fill='both')
list_frame.pack(side=tk.RIGHT, expand=True, fill='both')

refresh_item_list()
root.mainloop()