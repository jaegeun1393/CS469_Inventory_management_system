import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk
import base64
import sqlite3
from datetime import datetime
import io






def open_item_panel(item_id):
    print(item_id)

    item_window = tk.Toplevel()
    item_window.title("Item Details")

    conn = sqlite3.connect('stock.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE stock_date = ?", (item_id,))
    item_data = cur.fetchone()

    tk.Label(item_window, text=f"Name: {item_data[0]}").pack()
    quantity_var = tk.StringVar(value=item_data[4])
    tk.Label(item_window, text="Quantity:").pack()

    q_input = tk.Entry(item_window, textvariable=quantity_var)
    q_input.pack()




    def update_quantity():
        new_quantity = quantity_var.get()
        try:
            new_int = int(new_quantity)
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid input")
            return

        conn = sqlite3.connect('stock.db')
        cur = conn.cursor()    
        cur.execute("SELECT quantity FROM items WHERE stock_date=?", (item_id,))
        old_result = cur.fetchone()

        if old_result:
            print("=", old_result, new_int)

            old_quantity = old_result[0]
            if new_int == 0:
                response = messagebox.askyesno("Remove Item", "Quantity is 0. Do you want to remove the item from the list?")
                if response:

                    conn = sqlite3.connect('stock.db')
                    cur = conn.cursor()
                    cur.execute("DELETE FROM items WHERE stock_date=?", (item_id,))
                    conn.commit()

                    item_window.destroy()
                    refresh_list()  
                    return
                else:
                    return
                
            elif new_int < old_quantity:
                print("=")

                quantity_reduced = old_quantity - new_int
                today_date = datetime.now().strftime("%Y-%m-%d")
                cur.execute("INSERT INTO consume (date, consume) VALUES (?, ?)", (today_date, float(quantity_reduced)))
                conn.commit()

                print(today_date, quantity_reduced)
                

        if new_int >= 0:
            cur.execute("UPDATE items SET quantity=? WHERE stock_date=?", (new_quantity, item_id))
            conn.commit()

        cur.execute("SELECT * FROM consume")
        latest_record = cur.fetchall()
        print(latest_record)

        item_window.destroy()
        refresh_list() 

    tk.Button(item_window, text="Save Changes", command=update_quantity).pack()



def base64_convert(base64_string, tk_label):
    image_data = base64.b64decode(base64_string)
    
    image = Image.open(io.BytesIO(image_data))
    
    resized_image = image.resize((300, 200), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(resized_image)
    
    tk_label.configure(image=photo)
    tk_label.image = photo 




def refresh_list(search_query=None):
    for widget in item_table.winfo_children():
        widget.destroy()

    conn = sqlite3.connect('stock.db') 
    cur = conn.cursor()
    if search_query:
        cur.execute("SELECT stock_date, name, image, price, selling_price, quantity, location FROM items WHERE name LIKE ?", ('%' + search_query + '%',))
    else:
        cur.execute("SELECT stock_date, name, image, price, selling_price, quantity, location FROM items")
    rows = cur.fetchall()
    for index, row in enumerate(rows):
        tk.Label(item_table, text=row[0]).grid(row=index, column=0, sticky="w")
        tk.Label(item_table, text=row[1]).grid(row=index, column=1, sticky="w") 

        image_data = base64.b64decode(row[2])
        image = Image.open(io.BytesIO(image_data))
        resized_image = image.resize((100, 75), Image.Resampling.LANCZOS) 
        photo = ImageTk.PhotoImage(resized_image)
        item_table.images.append(photo) 

        image_label = tk.Label(item_table, image=photo)
        image_label.image = photo  
        image_label.grid(row=index, column=2)

        tk.Label(item_table, text=f"            Price: ${row[3]}").grid(row=index, column=3, sticky="w")
        tk.Label(item_table, text=f"Market Price: ${row[4]}").grid(row=index, column=4, sticky="w")
        tk.Label(item_table, text=f"Quantity: {row[5]}").grid(row=index, column=5, sticky="w")
        tk.Label(item_table, text=f"             {row[6]}").grid(row=index, column=6, sticky="w")  

        item_frame = tk.Frame(item_table)
        item_frame.grid(row=index, column=0, sticky="w")
        image_label.bind("<Button-1>", lambda event, idx=row[0]: open_item_panel(idx))







def scroll(event):
    root_item.configure(scrollregion=root_item.bbox("all"))


def show_item_list():
    global item_table, headertitle, root_item, v_scroll, h_scroll

    root = tk.Tk()  
    root.title("Item List")
    root.geometry("750x680")

    search_frame = tk.Frame(root)
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side="left", padx=6)
    search_button = tk.Button(search_frame, text="Search", command=lambda: refresh_list(search_entry.get()))
    search_button.pack(side="left", padx=6)
    search_frame.pack(side="top", fill="x")

    headertitle = tk.Frame(root)
    headers = ["Stock Date", "Item", "Image", "Price", "Selling Price", "Quantity", "Location"]
    header_widths = [12, 5, 20, 0, 12, 10, 10] 

    for i, (header, width) in enumerate(zip(headers, header_widths)):
        label = tk.Label(headertitle, text=header, font=('bold', 12), width=width)
        label.grid(row=0, column=i, sticky='w')

    headertitle.pack(side="top", fill="x")

    root_item = tk.Canvas(root)
    v_scroll = tk.Scrollbar(root, orient="vertical", command=root_item.yview)
    v_scroll.pack(side="right", fill="y")

    h_scroll = tk.Scrollbar(root, orient="horizontal", command=root_item.xview)
    h_scroll.pack(side="bottom", fill="x")

    root_item.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

    v_scroll.pack(side="right", fill="y")
    h_scroll.pack(side="bottom", fill="x")
    root_item.pack(side="left", fill="both", expand=True)

    item_table = tk.Frame(root_item)
    root_item.create_window((0, 0), window=item_table, anchor="nw")

    item_table.bind("<Configure>", scroll)
    item_table.images = []

    refresh_list() 

    root.mainloop()  

if __name__ == "__main__":
    show_item_list()