import tkinter as tk
from tkinter import ttk
import sqlite3
import base64
from io import BytesIO
from PIL import Image, ImageTk

def search_items(event):
    for item in table.get_children():
        table.delete(item)

    search_term = search_entry.get().lower()

    cur.execute("SELECT name, image, price, selling_price FROM items WHERE LOWER(name) LIKE ?", ('%' + search_term + '%',))
    rows = cur.fetchall()

    for row in rows:
        name, image, price, selling_price = row
        margin = cal_margin(price, selling_price)
        table.insert('', 'end', values=(name, price, selling_price, margin))

def save_to_database():
    sel_itm = table.selection()[0]  
    name = table.item(sel_itm, 'values')[0]
    
    price = b_price_enter.get()
    selling_price = s_price_enter.get()
    
    conn = sqlite3.connect('stock.db')
    cur = conn.cursor()
    cur.execute("UPDATE items SET price = ?, selling_price = ? WHERE name = ?", (price, selling_price, name))
    conn.commit()
    
    table.item(sel_itm, values=(name, price, selling_price, cal_margin(float(price), float(selling_price))))

def update_margin(event):
    selected_item = table.selection()[0]  
    values = table.item(selected_item, 'values')
    
    name = values[0]
    price = values[-3]  
    selling_price = values[-2] 

    item_name_entry.config(state='normal')  

    item_name_entry.delete(0, tk.END)
    item_name_entry.insert(0, name)

    item_name_entry.config(state='readonly')  

    b_price_enter.delete(0, tk.END)
    b_price_enter.insert(0, price)

    s_price_enter.delete(0, tk.END)
    s_price_enter.insert(0, selling_price)
    
    update_label(price, selling_price)

def update_label(price, selling_price):
    margin = cal_margin(float(price), float(selling_price))
    margin_value.config(text=f"{margin}")

def price_change(event):
    price = b_price_enter.get()
    selling_price = s_price_enter.get()

    if price and selling_price:
        try:
            update_label(float(price), float(selling_price))
        except ValueError:
            margin_value.config(text="wrong input")

def cal_margin(price, selling_price):
    if price and selling_price:
        return "{:.0%}".format((selling_price - price) / price)
    return ""

def get_image_from_base64(image_data):
    if image_data:
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        image.thumbnail((50, 50)) 

        return ImageTk.PhotoImage(image)
    else:
        return None 

















root = tk.Tk()
root.title('Price Edit')

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=3)

search_entry = ttk.Entry(root)
search_entry.grid(row=0, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E)) 
search_entry.bind('<KeyRelease>', search_items)

left_frame = ttk.Frame(root, padding="10")
left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
left_frame.columnconfigure(1, weight=1)

columns = ('Name', 'Price', 'Selling Price', 'Margin')
table = ttk.Treeview(left_frame, columns=columns, show='headings')
table.heading('Name', text='Name')
table.heading('Price', text='Price')
table.heading('Selling Price', text='Selling Price')
table.heading('Margin', text='Margin')

table.bind('<<TreeviewSelect>>', update_margin)

conn = sqlite3.connect('stock.db')
cur = conn.cursor()

cur.execute("SELECT name, image, price, selling_price FROM items")
rows = cur.fetchall()

for row in rows:
    name, image, price, selling_price = row
    margin = cal_margin(price, selling_price)
    imageconverted = get_image_from_base64(image)

    table.insert('', 'end', values=(name, price, selling_price, margin))

table.grid(row=0, column=0, sticky='nsew')

right_frame = ttk.Frame(root, padding="10")
right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

price_change_label = ttk.Label(right_frame, text='Price Change', font=('TkDefaultFont', 16))
price_change_label.grid(row=0, column=0, sticky=(tk.W, tk.N), pady=10)

item_name_entry = ttk.Entry(right_frame, state='disabled')
item_name_entry.grid(row=1, column=0, sticky=(tk.W, tk.E))



b_price_enter = ttk.Entry(right_frame)
b_price_enter.grid(row=2, column=0, pady=10, sticky=(tk.W, tk.E))
b_price_enter.bind('<KeyRelease>', price_change)

s_price_enter = ttk.Entry(right_frame)
s_price_enter.grid(row=3, column=0, pady=10, sticky=(tk.W, tk.E))
s_price_enter.bind('<KeyRelease>', price_change)



margin_label = ttk.Label(right_frame, text='Margin', font=('TkDefaultFont', 14))
margin_label.grid(row=4, column=0, pady=10, sticky=(tk.W))

margin_value = ttk.Label(right_frame, text='[]%', font=('TkDefaultFont', 14))
margin_value.grid(row=5, column=0, pady=10, sticky=(tk.W))

save_button = ttk.Button(right_frame, text='Save')
save_button.grid(row=6, column=0, pady=20, sticky=(tk.W, tk.E))
save_button.config(command=save_to_database)

root.mainloop()
