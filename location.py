from tkinter import ttk, Tk, PhotoImage
import sqlite3
from PIL import Image, ImageTk
import base64
import io

def search_items():
    search = search_entry.get()

    conn = sqlite3.connect('stock.db')  
    cur = conn.cursor()
    cur.execute('''SELECT name, image, quantity FROM items WHERE location = ?''', (search,))
    data = cur.fetchall()
    
    for item in storage_table.get_children():
        storage_table.delete(item)
    
    search = search_entry.get()
    location_frame.config(text=f"Location: {search}", style="White.TLabelframe")
    storage_table.image_refs = [] 

    for item in data:
        imgdata = base64.b64decode(item[1])
        image = Image.open(io.BytesIO(imgdata))
        photo = ImageTk.PhotoImage(image.resize((20, 20), Image.Resampling.LANCZOS))
        
        storage_table.image_refs.append(photo)
        
        storage_table.insert('', 'end', image=photo, values=(item[0], item[2]))


def clipboard(event):
    for s_item in loc_table.selection():
        item = loc_table.item(s_item)
        location = item['values'][0]  

        root.clipboard_clear()
        root.clipboard_append(location)


def fill_loc_table():
    conn = sqlite3.connect('stock.db')  
    cur = conn.cursor()

    cur.execute('''SELECT location, SUM(quantity) FROM items GROUP BY location''')
    locs = cur.fetchall()

    for loc in locs:
        loc_table.insert('', 'end', values=(loc[0], loc[1]))







root = Tk()
root.title("Inventory Search")
root.configure(bg='white') 

style = ttk.Style()
style.configure("White.TFrame", background="white")

root.geometry('800x400')
root.resizable(width=False, height=False)

search_frame = ttk.Frame(root, style="White.TFrame")
search_frame.pack(fill='x', padx=10, pady=5)

search_label = ttk.Label(search_frame, text="Search Location:", background="white")
search_label.pack(side='left', padx=5)

search_entry = ttk.Entry(search_frame)
search_entry.pack(side='left', padx=5, expand=True, fill='x')

search_button = ttk.Button(search_frame, text="Search", command=search_items)
search_button.pack(side='left', padx=5)

bottom_frame = ttk.Frame(root, style="White.TFrame")

bottom_frame.pack(fill='both', expand=True, padx=10, pady=5)

loc_search_frame = ttk.LabelFrame(bottom_frame, text="Location:", style="White.TLabelframe")
loc_search_frame.grid(row=0, column=0, sticky='nsew', padx=(10, 5), pady=5)


bottom_frame.grid_columnconfigure(0, weight=1)

storage_table = ttk.Treeview(loc_search_frame, columns=('Item Name', 'Image', 'Quantity'))
storage_table.heading('#0', text='Image')
storage_table.heading('#1', text='Item Name')
storage_table.heading('#2', text='Quantity')
storage_table.image_refs = []

storage_table.pack(fill='both', expand=True)

location_frame = ttk.LabelFrame(bottom_frame, text="Location")
location_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 10), pady=5)


bottom_frame.grid_columnconfigure(1, weight=1)  
loc_table = ttk.Treeview(location_frame, columns=('Location', 'Quantity'), show='headings')

loc_table.column('Location',  width=100, anchor='w')  
loc_table.column('Quantity', width=100, anchor='center')  

loc_table.heading('Location', text='Location')
loc_table.heading('Quantity', text='Quantity')

loc_table.pack(fill='both', expand=True)
fill_loc_table()

loc_table.bind('<<TreeviewSelect>>', clipboard)



bottom_frame.grid_columnconfigure(0, weight=40) 
bottom_frame.grid_columnconfigure(1, weight=2)  

root.mainloop()
